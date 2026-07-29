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
                .position = .init(71, 90, 71),
                .target = .init(0, 0, 0),
                .up = .init(0, 1, 0),
                .fovy = 60,
                .projection = .orthographic,
            },
            .player = try .init(
                .init(0, 0, 0),
            ),
            .prng = .init(@intFromFloat(rl.getTime() * 1000)),
            .world = undefined,
            .rand = undefined,
            .font = try .init(font_path),
        };

        game.rand = game.prng.random();
        game.world = try .init(gpa, game.rand, .{ 128, 128 });

        rl.playSound(game.title_music);

        return game;
    }

    /// Destroys `self` pointer as well.
    fn deinit(self: *Game, gpa: std.mem.Allocator) void {
        self.title_screen.deinit(gpa);
        self.title_music.unload();
        self.world.deinit(gpa);
        self.font.unload();
        rl.closeWindow();
        gpa.destroy(self);
    }

    fn loop(self: *Game) void {
        while (!rl.windowShouldClose()) {
            rl.clearBackground(.dark_gray);

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

                    // world stuff
                    self.world.draw();

                    // player stuff
                    self.player.update(&self.camera);
                    self.player.draw();

                    rl.endMode3D();
                },
            }

            rl.drawFPS(12, 12);

            rl.endDrawing();
        }
    }
};

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
