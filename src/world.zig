const std = @import("std");
const rl = @import("raylib");
const utils = @import("utils.zig");
const Palette = @import("Palette.zig");

const main = @import("main.zig");

const Tile = enum { none, ground, hwall, vwall, dwall, path };

const MinimapType = enum { grid, bsp };

const Terrain = union(enum) {
    ground: struct {
        x: f32,
        y: f32,
        w: f32,
        l: f32,
        color: rl.Color,

        pub fn init(x: f32, y: f32, w: f32, l: f32, color: rl.Color, scale: f32) @This() {
            return .{
                .x = (x + w / 2) * scale,
                .y = (y + l / 2) * scale,
                .w = w * scale,
                .l = l * scale,
                .color = color,
            };
        }

        pub fn draw(self: @This()) void {
            rl.drawPlane(
                .init(self.x, 0, self.y),
                .init(self.w, self.l),
                self.color,
            );
        }
    },

    wall: struct {
        // x and y are the CENTER of the rectangle
        // w and h are ENTIRE width and heights (NOT halved)
        x: f32,
        y: f32,
        w: f32,
        l: f32,
        h: f32,
        color: rl.Color,

        pub fn init(x: f32, y: f32, w: f32, l: f32, h: f32, color: rl.Color, scale: f32) @This() {
            // x and y is topleft, and width and height extend from there orthogonally
            return .{
                .x = (x + w / 2) * scale,
                .y = (y + l / 2) * scale,
                .w = w * scale,
                .l = l * scale,
                .h = h * scale,
                .color = color,
            };
        }

        pub fn draw(self: @This()) void {
            rl.drawCube(
                .init(self.x, self.h / 2, self.y),
                self.w,
                self.h,
                self.l,
                self.color,
            );
            rl.drawCubeWires(
                .init(self.x, self.h / 2, self.y),
                self.w,
                self.h,
                self.l,
                .sky_blue,
            );
        }
    },
};

pub const Rect = struct {
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
        terrains: std.ArrayList(Terrain),
        root_node: *Node,
        model: rl.Model,
        minimap_type: MinimapType = .bsp,

        pub fn init(gpa: std.mem.Allocator, rand: std.Random) !Self {
            var grid: [world_size]Tile = [_]Tile{.none} ** (world_size);

            // I. start the BSP by generating root node (which will recursively generate)
            // the children as well
            const root_node = try genNode(
                gpa,
                rand,
                &grid,
                .init(0, 0, @intCast(world_w), @intCast(world_h)),
                20,
            );

            // II. widen the paths from 1 -> 3 units wide
            widenWalls(&grid);

            // III. do some cellular automata to generate walls around ground and paths
            markWalls(&grid);

            // IV. greedy merge walls
            var terrains: std.ArrayList(Terrain) = .empty;
            const scale: f32 = 5;
            const wall_height: f32 = 4;
            try mergeWalls(gpa, &grid, &terrains, .horizontal, scale, wall_height);
            try mergeWalls(gpa, &grid, &terrains, .vertical, scale, wall_height);
            try createDiagonals(gpa, &grid, &terrains, scale, wall_height);

            // V. greedy mesh ground
            try mergeGround(gpa, &grid, &terrains, scale);

            // return finalized world
            return .{
                .grid = grid,
                .root_node = root_node,
                .terrains = terrains,
                .model = try rl.loadModel("resources/models/cube.obj"),
            };
        }

        pub fn deinit(self: *Self, gpa: std.mem.Allocator) void {
            self.root_node.deinit(gpa);
            rl.unloadModel(self.model);
            gpa.destroy(self.root_node);
            self.terrains.deinit(gpa);
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

                    switch (self.grid[i]) {
                        .hwall, .vwall, .dwall, .none, .ground, .path => continue,
                    }

                    rl.drawCube(
                        .init(@floatFromInt(x), 0, @floatFromInt(y)),
                        s,
                        s,
                        s,
                        switch (self.grid[i]) {
                            .path => .sky_blue,
                            .none => .black,
                            else => .black,
                        },
                    );
                }

                // terrain
                for (self.terrains.items) |terrain| {
                    switch (terrain) {
                        inline else => |t| t.draw(),
                    }
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
                    const rect = node.rect; // no scaling needed if S == 1; see note below
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
                    const c0x: f32 = @floatFromInt(c[0].rect.centerx());
                    const c0y: f32 = @floatFromInt(c[0].rect.centery());
                    const c1x: f32 = @floatFromInt(c[1].rect.centerx());
                    const c1y: f32 = @floatFromInt(c[1].rect.centery());

                    rl.drawCylinderEx(
                        .init(c0x, -1, c0y),
                        .init(c1x, -1, c1y),
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
            rect: Rect,
            content: union(enum) {
                children: [2]*Node,
                leaf: Rect,
            },
            color: rl.Color,

            fn deinit(self: *Node, gpa: std.mem.Allocator) void {
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

        const MIN_RECT_SIZE: i32 = 16;

        fn createDiagonals(
            gpa: std.mem.Allocator,
            grid: *[world_size]Tile,
            out: *std.ArrayList(Terrain),
            scale: f32,
            wall_height: f32,
        ) !void {
            // creates Wall objects from diagonal entries in the grid
            for (0..world_h) |y| {
                for (0..world_w) |x| {
                    const i = y * world_w + x;
                    if (grid[i] == .dwall) {
                        try out.append(
                            gpa,
                            .{
                                .wall = .init(
                                    @floatFromInt(x),
                                    @floatFromInt(y),
                                    1,
                                    1,
                                    wall_height,
                                    .maroon,
                                    scale,
                                ),
                            },
                        );
                    }
                }
            }
        }

        fn mergeWalls(
            gpa: std.mem.Allocator,
            grid: *[world_size]Tile,
            out: *std.ArrayList(Terrain),
            direction: enum { horizontal, vertical },
            scale: f32,
            wall_height: f32,
        ) !void {
            if (direction == .horizontal) {
                // iterate over all y levels
                for (0..world_h) |y| {
                    // reset x
                    var x: usize = 0;

                    // go over all x levels until we have to reset
                    while (x < world_w) {
                        const i = y * world_w + x;

                        // check if we can start merging
                        if (grid[i] == .hwall) {
                            // merge either horizontally
                            const start_x = x;
                            // continue merging until current tile isn't a wall anymore
                            while (isNeighbor(grid, x, y, 0, 0, .hwall)) : (x += 1) {}

                            // create the wall object
                            try out.append(gpa, .{
                                .wall = .init(
                                    @floatFromInt(start_x),
                                    @floatFromInt(y),
                                    @floatFromInt(x - start_x),
                                    1,
                                    wall_height,
                                    Palette.wall,
                                    scale,
                                ),
                            });
                        } else {
                            // no wall block; increment x regularly
                            x += 1;
                        }
                    }
                }
            } else if (direction == .vertical) {
                for (0..world_w) |x| {
                    var y: usize = 0;

                    while (y < world_h) {
                        const i = y * world_w + x;

                        if (grid[i] == .vwall) {
                            const start_y = y;
                            while (isNeighbor(grid, x, y, 0, 0, .vwall)) : (y += 1) {}

                            try out.append(gpa, .{
                                .wall = .init(
                                    @floatFromInt(x),
                                    @floatFromInt(start_y),
                                    1,
                                    @floatFromInt(y - start_y),
                                    wall_height,
                                    Palette.wall,
                                    scale,
                                ),
                            });
                        } else {
                            y += 1;
                        }
                    }
                }
            }
        }

        fn mergeGround(
            gpa: std.mem.Allocator,
            grid: *[world_size]Tile,
            out: *std.ArrayList(Terrain),
            scale: f32,
        ) !void {
            var merged: [world_size]bool = .{false} ** world_size;

            for (0..world_h) |y| {
                for (0..world_w) |x| {
                    const i = y * world_w + x;

                    if (merged[i]) continue;
                    if (grid[i] != .ground and grid[i] != .path) continue;

                    const start_x = x;
                    const start_y = y;
                    const tile_type = grid[i];

                    // greedily expands HORIZONTALLY first
                    var width: usize = 0;
                    while (start_x + width < world_w and
                        !merged[start_y * world_w + start_x + width] and
                        isNeighbor(grid, start_x + width, start_y, 0, 0, tile_type))
                    {
                        width += 1;
                    }

                    // greedily expands VERTICALLY while the entire row matches
                    var height: usize = 1;
                    while (start_y + height < world_h) {
                        var row_matches = true;

                        for (0..width) |dx| {
                            const check_x = start_x + dx;
                            const check_y = start_y + height;

                            if (merged[check_y * world_w + check_x] or
                                !isNeighbor(grid, check_x, check_y, 0, 0, tile_type))
                            {
                                row_matches = false;
                                break;
                            }
                        }

                        if (!row_matches) break;
                        height += 1;
                    }

                    // mark rectangle as merged
                    for (start_y..start_y + height) |yy| {
                        for (start_x..start_x + width) |xx| {
                            merged[yy * world_w + xx] = true;
                        }
                    }

                    try out.append(
                        gpa,
                        .{
                            .ground = .init(
                                @floatFromInt(start_x),
                                @floatFromInt(start_y),
                                @floatFromInt(width),
                                @floatFromInt(height),
                                if (tile_type == .ground) Palette.ground else Palette.path,
                                scale,
                            ),
                        },
                    );
                }
            }
        }

        fn widenWalls(grid: *[world_size]Tile) void {
            var marked: [world_size]bool = .{false} ** world_size;

            for (0..world_h) |y| {
                for (0..world_w) |x| {
                    const i = y * world_w + x;
                    if (marked[i]) continue;
                    if (grid[i] != .path) continue;

                    const on_horizontal_run =
                        isNeighbor(grid, x, y, -1, 0, .path) or isNeighbor(grid, x, y, 1, 0, .path);
                    const on_vertical_run =
                        isNeighbor(grid, x, y, 0, -1, .path) or isNeighbor(grid, x, y, 0, 1, .path);

                    // part of a horizontal run -> widen vertically (up/down)
                    if (on_horizontal_run) {
                        if (isNeighbor(grid, x, y, 0, -1, .none)) {
                            grid[i - world_w] = .path;
                            marked[i - world_w] = true;
                        }
                        if (isNeighbor(grid, x, y, 0, 1, .none)) {
                            grid[i + world_w] = .path;
                            marked[i + world_w] = true;
                        }
                    }

                    // part of a vertical run -> widen horizontally (left/right)
                    if (on_vertical_run) {
                        if (isNeighbor(grid, x, y, -1, 0, .none)) {
                            grid[i - 1] = .path;
                            marked[i - 1] = true;
                        }
                        if (isNeighbor(grid, x, y, 1, 0, .none)) {
                            grid[i + 1] = .path;
                            marked[i + 1] = true;
                        }
                    }
                }
            }
        }

        fn markWalls(grid: *[world_size]Tile) void {
            // if a ground tile borders a none tile, it gets set to wall
            // can modify while iterating since we only modify to wall (we don't check for it)
            for (0..world_h) |y| {
                for (0..world_w) |x| {
                    const i = y * world_w + x;

                    if (grid[i] != .none) continue;

                    if (isOccupied(grid, x, y, 0, 1)) {
                        grid[i] = .hwall;
                        continue;
                    }
                    if (isOccupied(grid, x, y, 1, 0)) {
                        grid[i] = .vwall;
                        continue;
                    }
                    if (isOccupied(grid, x, y, 1, 1)) {
                        grid[i] = .dwall;
                        continue;
                    }
                }
            }
            return;
        }

        fn isOccupied(grid: *[world_size]Tile, x: usize, y: usize, dx: isize, dy: isize) bool {
            return isNeighbor(grid, x, y, dx, dy, .ground) or
                isNeighbor(grid, x, y, dx, dy, .path);
        }

        fn isNeighbor(grid: *[world_size]Tile, x: usize, y: usize, dx: isize, dy: isize, tile_type: Tile) bool {
            // also used with offsets 0, 0 in order to make sure the current x and y are within bounds
            // in order to save on checking it everytime
            const nx = @as(isize, @intCast(x)) + dx;
            const ny = @as(isize, @intCast(y)) + dy;
            if (nx < 0 or ny < 0 or nx >= world_w or ny >= world_h) return false;
            const t = grid[@as(usize, @intCast(ny)) * world_w + @as(usize, @intCast(nx))];
            return t == tile_type;
        }

        fn genNode(gpa: std.mem.Allocator, rand: std.Random, grid: *[world_size]Tile, rect: Rect, max_leaves: usize) !*Node {
            var node = try gpa.create(Node);
            node.color = .init(
                rand.int(u8),
                rand.int(u8),
                rand.int(u8),
                255,
            );
            node.rect = rect;

            // precondition: node rect size (width and height) is both > MIN_RECT_SIZE
            std.debug.assert(node.rect.w >= MIN_RECT_SIZE);
            std.debug.assert(node.rect.h >= MIN_RECT_SIZE);

            // --- LLM BEGIN!
            // split direction, weighted by current aspect ratio
            // (horizontally means the split cut is along the x-axis)
            const ratio: f32 = @as(f32, @floatFromInt(node.rect.w)) / @as(f32, @floatFromInt(node.rect.h));
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

            var split1: Rect = undefined;
            var split2: Rect = undefined;
            const inner_proportion: rl.Vector2 = .init(0.6, 0.8);

            // finalize split direction given the randomness and biases
            if (split_dir == .hor) {
                // if can't split horizontally, check if it can split vertically
                if (node.rect.w < 2 * MIN_RECT_SIZE) {
                    split_dir = .none;
                    if (node.rect.h >= 2 * MIN_RECT_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .ver;
                    }
                }
            } else if (split_dir == .ver) {
                // if can't split horizontally, check if it can split vertically
                if (node.rect.h < 2 * MIN_RECT_SIZE) {
                    split_dir = .none;
                    if (node.rect.w >= 2 * MIN_RECT_SIZE and rand.float(f32) >= 0.5) {
                        split_dir = .hor;
                    }
                }
            }

            // create the nodes based on whether we split or not
            if (split_dir == .none) {
                // can't split anymore (it's are leaf)
                // create an inner rectangle which is a bit smaller
                const inner_min_w: i32 = @intFromFloat(@floor(inner_proportion.x * @as(f32, @floatFromInt(node.rect.w))));
                const inner_max_w: i32 = @intFromFloat(@floor(inner_proportion.y * @as(f32, @floatFromInt(node.rect.w))));
                const inner_min_h: i32 = @intFromFloat(@floor(inner_proportion.x * @as(f32, @floatFromInt(node.rect.h))));
                const inner_max_h: i32 = @intFromFloat(@floor(inner_proportion.y * @as(f32, @floatFromInt(node.rect.h))));

                // position that rectangle with a uniformly random offset within the larger rectangle
                const inner_w = rand.intRangeAtMost(i32, inner_min_w, inner_max_w);
                const inner_h = rand.intRangeAtMost(i32, inner_min_h, inner_max_h);
                // n and -n because we don't want bordering rects
                const inner_x = rand.intRangeAtMost(i32, 1, node.rect.w - inner_w - 1) + node.rect.x;
                const inner_y = rand.intRangeAtMost(i32, 1, node.rect.h - inner_h - 1) + node.rect.y;

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
                // we can only split if our size is at least 2 * MIN_RECT_SIZE
                // decide the split proportion
                const split_min_x = MIN_RECT_SIZE;
                const split_max_x = node.rect.w - MIN_RECT_SIZE;
                const split_x: i32 = rand.intRangeAtMost(i32, split_min_x, split_max_x);

                // convert proportion to two split rectangles (rects)
                split1 = .init(
                    node.rect.x,
                    node.rect.y,
                    split_x,
                    node.rect.h,
                );
                split2 = .init(
                    node.rect.x + split_x,
                    node.rect.y,
                    node.rect.w - split_x,
                    node.rect.h,
                );
            } else if (split_dir == .ver) {
                const split_min_y = MIN_RECT_SIZE;
                const split_max_y = node.rect.h - MIN_RECT_SIZE;
                const split_y = rand.intRangeAtMost(i32, split_min_y, split_max_y);
                split1 = .init(
                    node.rect.x,
                    node.rect.y,
                    node.rect.w,
                    split_y,
                );
                split2 = .init(
                    node.rect.x,
                    node.rect.y + split_y,
                    node.rect.w,
                    node.rect.h - split_y,
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
