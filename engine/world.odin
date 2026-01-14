package engine

import "core:math/rand"

World :: struct {
	root_node: Node,
}

Rect :: struct {
	x, y, w, h: u32,
}

Node :: struct {
	rect: Rect,
	content: union {
		[2]^Node, // child nodes
		[2]u32,   // leaf size
	},
}

MIN_LEAF_SIZE: u32 : 8

// `tiles` is the resolution of the world measured in tiles
world_init :: proc(resolution: [2]u32) -> World {
	return {root_node = gen_node({0, 0, resolution.x, resolution.y})^}
}

gen_node :: proc(rect: Rect) -> ^Node {
	node := new(Node)
	node.rect = rect

	// stop splitting if too small, return leaf
	if rect.w < MIN_LEAF_SIZE * 2 || rect.h < MIN_LEAF_SIZE * 2 {
		node.content = [2]u32 {
			u32(rand.float32_range(f32(rect.w) * 0.4, f32(rect.w) * 0.6)),
			u32(rand.float32_range(f32(rect.h) * 0.4, f32(rect.h) * 0.6)),
		}
		return node
	}

	split_vertical: bool
	switch {
	case rect.w > rect.h:
		split_vertical = true
	case rect.h > rect.w:
		split_vertical = false
	case:
		split_vertical = rand.choice([]bool{true, false})
	}

	min := MIN_LEAF_SIZE
	if split_vertical {
		max := rect.w - MIN_LEAF_SIZE
		if min >= max do return node

		split := rand.uint32_range(min, max)

		node.content = [2]^Node {
			gen_node({rect.x, rect.y, split, rect.h}),
			gen_node({rect.x + split, rect.y, rect.w - split, rect.h}),
		}
	} else {
		max := rect.h - MIN_LEAF_SIZE
		if min >= max do return node

		split := rand.uint32_range(min, max)

		node.content = [2]^Node {
			gen_node({rect.x, rect.y, rect.w, split}),
			gen_node({rect.x, rect.y + split, rect.w, rect.h - split}),
		}
	}

	return node
}
