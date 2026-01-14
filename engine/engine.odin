package engine

import "core:path/slashpath"
import "core:strings"
import rl "vendor:raylib"

Texture :: struct {
	frames: [dynamic]rl.Texture,
}

texture_init :: proc(
	frames_paths: [][]string, // list of file paths
	width: i32 = 0,
	height: i32 = 0,
) -> (
	image: Texture,
) {
	alloc := context.temp_allocator

	for path, i in frames_paths {
		joined_path := slashpath.join(path, alloc)
		joined_path_cstring := strings.clone_to_cstring(joined_path, alloc)
		img := rl.LoadImage(joined_path_cstring)
		defer rl.UnloadImage(img)

		if width != 0 && height == 0 || width == 0 && height != 0 {
			panic("Error: initTexture call received invalid dimensions")
		}

		if width != 0 && height != 0 {
			rl.ImageResizeNN(&img, width, height)
		}

		append(&image.frames, rl.LoadTextureFromImage(img))
	}

	return
}

texture_deinit :: proc(self: ^Texture) {
	for frame in self.frames {
		rl.UnloadTexture(frame)
	}
}

FontSize :: enum {
	TITLE = 48,
}
