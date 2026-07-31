const std = @import("std");
const rl = @import("raylib");
const utils = @import("utils.zig");

const main = @import("main.zig");

const Tile = enum { none, ground, wall, path };

const MinimapType = enum { grid, bsp };

pub const Room = struct {
    x: i32,
    y: i32,
    w: i32,
    h: i32,

    pub fn init(x: i32, y: i32, w: i32, h: i32) @This() {
        return .{ .x = x, .y = y, .w = w, .h = h };
    }

    pub fn centerx(self: @This()) i32 {
        return self.x + @divFloor(self.w, 2);
    }

    pub fn centery(self: @This()) i32 {
        return self.y + @divFloor(self.h, 2);
    }

    pub fn right(self: @This()) i32 {
        return self.x + self.w;
    }

    pub fn bottom(self: @This()) i32 {
        return self.y + self.h;
    }

    pub fn scale(self: @This(), s: f32) @This() {
        return .init(
            @intFromFloat(@as(f32, @floatFromInt(self.x)) * s),
            @intFromFloat(@as(f32, @floatFromInt(self.y)) * s),
            @intFromFloat(@as(f32, @floatFromInt(self.w)) * s),
            @intFromFloat(@as(f32, @floatFromInt(self.h)) * s),
        );
    }
};

pub fn World(comptime world_w: usize, comptime world_h: usize) type {
    const world_size = world_w * world_h;

    return struct {
        const Self = @This();

        grid: [world_size]Tile,
        root_node: *Node,
        model: rl.Model,
        minimap_type: MinimapType = .bsp,

        pub fn init(gpa: std.mem.Allocator, rand: std.Random) !Self {
            var grid: [world_size]Tile = [_]Tile{.none} ** (world_size);

            const root_node = try genNode(
                gpa,
                rand,
                &grid,
                .init(0, 0, @intCast(world_w), @intCast(world_h)),
                20,
            );

            markWalls(&grid);

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

        pub fn update(self: *Self) void {
            if (rl.isKeyPressed(.one)) self.minimap_type = .grid;
            if (rl.isKeyPressed(.two)) self.minimap_type = .bsp;
        }

        pub fn draw(self: *Self) void {
            if (self.minimap_type == .grid) {
                const s: f32 = 0.5;

                for (0..self.grid.len) |i| {
                    const x = i % world_w;
                    const y = i / world_w;
                    rl.drawCube(
                        .init(@floatFromInt(x), 0, @floatFromInt(y)),
                        s,
                        s,
                        s,
                        switch (self.grid[i]) {
                            .ground => .dark_brown,
                            .path => .light_gray,
                            .wall => .orange,
                            else => .black,
                        },
                    );
                }
            }

            if (self.minimap_type == .bsp) {
                drawNode(self.root_node);
            }
        }

        pub fn drawNode(node: *Node) void {
            switch (node.content) {
                .leaf => |inner| {
                    // rect borders
                    const color: rl.Color = .init(0, 240, 0, 255);
                    const rect = node.room; // no scaling needed if S == 1; see note below
                    const rx: f32 = @floatFromInt(rect.x);
                    const ry: f32 = @floatFromInt(rect.y);
                    const rw: f32 = @floatFromInt(rect.w);
                    const rh: f32 = @floatFromInt(rect.h);

                    const center: rl.Vector3 = .init(
                        rx + rw / 2,
                        0,
                        ry + rh / 2,
                    );
                    const p1: rl.Vector3 = .init(center.x - rw / 2, center.y, center.z - rh / 2);
                    const p2: rl.Vector3 = .init(center.x + rw / 2, center.y, center.z - rh / 2);
                    const p3: rl.Vector3 = .init(center.x + rw / 2, center.y, center.z + rh / 2);
                    const p4: rl.Vector3 = .init(center.x - rw / 2, center.y, center.z + rh / 2);
                    rl.drawLine3D(p1, p2, color);
                    rl.drawLine3D(p2, p3, color);
                    rl.drawLine3D(p3, p4, color);
                    rl.drawLine3D(p4, p1, color);

                    // plane itself
                    const ix: f32 = @floatFromInt(inner.x);
                    const iy: f32 = @floatFromInt(inner.y);
                    const iw: f32 = @floatFromInt(inner.w);
                    const ih: f32 = @floatFromInt(inner.h);

                    rl.drawPlane(
                        .init(
                            ix + iw / 2,
                            0,
                            iy + ih / 2,
                        ),
                        .init(iw, ih),
                        node.color,
                    );
                },
                .children => |c| {
                    // node has children; for each child node, draw corridor between its rect centers
                    const c0x: f32 = @floatFromInt(c[0].room.centerx());
                    const c0y: f32 = @floatFromInt(c[0].room.centery());
                    const c1x: f32 = @floatFromInt(c[1].room.centerx());
                    const c1y: f32 = @floatFromInt(c[1].room.centery());

                    rl.drawCylinderEx(
                        .init(c0x, 0.1, c0y),
                        .init(c1x, 0.1, c1y),
                        0.4,
                        0.4,
                        8,
                        .light_gray,
                    );

                    drawNode(c[0]);
                    drawNode(c[1]);
                },
            }
        }

        pub const Node = struct {
            room: Room,
            content: union(enum) {
                children: [2]*Node,
                leaf: Room,
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

        const MIN_ROOM_SIZE: i32 = 8;

        fn markWalls(grid: *[world_size]Tile) void {
            // if a ground tile borders a none tile, it gets set to wall
            // can modify while iterating since we only modify to wall (we don't check for it)
            for (0..world_h) |y| {
                for (0..world_w) |x| {
                    const i = y * world_w + x;

                    if (grid[i] != .none) continue;

                    if (isOccupied(grid, x, y, -1, 0) or
                        isOccupied(grid, x, y, 1, 0) or
                        isOccupied(grid, x, y, 0, -1) or
                        isOccupied(grid, x, y, 0, 1) or
                        isOccupied(grid, x, y, -1, -1) or
                        isOccupied(grid, x, y, 1, -1) or
                        isOccupied(grid, x, y, 1, 1) or
                        isOccupied(grid, x, y, -1, 1))
                    {
                        grid[i] = .wall;
                    }
                }
            }
            return;
        }

        fn isOccupied(grid: *[world_size]Tile, x: usize, y: usize, dx: isize, dy: isize) bool {
            const nx = @as(isize, @intCast(x)) + dx;
            const ny = @as(isize, @intCast(y)) + dy;
            if (nx < 0 or ny < 0 or nx >= world_w or ny >= world_h) return false;
            const t = grid[@as(usize, @intCast(ny)) * world_w + @as(usize, @intCast(nx))];
            return t == .ground or t == .path;
        }

        fn genNode(gpa: std.mem.Allocator, rand: std.Random, grid: *[world_size]Tile, room: Room, max_leaves: usize) !*Node {
            var node = try gpa.create(Node);
            node.color = .init(
                rand.int(u8),
                rand.int(u8),
                rand.int(u8),
                255,
            );
            node.room = room;
            node.paths = .empty;

            // precondition: node rect size (width and height) is both > MIN_ROOM_SIZE
            std.debug.assert(node.room.w >= MIN_ROOM_SIZE);
            std.debug.assert(node.room.h >= MIN_ROOM_SIZE);

            // --- LLM BEGIN!
            // split direction, weighted by current aspect ratio
            // (horizontally means the split cut is along the x-axis)
            const ratio: f32 = @as(f32, @floatFromInt(node.room.w)) / @as(f32, @floatFromInt(node.room.h));
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

            var split1: Room = undefined;
            var split2: Room = undefined;
            const inner_proportion: rl.Vector2 = .init(0.6, 0.8);

            // finalize split direction given the randomness and biases
            if (split_dir == .hor) {
                // if can't split horizontally, check if it can split vertically
                if (node.room.w < 2 * MIN_ROOM_SIZE) {
                    split_dir = .none;
                    if (node.room.h >= 2 * MIN_ROOM_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .ver;
                    }
                }
            } else if (split_dir == .ver) {
                // if can't split horizontally, check if it can split vertically
                if (node.room.h < 2 * MIN_ROOM_SIZE) {
                    split_dir = .none;
                    if (node.room.w >= 2 * MIN_ROOM_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .hor;
                    }
                }
            }

            // create the nodes based on whether we split or not
            if (split_dir == .none) {
                // can't split anymore (it's are leaf)
                // create an inner rectangle which is a bit smaller
                const inner_min_w: i32 = @intFromFloat(@floor(inner_proportion.x * @as(f32, @floatFromInt(node.room.w))));
                const inner_max_w: i32 = @intFromFloat(@floor(inner_proportion.y * @as(f32, @floatFromInt(node.room.w))));
                const inner_min_h: i32 = @intFromFloat(@floor(inner_proportion.x * @as(f32, @floatFromInt(node.room.h))));
                const inner_max_h: i32 = @intFromFloat(@floor(inner_proportion.y * @as(f32, @floatFromInt(node.room.h))));

                // position that rectangle with a uniformly random offset within the larger rectangle
                const inner_w = rand.intRangeAtMost(i32, inner_min_w, inner_max_w);
                const inner_h = rand.intRangeAtMost(i32, inner_min_h, inner_max_h);
                // 1 and -1 because we don't want bordering rooms
                const inner_x = rand.intRangeAtMost(i32, 1, node.room.w - inner_w - 1) + node.room.x;
                const inner_y = rand.intRangeAtMost(i32, 1, node.room.h - inner_h - 1) + node.room.y;

                node.content = .{
                    .leaf = .init(inner_x, inner_y, inner_w, inner_h),
                };

                // mark territory in the grid
                for (@intCast(node.content.leaf.y)..@intCast(node.content.leaf.bottom())) |y| {
                    for (@intCast(node.content.leaf.x)..@intCast(node.content.leaf.right())) |x| {
                        grid[y * world_w + x] = .ground;
                    }
                }

                return node;
            }

            // can split yaay!!
            if (split_dir == .hor) {
                // we can only split if our size is at least 2 * MIN_ROOM_SIZE
                // decide the split proportion
                const split_min_x = MIN_ROOM_SIZE;
                const split_max_x = node.room.w - MIN_ROOM_SIZE;
                const split_x: i32 = rand.intRangeAtMost(i32, split_min_x, split_max_x);

                // convert proportion to two split rectangles (rooms)
                split1 = .init(
                    node.room.x,
                    node.room.y,
                    split_x,
                    node.room.h,
                );
                split2 = .init(
                    node.room.x + split_x,
                    node.room.y,
                    node.room.w - split_x,
                    node.room.h,
                );
            } else if (split_dir == .ver) {
                const split_min_y = MIN_ROOM_SIZE;
                const split_max_y = node.room.h - MIN_ROOM_SIZE;
                const split_y = rand.intRangeAtMost(i32, split_min_y, split_max_y);
                split1 = .init(
                    node.room.x,
                    node.room.y,
                    node.room.w,
                    split_y,
                );
                split2 = .init(
                    node.room.x,
                    node.room.y + split_y,
                    node.room.w,
                    node.room.h - split_y,
                );
            }

            // carve the path between the two nodes in the grid since we just splat
            const cx1: usize = @intCast(split1.centerx());
            const cy1: usize = @intCast(split1.centery());
            const cx2: usize = @intCast(split2.centerx());
            const cy2: usize = @intCast(split2.centery());

            if (split_dir == .hor) {
                // draw a horizontal line (changes in x)
                const y = cy1;
                var x = @min(cx1, cx2);
                while (x <= @max(cx1, cx2)) : (x += 1) {
                    if (grid[y * world_w + x] == .none) grid[y * world_w + x] = .path;
                }
            } else if (split_dir == .ver) {
                // draw a vertical line (changes in y)
                const x = cx1;
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
