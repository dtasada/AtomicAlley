package main

import "core:math/rand"
import "core:path/slashpath"
import "core:strings"

import rl "vendor:raylib"

import "engine"

State :: enum {
	TITLE,
	IN_GAME,
}

Screen :: struct {
	width, height: i32,
}

Game :: struct {
	screen:       Screen,
	title_screen: engine.Texture,
	title_music:  rl.Sound,
	state:        State,
	camera:       rl.Camera3D,
	world:        engine.World,
	player:       Player,
}

Player :: struct {
	position: rl.Vector3,
	speed:    rl.Vector2,
}

game_init :: proc() -> (game: Game) {
	width: i32 = 1280
	height: i32 = 720

	rl.InitWindow(width, height, "Atomic Alley")
	rl.InitAudioDevice()
	rl.SetTargetFPS(60)

	game = Game {
		screen = {width = width, height = height},
		title_screen = engine.texture_init(
			{
				{"resources", "images", "menu", "title0.png"},
				{"resources", "images", "menu", "title1.png"},
			},
			width = width,
			height = height,
		),
		title_music = rl.LoadSound(
			strings.clone_to_cstring(
				slashpath.join({"resources", "sfx", "MainMenuMusic.mp3"}, context.temp_allocator),
				context.temp_allocator,
			),
		),
		state = .TITLE,
		camera = rl.Camera3D {
			position = {-64, 64, -64},
			target = {64, 0, 64},
			up = {0, 1, 0},
			fovy = 60,
			projection = .ORTHOGRAPHIC,
		},
		world = engine.world_init({128, 128}),
		player = {position = {-64, 0, -64}, speed = {0.5, 0.5}},
	}

	rl.PlaySound(game.title_music)

	return
}

game_deinit :: proc(self: ^Game) {
	engine.texture_deinit(&self.title_screen)
	rl.UnloadSound(self.title_music)
	rl.CloseWindow()
}

game_loop :: proc(self: ^Game) {
	for !rl.WindowShouldClose() {
		rl.ClearBackground(rl.BLACK)

		rl.BeginDrawing()

		switch self.state {
		case .TITLE:
			switch {
			case rand.int_range(0, 100) >= 94:
				rl.DrawTexture(self.title_screen.frames[1], 0, 0, rl.WHITE)
			case:
				rl.DrawTexture(self.title_screen.frames[0], 0, 0, rl.WHITE)
			}
			text_size := rl.MeasureTextEx(
				font,
				"press <SPACE> to continue",
				f32(engine.FontSize.TITLE),
				0.0,
			)
			rl.DrawTextEx(
				font,
				"press <SPACE> to continue",
				{
					f32(self.screen.width) / 2 - text_size.x / 2,
					f32(self.screen.height) - text_size.y / 2 - 128,
				},
				f32(engine.FontSize.TITLE),
				0.0,
				rl.WHITE,
			)

			if rl.IsKeyPressed(.SPACE) do self.state = .IN_GAME

		case .IN_GAME:
			rl.BeginMode3D(self.camera)

			if rl.IsKeyDown(.W) do rl.CameraMoveForward(&self.camera, self.player.speed.y, true)
			if rl.IsKeyDown(.A) do rl.CameraMoveRight(&self.camera, -self.player.speed.x, true)
			if rl.IsKeyDown(.S) do rl.CameraMoveForward(&self.camera, -self.player.speed.y, true)
			if rl.IsKeyDown(.D) do rl.CameraMoveRight(&self.camera, self.player.speed.x, true)

			self.player.position = self.camera.target
			rl.DrawSphere(self.player.position, 1, rl.RED)

			draw_node(&self.world.root_node)

			rl.EndMode3D()
		}

		rl.DrawFPS(12, 12)

		rl.EndDrawing()
	}
}

draw_node :: proc(node: ^engine.Node) {
	if node == nil do return

	for path in node.paths {
		rl.DrawPlane(
			{f32(path.x) + f32(path.w) / 2, 0, f32(path.y) + f32(path.h) / 2},
			{f32(path.w), f32(path.h)},
			rl.GRAY,
		)
	}

	switch c in node.content {
	case [2]^engine.Node:
		draw_node(c[0])
		draw_node(c[1])
	case [2]u32:
		r_gen := rand.create(u64(uintptr(node)))
		gen := rand.default_random_generator(&r_gen)
		color := rl.Color {
			u8(rand.int_range(0, 256, gen)),
			u8(rand.int_range(0, 256, gen)),
			u8(rand.int_range(0, 256, gen)),
			255,
		}

		rl.DrawPlane(
			{f32(node.rect.x) + f32(node.rect.w) / 2, 0, f32(node.rect.y) + f32(node.rect.h) / 2},
			{f32(c[0]), f32(c[1])},
			color,
		)
	}
}

font: rl.Font

main :: proc() {
	game := game_init()
	defer game_deinit(&game)

	font = rl.LoadFont(
		strings.clone_to_cstring(
			slashpath.join({"resources", "fonts", "Chicago.ttf"}, context.temp_allocator),
			context.temp_allocator,
		),
	)
	defer rl.UnloadFont(font)

	game_loop(&game)
}
