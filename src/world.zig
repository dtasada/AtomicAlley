const std = @import("std");
const rl = @import("raylib");
const utils = @import("utils.zig");

const Self = @This();

const main = @import("main.zig");

tiles: std.ArrayList(Tile),
root_node: *Node,
model: rl.Model,

// "tiles" is the resolution of the world measured in tiles
pub fn init(gpa: std.mem.Allocator, rand: std.Random, resolution: [2]u32) !Self {
    var world: Self = .{
        .tiles = .empty,
        .root_node = try genNode(
            gpa,
            rand,
            .init(
                0,
                0,
                @floatFromInt(resolution[0]),
                @floatFromInt(resolution[1]),
            ),
            20,
        ),
        .model = try rl.loadModel("resources/models/cube.obj"),
    };
    // _ = try genCorridors(alloc, world.root_node);
    try world.genTiles(gpa, world.root_node);
    return world;
}

pub fn deinit(self: *Self, gpa: std.mem.Allocator) void {
    self.root_node.deinit(gpa);
    self.tiles.deinit(gpa);
    rl.unloadModel(self.model);
    gpa.destroy(self.root_node);
}

pub fn genTiles(self: *Self, gpa: std.mem.Allocator, node: *Node) !void {
    // only if it's a leaf, we operate on it
    switch (node.content) {
        .children => |c| {
            // node has children, so shift focus on them
            try self.genTiles(gpa, c[0]);
            try self.genTiles(gpa, c[1]);
        },
        .leaf => |inner| {
            // node is a child, so has an inner rect (an actual room); we need to process it
            for (0..@intFromFloat(inner.height)) |y| {
                for (0..@intFromFloat(inner.width)) |x| {
                    const s: f32 = 5;
                    const tile_pos: rl.Vector3 = .init(
                        (inner.x + @as(f32, @floatFromInt(x))) * s,
                        0,
                        (inner.y + @as(f32, @floatFromInt(y))) * s,
                    );
                    try self.tiles.append(gpa, .{
                        .pos = tile_pos,
                        .index = 0,
                    });
                }
            }
        },
    }
}

pub fn draw(self: Self) void {
    // draw the debug minimap nodes
    self.drawNode(self.root_node);

    // draw the actual tiles
    for (self.tiles.items) |tile| {
        rl.drawModel(self.model, tile.pos, 2, .white);
    }
}

pub fn drawNode(self: Self, node: *Node) void {
    switch (node.content) {
        .children => |c| {
            // node has children; for each child node, draw corridor between its rect centers
            rl.drawCylinderEx(
                .init(c[0].rect.x + c[0].rect.width / 2, 0.1, c[0].rect.y + c[0].rect.height / 2),
                .init(c[1].rect.x + c[1].rect.width / 2, 0.1, c[1].rect.y + c[1].rect.height / 2),
                0.4,
                0.4,
                8,
                .dark_purple,
            );

            // recurse
            self.drawNode(c[0]);
            self.drawNode(c[1]);
        },
        .leaf => |inner| {
            // rect borders
            const color: rl.Color = .init(0, 240, 0, 255);
            const w: f32 = node.rect.width;
            const h: f32 = node.rect.height;
            const center: rl.Vector3 = .init(
                node.rect.x + node.rect.width / 2,
                0,
                node.rect.y + node.rect.height / 2,
            );
            const p1: rl.Vector3 = .init(center.x - w / 2, center.y, center.z - h / 2);
            const p2: rl.Vector3 = .init(center.x + w / 2, center.y, center.z - h / 2);
            const p3: rl.Vector3 = .init(center.x + w / 2, center.y, center.z + h / 2);
            const p4: rl.Vector3 = .init(center.x - w / 2, center.y, center.z + h / 2);
            rl.drawLine3D(p1, p2, color);
            rl.drawLine3D(p2, p3, color);
            rl.drawLine3D(p3, p4, color);
            rl.drawLine3D(p4, p1, color);

            // plane itself
            rl.drawPlane(
                .init(
                    inner.x + inner.width / 2,
                    0,
                    inner.y + inner.height / 2,
                ),
                .init(inner.width, inner.height),
                node.color,
            );
        },
    }
}

pub const Tile = struct {
    pos: rl.Vector3,
    index: usize,
};

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

const MIN_LEAF_SIZE: f32 = 12;

fn genCorridors(gpa: std.mem.Allocator, rand: std.Random, node: *Node) !rl.Rectangle {
    switch (node.content) {
        .leaf => |size| {
            const x = node.rect.x + (node.rect.width - size[0]) / 2;
            const y = node.rect.y + (node.rect.height - size[1]) / 2;
            return .init(x, y, size[0], size[1]);
        },

        .children => |c| {
            const left = try genCorridors(gpa, c[0]);
            const right = try genCorridors(gpa, c[1]);

            const cx1 = left.x + left.w / 2;
            const cy1 = left.y + left.h / 2;
            const cx2 = right.x + right.w / 2;
            const cy2 = right.y + right.h / 2;

            const width = 2;

            if (rand.boolean()) {
                // Horizontal then Vertical
                const hx = @min(cx1, cx2);
                const hy = cy1 - width / 2;
                const hw = (if (cx1 > cx2) cx1 - cx2 else cx2 - cx1) + width;
                const hh = width;
                try node.paths.append(gpa, .init(hx, hy, hw, hh));

                const vx = cx2 - width / 2;
                const vy = @min(cy1, cy2);
                const vw = width;
                const vh = (if (cy1 > cy2) cy1 - cy2 else cy2 - cy1) + width;
                try node.paths.append(gpa, .init(vx, vy, vw, vh));
            } else {
                // Vertical then Horizontal
                const vx = cx1 - width / 2;
                const vy = @min(cy1, cy2);
                const vw = width;
                const vh = (if (cy1 > cy2) cy1 - cy2 else cy2 - cy1) + width;
                try node.paths.append(gpa, .init(vx, vy, vw, vh));

                const hx = @min(cx1, cx2);
                const hy = cy2 - width / 2;
                const hw = (if (cx1 > cx2) cx1 - cx2 else cx2 - cx1) + width;
                const hh = width;
                try node.paths.append(gpa, .init(hx, hy, hw, hh));
            }

            return if (rand.boolean()) right else left;
        },
    }
}

fn genNode(gpa: std.mem.Allocator, rand: std.Random, rect: rl.Rectangle, max_leaves: usize) !*Node {
    var node = try gpa.create(Node);
    node.color = .init(
        rand.int(u8),
        rand.int(u8),
        rand.int(u8),
        255,
    );
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
    const split_range: rl.Vector2 = .init(0.7, 0.9);

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
        // create an inner rectangle which is a bit smaller
        const inner_w = utils.floatB(rand, split_range.x, split_range.y) * node.rect.width;
        const inner_h = utils.floatB(rand, split_range.x, split_range.y) * node.rect.height;
        const inner_x = utils.floatB(rand, node.rect.x, node.rect.x + node.rect.width - inner_w);
        const inner_y = utils.floatB(rand, node.rect.y, node.rect.y + node.rect.height - inner_h);
        node.content = .{
            .leaf = .init(inner_x, inner_y, inner_w, inner_h),
        };
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

    // create the two nodes
    if (split_dir != .none) {
        node.content = .{
            .children = .{
                try genNode(gpa, rand, split1, max_leaves),
                try genNode(gpa, rand, split2, max_leaves),
            },
        };
    }

    return node;
}
