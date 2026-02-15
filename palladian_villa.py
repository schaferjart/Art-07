#!/usr/bin/env python3
"""
Socrates' Palladian Villa
Shape Grammar Rules:
1. SYMMETRY: All operations mirror across central axis
2. PROPORTION: Golden ratio (1:1.618) and musical intervals (4:3, 3:2)
3. HIERARCHY: Base (rusticated) → Piano Nobile (refined) → Attic → Pediment
4. RHYTHM: Column/pilaster spacing follows harmonic progression
"""
import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# === SHAPE GRAMMAR DEFINITIONS ===

def create_cube(name, size, location, rotation=(0,0,0)):
    """Basic shape: Cube"""
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    return obj

def create_cylinder(name, radius, depth, location, rotation=(0,0,0), vertices=16):
    """Basic shape: Cylinder (for columns)"""
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location, rotation=rotation)
    obj = bpy.context.active_object
    obj.name = name
    return obj

def mirror_x(obj, offset=0):
    """Rule: Mirror across X axis"""
    bpy.ops.object.duplicate()
    mirrored = bpy.context.active_object
    mirrored.location.x = -mirrored.location.x + (2 * offset)
    return mirrored

def create_symmetric_pair(name, location, size, spacing):
    """Rule: Create symmetric pair"""
    left = create_cube(f"{name}_L", size, (location[0] - spacing/2, location[1], location[2]))
    right = create_cube(f"{name}_R", size, (location[0] + spacing/2, location[1], location[2]))
    return left, right

# === MATERIALS ===
def create_material(name, color, roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
    return mat

# Rusticated stone (ground floor)
stone_rustic = create_material("RusticStone", (0.55, 0.5, 0.45), roughness=0.9)
# Refined stucco (piano nobile)
stucco_refined = create_material("RefinedStucco", (0.95, 0.93, 0.88), roughness=0.4)
# Marble/limestone (columns, details)
marble = create_material("Marble", (0.98, 0.97, 0.94), roughness=0.2)
# Roof tiles
roof_tiles = create_material("RoofTiles", (0.35, 0.2, 0.15), roughness=0.8)
# Glass
window_glass = create_material("WindowGlass", (0.1, 0.15, 0.2), roughness=0.1, metallic=0.8)

# === PALLADIAN PROPORTIONS ===
# Based on Villa Rotonda / Villa Barbaro proportions
MODULE = 2.0  # Base unit
center_x, center_y = 0, 0

# Overall dimensions (1:1.618 golden ratio)
VILLA_WIDTH = MODULE * 16
VILLA_DEPTH = MODULE * 10
VILLA_HEIGHT_BASE = MODULE * 2.5
VILLA_HEIGHT_PIANO = MODULE * 3.5
VILLA_HEIGHT_ATTIC = MODULE * 1.5

# === CONSTRUCTION: BASEMENT (RUSTICATED) ===
print("Building rusticated base...")
base = create_cube("Base", (VILLA_WIDTH/2, VILLA_DEPTH/2, VILLA_HEIGHT_BASE/2), 
                   (center_x, center_y, VILLA_HEIGHT_BASE/2))
base.data.materials.append(stone_rustic)

# Add rustication texture via displacement (simplified as bands)
for i in range(5):
    z = (i + 0.5) * (VILLA_HEIGHT_BASE / 5)
    band = create_cube(f"RusticBand_{i}", (VILLA_WIDTH/2 + 0.1, VILLA_DEPTH/2 + 0.1, 0.05),
                       (center_x, center_y, z))
    band.data.materials.append(stone_rustic)

# === CONSTRUCTION: PIANO NOBILE (MAIN FLOOR) ===
print("Building piano nobile...")
piano_y = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO/2
piano_nobile = create_cube("PianoNobile", (VILLA_WIDTH/2 - 0.2, VILLA_DEPTH/2 - 0.2, VILLA_HEIGHT_PIANO/2),
                           (center_x, center_y, piano_y))
piano_nobile.data.materials.append(stucco_refined)

# === CONSTRUCTION: ATTIC ===
print("Building attic...")
attic_y = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO + VILLA_HEIGHT_ATTIC/2
attic = create_cube("Attic", (VILLA_WIDTH/2 - 0.4, VILLA_DEPTH/2 - 0.4, VILLA_HEIGHT_ATTIC/2),
                    (center_x, center_y, attic_y))
attic.data.materials.append(stucco_refined)

# === CONSTRUCTION: PEDIMENT (CENTRAL) ===
print("Building central pediment...")
pediment_width = VILLA_WIDTH * 0.6
pediment_height = MODULE * 2
pediment_depth = VILLA_DEPTH * 0.3
pediment_y = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO + VILLA_HEIGHT_ATTIC + pediment_height/2

# Triangular pediment using a prism (simplified as scaled cube for now)
pediment = create_cube("Pediment", (pediment_width/2, pediment_depth/2, pediment_height/2),
                       (center_x, center_y, pediment_y))
pediment.data.materials.append(stucco_refined)

# === COLUMNS / PILASTERS (TUSCAN ORDER - SIMPLIFIED) ===
print("Building column order...")
COL_HEIGHT = VILLA_HEIGHT_PIANO
COL_RADIUS = MODULE * 0.25
COL_SPACING = MODULE * 2.5

# Front portico columns (6 columns, 3 pairs)
portico_depth = VILLA_DEPTH/2 + COL_RADIUS * 2
for i in range(3):
    x_offset = (i - 1) * COL_SPACING * 2
    # Front row
    col_front = create_cylinder(f"Column_F_{i}", COL_RADIUS, COL_HEIGHT,
                                (center_x + x_offset, portico_depth, VILLA_HEIGHT_BASE + COL_HEIGHT/2))
    col_front.data.materials.append(marble)
    # Mirror for symmetry if not center
    if x_offset != 0:
        col_front_mirrored = create_cylinder(f"Column_F_{i}_mir", COL_RADIUS, COL_HEIGHT,
                                             (center_x - x_offset, portico_depth, VILLA_HEIGHT_BASE + COL_HEIGHT/2))
        col_front_mirrored.data.materials.append(marble)

# === WINDOWS (RHYTHMIC GRID) ===
print("Placing windows...")
WIN_WIDTH = MODULE * 0.8
WIN_HEIGHT = MODULE * 1.5
WIN_DEPTH = 0.2

# Piano nobile windows (symmetric grid)
win_z = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO * 0.6
win_positions = [
    (MODULE * 3, 0), (MODULE * 5, 0), (MODULE * 7, 0),
    (0, MODULE * 3), (0, MODULE * 4)
]

for x, y in win_positions:
    if x != 0:  # Skip center on front (that's the door/portico)
        win = create_cube(f"Window_{x}_{y}", (WIN_WIDTH/2, WIN_DEPTH, WIN_HEIGHT/2),
                          (center_x + x, y if y != 0 else VILLA_DEPTH/2 - 0.3, win_z))
        win.data.materials.append(window_glass)
        # Mirror
        if x != 0:
            win_mir = create_cube(f"Window_mir_{x}_{y}", (WIN_WIDTH/2, WIN_DEPTH, WIN_HEIGHT/2),
                                  (center_x - x, y if y != 0 else VILLA_DEPTH/2 - 0.3, win_z))
            win_mir.data.materials.append(window_glass)

# === CENTRAL DOME (PALLADIAN FEATURE) ===
print("Building dome...")
dome_base = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO + VILLA_HEIGHT_ATTIC + pediment_height
dome_radius = pediment_width * 0.35

# Dome base (drum)
bpy.ops.mesh.primitive_cylinder_add(radius=dome_radius, depth=MODULE, vertices=32,
                                    location=(center_x, center_y, dome_base + MODULE/2))
drum = bpy.context.active_object
drum.name = "DomeDrum"
drum.data.materials.append(stucco_refined)

# The dome itself (UV sphere, upper half)
bpy.ops.mesh.primitive_uv_sphere_add(radius=dome_radius, segments=32, ring_count=16,
                                     location=(center_x, center_y, dome_base + MODULE))
dome = bpy.context.active_object
dome.name = "Dome"
dome.scale.z = 0.6  # Squash to proper dome proportion
dome.data.materials.append(stucco_refined)

# Cupola on top
bpy.ops.mesh.primitive_cylinder_add(radius=dome_radius*0.15, depth=MODULE*0.8, vertices=16,
                                    location=(center_x, center_y, dome_base + MODULE + dome_radius*0.6))
cupola = bpy.context.active_object
cupola.name = "Cupola"
cupola.data.materials.append(marble)

# === ROOF ===
print("Building roof...")
roof_height = MODULE * 1.5
roof_y = VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO + VILLA_HEIGHT_ATTIC

# Main hipped roof (simplified as sloped planes)
roof = create_cube("Roof", (VILLA_WIDTH/2 + 0.3, VILLA_DEPTH/2 + 0.3, roof_height/2),
                   (center_x, center_y, roof_y + roof_height/2))
roof.data.materials.append(roof_tiles)

# === STAIRS ===
print("Adding stairs...")
stairs_width = COL_SPACING * 4
stairs_depth = MODULE * 1.5
stairs_height = VILLA_HEIGHT_BASE
stairs_steps = 7

for i in range(stairs_steps):
    step_height = stairs_height / stairs_steps
    step_depth = stairs_depth / stairs_steps
    y_pos = portico_depth + stairs_depth - (i + 0.5) * step_depth
    z_pos = (i + 0.5) * step_height
    step = create_cube(f"Step_{i}", (stairs_width/2, step_depth/2, step_height/2),
                       (center_x, y_pos, z_pos))
    step.data.materials.append(stone_rustic)

# === LIGHTING ===
print("Setting up lighting...")
# Sun (warm, angled like morning sun)
bpy.ops.object.light_add(type='SUN', location=(20, -20, 30))
sun = bpy.context.active_object
sun.data.energy = 5.0
sun.data.color = (1.0, 0.95, 0.85)
sun.rotation_euler = (math.radians(50), 0, math.radians(45))

# Fill light (cool, opposite side)
bpy.ops.object.light_add(type='AREA', location=(-15, 10, 15))
fill = bpy.context.active_object
fill.data.energy = 2.0
fill.data.color = (0.75, 0.8, 0.9)
fill.data.size = 10.0

# Rim light (dramatic, highlights edges)
bpy.ops.object.light_add(type='SUN', location=(0, 30, 10))
rim = bpy.context.active_object
rim.data.energy = 1.5
rim.data.color = (0.9, 0.9, 1.0)
rim.rotation_euler = (math.radians(80), 0, math.radians(180))

# === CAMERA ===
print("Positioning camera...")
# Three-quarter view, classic architectural perspective
cam_distance = max(VILLA_WIDTH, VILLA_DEPTH) * 1.8
cam_angle = math.radians(30)
bpy.ops.object.camera_add(location=(cam_distance * math.cos(cam_angle), 
                                     -cam_distance * math.sin(cam_angle), 
                                     VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO))
camera = bpy.context.active_object
camera.name = "ArchitectCamera"

# Point at villa center
direction = Vector((center_x, center_y, VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO/2)) - camera.location
rot_quat = direction.to_track_quat('-Z', 'Y')
camera.rotation_euler = rot_quat.to_euler()

# === RENDER SETTINGS ===
print("Configuring render...")
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 128  # Higher quality for architecture
scene.render.resolution_x = 1200
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100

# Output
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/data/.openclaw/workspace/art/palladian_villa.png'

print("🏛️ Rendering Palladian Villa...")
print(f"   Dimensions: {VILLA_WIDTH:.1f} x {VILLA_DEPTH:.1f} x {VILLA_HEIGHT_BASE + VILLA_HEIGHT_PIANO + VILLA_HEIGHT_ATTIC:.1f}m")
print(f"   Style: Rusticated base + Piano Nobile + Attic + Pediment + Dome")
print(f"   Features: Symmetrical portico, column order, rhythmic windows")
print(f"   Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"   Samples: {scene.cycles.samples}")

bpy.ops.render.render(write_still=True)

print(f"\n✅ Architectural render complete!")
print(f"   Saved to: {scene.render.filepath}")
print(f"   Shape Grammar Rules Applied: Symmetry, Proportion, Hierarchy, Rhythm")
