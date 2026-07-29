const std = @import("std");
const rl = @import("raylib");

pub fn scaleRect(rect: rl.Rectangle, scale: f32) rl.Rectangle {
    return .{
        .x = rect.x * scale,
        .y = rect.y * scale,
        .width = rect.width * scale,
        .height = rect.height * scale,
    };
}

// floatBetween
pub fn floatB(rand: std.Random, a: f32, b: f32) f32 {
    return a + rand.float(f32) * (b - a);
}

// float between but normally distributed & clamped
pub fn floatNormB(rand: std.Random, min: f32, max: f32) f32 {
    const mean = (min + max) / 2;
    const stddev = (max - min) / 6;
    // ~99.7% falls inside [min, max]
    // so when we pass stddev to floatNorm it makes sure ~99.7% falls inside stddev * n
    const val = mean + stddev * rand.floatNorm(f32);
    return std.math.clamp(val, min, max);
}

pub fn imageLoadGrid(
    gpa: std.mem.Allocaotr,
    path: []const []const u8,
    columns: usize,
    rows: usize,
    scale: f32,
) [][]rl.Texture {
    var image = try rl.loadImage(path);
    image.resize(image.width * scale, image.height * scale);

    const frame_width = image.width / columns;
    const frame_height = image.height / rows;

    const ret = try gpa.alloc([]rl.Texture, rows);

    for (0..rows) |y| {
        const row = image.copyRec(.init(0, y * frame_height, image.get_width(), frame_height));
        const row_sheet = try gpa.alloc(rl.Texture, columns);
        for (0..columns) |x| {
            const frame = row.copyRec(.init(
                x * frame_width,
                0,
                frame_width,
                frame_height,
            ));

            row_sheet.append(frame);
        }

        ret.append(row_sheet);
    }
}

pub fn imageLoadRow(gpa: std.mem.Allocator, path: []const []const u8, columns: usize, scale: f32) ![]rl.Texture {
    const path_str = try std.fs.path.joinZ(gpa, path);
    defer gpa.free(path_str);
    var image = try rl.loadImage(path_str);
    image.resize(
        @intFromFloat(@as(f32, @floatFromInt(image.width)) * scale),
        @intFromFloat(@as(f32, @floatFromInt(image.height)) * scale),
    );

    const frame_width = @as(usize, @intCast(image.width)) / columns;
    const ret = try gpa.alloc(rl.Texture, columns);
    for (0..columns) |i|
        ret[i] = try image.copyRec(.init(
            @floatFromInt(i * frame_width),
            0,
            @floatFromInt(frame_width),
            @floatFromInt(image.height),
        )).toTexture();

    return ret;
}

pub fn imageLoad(path: [:0]const u8, scale: f32) !rl.Texture {
    var image = try rl.loadImage(path);
    image.resize(image.width * scale, image.height * scale);
    return image.toTexture();
}
