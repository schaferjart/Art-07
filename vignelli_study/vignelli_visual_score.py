import bpy
import random
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# VIGNELLI PARAMETERS
COLS = 12
ROWS = 12
MODULE_SIZE = 1.0
GUTTER = 0.1
VIGNELLI_RED = (0.85, 0.1, 0.05, 1.0)
BONE_WHITE = (0.95, 0.95, 0.9, 1.0)

def create_mat(name, color):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = 0.1 # Sharp, modern
    return mat

red_m = create_mat("VignelliRed", VIGNELLI_RED)
white_m = create_mat("ArchitecturalWhite", BONE_WHITE)

# Generate Grid
for c in range(COLS):
    for r in range(ROWS):
        # The "Logic": Create a varied extrusions based on a grid pattern
        # Every 3rd row/col is a "dominant" beat
        is_beat = (c % 3 == 0) or (r % 4 == 0)
        
        x = c * (MODULE_SIZE + GUTTER)
        y = r * (MODULE_SIZE + GUTTER)
        
        height = random.uniform(0.1, 0.5)
        if is_beat:
            height = random.uniform(2.0, 4.0)
            
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2))
        block = bpy.context.active_object
        block.scale = (MODULE_SIZE, MODULE_SIZE, height)
        
        # Color logic: Red for the beats, white for the texture
        block.data.materials.append(red_m if is_beat and random.random() > 0.3 else white_m)

# Ground
bpy.ops.mesh.primitive_plane_add(size=100, location=(0,0,0))
ground = bpy.context.active_object
ground.data.materials.append(white_m)

# Lighting: Strong, graphic shadows
bpy.ops.object.light_add(type='SUN', location=(10, -10, 20))
sun = bpy.context.active_object
sun.data.energy = 5
sun.rotation_euler = (math.radians(45), 0, math.radians(45))

# Camera: High-angle isometric-style perspective
cam_pos = (COLS * 2, -COLS, COLS * 1.5)
bpy.ops.object.camera_add(location=cam_pos)
cam = bpy.context.active_object
cam.data.type = 'ORTHO'
cam.data.ortho_scale = COLS * 1.5
# Look at center
direction = Vector((COLS/2, ROWS/2, 0)) - Vector(cam_pos)
# (Simplified rotation for now)
cam.rotation_euler = (math.radians(55), 0, math.radians(45))

# Render
bpy.context.scene.camera = cam
bpy.context.scene.render.filepath = "/data/.openclaw/workspace/art/renders/2026-02-15/vignelli_visual_score_01.png"
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 1200
bpy.ops.render.render(write_still=True)
