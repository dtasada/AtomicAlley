const std = @import("std");
const rl = @import("raylib");
const engine = @import("engine.zig");
const World = @import("world.zig");
const Player = @import("Player.zig");
const rcamera = @import("rcamera.zig");
const objects = @import("objects.zig");
const utils = @import("utils.zig");

const State = enum {
    title,
    in_game,
};

const Screen = struct {
    width: i32,
    height: i32,
};

const Game = struct {
    screen: Screen,
    title_screen: engine.Texture,
    title_music: rl.Sound,
    state: State,
    camera: rl.Camera3D,
    world: World,
    player: Player,
    prng: std.Random.DefaultPrng,
    rand: std.Random,
    font: rl.Font,

    model: rl.Model,

    fn init(gpa: std.mem.Allocator) !*Game {
        const width: i32 = 1280;
        const height: i32 = 720;

        rl.initWindow(width, height, "Atomic Alley");
        rl.initAudioDevice();
        rl.setTargetFPS(60);

        const font_path = try std.fs.path.joinZ(gpa, &.{ "resources", "fonts", "Chicago.ttf" });
        defer gpa.free(font_path);

        const game = try gpa.create(Game);
        game.* = .{
            .screen = .{ .width = width, .height = height },
            .title_screen = try .init(
                gpa,
                &.{
                    &.{ "resources", "images", "menu", "title0.png" },
                    &.{ "resources", "images", "menu", "title1.png" },
                },
                width,
                height,
            ),
            .title_music = b: {
                const sound_path = try std.fs.path.joinZ(gpa, &.{ "resources", "sfx", "MainMenuMusic.mp3" });
                defer gpa.free(sound_path);
                break :b try rl.loadSound(sound_path);
            },
            .state = .title,
            .camera = .{
                .position = .init(0, 0, 100),
                .target = .init(0, 0, 0),
                .up = .init(0, 1, 0),
                .fovy = 60,
                .projection = .orthographic,
            },
            .player = try .init(
                .init(0, 0, 0),
                .init(0.5, 0.5),
            ),
            .prng = .init(@intFromFloat(rl.getTime() * 1000)),
            .world = undefined,
            .rand = undefined,
            .font = try .init(font_path),
            .model = try rl.loadModel("resources/models/cube.obj"),
        };

        game.rand = game.prng.random();
        game.world = try .init(gpa, game.rand, .{ 64, 64 });

        rl.playSound(game.title_music);

        return game;
    }

    /// Destroys `self` pointer as well.
    fn deinit(self: *Game, gpa: std.mem.Allocator) void {
        self.title_screen.deinit(gpa);
        self.title_music.unload();
        self.world.deinit(gpa);
        self.font.unload();
        self.model.unload();
        rl.closeWindow();
        gpa.destroy(self);
    }

    fn loop(self: *Game) void {
        while (!rl.windowShouldClose()) {
            rl.clearBackground(.black);

            // self.camera.update(.third_person);
            rl.beginDrawing();

            switch (self.state) {
                .title => {
                    if (self.rand.intRangeAtMost(u8, 0, 100) >= 94)
                        self.title_screen.frames.items[1].draw(0, 0, .white)
                    else
                        self.title_screen.frames.items[0].draw(0, 0, .white);

                    const text_size = rl.measureTextEx(
                        self.font,
                        "press <SPACE> to continue",
                        @intFromEnum(engine.FontSize.title),
                        0.0,
                    );
                    rl.drawTextEx(
                        self.font,
                        "press <SPACE> to continue",
                        .init(
                            @as(f32, @floatFromInt(self.screen.width)) / 2.0 - text_size.x / 2.0,
                            @as(f32, @floatFromInt(self.screen.height)) - text_size.y / 2 - 128,
                        ),
                        @intFromEnum(engine.FontSize.title),
                        0.0,
                        .white,
                    );

                    if (rl.isKeyPressed(.space)) self.state = .in_game;
                },
                .in_game => {
                    rl.beginMode3D(self.camera);

                    self.player.update(&self.camera);
                    self.player.draw();

                    drawNode(self.world.root_node);

                    rl.endMode3D();
                },
            }

            rl.drawFPS(12, 12);

            rl.endDrawing();
        }
    }
};

fn drawNode(node: *World.Node) void {
    switch (node.content) {
        .children => |c| {
            // node has children; for each child node, draw corridor between its rect centers
            rl.drawCylinderEx(
                .init(c[0].rect.x + c[0].rect.width / 2, c[0].rect.y + c[0].rect.height / 2, 0.1),
                .init(c[1].rect.x + c[1].rect.width / 2, c[1].rect.y + c[1].rect.height / 2, 0.1),
                0.4,
                0.4,
                8,
                .dark_purple,
            );

            // resurse
            drawNode(c[0]);
            drawNode(c[1]);
        },
        .leaf => |inner| {
            // rect borders
            const color: rl.Color = .init(0, 240, 0, 255);
            const w: f32 = node.rect.width;
            const h: f32 = node.rect.height;
            const center: rl.Vector3 = .init(
                node.rect.x + node.rect.width / 2,
                node.rect.y + node.rect.height / 2,
                0,
            );
            const p1: rl.Vector3 = .init(center.x - w / 2, center.y - h / 2, center.z);
            const p2: rl.Vector3 = .init(center.x + w / 2, center.y - h / 2, center.z);
            const p3: rl.Vector3 = .init(center.x + w / 2, center.y + h / 2, center.z);
            const p4: rl.Vector3 = .init(center.x - w / 2, center.y + h / 2, center.z);
            rl.drawLine3D(p1, p2, color);
            rl.drawLine3D(p2, p3, color);
            rl.drawLine3D(p3, p4, color);
            rl.drawLine3D(p4, p1, color);

            // plane itself
            rl.drawPlane(
                .init(
                    inner.x + inner.width / 2,
                    inner.y + inner.height / 2,
                    0,
                ),
                .init(inner.width, inner.height),
                node.color,
            );
        },
    }
}

pub fn main() !void {
    var debug_allocator: std.heap.DebugAllocator(.{}) = .init;
    defer _ = debug_allocator.deinit();
    const gpa = debug_allocator.allocator();

    var game: *Game = try .init(gpa);
    defer game.deinit(gpa);

    const atom_images = try utils.imageLoadRow(gpa, &.{ "resources", "images", "atoms", "atoms.png" }, 7, 1.0);
    defer gpa.free(atom_images);
    @memcpy(&objects.atom_images.values, atom_images);

    objects.atoms = .init(.{
        .argon = .initBuiltin(
            .argon,
            "Argon",
            &.{.init(.none, .set_abs, 0.0)},
            .init(50, 50, 50, 255),
        ),
        .arsenic = .initBuiltin(.arsenic, "Arsenic", &.{
            .init(.damage, .rel_coef, 0.2),
            .init(.max_health, .rel_coef, -0.2),
        }, .init(163, 0, 0, 255)),
        .krypton = .initBuiltin(.krypton, "Krypton", &.{
            .init(.dash_cooldown, .rel_coef, -0.5),
            .init(.dash_range, .rel_coef, 1.0),
        }, .init(0, 0, 80, 255)),
        .oganesson = .initBuiltin(.oganesson, "Oganesson", &.{}, .init(255, 255, 255, 255)),
        .osmium = .initBuiltin(.osmium, "Osmium", &.{.init(.none, .set_abs, 0.0)}, .init(50, 50, 50, 255)),
        .silicon = .initBuiltin(.silicon, "Silicon", &.{
            .init(.movement_speed, .rel_coef, -0.2),
            .init(.max_health, .rel_coef, 0.2),
        }, .init(254, 251, 234, 255)),
        .vanadium = .initBuiltin(.vanadium, "Vanadium", &.{
            .init(.crit_change, .rel_coef, 0.5),
            .init(.movement_speed, .rel_coef, -0.2),
        }, .init(0, 200, 0, 255)),
    });

    game.loop();
}
