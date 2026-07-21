const std = @import("std");
const rl = @import("raylib");
const utils = @import("utils.zig");

const World = @This();

const main = @import("main.zig");

tiles: std.ArrayList(Tile),
root_node: *Node,

// `tiles` is the resolution of the world measured in tiles
pub fn init(gpa: std.mem.Allocator, rand: std.Random, resolution: [2]u32) !World {
    const world: World = .{
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
    };
    // _ = try genCorridors(alloc, world.root_node);
    return world;
}

pub fn deinit(self: *World, gpa: std.mem.Allocator) void {
    self.root_node.deinit(gpa);
    gpa.destroy(self.root_node);
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

const MIN_LEAF_SIZE: f32 = 16;

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

    // horizontally means the products are in the x-axis
    const splits_horizontally = rand.boolean();

    var split1: rl.Rectangle = undefined;
    var split2: rl.Rectangle = undefined;
    const split_range: rl.Vector2 = .init(0.7, 0.9);

    // check whether current node is too small to split
    const split_axis = if (splits_horizontally) node.rect.width else node.rect.height;
    if (split_axis < 2 * MIN_LEAF_SIZE) {
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
    if (splits_horizontally) {
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
    } else {
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
    node.content = .{
        .children = .{
            try genNode(gpa, rand, split1, max_leaves),
            try genNode(gpa, rand, split2, max_leaves),
        },
    };

    return node;
}
