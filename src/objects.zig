const std = @import("std");
const rl = @import("raylib");

pub const MagnitudeType = enum {
    set_abs,
    rel_num,
    rel_coef,
    set_coef,
};

pub const PropertyType = enum {
    crit_change,
    damage,
    dash_cooldown,
    dash_damage,
    dash_range,
    max_health,
    movement_speed,
    none,
};

pub const Property = struct {
    type: PropertyType,
    mag_type: MagnitudeType,
    magnitude: f32,

    pub fn init(t: PropertyType, mag_type: MagnitudeType, magnitude: f32) Property {
        return .{
            .type = t,
            .mag_type = mag_type,
            .magnitude = magnitude,
        };
    }
};

pub const AtomType = enum {
    argon,
    arsenic,
    silicon,
    osmium,
    krypton,
    vanadium,
    bismuthy,
    oganesson,
};

pub var atom_images: []rl.Texture = undefined;
pub var atoms: std.EnumMap(AtomType, Atom) = .init(.{});

const Atom = struct {
    name: []const u8,
    texture: rl.Texture,
    color: rl.Color,
    properties: []Property,

    const ARSENIC: Atom = .initComptime(
        "Arsenic",
        &.{
            .init(.damage, .rel_coef, 0.2),
            .init(.max_health, .rel_coef, -0.2),
        },
        .init(163, 0, 0),
    );
    const BISMUTH: Atom = .initComptime("Bismuth", &.{}, .init(227, 171, 188));
    const KRYPTON: Atom = .initComptime(
        "Krypton",
        &.{
            .init(.dash_cooldown, .rel_coef, -0.5),
            .init(.dash_range, .rel_coef, 1.0),
        },
        .init(0, 0, 80),
    );
    const OSMIUM: Atom = .initComptime(
        "Osmium",
        &.{.init(.none, .set_abs, 0.0)},
        .init(50, 50, 50),
    );
    const SILICON: Atom = .initComptime(
        "Silicon",
        &.{
            .init(.movement_speed, .rel_coef, -0.2),
            .init(.max_health, .rel_coef, 0.2),
        },
        .init(254, 251, 234),
    );
    const VANADIUM: Atom = .initComptime(
        "Vanadium",
        &.{
            .init(.crit_change, .rel_coef, 0.5),
            .init(.movement_speed, .rel_coef, -0.2),
        },
        .init(0, 200, 0),
    );

    pub fn initComptime(
        comptime name: []const u8,
        comptime properties: []Property,
        comptime color: rl.Color,
    ) Atom {
        return .{
            .name = name,
            .texture = atom_images[index],
            .properties = properties,
            .color = color,
        };
    }

    pub fn init(gpa: std.mem.Allocator, t: AtomType) !Atom {
        return .{
            .name = try std.ascii.allocUpperString(gpa, @tagName(t)),
        };
    }
};
