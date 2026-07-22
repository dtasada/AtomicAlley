const rl = @import("raylib");
const Self = @This();
const rcamera = @import("rcamera.zig");

pos: rl.Vector3,
vel: rl.Vector2,
model: rl.Model,

pub fn init(pos: rl.Vector3, vel: rl.Vector2) !Self {
    return .{
        .pos = pos,
        .vel = vel,
        .model = try rl.loadModel("resources/models/dexter.obj"),
    };
}

pub fn update(self: *Self, camera: *rl.Camera) void {
    if (rl.isKeyDown(.w)) self.pos.y += self.vel.y;
    if (rl.isKeyDown(.a)) self.pos.x -= self.vel.x;
    if (rl.isKeyDown(.s)) self.pos.y -= self.vel.y;
    if (rl.isKeyDown(.d)) self.pos.x += self.vel.x;

    const m: f32 = 0.2;
    const delta = rl.Vector3.init(
        self.pos.x - camera.position.x,
        self.pos.y - camera.position.y,
        0,
    ).scale(m);
    camera.position = camera.position.add(delta);
    camera.target = camera.target.add(delta);
}

pub fn draw(self: Self) void {
    rl.drawModel(
        self.model,
        self.pos,
        1.8,
        .gray,
    );
}

pub fn deinit(self: *Self) void {
    rl.unloadModel(self.model);
}
