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
    oganesson,
};

pub var atom_images: std.EnumArray(AtomType, rl.Texture) = .initUndefined();
pub var atoms: std.EnumArray(AtomType, Atom) = .initUndefined();

const Atom = struct {
    name: []const u8,
    texture: rl.Texture,
    color: rl.Color,
    properties: []const Property,

    pub fn initBuiltin(
        comptime t: AtomType,
        comptime name: []const u8,
        comptime properties: []const Property,
        comptime color: rl.Color,
    ) Atom {
        return .{
            .name = name,
            .texture = atom_images.get(t),
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
