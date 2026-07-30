const std = @import("std");
const rl = @import("raylib");
const utils = @import("utils.zig");

const main = @import("main.zig");

const Tile = enum { none, ground, wall, path };

pub fn World(comptime world_w: usize, comptime world_h: usize) type {
    return struct {
        const Self = @This();

        grid: [world_w * world_h]Tile,
        root_node: *Node,
        model: rl.Model,

        pub fn init(gpa: std.mem.Allocator, rand: std.Random) !Self {
            var grid: [world_w * world_h]Tile = [_]Tile{.none} ** (world_w * world_h);

            const root_node = try genNode(
                gpa,
                rand,
                &grid,
                .init(0, 0, @floatFromInt(world_w), @floatFromInt(world_h)),
                20,
            );

            return .{
                .grid = grid,
                .root_node = root_node,
                .model = try rl.loadModel("resources/models/cube.obj"),
            };
        }

        pub fn deinit(self: *Self, gpa: std.mem.Allocator) void {
            self.root_node.deinit(gpa);
            rl.unloadModel(self.model);
            gpa.destroy(self.root_node);
        }

        pub fn draw(self: *Self) void {
            drawNode(self.root_node);
            const s: f32 = 0.5;

            for (0..self.grid.len) |i| {
                const x = i % world_w;
                const y = i / world_h;
                rl.drawCube(
                    .init(@floatFromInt(x), 3, @floatFromInt(y)),
                    s,
                    s,
                    s,
                    switch (self.grid[i]) {
                        .ground => .init(137, 207, 240, 255),
                        .path => .gray,
                        else => .white,
                    },
                );
            }
        }

        pub fn drawNode(node: *Node) void {
            const S: f32 = 1;
            switch (node.content) {
                .leaf => |inner| {
                    // rect borders
                    const color: rl.Color = .init(0, 240, 0, 255);
                    const rect = utils.scaleRect(node.rect, S);
                    const center: rl.Vector3 = .init(
                        rect.x + rect.width / 2,
                        0,
                        rect.y + rect.height / 2,
                    );
                    const p1: rl.Vector3 = .init(center.x - rect.width / 2, center.y, center.z - rect.height / 2);
                    const p2: rl.Vector3 = .init(center.x + rect.width / 2, center.y, center.z - rect.height / 2);
                    const p3: rl.Vector3 = .init(center.x + rect.width / 2, center.y, center.z + rect.height / 2);
                    const p4: rl.Vector3 = .init(center.x - rect.width / 2, center.y, center.z + rect.height / 2);
                    rl.drawLine3D(p1, p2, color);
                    rl.drawLine3D(p2, p3, color);
                    rl.drawLine3D(p3, p4, color);
                    rl.drawLine3D(p4, p1, color);

                    // plane itself
                    const scaled_inner = utils.scaleRect(inner, S);
                    rl.drawPlane(
                        .init(
                            scaled_inner.x + scaled_inner.width / 2,
                            0,
                            scaled_inner.y + scaled_inner.height / 2,
                        ),
                        .init(scaled_inner.width, scaled_inner.height),
                        node.color,
                    );
                },
                .children => |c| {
                    drawNode(c[0]);
                    drawNode(c[1]);
                },
            }
        }

        pub const Node = struct {
            rect: rl.Rectangle,
            content: union(enum) {
                children: [2]*Node,
                leaf: rl.Rectangle,
            },
            paths: std.ArrayList(rl.Rectangle),
            color: rl.Color,

            fn deinit(self: *Node, gpa: std.mem.Allocator) void {
                self.paths.deinit(gpa);

                switch (self.content) {
                    .children => |c| {
                        c[0].deinit(gpa);
                        gpa.destroy(c[0]);
                        c[1].deinit(gpa);
                        gpa.destroy(c[1]);
                    },
                    .leaf => {},
                }
            }
        };

        const MIN_LEAF_SIZE: f32 = 8;

        fn genNode(gpa: std.mem.Allocator, rand: std.Random, grid: *[world_w * world_h]Tile, rect: rl.Rectangle, max_leaves: usize) !*Node {
            var node = try gpa.create(Node);
            node.color = .init(92, 64, 51, 255);
            node.rect = rect;
            node.paths = .empty;

            // precondition: node rect size (width and height) is both > MIN_LEAF_SIZE
            std.debug.assert(node.rect.width >= MIN_LEAF_SIZE);
            std.debug.assert(node.rect.height >= MIN_LEAF_SIZE);

            // --- LLM BEGIN!
            // split direction, weighted by current aspect ratio
            // (horizontally means the split cut is along the x-axis)
            const ratio = node.rect.width / node.rect.height;
            // probability of choosing a horizontal split (cutting the width down)
            // 0.5 when square, pulls toward 1.0 as width >>> height, toward 0.0 as height >>> width
            var p_hor: f32 = 0.5;
            const BIAS_STRENGTH: f32 = 0.4; // how strongly elongation is corrected (0 = no bias, 0.5 = max)
            if (ratio > 1.0) {
                p_hor = 0.5 + BIAS_STRENGTH * @min((ratio - 1.0) / 3.0, 1.0);
            } else if (ratio < 1.0) {
                p_hor = 0.5 - BIAS_STRENGTH * @min((1.0 / ratio - 1.0) / 3.0, 1.0);
            }
            // --- LLM END!

            // split direction
            // (horizontally means the products are in the x-axis)
            var split_dir: enum { hor, ver, none } = if (rand.float(f32) < p_hor) .hor else .ver;

            var split1: rl.Rectangle = undefined;
            var split2: rl.Rectangle = undefined;
            const inner_portion: rl.Vector2 = .init(0.55, 0.9);

            if (split_dir == .hor) {
                // if can't split horizontally, check if it can split vertically
                if (node.rect.width < 2 * MIN_LEAF_SIZE) {
                    split_dir = .none;
                    if (node.rect.height >= 2 * MIN_LEAF_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .ver;
                    }
                }
            } else if (split_dir == .ver) {
                // if can't split horizontally, check if it can split vertically
                if (node.rect.height < 2 * MIN_LEAF_SIZE) {
                    split_dir = .none;
                    if (node.rect.width >= 2 * MIN_LEAF_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .hor;
                    }
                }
            }

            if (split_dir == .none) {
                // can't split anymore (it's are leaf)
                // create an inner rectangle which is a bit smaller
                const inner_w = utils.floatB(rand, inner_portion.x, inner_portion.y) * node.rect.width;
                const inner_h = utils.floatB(rand, inner_portion.x, inner_portion.y) * node.rect.height;
                const inner_x = utils.floatB(rand, node.rect.x, node.rect.x + node.rect.width - inner_w);
                const inner_y = utils.floatB(rand, node.rect.y, node.rect.y + node.rect.height - inner_h);
                node.content = .{
                    .leaf = .init(inner_x, inner_y, inner_w, inner_h),
                };

                // mark territory in the grid
                for (@as(usize, @intFromFloat(node.content.leaf.y))..@as(usize, @intFromFloat(node.content.leaf.y + node.content.leaf.height))) |y| {
                    for (@as(usize, @intFromFloat(node.content.leaf.x))..@as(usize, @intFromFloat(node.content.leaf.x + node.content.leaf.width))) |x| {
                        grid[y * world_w + x] = .ground;
                    }
                }

                return node;
            }

            // can split yaay!!
            if (split_dir == .hor) {
                // we can only split if our size is at least 2 * MIN_LEAF_SIZE
                const split_min_x = MIN_LEAF_SIZE;
                const split_max_x = node.rect.width - MIN_LEAF_SIZE;
                const split_x = utils.floatB(rand, split_min_x, split_max_x);
                split1 = .init(
                    node.rect.x,
                    node.rect.y,
                    split_x,
                    node.rect.height,
                );
                split2 = .init(
                    node.rect.x + split_x,
                    node.rect.y,
                    node.rect.width - split_x,
                    node.rect.height,
                );
            } else if (split_dir == .ver) {
                const split_min_y = MIN_LEAF_SIZE;
                const split_max_y = node.rect.height - MIN_LEAF_SIZE;
                const split_y = utils.floatB(rand, split_min_y, split_max_y);
                split1 = .init(
                    node.rect.x,
                    node.rect.y,
                    node.rect.width,
                    split_y,
                );
                split2 = .init(
                    node.rect.x,
                    node.rect.y + split_y,
                    node.rect.width,
                    node.rect.height - split_y,
                );
            }

            // carve the path between the two nodes in the grid since we just splat
            const cx1: usize = @intFromFloat(split1.x + split1.width / 2);
            const cy1: usize = @intFromFloat(split1.y + split1.height / 2);
            const cx2: usize = @intFromFloat(split2.x + split2.width / 2);
            const cy2: usize = @intFromFloat(split2.y + split2.height / 2);

            if (split_dir == .hor) {
                // draw a horizontal line
                const y = cy1; // == cy2
                var x = @min(cx1, cx2);
                while (x <= @max(cx1, cx2)) : (x += 1) {
                    if (grid[y * world_w + x] == .none) grid[y * world_w + x] = .path;
                }
            } else if (split_dir == .ver) {
                // draw a vertical line
                const x = cx1; // == cx2
                var y = @min(cy1, cy2);
                while (y <= @max(cy1, cy2)) : (y += 1) {
                    if (grid[y * world_w + x] == .none) grid[y * world_w + x] = .path;
                }
            }

            // we already confirmed node can split
            node.content = .{
                .children = .{
                    try genNode(gpa, rand, grid, split1, max_leaves),
                    try genNode(gpa, rand, grid, split2, max_leaves),
                },
            };

            return node;
        }
    };
}
