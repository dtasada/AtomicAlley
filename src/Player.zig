const std = @import("std");
const rl = @import("raylib");
const rcamera = @import("rcamera.zig");
const Self = @This();

pos: rl.Vector3,
model: rl.Model,

pub fn init(pos: rl.Vector3, light_shader: rl.Shader) !Self {
    const model = try rl.loadModel("resources/models/dexter.obj");
    model.materials[0].shader = light_shader;

    return .{ .pos = pos, .model = model };
}

pub fn update(self: *Self, camera: *rl.Camera) void {
    var move_vec: rl.Vector2 = .zero();
    if (rl.isKeyDown(.w)) {
        move_vec = move_vec.add(rl.Vector2.init(0, -1).rotate(std.math.pi * -(1.0 / 4.0)));
    }
    if (rl.isKeyDown(.a)) {
        move_vec = move_vec.add(rl.Vector2.init(0, -1).rotate(std.math.pi * -(3.0 / 4.0)));
    }
    if (rl.isKeyDown(.s)) {
        move_vec = move_vec.add(rl.Vector2.init(0, -1).rotate(std.math.pi * (3.0 / 4.0)));
    }
    if (rl.isKeyDown(.d)) {
        move_vec = move_vec.add(rl.Vector2.init(0, -1).rotate(std.math.pi * (1.0 / 4.0)));
    }
    move_vec = move_vec.normalize().scale(0.7);
    self.pos.x += move_vec.x;
    self.pos.z += move_vec.y;

    const m: f32 = 0.2;
    const delta = rl.Vector3.init(
        self.pos.x - camera.target.x,
        0,
        self.pos.z - camera.target.z,
    ).scale(m);
    camera.position = camera.position.add(delta);
    camera.target = camera.target.add(delta);
}

pub fn draw(self: Self) void {
    rl.drawModel(self.model, self.pos, 1.8, .light_gray);
}

pub fn deinit(self: *Self) void {
    rl.unloadModel(self.model);
}
