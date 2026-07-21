const std = @import("std");
const rl = @import("raylib");

const World = @This();

const main = @import("main.zig");

tiles: std.ArrayList(Tile),
root_node: *Node,

// `tiles` is the resolution of the world measured in tiles
pub fn init(alloc: std.mem.Allocator, resolution: [2]u32) !World {
    const world: World = .{
        .root_node = try genNode(alloc, .init(0, 0, resolution[0], resolution[1])),
    };
    _ = try createCorridors(alloc, world.root_node);
    return world;
}

pub fn deinit(self: *World, alloc: std.mem.Allocator) void {
    self.root_node.deinit(alloc);
    alloc.destroy(self.root_node);
}

pub const Tile = struct {
    pos: rl.Vector3,
    index: usize,
};

const Rect = struct {
    x: u32,
    y: u32,
    w: u32,
    h: u32,

    pub fn init(x: u32, y: u32, w: u32, h: u32) Rect {
        return .{
            .x = x,
            .y = y,
            .w = w,
            .h = h,
        };
    }
};

pub const Node = struct {
    rect: Rect,
    content: union(enum) {
        children: [2]*Node,
        leaf: [2]u32,
    },
    paths: std.ArrayList(Rect),

    fn deinit(self: *Node, alloc: std.mem.Allocator) void {
        self.paths.deinit(alloc);

        switch (self.content) {
            .children => |c| {
                c[0].deinit(alloc);
                alloc.destroy(c[0]);
                c[1].deinit(alloc);
                alloc.destroy(c[1]);
            },
            .leaf => {},
        }
    }
};

const MIN_LEAF_SIZE: u32 = 16;

fn createCorridors(alloc: std.mem.Allocator, node: *Node) !Rect {
    switch (node.content) {
        .leaf => |size| {
            const x = node.rect.x + (node.rect.w - size[0]) / 2;
            const y = node.rect.y + (node.rect.h - size[1]) / 2;
            return .init(x, y, size[0], size[1]);
        },

        .children => |c| {
            const left = try createCorridors(alloc, c[0]);
            const right = try createCorridors(alloc, c[1]);

            const cx1 = left.x + left.w / 2;
            const cy1 = left.y + left.h / 2;
            const cx2 = right.x + right.w / 2;
            const cy2 = right.y + right.h / 2;

            const width = 2;

            if (main.rand.boolean()) {
                // Horizontal then Vertical
                const hx = @min(cx1, cx2);
                const hy = cy1 - width / 2;
                const hw = (if (cx1 > cx2) cx1 - cx2 else cx2 - cx1) + width;
                const hh = width;
                try node.paths.append(alloc, .init(hx, hy, hw, hh));

                const vx = cx2 - width / 2;
                const vy = @min(cy1, cy2);
                const vw = width;
                const vh = (if (cy1 > cy2) cy1 - cy2 else cy2 - cy1) + width;
                try node.paths.append(alloc, .init(vx, vy, vw, vh));
            } else {
                // Vertical then Horizontal
                const vx = cx1 - width / 2;
                const vy = @min(cy1, cy2);
                const vw = width;
                const vh = (if (cy1 > cy2) cy1 - cy2 else cy2 - cy1) + width;
                try node.paths.append(alloc, .init(vx, vy, vw, vh));

                const hx = @min(cx1, cx2);
                const hy = cy2 - width / 2;
                const hw = (if (cx1 > cx2) cx1 - cx2 else cx2 - cx1) + width;
                const hh = width;
                try node.paths.append(alloc, .init(hx, hy, hw, hh));
            }

            return if (main.rand.boolean()) right else left;
        },
    }
}

fn genNode(alloc: std.mem.Allocator, rect: Rect) !*Node {
    var node = try alloc.create(Node);
    node.rect = rect;
    node.paths = .empty;

    // stop splitting if too small, return leaf
    if (rect.w < MIN_LEAF_SIZE * 2 or rect.h < MIN_LEAF_SIZE * 2) {
        const w: f32 = @floatFromInt(rect.w);
        const h: f32 = @floatFromInt(rect.h);
        node.content = .{
            .leaf = .{
                // interval: [0.4, 0.6)
                @intFromFloat((0.4 + main.rand.float(f32) / 5) * w),
                @intFromFloat((0.4 + main.rand.float(f32) / 5) * h),
            },
        };
        return node;
    }

    const min = MIN_LEAF_SIZE;
    if (rect.w > rect.h or rect.w == rect.h and main.rand.boolean()) {
        const max = rect.w - MIN_LEAF_SIZE;
        if (min >= max) {
            const w: f32 = @floatFromInt(rect.w);
            const h: f32 = @floatFromInt(rect.h);
            node.content = .{
                .leaf = .{
                    @intFromFloat(main.rand.float(f32) * (w * 0.6 - w * 0.4) + w * 0.4),
                    @intFromFloat(main.rand.float(f32) * (h * 0.6 - h * 0.4) + h * 0.4),
                },
            };
            return node;
        }

        const split = main.rand.intRangeAtMost(u32, min, max);

        node.content = .{
            .children = .{
                try genNode(alloc, .init(rect.x, rect.y, split, rect.h)),
                try genNode(alloc, .init(rect.x + split, rect.y, rect.w - split, rect.h)),
            },
        };
    } else {
        const max = rect.h - MIN_LEAF_SIZE;
        if (min >= max) {
            const w: f32 = @floatFromInt(rect.w);
            const h: f32 = @floatFromInt(rect.h);
            node.content = .{
                .leaf = .{
                    @intFromFloat(main.rand.float(f32) * (w * 0.6 - w * 0.4) + w * 0.4),
                    @intFromFloat(main.rand.float(f32) * (h * 0.6 - h * 0.4) + h * 0.4),
                },
            };
            return node;
        }

        // split horizontal instead
        const split = main.rand.intRangeAtMost(u32, min, max);

        node.content = .{
            .children = .{
                try genNode(alloc, .init(rect.x, rect.y, rect.w, split)),
                try genNode(alloc, .init(rect.x, rect.y + split, rect.w, rect.h - split)),
            },
        };
    }

    return node;
}
