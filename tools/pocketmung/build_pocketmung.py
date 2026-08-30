#!/usr/bin/env python3
"""
PocketMung / HAPPY PLAY enclosure generator
-------------------------------------------
Procedurally builds an editable Blender scene inspired by the supplied six-view
concept image. The default visible collection is the clean reference shell.
A production-oriented display/port variant and internal placeholders are also
included and hidden by default.

Run in Blender:
    blender -b --python build_pocketmung.py -- --output-dir /path/to/output

All model dimensions are authored in millimetres (1 Blender Unit = 1 mm).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable, Sequence

import bpy
from mathutils import Vector


# -----------------------------------------------------------------------------
# Main adjustable parameters (millimetres)
# -----------------------------------------------------------------------------
P = {
    "body_width": 78.0,
    "body_depth": 42.0,
    "body_height": 96.0,
    "body_bottom_z": 4.0,
    "body_corner_radius": 14.5,
    "wall_thickness": 2.4,
    "shell_gap": 0.55,
    "ear_base_x": 25.0,
    "ear_base_y": -0.5,
    "ear_base_z": 91.0,
    "ear_height": 31.5,
    "ear_base_rx": 10.2,
    "ear_base_ry": 7.2,
    "tail_base_z": 22.5,
    "tail_height": 26.0,
    "display_width": 44.0,
    "display_height": 55.5,
    "display_center_z": 57.0,
    "bezel_width": 51.0,
    "bezel_height": 63.0,
    "usb_center_z": 38.0,
    "button_center_z": 64.0,
}

BODY_CENTER_Z = P["body_bottom_z"] + P["body_height"] * 0.5
BODY_TOP_Z = P["body_bottom_z"] + P["body_height"]
FRONT_Y = -P["body_depth"] * 0.5
REAR_Y = P["body_depth"] * 0.5


# -----------------------------------------------------------------------------
# Generic Blender helpers
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(Path.cwd() / "dist" / "pocketmung"))
    return parser.parse_args(argv)


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.materials,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)
    for collection in list(bpy.data.collections):
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    base = bpy.data.collections.get("Collection")
    if base:
        base.name = "00_SCENE_ROOT"


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "MILLIMETERS"
    scene.unit_settings.scale_length = 0.001
    scene.render.resolution_x = 900
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    # Blender 3.x/4.x/5.x use different identifiers for Eevee.
    for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "BLENDER_WORKBENCH"):
        try:
            scene.render.engine = engine_name
            break
        except Exception:
            continue
    # Blender versions expose slightly different Eevee settings.
    if hasattr(scene, "eevee"):
        if hasattr(scene.eevee, "taa_render_samples"):
            scene.eevee.taa_render_samples = 96
        if hasattr(scene.eevee, "use_gtao"):
            scene.eevee.use_gtao = True
            scene.eevee.gtao_distance = 3
            scene.eevee.gtao_factor = 1.2
    scene.render.image_settings.color_mode = "RGBA"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        try:
            scene.view_settings.look = "Medium High Contrast"
        except Exception:
            pass
    scene.world.use_nodes = True
    world_bg = scene.world.node_tree.nodes.get("Background")
    if world_bg:
        world_bg.inputs["Color"].default_value = (0.055, 0.050, 0.048, 1.0)
        world_bg.inputs["Strength"].default_value = 0.42


def ensure_collection(name: str, parent: bpy.types.Collection | None = None) -> bpy.types.Collection:
    existing = bpy.data.collections.get(name)
    if existing:
        return existing
    c = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(c)
    return c


def move_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def add_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> None:
    if obj.name not in collection.objects:
        collection.objects.link(obj)


def activate(obj: bpy.types.Object) -> None:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)


def deselect_all() -> None:
    bpy.ops.object.select_all(action="DESELECT")


def apply_modifier(obj: bpy.types.Object, modifier_name: str) -> None:
    deselect_all()
    activate(obj)
    bpy.ops.object.modifier_apply(modifier=modifier_name)


def set_smooth(obj: bpy.types.Object) -> None:
    if obj.type == "MESH":
        for poly in obj.data.polygons:
            poly.use_smooth = True


def make_material(
    name: str,
    color: tuple[float, float, float, float],
    roughness: float = 0.35,
    metallic: float = 0.0,
    transmission: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    for key in ("Transmission Weight", "Transmission"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = transmission
            break
    for key in ("Coat Weight", "Clearcoat"):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = 0.16 if transmission > 0 else 0.05
            break
    for key in ("Subsurface Weight", "Subsurface"):
        if key in bsdf.inputs and name.startswith("MAT_Shell"):
            bsdf.inputs[key].default_value = 0.018
            break
    if emission is not None:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = emission
            bsdf.inputs["Emission Strength"].default_value = emission_strength
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = emission
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    if obj.data and hasattr(obj.data, "materials"):
        obj.data.materials.clear()
        obj.data.materials.append(mat)


def rounded_box(
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    radius: float,
    material: bpy.types.Material | None,
    collection: bpy.types.Collection,
    segments: int = 8,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if radius > 0.0:
        bevel = obj.modifiers.new("Precision edge radius", "BEVEL")
        bevel.width = min(radius, min(dimensions) * 0.49)
        bevel.segments = max(1, segments)
        bevel.limit_method = "ANGLE"
        bevel.harden_normals = True
        apply_modifier(obj, bevel.name)
        set_smooth(obj)
    try:
        normal = obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
        normal.keep_sharp = True
        apply_modifier(obj, normal.name)
    except Exception:
        pass
    if material:
        assign_material(obj, material)
    move_to_collection(obj, collection)
    return obj


def duplicate_object(
    src: bpy.types.Object,
    name: str,
    collection: bpy.types.Collection,
    linked_mesh: bool = False,
) -> bpy.types.Object:
    obj = src.copy()
    obj.data = src.data if linked_mesh else src.data.copy()
    obj.name = name
    collection.objects.link(obj)
    return obj


def boolean_apply(
    target: bpy.types.Object,
    cutter: bpy.types.Object,
    operation: str,
    name: str,
) -> None:
    mod = target.modifiers.new(name, "BOOLEAN")
    mod.operation = operation
    if hasattr(mod, "solver"):
        mod.solver = "EXACT"
    mod.object = cutter
    apply_modifier(target, mod.name)
    target.data.validate(verbose=False)
    target.data.update()


def remove_object(obj: bpy.types.Object) -> None:
    bpy.data.objects.remove(obj, do_unlink=True)


def cut_with_rounded_box(
    target: bpy.types.Object,
    name: str,
    dimensions: tuple[float, float, float],
    location: tuple[float, float, float],
    radius: float,
    cutters: bpy.types.Collection,
) -> None:
    cutter = rounded_box(name, dimensions, location, radius, None, cutters, segments=6)
    boolean_apply(target, cutter, "DIFFERENCE", f"Cut {name}")
    remove_object(cutter)


def make_uv_sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    segments: int = 48,
    rings: int = 24,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    set_smooth(obj)
    assign_material(obj, material)
    move_to_collection(obj, collection)
    return obj


def create_cylinder_y(
    name: str,
    radius: float,
    depth: float,
    location: tuple[float, float, float],
    material: bpy.types.Material | None,
    collection: bpy.types.Collection,
    vertices: int = 48,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices,
        radius=radius,
        depth=depth,
        location=location,
        rotation=(math.radians(90), 0.0, 0.0),
    )
    obj = bpy.context.object
    obj.name = name
    if material:
        assign_material(obj, material)
    set_smooth(obj)
    move_to_collection(obj, collection)
    return obj


def create_tube_y(
    name: str,
    outer_radius: float,
    inner_radius: float,
    depth: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    outer = create_cylinder_y(name, outer_radius, depth, location, material, collection)
    inner = create_cylinder_y(name + "_Bore", inner_radius, depth + 2.0, location, None, collection)
    boolean_apply(outer, inner, "DIFFERENCE", "Bore")
    remove_object(inner)
    return outer


# -----------------------------------------------------------------------------
# Rounded rectangle mesh helpers (plane is X/Z, extrusion along Y)
# -----------------------------------------------------------------------------
def rounded_rect_points(width: float, height: float, radius: float, segments: int = 8) -> list[tuple[float, float]]:
    radius = min(radius, width * 0.5, height * 0.5)
    corners = [
        (width * 0.5 - radius, height * 0.5 - radius, 0.0),
        (-width * 0.5 + radius, height * 0.5 - radius, 90.0),
        (-width * 0.5 + radius, -height * 0.5 + radius, 180.0),
        (width * 0.5 - radius, -height * 0.5 + radius, 270.0),
    ]
    pts: list[tuple[float, float]] = []
    for cx, cz, start_deg in corners:
        for i in range(segments):
            a = math.radians(start_deg + 90.0 * i / segments)
            pts.append((cx + radius * math.cos(a), cz + radius * math.sin(a)))
    return pts


def create_rounded_rect_prism(
    name: str,
    width: float,
    height: float,
    depth: float,
    radius: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    bevel: float = 0.3,
    segments: int = 10,
) -> bpy.types.Object:
    pts = rounded_rect_points(width, height, radius, segments)
    x0, y0, z0 = location
    yf = y0 - depth * 0.5
    yb = y0 + depth * 0.5
    verts = [(x0 + x, yf, z0 + z) for x, z in pts] + [(x0 + x, yb, z0 + z) for x, z in pts]
    n = len(pts)
    faces: list[tuple[int, ...]] = []
    faces.append(tuple(reversed(range(n))))
    faces.append(tuple(range(n, 2 * n)))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    if bevel > 0:
        mod = obj.modifiers.new("Soft perimeter", "BEVEL")
        mod.width = min(bevel, depth * 0.45)
        mod.segments = 3
        apply_modifier(obj, mod.name)
    set_smooth(obj)
    return obj


def create_rounded_rect_ring(
    name: str,
    outer_w: float,
    outer_h: float,
    inner_w: float,
    inner_h: float,
    depth: float,
    outer_r: float,
    inner_r: float,
    location: tuple[float, float, float],
    material: bpy.types.Material,
    collection: bpy.types.Collection,
    segments: int = 10,
) -> bpy.types.Object:
    outer = rounded_rect_points(outer_w, outer_h, outer_r, segments)
    inner = rounded_rect_points(inner_w, inner_h, inner_r, segments)
    assert len(outer) == len(inner)
    x0, y0, z0 = location
    ya = y0 - depth * 0.5
    yb = y0 + depth * 0.5
    verts = (
        [(x0 + x, ya, z0 + z) for x, z in outer]
        + [(x0 + x, yb, z0 + z) for x, z in outer]
        + [(x0 + x, ya, z0 + z) for x, z in inner]
        + [(x0 + x, yb, z0 + z) for x, z in inner]
    )
    n = len(outer)
    oa, ob, ia, ib = 0, n, 2 * n, 3 * n
    faces: list[tuple[int, ...]] = []
    for i in range(n):
        j = (i + 1) % n
        faces.append((oa + i, oa + j, ob + j, ob + i))
        faces.append((ia + j, ia + i, ib + i, ib + j))
        faces.append((oa + i, ia + i, ia + j, oa + j))
        faces.append((ob + j, ib + j, ib + i, ob + i))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    set_smooth(obj)
    bevel = obj.modifiers.new("Ring edge softening", "BEVEL")
    bevel.width = min(0.35, depth * 0.2)
    bevel.segments = 3
    apply_modifier(obj, bevel.name)
    return obj


# -----------------------------------------------------------------------------
# Character parts: ears, inner ear, tail and feet
# -----------------------------------------------------------------------------
def create_ear_mesh(
    name: str,
    side: int,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    rings = 16
    segs = 32
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for i in range(rings):
        t = i / (rings - 1)
        # Slight outward and forward lean, broad organic base, rounded tip.
        cx = side * (P["ear_base_x"] + 2.1 * t - 0.9 * t * t)
        cy = P["ear_base_y"] - 1.2 * t + 0.35 * math.sin(math.pi * t)
        z = P["ear_base_z"] + P["ear_height"] * t
        rx = P["ear_base_rx"] * (1.0 - t) ** 0.74 + 0.55
        ry = P["ear_base_ry"] * (1.0 - t) ** 0.82 + 0.45
        for s in range(segs):
            a = 2.0 * math.pi * s / segs
            local_x = rx * math.cos(a)
            # Inner side is a little straighter than the outer side.
            if side * local_x < 0:
                local_x *= 0.78 + 0.10 * t
            local_y = ry * math.sin(a)
            if local_y > 0:
                local_y *= 0.90
            # Mild vertical undulation makes the base conform more naturally.
            zz = z + 0.20 * math.cos(a) * (1.0 - t)
            verts.append((cx + local_x, cy + local_y, zz))
    for i in range(rings - 1):
        for s in range(segs):
            n = (s + 1) % segs
            a = i * segs + s
            b = i * segs + n
            c = (i + 1) * segs + n
            d = (i + 1) * segs + s
            faces.append((a, b, c, d))
    faces.append(tuple(reversed(range(segs))))
    faces.append(tuple((rings - 1) * segs + s for s in range(segs)))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    set_smooth(obj)
    subdiv = obj.modifiers.new("Organic ear smoothing", "SUBSURF")
    subdiv.levels = 1
    subdiv.render_levels = 2
    apply_modifier(obj, subdiv.name)
    return obj


def teardrop_outline(width: float, height: float, count: int = 32) -> list[tuple[float, float]]:
    # Rounded bottom with a progressively sharpened top.
    pts: list[tuple[float, float]] = []
    half = count // 2
    for i in range(half + 1):
        t = i / half
        z = -height * 0.46 + height * 0.92 * t
        w = (width * 0.5) * (math.sin(math.pi * (0.08 + 0.92 * t)) ** 0.68) * (1.0 - 0.52 * t)
        pts.append((w, z))
    for i in range(half - 1, -1, -1):
        t = i / half
        z = -height * 0.46 + height * 0.92 * t
        w = (width * 0.5) * (math.sin(math.pi * (0.08 + 0.92 * t)) ** 0.68) * (1.0 - 0.52 * t)
        pts.append((-w, z))
    return pts


def ear_front_surface_y(side: int, x: float, z: float) -> float:
    t = max(0.0, min(0.98, (z - P["ear_base_z"]) / P["ear_height"]))
    cx = side * (P["ear_base_x"] + 2.1 * t - 0.9 * t * t)
    cy = P["ear_base_y"] - 1.2 * t + 0.35 * math.sin(math.pi * t)
    rx = P["ear_base_rx"] * (1.0 - t) ** 0.74 + 0.55
    ry = P["ear_base_ry"] * (1.0 - t) ** 0.82 + 0.45
    dx = x - cx
    if side * dx < 0:
        # Undo the inner-side compression used by the outer ear mesh.
        dx /= max(0.25, 0.78 + 0.10 * t)
    q = max(0.02, 1.0 - (dx / max(rx, 0.001)) ** 2)
    return cy - ry * math.sqrt(q)


def create_ear_inner_patch(
    name: str,
    side: int,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    pts = teardrop_outline(8.8, 18.5, 34)
    cx = side * 24.2
    cz = 104.8
    outer_offset = 0.18
    inset_depth = 0.62
    front_loop: list[tuple[float, float, float]] = []
    back_loop: list[tuple[float, float, float]] = []
    for u, v in pts:
        x = cx + u
        z = cz + v
        surface_y = ear_front_surface_y(side, x, z)
        front_loop.append((x, surface_y - outer_offset, z))
        back_loop.append((x, surface_y + inset_depth, z))
    verts = front_loop + back_loop
    n = len(pts)
    faces: list[tuple[int, ...]] = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    bevel = obj.modifiers.new("Inset softness", "BEVEL")
    bevel.width = 0.34
    bevel.segments = 3
    apply_modifier(obj, bevel.name)
    set_smooth(obj)
    return obj


def create_curve(
    name: str,
    points: Sequence[tuple[float, float, float]],
    bevel_depth: float,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    curve = bpy.data.curves.new(name + "_Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 16
    curve.bevel_depth = bevel_depth
    curve.bevel_resolution = 3
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for p, co in zip(spline.bezier_points, points):
        p.co = co
        p.handle_left_type = "AUTO"
        p.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    assign_material(obj, material)
    # Convert decorative curves to meshes so they survive GLB/STL export.
    deselect_all()
    activate(obj)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.name = name
    set_smooth(obj)
    return obj


def create_tail(
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    segs = 36
    profile = [
        (0.00, 0.45, 0.35, 0.0),
        (0.06, 3.2, 2.0, 0.8),
        (0.16, 5.1, 3.2, 1.7),
        (0.30, 5.7, 3.8, 2.6),
        (0.47, 5.2, 3.5, 3.2),
        (0.64, 4.2, 2.8, 3.0),
        (0.79, 3.0, 2.0, 2.6),
        (0.91, 1.65, 1.05, 2.0),
        (1.00, 0.35, 0.28, 1.4),
    ]
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []
    for t, rx, ry, yoff in profile:
        z = P["tail_base_z"] + P["tail_height"] * t
        cy = REAR_Y - 0.9 + yoff
        for s in range(segs):
            a = 2 * math.pi * s / segs
            x = rx * math.cos(a)
            y = cy + ry * math.sin(a)
            verts.append((x, y, z))
    for i in range(len(profile) - 1):
        for s in range(segs):
            n = (s + 1) % segs
            faces.append((i * segs + s, i * segs + n, (i + 1) * segs + n, (i + 1) * segs + s))
    faces.append(tuple(reversed(range(segs))))
    faces.append(tuple((len(profile) - 1) * segs + s for s in range(segs)))
    mesh = bpy.data.meshes.new("Tail_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate()
    mesh.update()
    obj = bpy.data.objects.new("Tail_Teardrop", mesh)
    collection.objects.link(obj)
    assign_material(obj, material)
    set_smooth(obj)
    subdiv = obj.modifiers.new("Tail smoothing", "SUBSURF")
    subdiv.levels = 1
    subdiv.render_levels = 2
    apply_modifier(obj, subdiv.name)
    return obj


def create_feet(material: bpy.types.Material, collection: bpy.types.Collection) -> list[bpy.types.Object]:
    feet: list[bpy.types.Object] = []
    for ix, x in enumerate((-26.5, 26.5)):
        for iy, y in enumerate((-12.7, 12.7)):
            foot = make_uv_sphere(
                f"Foot_{'L' if x < 0 else 'R'}_{'Front' if y < 0 else 'Rear'}",
                (x, y, 2.4),
                (4.7, 4.2, 2.1),
                material,
                collection,
                segments=32,
                rings=16,
            )
            feet.append(foot)
    return feet


# -----------------------------------------------------------------------------
# Body shells and production details
# -----------------------------------------------------------------------------
def create_hollow_half(
    outer_master: bpy.types.Object,
    name: str,
    front: bool,
    collection: bpy.types.Collection,
    cutters: bpy.types.Collection,
) -> bpy.types.Object:
    half = duplicate_object(outer_master, name, collection)
    gap = P["shell_gap"]
    if front:
        loc_y = -100.0 - gap * 0.25
        dim_y = 200.0 - gap * 0.5
    else:
        loc_y = 100.0 + gap * 0.25
        dim_y = 200.0 - gap * 0.5
    slice_box = rounded_box(
        name + "_HalfSpace",
        (300.0, dim_y, 300.0),
        (0.0, loc_y, BODY_CENTER_Z),
        0.0,
        None,
        cutters,
        segments=1,
    )
    boolean_apply(half, slice_box, "INTERSECT", "Split shell")
    remove_object(slice_box)

    wall = P["wall_thickness"]
    inner = rounded_box(
        name + "_InnerCavity",
        (
            P["body_width"] - 2 * wall,
            P["body_depth"] - 2 * wall,
            P["body_height"] - 2 * wall,
        ),
        (0.0, 0.0, BODY_CENTER_Z),
        max(1.0, P["body_corner_radius"] - wall),
        None,
        cutters,
        segments=8,
    )
    boolean_apply(half, inner, "DIFFERENCE", "Hollow shell")
    remove_object(inner)
    return half


def cut_usb_port(shell: bpy.types.Object, cutters: bpy.types.Collection) -> None:
    cut_with_rounded_box(
        shell,
        shell.name + "_USB_Cut",
        (12.0, 11.8, 6.2),
        (P["body_width"] * 0.5 - 0.6, -8.5, P["usb_center_z"]),
        2.0,
        cutters,
    )


def cut_display(shell: bpy.types.Object, cutters: bpy.types.Collection) -> None:
    cut_with_rounded_box(
        shell,
        shell.name + "_DisplayCut",
        (P["display_width"], 11.5, P["display_height"]),
        (0.0, FRONT_Y - 0.2, P["display_center_z"]),
        6.0,
        cutters,
    )


def cut_speaker_holes(shell: bpy.types.Object, cutters: bpy.types.Collection) -> None:
    positions = [(-8.0, 0.0), (-4.0, 1.2), (0.0, 1.7), (4.0, 1.2), (8.0, 0.0)]
    for i, (x, dz) in enumerate(positions):
        cutter = create_cylinder_y(
            f"SpeakerHole_{i+1}",
            1.05,
            8.0,
            (x, REAR_Y - 0.3, 15.8 + dz),
            None,
            cutters,
            vertices=32,
        )
        boolean_apply(shell, cutter, "DIFFERENCE", f"Speaker hole {i+1}")
        remove_object(cutter)


def cut_tail_socket(shell: bpy.types.Object, cutters: bpy.types.Collection) -> None:
    cutter = create_cylinder_y(
        shell.name + "_TailSocket",
        2.45,
        9.0,
        (0.0, REAR_Y - 1.2, P["tail_base_z"] + 5.0),
        None,
        cutters,
        vertices=40,
    )
    boolean_apply(shell, cutter, "DIFFERENCE", "Tail mounting socket")
    remove_object(cutter)


def add_shell_lip(material: bpy.types.Material, collection: bpy.types.Collection) -> bpy.types.Object:
    wall = P["wall_thickness"]
    return create_rounded_rect_ring(
        "Rear_Alignment_Lip",
        P["body_width"] - 2 * wall - 0.5,
        P["body_height"] - 2 * wall - 0.5,
        P["body_width"] - 2 * wall - 3.2,
        P["body_height"] - 2 * wall - 3.2,
        2.1,
        max(2.0, P["body_corner_radius"] - wall - 0.3),
        max(1.0, P["body_corner_radius"] - wall - 1.9),
        (0.0, -0.75, BODY_CENTER_Z),
        material,
        collection,
        segments=10,
    )


def create_button(material: bpy.types.Material, collection: bpy.types.Collection) -> bpy.types.Object:
    btn = rounded_box(
        "Side_Power_Button",
        (2.2, 7.0, 10.2),
        (P["body_width"] * 0.5 + 0.75, -7.0, P["button_center_z"]),
        1.1,
        material,
        collection,
        segments=5,
    )
    return btn


def create_screen_components(
    shell_mat: bpy.types.Material,
    glass_mat: bpy.types.Material,
    screen_mat: bpy.types.Material,
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    bezel = create_rounded_rect_ring(
        "Display_Bezel",
        P["bezel_width"],
        P["bezel_height"],
        P["display_width"] - 0.8,
        P["display_height"] - 0.8,
        2.0,
        7.7,
        5.6,
        (0.0, FRONT_Y - 1.15, P["display_center_z"]),
        shell_mat,
        collection,
        segments=12,
    )
    glass = create_rounded_rect_prism(
        "Display_Glass",
        P["display_width"] - 1.4,
        P["display_height"] - 1.4,
        1.1,
        5.2,
        (0.0, FRONT_Y - 2.15, P["display_center_z"]),
        glass_mat,
        collection,
        bevel=0.35,
        segments=12,
    )
    active = create_rounded_rect_prism(
        "Display_Active_Area",
        P["display_width"] - 5.0,
        P["display_height"] - 5.0,
        0.35,
        3.9,
        (0.0, FRONT_Y - 1.48, P["display_center_z"]),
        screen_mat,
        collection,
        bevel=0.08,
        segments=12,
    )
    return [bezel, glass, active]


# -----------------------------------------------------------------------------
# Internal placeholders and engineering details
# -----------------------------------------------------------------------------
def create_internals(
    shell_mat: bpy.types.Material,
    pcb_mat: bpy.types.Material,
    metal_mat: bpy.types.Material,
    battery_mat: bpy.types.Material,
    collection: bpy.types.Collection,
) -> list[bpy.types.Object]:
    objs: list[bpy.types.Object] = []
    boss_positions = [(-26.5, 23.0), (26.5, 23.0), (-26.5, 78.0), (26.5, 78.0)]
    for i, (x, z) in enumerate(boss_positions, 1):
        boss = create_tube_y(
            f"Rear_Screw_Boss_{i}", 4.0, 1.45, 13.5, (x, 7.8, z), shell_mat, collection
        )
        objs.append(boss)
        front_post = create_tube_y(
            f"Front_Screw_Post_{i}", 3.3, 1.20, 5.2, (x, -3.1, z), shell_mat, collection
        )
        objs.append(front_post)

    pcb = rounded_box("PCB_Placeholder", (43.0, 1.6, 67.0), (0.0, -7.0, 52.0), 2.0, pcb_mat, collection, segments=4)
    objs.append(pcb)
    lcd = rounded_box("LCD_Module_Placeholder", (41.0, 4.2, 58.0), (0.0, -12.2, 57.0), 3.0, metal_mat, collection, segments=4)
    objs.append(lcd)
    battery = rounded_box("Battery_1000mAh_Placeholder", (50.0, 8.0, 31.0), (0.0, 10.5, 36.0), 4.0, battery_mat, collection, segments=5)
    objs.append(battery)
    usb = rounded_box("USB_C_Connector_Placeholder", (8.8, 10.0, 3.4), (35.2, -8.5, P["usb_center_z"]), 0.8, metal_mat, collection, segments=3)
    objs.append(usb)
    return objs


# -----------------------------------------------------------------------------
# Scene organisation, cameras, lighting and exports
# -----------------------------------------------------------------------------
def create_root_empty(collection: bpy.types.Collection) -> bpy.types.Object:
    root = bpy.data.objects.new("PocketMung_MASTER", None)
    collection.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root.empty_display_size = 8.0
    root["units"] = "millimetres"
    root["concept_source"] = "User supplied six-view rounded pet-device image"
    for key, value in P.items():
        root[key] = value
    root["overall_height_with_ears_mm"] = round(P["ear_base_z"] + P["ear_height"], 2)
    root["note"] = "Concept dimensions are inferred; verify exact PCB/connector measurements before manufacturing."
    return root


def add_reference_dimensions(collection: bpy.types.Collection, material: bpy.types.Material) -> None:
    # Thin dimension bars hidden by default; useful when opening the .blend.
    bars = [
        ("DIM_Width_78mm", (P["body_width"], 0.55, 0.55), (0.0, -34.0, -6.0)),
        ("DIM_Height_96mm", (0.55, 0.55, P["body_height"]), (-48.0, -30.0, BODY_CENTER_Z)),
        ("DIM_Depth_42mm", (0.55, P["body_depth"], 0.55), (48.0, 0.0, -6.0)),
    ]
    for name, dims, loc in bars:
        rounded_box(name, dims, loc, 0.25, material, collection, segments=2)


def look_at(obj: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_camera_and_lights(
    collection: bpy.types.Collection,
    floor_mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_plane_add(size=800.0, location=(0.0, 0.0, -0.05))
    floor = bpy.context.object
    floor.name = "Studio_Floor"
    assign_material(floor, floor_mat)
    move_to_collection(floor, collection)

    camera_data = bpy.data.cameras.new("PocketMung_Camera")
    camera = bpy.data.objects.new("PocketMung_Camera", camera_data)
    collection.objects.link(camera)
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = 145.0
    camera_data.lens = 70.0
    bpy.context.scene.camera = camera

    light_specs = [
        ("Key_Light", "AREA", (-120.0, -140.0, 180.0), 180000.0, 115.0, (1.0, 0.82, 0.67)),
        ("Fill_Light", "AREA", (130.0, -100.0, 105.0), 105000.0, 95.0, (0.70, 0.82, 1.0)),
        ("Rim_Light", "AREA", (45.0, 110.0, 165.0), 165000.0, 85.0, (1.0, 0.48, 0.20)),
        ("Top_Softbox", "AREA", (0.0, 0.0, 230.0), 90000.0, 100.0, (1.0, 0.95, 0.90)),
    ]
    for name, typ, loc, energy, size, color in light_specs:
        data = bpy.data.lights.new(name, typ)
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        obj = bpy.data.objects.new(name, data)
        collection.objects.link(obj)
        obj.location = loc
        look_at(obj, (0.0, 0.0, 55.0))
    return camera


def set_collection_visibility(collection: bpy.types.Collection, visible: bool) -> None:
    collection.hide_render = not visible
    collection.hide_viewport = not visible


def render_views(
    output_dir: Path,
    camera: bpy.types.Object,
    ref_collection: bpy.types.Collection,
    prod_collection: bpy.types.Collection,
) -> None:
    scene = bpy.context.scene
    target = (0.0, 0.0, 55.0)
    views = {
        "reference_front": ((0.0, -300.0, 59.0), 142.0),
        "reference_rear": ((0.0, 300.0, 59.0), 142.0),
        "reference_right": ((280.0, 0.0, 59.0), 142.0),
        "reference_top": ((0.0, -1.0, 315.0), 142.0),
        "reference_iso": ((175.0, -225.0, 155.0), 150.0),
    }
    set_collection_visibility(ref_collection, True)
    set_collection_visibility(prod_collection, False)
    for name, (loc, scale) in views.items():
        camera.location = loc
        camera.data.ortho_scale = scale
        look_at(camera, target)
        scene.render.filepath = str(output_dir / f"{name}.png")
        bpy.ops.render.render(write_still=True)

    set_collection_visibility(ref_collection, False)
    set_collection_visibility(prod_collection, True)
    camera.location = (0.0, -300.0, 59.0)
    camera.data.ortho_scale = 142.0
    look_at(camera, target)
    scene.render.filepath = str(output_dir / "production_front.png")
    bpy.ops.render.render(write_still=True)

    set_collection_visibility(ref_collection, True)
    set_collection_visibility(prod_collection, False)


def select_objects(objects: Iterable[bpy.types.Object]) -> list[bpy.types.Object]:
    deselect_all()
    valid = [obj for obj in objects if obj and obj.type == "MESH"]
    for obj in valid:
        obj.hide_set(False)
        obj.select_set(True)
    if valid:
        bpy.context.view_layer.objects.active = valid[0]
    return valid


def export_stl(path: Path, objects: Sequence[bpy.types.Object]) -> None:
    valid = select_objects(objects)
    if not valid:
        return
    try:
        bpy.ops.wm.stl_export(
            filepath=str(path),
            export_selected_objects=True,
            apply_modifiers=True,
            global_scale=1.0,
            ascii_format=False,
        )
    except Exception:
        try:
            bpy.ops.preferences.addon_enable(module="io_mesh_stl")
        except Exception:
            pass
        bpy.ops.export_mesh.stl(
            filepath=str(path),
            use_selection=True,
            global_scale=1.0,
            use_scene_unit=False,
            ascii=False,
        )


def export_glb(path: Path, objects: Sequence[bpy.types.Object]) -> None:
    valid = select_objects(objects)
    if not valid:
        return
    bpy.ops.export_scene.gltf(
        filepath=str(path),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_materials="EXPORT",
        export_yup=True,
    )


def add_readme_text() -> None:
    text = bpy.data.texts.new("README_PocketMung_KR.txt")
    text.write(
        "POCKETMUNG / HAPPY PLAY Blender model\n\n"
        "기준 단위: mm (1 Blender Unit = 1 mm)\n"
        "기본 표시: 첨부 이미지와 같은 깨끗한 레퍼런스 외관\n"
        "숨김 컬렉션 02_PRODUCTION_VARIANT: 세로형 디스플레이, USB-C, 전원 버튼, 스피커 홀 포함\n"
        "숨김 컬렉션 03_INTERNALS: PCB/LCD/배터리 자리와 나사 보스\n"
        "숨김 컬렉션 04_DIMENSIONS: 주요 치수 막대\n\n"
        "주요 외형 치수\n"
        "- 본체 78 x 42 x 96 mm\n"
        "- 귀 포함 높이 약 122.5 mm\n"
        "- 벽 두께 2.4 mm\n"
        "- 전후면 셸 간격 0.55 mm\n\n"
        "주의: 이미지 기반 콘셉트 치수입니다. 실제 제작 전 사용 보드, 배터리, USB-C 위치를 실측해 조정하세요.\n"
        "재생성/수정은 Text Editor의 SOURCE_build_pocketmung.py 또는 동봉 Python 스크립트를 사용하세요.\n"
    )
    try:
        source = Path(__file__).read_text(encoding="utf-8")
        src_text = bpy.data.texts.new("SOURCE_build_pocketmung.py")
        src_text.write(source)
    except Exception:
        pass


def write_manifest(output_dir: Path, objects: dict[str, bpy.types.Object | list[bpy.types.Object]]) -> None:
    manifest = {
        "name": "PocketMung / HAPPY PLAY enclosure",
        "units": "mm",
        "parameters": P,
        "outputs": {
            "blend": "PocketMung_HappyPlay_Detailed.blend",
            "reference_glb": "PocketMung_reference_assembly.glb",
            "production_glb": "PocketMung_production_assembly.glb",
            "stl_directory": "stl/",
        },
        "collections": {
            "01_REFERENCE_ASSEMBLY": "Clean shell matching the supplied multi-view concept",
            "02_PRODUCTION_VARIANT": "Display/USB/button/speaker implementation",
            "03_INTERNALS": "Editable placeholders and screw bosses",
            "04_DIMENSIONS": "Hidden measurement guides",
        },
        "manufacturing_note": "Concept-derived dimensions; verify all electronics before final print.",
    }
    (output_dir / "PocketMung_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    readme = f"""POCKETMUNG / HAPPY PLAY 상세 Blender 모델

파일 구성
- PocketMung_HappyPlay_Detailed.blend : 기본 레퍼런스 외관 + 숨김 생산형/내부 구조
- PocketMung_reference_assembly.glb : 첨부 이미지에 가까운 깨끗한 외관
- PocketMung_production_assembly.glb : 디스플레이/USB-C/전원 버튼/스피커 홀 버전
- stl/*.stl : 파트별 3D 프린팅 파일
- preview_*.png : 정면/후면/측면/상단/아이소메트릭 렌더

주요 치수
- 본체: {P['body_width']} x {P['body_depth']} x {P['body_height']} mm
- 귀 포함 높이: 약 {P['ear_base_z'] + P['ear_height']:.1f} mm
- 기본 벽 두께: {P['wall_thickness']} mm
- 전후면 분할 간격: {P['shell_gap']} mm

Blender에서
1. 01_REFERENCE_ASSEMBLY가 기본으로 보입니다.
2. Outliner에서 01을 끄고 02_PRODUCTION_VARIANT를 켜면 실제 디바이스용 버전이 보입니다.
3. 03_INTERNALS에서 PCB/LCD/배터리 자리와 나사 보스를 확인할 수 있습니다.
4. Text Editor의 SOURCE_build_pocketmung.py에서 파라미터를 바꿔 다시 생성할 수 있습니다.

주의
첨부 이미지에서 외형 비율을 추정해 만든 콘셉트 모델입니다. 실제 출력 전에 Waveshare 보드, 배터리, USB-C 및 체결 부품을 캘리퍼스로 실측해 최종 치수를 조정해야 합니다.
"""
    (output_dir / "README_KR.txt").write_text(readme, encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    stl_dir = output_dir / "stl"
    output_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)

    clear_scene()
    configure_scene()

    root_collection = bpy.data.collections.get("00_SCENE_ROOT") or ensure_collection("00_SCENE_ROOT")
    common = ensure_collection("00_COMMON_CHARACTER_PARTS")
    ref = ensure_collection("01_REFERENCE_ASSEMBLY")
    prod = ensure_collection("02_PRODUCTION_VARIANT")
    internals = ensure_collection("03_INTERNALS")
    dimensions = ensure_collection("04_DIMENSIONS")
    scene_collection = ensure_collection("90_STUDIO")
    cutters = ensure_collection("99_TEMP_CUTTERS")

    # Materials tuned to the supplied warm-white/orange concept render.
    shell_mat = make_material("MAT_Shell_Warm_White", (0.955, 0.935, 0.910, 1.0), roughness=0.31)
    orange_mat = make_material("MAT_Ear_Orange", (1.000, 0.255, 0.035, 1.0), roughness=0.27)
    inner_orange_mat = make_material("MAT_Inner_Ear", (0.62, 0.075, 0.012, 1.0), roughness=0.34)
    crease_mat = make_material("MAT_Ear_Crease", (0.33, 0.030, 0.006, 1.0), roughness=0.40)
    seam_mat = make_material("MAT_Seam_Shadow", (0.18, 0.17, 0.16, 1.0), roughness=0.48)
    glass_mat = make_material("MAT_Display_Glass", (0.018, 0.022, 0.030, 1.0), roughness=0.08, metallic=0.05, transmission=0.22)
    screen_mat = make_material("MAT_Display_Active", (0.040, 0.115, 0.155, 1.0), roughness=0.20, emission=(0.020, 0.220, 0.290, 1.0), emission_strength=0.35)
    pcb_mat = make_material("MAT_PCB", (0.035, 0.26, 0.11, 1.0), roughness=0.55)
    metal_mat = make_material("MAT_Metal", (0.34, 0.36, 0.39, 1.0), roughness=0.28, metallic=0.75)
    battery_mat = make_material("MAT_Battery", (0.50, 0.53, 0.56, 1.0), roughness=0.42, metallic=0.25)
    dim_mat = make_material("MAT_Dimensions", (0.12, 0.48, 1.0, 1.0), roughness=0.35, emission=(0.06, 0.20, 0.80, 1.0), emission_strength=0.25)
    floor_mat = make_material("MAT_Studio_Floor", (0.105, 0.092, 0.085, 1.0), roughness=0.52)

    root = create_root_empty(root_collection)

    outer_master = rounded_box(
        "Body_Outer_Master",
        (P["body_width"], P["body_depth"], P["body_height"]),
        (0.0, 0.0, BODY_CENTER_Z),
        P["body_corner_radius"],
        shell_mat,
        cutters,
        segments=10,
    )

    # Clean reference shells.
    ref_front = create_hollow_half(outer_master, "REF_Body_Front_Blank", True, ref, cutters)
    ref_rear = create_hollow_half(outer_master, "REF_Body_Rear", False, ref, cutters)
    cut_tail_socket(ref_rear, cutters)
    ref_lip = add_shell_lip(shell_mat, ref)

    # Production variant uses independent meshes at the same coordinates.
    prod_front = duplicate_object(ref_front, "PROD_Body_Front_Display", prod)
    prod_rear = duplicate_object(ref_rear, "PROD_Body_Rear", prod)
    cut_display(prod_front, cutters)
    cut_usb_port(prod_front, cutters)
    cut_speaker_holes(prod_rear, cutters)
    prod_lip = duplicate_object(ref_lip, "PROD_Rear_Alignment_Lip", prod)
    screen_parts = create_screen_components(shell_mat, glass_mat, screen_mat, prod)
    button = create_button(orange_mat, prod)

    # Very thin seam shadow ring, visible only in the reference assembly.
    seam = create_rounded_rect_ring(
        "Reference_Seam_Shadow",
        P["body_width"] - 0.8,
        P["body_height"] - 0.8,
        P["body_width"] - 2.0,
        P["body_height"] - 2.0,
        0.35,
        P["body_corner_radius"] - 0.4,
        P["body_corner_radius"] - 1.0,
        (0.0, 0.0, BODY_CENTER_Z),
        seam_mat,
        ref,
        segments=10,
    )

    # Character parts shared visually by both variants.
    ear_l = create_ear_mesh("Ear_Left_Orange", -1, orange_mat, common)
    ear_r = create_ear_mesh("Ear_Right_Orange", 1, orange_mat, common)
    inner_l = create_ear_inner_patch("Ear_Left_Inner_Recess", -1, inner_orange_mat, common)
    inner_r = create_ear_inner_patch("Ear_Right_Inner_Recess", 1, inner_orange_mat, common)
    # Ear fold/crease details, mirrored.
    crease_objs: list[bpy.types.Object] = []
    for side, label in [(-1, "Left"), (1, "Right")]:
        crease_objs.append(
            create_curve(
                f"Ear_{label}_Fold_1",
                [
                    (side * 24.0, ear_front_surface_y(side, side * 24.0, 99.0) - 0.28, 99.0),
                    (side * 25.2, ear_front_surface_y(side, side * 25.2, 102.5) - 0.28, 102.5),
                    (side * 25.5, ear_front_surface_y(side, side * 25.5, 106.2) - 0.28, 106.2),
                ],
                0.28,
                crease_mat,
                common,
            )
        )
        crease_objs.append(
            create_curve(
                f"Ear_{label}_Fold_2",
                [
                    (side * 22.8, ear_front_surface_y(side, side * 22.8, 99.6) - 0.28, 99.6),
                    (side * 23.8, ear_front_surface_y(side, side * 23.8, 101.6) - 0.28, 101.6),
                    (side * 24.1, ear_front_surface_y(side, side * 24.1, 103.8) - 0.28, 103.8),
                ],
                0.20,
                crease_mat,
                common,
            )
        )
    tail = create_tail(shell_mat, common)
    tail_pin = create_cylinder_y("Tail_Mounting_Pin", 2.25, 7.5, (0.0, REAR_Y - 0.7, P["tail_base_z"] + 5.0), shell_mat, common, vertices=40)
    feet = create_feet(shell_mat, common)

    internal_objs = create_internals(shell_mat, pcb_mat, metal_mat, battery_mat, internals)
    add_reference_dimensions(dimensions, dim_mat)
    camera = setup_camera_and_lights(scene_collection, floor_mat)
    add_readme_text()

    remove_object(outer_master)
    # Temp collection should now be empty and hidden.
    set_collection_visibility(cutters, False)
    set_collection_visibility(internals, False)
    set_collection_visibility(dimensions, False)
    set_collection_visibility(prod, False)
    set_collection_visibility(ref, True)
    set_collection_visibility(common, True)

    # Parenting keeps the Outliner tidy without destroying separate print parts.
    for collection in (common, ref, prod, internals, dimensions):
        for obj in collection.objects:
            if obj != root and obj.parent is None:
                obj.parent = root

    # Render before export; render state is restored to reference variant.
    render_views(output_dir, camera, ref, prod)

    # Exporters cannot select objects from a hidden collection, so temporarily
    # make both variants available. Selection still limits each export.
    set_collection_visibility(ref, True)
    set_collection_visibility(prod, True)
    set_collection_visibility(common, True)

    common_meshes = [o for o in common.objects if o.type == "MESH"]
    ref_meshes = [ref_front, ref_rear, ref_lip, seam] + common_meshes
    prod_meshes = [prod_front, prod_rear, prod_lip, button] + screen_parts + common_meshes

    export_glb(output_dir / "PocketMung_reference_assembly.glb", ref_meshes)
    export_glb(output_dir / "PocketMung_production_assembly.glb", prod_meshes)

    export_stl(stl_dir / "Body_Front_Blank.stl", [ref_front])
    export_stl(stl_dir / "Body_Front_Display.stl", [prod_front])
    export_stl(stl_dir / "Body_Rear_Clean.stl", [ref_rear, ref_lip])
    export_stl(stl_dir / "Body_Rear_Production.stl", [prod_rear, prod_lip])
    export_stl(stl_dir / "Ear_Left.stl", [ear_l, inner_l] + [o for o in crease_objs if "Left" in o.name])
    export_stl(stl_dir / "Ear_Right.stl", [ear_r, inner_r] + [o for o in crease_objs if "Right" in o.name])
    export_stl(stl_dir / "Tail.stl", [tail, tail_pin])
    export_stl(stl_dir / "Feet_Set.stl", feet)
    export_stl(stl_dir / "Reference_Assembly.stl", ref_meshes)
    export_stl(stl_dir / "Production_Assembly.stl", prod_meshes)

    write_manifest(output_dir, {})

    # Save with the clean reference version visible by default.
    set_collection_visibility(ref, True)
    set_collection_visibility(prod, False)
    set_collection_visibility(internals, False)
    set_collection_visibility(dimensions, False)
    deselect_all()
    bpy.context.view_layer.objects.active = None
    blend_path = output_dir / "PocketMung_HappyPlay_Detailed.blend"
    try:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), compress=True)
    except TypeError:
        bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    print("\nPocketMung model generated successfully")
    print(f"BLEND: {blend_path}")
    print(f"OUTPUT: {output_dir}")


if __name__ == "__main__":
    main()
