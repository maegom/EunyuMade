#!/usr/bin/env python3
"""Idempotently refine the PocketMung ears to match the supplied soft 6-view concept."""

from pathlib import Path

path = Path(__file__).with_name("build_pocketmung.py")
text = path.read_text(encoding="utf-8")

simple = {
    '    "ear_base_z": 91.0,\n': '    "ear_base_z": 90.5,\n',
    '    "ear_height": 31.5,\n': '    "ear_height": 29.5,\n',
    '    "ear_base_rx": 10.2,\n': '    "ear_base_rx": 11.0,\n',
    '    "ear_base_ry": 7.2,\n': '    "ear_base_ry": 7.9,\n',
    '        "- 귀 포함 높이 약 122.5 mm\\n"\n': '        "- 귀 포함 높이 약 120.0 mm\\n"\n',
}
for old, new in simple.items():
    if old in text:
        text = text.replace(old, new)
    elif new not in text:
        raise RuntimeError(f"Expected parameter line not found: {old!r}")

old_ear = '''def create_ear_mesh(
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
'''

new_ear = '''def create_ear_mesh(
    name: str,
    side: int,
    material: bpy.types.Material,
    collection: bpy.types.Collection,
) -> bpy.types.Object:
    # The supplied concept has short, plush ears rather than needle-like cones.
    # The final ring stops below the tip and is closed with a raised apex so the
    # subdivision surface produces a softly rounded cap.
    rings = 18
    segs = 40
    ring_t_max = 0.965
    verts: list[tuple[float, float, float]] = []
    faces: list[tuple[int, ...]] = []
    for i in range(rings):
        t = ring_t_max * i / (rings - 1)
        cx = side * (P["ear_base_x"] + 1.70 * t - 0.45 * t * t)
        cy = P["ear_base_y"] - 0.78 * t + 0.26 * math.sin(math.pi * t)
        z = P["ear_base_z"] + P["ear_height"] * t
        rx = P["ear_base_rx"] * (1.0 - t) ** 0.58 + 0.30
        ry = P["ear_base_ry"] * (1.0 - t) ** 0.65 + 0.26
        for s in range(segs):
            a = 2.0 * math.pi * s / segs
            local_x = rx * math.cos(a)
            # Keep the inward edge slightly straighter, as in the reference.
            if side * local_x < 0:
                local_x *= 0.82 + 0.08 * t
            local_y = ry * math.sin(a)
            if local_y > 0:
                local_y *= 0.93
            # A shallow sloped base helps the ear disappear naturally into the top.
            zz = z + 0.28 * math.cos(a) * (1.0 - t)
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

    apex_index = len(verts)
    apex_x = side * (P["ear_base_x"] + 1.32)
    apex_y = P["ear_base_y"] - 0.78
    apex_z = P["ear_base_z"] + P["ear_height"] + 0.55
    verts.append((apex_x, apex_y, apex_z))
    last = (rings - 1) * segs
    for s in range(segs):
        n = (s + 1) % segs
        faces.append((last + s, last + n, apex_index))

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
'''
if old_ear in text:
    text = text.replace(old_ear, new_ear)
elif new_ear not in text:
    raise RuntimeError("Original ear mesh function was not found")

old_surface = '''def ear_front_surface_y(side: int, x: float, z: float) -> float:
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
'''
new_surface = '''def ear_front_surface_y(side: int, x: float, z: float) -> float:
    t = max(0.0, min(0.965, (z - P["ear_base_z"]) / P["ear_height"]))
    cx = side * (P["ear_base_x"] + 1.70 * t - 0.45 * t * t)
    cy = P["ear_base_y"] - 0.78 * t + 0.26 * math.sin(math.pi * t)
    rx = P["ear_base_rx"] * (1.0 - t) ** 0.58 + 0.30
    ry = P["ear_base_ry"] * (1.0 - t) ** 0.65 + 0.26
    dx = x - cx
    if side * dx < 0:
        dx /= max(0.25, 0.82 + 0.08 * t)
    q = max(0.02, 1.0 - (dx / max(rx, 0.001)) ** 2)
    return cy - ry * math.sqrt(q)
'''
if old_surface in text:
    text = text.replace(old_surface, new_surface)
elif new_surface not in text:
    raise RuntimeError("Original ear surface helper was not found")

old_patch = '''    pts = teardrop_outline(8.8, 18.5, 34)
    cx = side * 24.2
    cz = 104.8
    outer_offset = 0.18
    inset_depth = 0.62
'''
new_patch = '''    pts = teardrop_outline(10.4, 17.2, 38)
    cx = side * 24.0
    cz = 103.2
    outer_offset = 0.28
    inset_depth = 0.68
'''
if old_patch in text:
    text = text.replace(old_patch, new_patch)
elif new_patch not in text:
    raise RuntimeError("Original inner-ear patch parameters were not found")

path.write_text(text, encoding="utf-8")
print(f"Refined ear geometry in {path}")
