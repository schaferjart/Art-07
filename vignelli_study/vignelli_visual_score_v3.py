#!/usr/bin/env python3
"""
Vignelli Visual Score V3: Color as Data
Response to Critic Session 02: "This is a morgue"

Key Changes:
- Color temperature driven by spatial position (warm→cool gradient)
- Josef Albers color interaction: simultaneous contrast
- Material roughness varies with grid "importance"
- Height + Color both use Fibonacci logic
"""
import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Grid parameters
COLS = 12
ROWS = 12
MODULE_SIZE = 1.0
GUTTER = 0.1
FIB = [1, 2, 3, 5, 8, 13]

def color_from_temperature(t):
    """
    t = 0.0 (cool/blue) → 1.0 (warm/red)
    Josef Albers principle: Color is relational, not absolute
    """
    # Cool: cyan-blue
    cool = Vector((0.2, 0.5, 0.85))
    # Warm: orange-red
    warm = Vector((0.95, 0.4, 0.15))
    
    color = cool.lerp(warm, t)
    return (*color, 1.0)

def create_material(name, color, roughness, transmission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Transmission Weight'].default_value = transmission
    bsdf.inputs['IOR'].default_value = 1.45
    return mat

# Generate materials palette (7 temperature stops)
materials = []
for i in range(7):
    t = i / 6.0
    color = color_from_temperature(t)
    # Roughness: warmer = glossier (more "important")
    roughness = 0.7 - (t * 0.5)  # 0.7→0.2
    transmission = 0.1 if i % 2 == 0 else 0.0  # Subtle glass on even steps
    mat = create_material(f"Temp_{i}", color, roughness, transmission)
    materials.append(mat)

# Generate Grid
center = Vector((COLS * (MODULE_SIZE + GUTTER) / 2, ROWS * (MODULE_SIZE + GUTTER) / 2))

for c in range(COLS):
    for r in range(ROWS):
        x = c * (MODULE_SIZE + GUTTER)
        y = r * (MODULE_SIZE + GUTTER)
        pos = Vector((x, y))
        
        # Distance from center (normalized)
        dist = (pos - center).length
        max_dist = center.length
        normalized_dist = dist / max_dist
        
        # Temperature: center=warm (1.0), edges=cool (0.0)
        temperature = 1.0 - normalized_dist
        
        # Select material based on temperature
        mat_index = int(temperature * 6)
        mat_index = max(0, min(6, mat_index))
        
        # Fibonacci height (same as v2)
        is_harmonic_x = (c % 3 == 0)
        is_harmonic_y = (r % 4 == 0)
        fib_index = (c + r) % len(FIB)
        
        if is_harmonic_x and is_harmonic_y:
            height = FIB[fib_index] * 0.35  # Taller peaks
        elif is_harmonic_x or is_harmonic_y:
            height = FIB[fib_index] * 0.2
        else:
            height = 0.1
        
        # Create block
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2))
        block = bpy.context.active_object
        block.scale = (MODULE_SIZE, MODULE_SIZE, height)
        block.data.materials.append(materials[mat_index])

# Ground (neutral cool gray)
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = create_material("Ground", (0.15, 0.15, 0.18, 1.0), 0.8)
ground.data.materials.append(ground_mat)

# Lighting: Warmer key, cooler fill (chromatic contrast)
bpy.ops.object.light_add(type='SUN', location=(15, -10, 25))
sun = bpy.context.active_object
sun.data.energy = 5.5
sun.data.color = (1.0, 0.92, 0.8)  # Warm sunlight
sun.rotation_euler = (math.radians(60), 0, math.radians(35))

# Cool fill light
bpy.ops.object.light_add(type='AREA', location=(-12, 12, 18))
fill = bpy.context.active_object
fill.data.energy = 3.0
fill.data.color = (0.7, 0.85, 1.0)  # Cool sky
fill.data.size = 8.0

# Camera
cam_pos = (COLS * 2.5, -COLS * 1.5, COLS * 2)
bpy.ops.object.camera_add(location=cam_pos)
cam = bpy.context.active_object
direction = Vector((COLS/2, ROWS/2, 0)) - Vector(cam_pos)
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Render
scene = bpy.context.scene
scene.camera = cam
scene.render.filepath = "/data/.openclaw/workspace/art/renders/2026-02-16/vignelli_visual_score_v3.png"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1600
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.cycles.device = 'CPU'

print("🎨 Rendering Vignelli V3: Color as Data...")
bpy.ops.render.render(write_still=True)
print(f"✅ Render complete: {scene.render.filepath}")
