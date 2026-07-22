const std = @import("std");
const rl = @import("raylib");

pub const Texture = struct {
    frames: std.ArrayList(rl.Texture),

    pub fn init(
        gpa: std.mem.Allocator,
        frames_paths: []const []const []const u8, // list of file paths
        width: i32,
        height: i32,
    ) !Texture {
        var image: Texture = .{ .frames = .empty };

        for (frames_paths) |path| {
            const joined_path = try std.fs.path.joinZ(gpa, path);
            defer gpa.free(joined_path);
            var img: rl.Image = try .init(joined_path);
            defer img.unload();

            if (width != 0 and height == 0 or width == 0 and height != 0)
                @panic("Error: initTexture call received invalid dimensions");

            if (width != 0 and height != 0)
                img.resizeNN(width, height);

            try image.frames.append(gpa, try .fromImage(img));
        }

        return image;
    }

    pub fn deinit(self: *Texture, allocgpa: std.mem.Allocator) void {
        for (self.frames.items) |frame|
            frame.unload();

        self.frames.deinit(allocgpa);
    }
};

pub const FontSize = enum(u32) {
    title = 48,
};
