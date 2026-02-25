const std = @import("std");
const rl = @import("raylib");
const engine = @import("engine.zig");
const World = @import("world.zig");
const rcamera = @import("rcamera.zig");

const State = enum {
    title,
    in_game,
};

const Screen = struct {
    width: i32,
    height: i32,
};

const Player = struct {
    position: rl.Vector3,
    speed: rl.Vector2,
};

const Game = struct {
    screen: Screen,
    title_screen: engine.Texture,
    title_music: rl.Sound,
    state: State,
    camera: rl.Camera3D,
    world: World,
    player: Player,

    fn init(alloc: std.mem.Allocator) !Game {
        const width: i32 = 1280;
        const height: i32 = 720;

        rl.initWindow(width, height, "Atomic Alley");
        rl.initAudioDevice();
        rl.setTargetFPS(60);

        const game: Game = .{
            .screen = .{ .width = width, .height = height },
            .title_screen = try .init(
                alloc,
                &.{
                    &.{ "resources", "images", "menu", "title0.png" },
                    &.{ "resources", "images", "menu", "title1.png" },
                },
                width,
                height,
            ),
            .title_music = b: {
                const sound_path = try std.fs.path.joinZ(alloc, &.{ "resources", "sfx", "MainMenuMusic.mp3" });
                defer alloc.free(sound_path);
                break :b try rl.loadSound(sound_path);
            },
            .state = .title,
            .camera = .{
                .position = .init(-64, 64, -64),
                .target = .init(64, 0, 64),
                .up = .init(0, 1, 0),
                .fovy = 60,
                .projection = .orthographic,
            },
            .world = try .init(alloc, .{ 128, 128 }),
            .player = .{ .position = .init(-64, 0, -64), .speed = .init(0.5, 0.5) },
        };

        rl.playSound(game.title_music);

        return game;
    }

    fn deinit(self: *Game, alloc: std.mem.Allocator) void {
        self.title_screen.deinit(alloc);
        self.title_music.unload();
        self.world.deinit(alloc);
        rl.closeWindow();
    }

    fn loop(self: *Game) void {
        while (!rl.windowShouldClose()) {
            rl.clearBackground(.black);

            rl.beginDrawing();

            switch (self.state) {
                .title => {
                    if (rand.intRangeAtMost(u8, 0, 100) >= 94)
                        self.title_screen.frames.items[1].draw(0, 0, .white)
                    else
                        self.title_screen.frames.items[0].draw(0, 0, .white);

                    const text_size = rl.measureTextEx(
                        font,
                        "press <SPACE> to continue",
                        @intFromEnum(engine.FontSize.title),
                        0.0,
                    );
                    rl.drawTextEx(
                        font,
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

                    if (rl.isKeyDown(.w)) rcamera.moveForward(&self.camera, self.player.speed.y, true);
                    if (rl.isKeyDown(.a)) rcamera.moveRight(&self.camera, -self.player.speed.x, true);
                    if (rl.isKeyDown(.s)) rcamera.moveForward(&self.camera, -self.player.speed.y, true);
                    if (rl.isKeyDown(.d)) rcamera.moveRight(&self.camera, self.player.speed.x, true);

                    self.player.position = self.camera.target;
                    rl.drawSphere(self.player.position, 1, .red);

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
    for (node.paths.items) |path| {
        rl.drawPlane(
            .init(
                @as(f32, @floatFromInt(path.x)) + @as(f32, @floatFromInt(path.w)) / 2.0,
                0,
                @as(f32, @floatFromInt(path.y)) + @as(f32, @floatFromInt(path.h)) / 2.0,
            ),
            .init(@floatFromInt(path.w), @floatFromInt(path.h)),
            .gray,
        );
    }

    switch (node.content) {
        .children => |c| {
            drawNode(c[0]);
            drawNode(c[1]);
        },
        .leaf => |c| {
            var prng_ = std.Random.DefaultPrng.init(@intFromPtr(&c));
            const rand_ = prng_.random();
            const color: rl.Color = .init(
                rand_.intRangeAtMost(u8, 0, 255),
                rand_.intRangeAtMost(u8, 0, 255),
                rand_.intRangeAtMost(u8, 0, 255),
                255,
            );

            rl.drawPlane(
                .init(
                    @as(f32, @floatFromInt(node.rect.x)) + @as(f32, @floatFromInt(node.rect.w)) / 2.0,
                    0.0,
                    @as(f32, @floatFromInt(node.rect.y)) + @as(f32, @floatFromInt(node.rect.h)) / 2,
                ),
                .init(@floatFromInt(c[0]), @floatFromInt(c[1])),
                color,
            );
        },
    }
}

var font: rl.Font = undefined;

var prng: std.Random.DefaultPrng = undefined;
pub var rand: std.Random = undefined;

pub fn main() !void {
    var gpa: std.heap.DebugAllocator(.{}) = .init;
    defer _ = gpa.deinit();
    const alloc = gpa.allocator();

    prng = .init(blk: {
        var seed: u64 = undefined;
        std.posix.getrandom(std.mem.asBytes(&seed)) catch {};
        break :blk seed;
    });
    rand = prng.random();

    var game: Game = try .init(alloc);
    defer game.deinit(alloc);

    const font_path = try std.fs.path.joinZ(alloc, &.{ "resources", "fonts", "Chicago.ttf" });
    defer alloc.free(font_path);
    font = try .init(font_path);
    defer font.unload();

    game.loop();
}
