#!/usr/bin/env python3
"""
Villa Rotonda - Accurate Reconstruction
Based on Palladio's Villa Capra (1560s)

Key Features:
- Square plan with four identical porticos
- Six Ionic columns per portico
- Central circular hall with dome
- Piano nobile raised on basement
- Orthographic cameras for plan and section
"""
import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# === PALLADIAN PROPORTIONS (based on research) ===
MODULE = 2.0

CIRCLE_DIAMETER = MODULE * 15
BUILDING_SIZE = MODULE * 10.5

BASEMENT_HEIGHT = MODULE * 2.5
PIANO_NOBILE_HEIGHT = MODULE * 4.0
ATTIC_HEIGHT = MODULE * 1.2
DOME_HEIGHT = MODULE * 3.5

PORTICO_DEPTH = MODULE * 3
PORTICO_WIDTH = MODULE * 8
COLUMN_HEIGHT = MODULE * 3.2
COLUMN_RADIUS = MODULE * 0.22
INTERCOLUMNATION = MODULE * 1.8

CENTRAL_HALL_DIAMETER = MODULE * 6
DOME_DRUM_HEIGHT = MODULE * 1.5

# === MATERIALS ===
def create_material(name, color, roughness=0.5):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

stone_base = create_material("StoneBase", (0.55, 0.52, 0.48), 0.9)
stucco_wall = create_material("StuccoWall", (0.92, 0.90, 0.85), 0.4)
marble_column = create_material("MarbleColumn", (0.95, 0.95, 0.93), 0.2)
roof_tile = create_material("RoofTile", (0.42, 0.28, 0.18), 0.7)
window_glass = create_material("WindowGlass", (0.15, 0.18, 0.22), 0.1)
dome_lead = create_material("DomeLead", (0.35, 0.38, 0.42), 0.3)
interior_wall = create_material("InteriorWall", (0.85, 0.82, 0.75), 0.5)

# === FUNCTIONS ===
def create_cube(name, size, location, material=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if material:
        obj.data.materials.append(material)
    return obj

def create_cylinder(name, radius, depth, location, vertices=32, material=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=vertices, location=location)
    obj = bpy.context.active_object
    obj.name = name
    if material:
        obj.data.materials.append(material)
    return obj

def create_portico(direction_angle, name_suffix):
    rad = math.radians(direction_angle)
    offset = BUILDING_SIZE/2 + PORTICO_DEPTH/2
    x = math.sin(rad) * offset
    y = math.cos(rad) * offset
    
    # Pediment
    portico_roof = create_cube(f"PorticoRoof_{name_suffix}", (PORTICO_WIDTH/2, PORTICO_DEPTH/2, 0.3), (x, y, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + 0.5), stucco_wall)
    
    # Six columns
    for i in range(6):
        col_x_offset = (i - 2.5) * INTERCOLUMNATION
        if direction_angle in [0, 180]:
            col_x = x + col_x_offset
            col_y = y
        else:
            col_x = x
            col_y = y + col_x_offset
        col = create_cylinder(f"Column_{name_suffix}_{i}", COLUMN_RADIUS, COLUMN_HEIGHT, (col_x, col_y, BASEMENT_HEIGHT + COLUMN_HEIGHT/2), 16, marble_column)
    
    # Stairs
    stair_width = PORTICO_WIDTH * 0.7
    stair_depth = PORTICO_DEPTH * 0.4
    num_steps = 7
    for i in range(num_steps):
        step_height = BASEMENT_HEIGHT / num_steps
        step_z = (i + 0.5) * step_height
        step_offset = (i + 0.5) * (stair_depth / num_steps)
        step_x = x + math.sin(rad) * step_offset
        step_y = y + math.cos(rad) * step_offset
        step = create_cube(f"Stairs_{name_suffix}_{i}", (stair_width/2, stair_depth/num_steps/2, step_height/2), (step_x, step_y, step_z), stone_base)

# === BUILD ===
print("Building Villa Rotonda...")

# Basement
basement = create_cube("Basement", (BUILDING_SIZE/2 + 0.2, BUILDING_SIZE/2 + 0.2, BASEMENT_HEIGHT/2), (0, 0, BASEMENT_HEIGHT/2), stone_base)

# Piano nobile
main_body = create_cube("MainBody", (BUILDING_SIZE/2 - 0.1, BUILDING_SIZE/2 - 0.1, PIANO_NOBILE_HEIGHT/2), (0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT/2), stucco_wall)

# Four porticos
print("  Creating four porticos...")
for angle, suffix in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
    create_portico(angle, suffix)

# Attic
attic = create_cube("Attic", (BUILDING_SIZE/2 - 0.3, BUILDING_SIZE/2 - 0.3, ATTIC_HEIGHT/2), (0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + ATTIC_HEIGHT/2), stucco_wall)

# Dome drum
drum = create_cylinder("DomeDrum", CENTRAL_HALL_DIAMETER/2 + 0.3, DOME_DRUM_HEIGHT, (0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + ATTIC_HEIGHT + DOME_DRUM_HEIGHT/2), 48, stucco_wall)

# Dome
bpy.ops.mesh.primitive_uv_sphere_add(radius=CENTRAL_HALL_DIAMETER/2 + 0.3, segments=48, ring_count=24, location=(0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + ATTIC_HEIGHT + DOME_DRUM_HEIGHT))
dome = bpy.context.active_object
dome.name = "Dome"
dome.scale.z = 0.5
dome.data.materials.append(dome_lead)

# Lantern
lantern_base = BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + ATTIC_HEIGHT + DOME_DRUM_HEIGHT + CENTRAL_HALL_DIAMETER/4
bpy.ops.mesh.primitive_cylinder_add(radius=CENTRAL_HALL_DIAMETER/10, depth=MODULE, vertices=16, location=(0, 0, lantern_base + MODULE/2))
lantern = bpy.context.active_object
lantern.name = "Lantern"
lantern.data.materials.append(stucco_wall)

bpy.ops.mesh.primitive_uv_sphere_add(radius=CENTRAL_HALL_DIAMETER/8, segments=24, ring_count=12, location=(0, 0, lantern_base + MODULE))
lantern_dome = bpy.context.active_object
lantern_dome.name = "LanternDome"
lantern_dome.scale.z = 0.5
lantern_dome.data.materials.append(dome_lead)

# Roof
roof = create_cube("MainRoof", (BUILDING_SIZE/2 + 0.5, BUILDING_SIZE/2 + 0.5, MODULE), (0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT + ATTIC_HEIGHT + MODULE/2 - 0.3), roof_tile)

# Windows
win_width = MODULE * 0.6
win_height = MODULE * 1.8
win_z = BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT * 0.6
positions = [(0, -BUILDING_SIZE/2 + 0.2), (0, BUILDING_SIZE/2 - 0.2), (BUILDING_SIZE/2 - 0.2, 0), (-BUILDING_SIZE/2 + 0.2, 0), (BUILDING_SIZE/4, -BUILDING_SIZE/2 + 0.2), (-BUILDING_SIZE/4, -BUILDING_SIZE/2 + 0.2), (BUILDING_SIZE/4, BUILDING_SIZE/2 - 0.2), (-BUILDING_SIZE/4, BUILDING_SIZE/2 - 0.2)]
for i, (x, y) in enumerate(positions):
    create_cube(f"Window_{i}", (win_width/2, 0.1, win_height/2), (x, y, win_z), window_glass)

# Interior hall
hall_lower = create_cylinder("HallLower", CENTRAL_HALL_DIAMETER/2 - 0.5, PIANO_NOBILE_HEIGHT * 0.6, (0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT * 0.3), 48, interior_wall)

# Lighting
bpy.ops.object.light_add(type='SUN', location=(25, -25, 35))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.data.color = (1.0, 0.92, 0.82)
sun.rotation_euler = (math.radians(55), 0, math.radians(45))

bpy.ops.object.light_add(type='AREA', location=(-20, 15, 20))
fill = bpy.context.active_object
fill.data.energy = 1.5
fill.data.color = (0.75, 0.8, 0.9)
fill.data.size = 15.0

# === CAMERAS ===
print("Creating cameras...")

# Perspective
cam_dist = BUILDING_SIZE * 2.5
bpy.ops.object.camera_add(location=(cam_dist * 0.7, -cam_dist * 0.7, BUILDING_SIZE * 0.8))
persp_cam = bpy.context.active_object
persp_cam.name = "PerspectiveCamera"
direction = Vector((0, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT/2)) - persp_cam.location
persp_cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Plan (ortho top)
bpy.ops.object.camera_add(location=(0, 0, BUILDING_SIZE * 2))
plan_cam = bpy.context.active_object
plan_cam.name = "PlanCamera"
plan_cam.data.type = 'ORTHO'
plan_cam.data.ortho_scale = BUILDING_SIZE * 2.5
plan_cam.rotation_euler = (0, 0, 0)

# Section (ortho cut through)
bpy.ops.object.camera_add(location=(BUILDING_SIZE * 2, 0, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT/2))
section_cam = bpy.context.active_object
section_cam.name = "SectionCamera"
section_cam.data.type = 'ORTHO'
section_cam.data.ortho_scale = BUILDING_SIZE * 1.8
section_cam.rotation_euler = (math.radians(90), 0, math.radians(90))

# Elevation (ortho front)
bpy.ops.object.camera_add(location=(0, -BUILDING_SIZE * 2, BASEMENT_HEIGHT + PIANO_NOBILE_HEIGHT/2))
front_cam = bpy.context.active_object
front_cam.name = "FrontElevationCamera"
front_cam.data.type = 'ORTHO'
front_cam.data.ortho_scale = BUILDING_SIZE * 1.5
front_cam.rotation_euler = (math.radians(90), 0, 0)

# Render
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 192
scene.render.resolution_x = 1600
scene.render.resolution_y = 1200

# Render Perspective
scene.camera = persp_cam
scene.render.filepath = '/data/.openclaw/workspace/art/villa_rotonda_perspective.png'
print("Rendering perspective view...")
bpy.ops.render.render(write_still=True)

# Render Plan
scene.camera = plan_cam
scene.render.filepath = '/data/.openclaw/workspace/art/villa_rotonda_plan.png'
print("Rendering plan view...")
bpy.ops.render.render(write_still=True)

# Render Section
scene.camera = section_cam
scene.render.filepath = '/data/.openclaw/workspace/art/villa_rotonda_section.png'
print("Rendering section view...")
bpy.ops.render.render(write_still=True)

# Render Elevation
scene.camera = front_cam
scene.render.filepath = '/data/.openclaw/workspace/art/villa_rotonda_elevation.png'
print("Rendering elevation view...")
bpy.ops.render.render(write_still=True)

print("\n✅ Villa Rotonda complete!")
print("   - Perspective: 3/4 view")
print("   - Plan: Orthographic top view")
print("   - Section: Orthographic cut-through")
print("   - Elevation: Orthographic front facade")
