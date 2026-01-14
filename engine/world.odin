package engine

import "core:math"
import "core:math/rand"

World :: struct {
	root_node: Node,
}

Rect :: struct {
	x, y, w, h: u32,
}

Node :: struct {
	rect:    Rect,
	content: union {
		[2]^Node, // child nodes
		[2]u32, // leaf size
	},
	paths:   [dynamic]Rect,
}

MIN_LEAF_SIZE: u32 : 16

// `tiles` is the resolution of the world measured in tiles
world_init :: proc(resolution: [2]u32) -> World {
	world := World {
		root_node = gen_node({0, 0, resolution.x, resolution.y})^,
	}
	create_corridors(&world.root_node)
	return world
}

create_corridors :: proc(node: ^Node) -> Rect {
	if node == nil do return {}

	switch c in node.content {
	case [2]u32:
		w, h := c[0], c[1]
		x := node.rect.x + (node.rect.w - w) / 2
		y := node.rect.y + (node.rect.h - h) / 2
		return Rect{x, y, w, h}

	case [2]^Node:
		left := create_corridors(c[0])
		right := create_corridors(c[1])

		cx1 := int(left.x) + int(left.w) / 2
		cy1 := int(left.y) + int(left.h) / 2
		cx2 := int(right.x) + int(right.w) / 2
		cy2 := int(right.y) + int(right.h) / 2

		width := 2

		if rand.int_range(0, 2) == 0 {
			// Horizontal then Vertical
			hx := min(cx1, cx2)
			hy := cy1 - width / 2
			hw := abs(cx1 - cx2) + width
			hh := width
			append(&node.paths, Rect{u32(hx), u32(hy), u32(hw), u32(hh)})

			vx := cx2 - width / 2
			vy := min(cy1, cy2)
			vw := width
			vh := abs(cy1 - cy2) + width
			append(&node.paths, Rect{u32(vx), u32(vy), u32(vw), u32(vh)})
		} else {
			// Vertical then Horizontal
			vx := cx1 - width / 2
			vy := min(cy1, cy2)
			vw := width
			vh := abs(cy1 - cy2) + width
			append(&node.paths, Rect{u32(vx), u32(vy), u32(vw), u32(vh)})

			hx := min(cx1, cx2)
			hy := cy2 - width / 2
			hw := abs(cx1 - cx2) + width
			hh := width
			append(&node.paths, Rect{u32(hx), u32(hy), u32(hw), u32(hh)})
		}

		if rand.int_range(0, 2) == 0 {
			return left
		} else {
			return right
		}
	}

	return {}
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
