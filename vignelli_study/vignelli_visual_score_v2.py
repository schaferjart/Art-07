import bpy
import math
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# VIGNELLI & FIBONACCI PARAMETERS
COLS = 12
ROWS = 12
MODULE_SIZE = 1.0
GUTTER = 0.1
VIGNELLI_RED = (0.85, 0.1, 0.05, 1.0)
BONE_WHITE = (0.95, 0.95, 0.9, 1.0)
FIB = [1, 2, 3, 5, 8, 13]

def create_mat(name, color, roughness):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    return mat

# Differentiated materiality per critic's mandate
red_m = create_mat("VignelliRed", VIGNELLI_RED, 0.05)      # Sharp, glossy, commanding
white_m = create_mat("ArchitecturalWhite", BONE_WHITE, 0.4) # Matte, soft, textural

# Generate Grid with Harmonic Logic
for c in range(COLS):
    for r in range(ROWS):
        # The Logic: Rhythmic subdivision (3 and 4)
        is_harmonic_x = (c % 3 == 0)
        is_harmonic_y = (r % 4 == 0)
        is_red = is_harmonic_x and is_harmonic_y # Strict intersection
        
        x = c * (MODULE_SIZE + GUTTER)
        y = r * (MODULE_SIZE + GUTTER)
        
        # Fibonacci-based height progression: (c+r) index into sequence
        # Scaled to keep architectural proportions
        fib_index = (c + r) % len(FIB)
        height = FIB[fib_index] * 0.25 if (is_harmonic_x or is_harmonic_y) else 0.1
            
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height/2))
        block = bpy.context.active_object
        block.scale = (MODULE_SIZE, MODULE_SIZE, height)
        
        # Color assignment: Pure system, zero randomness
        block.data.materials.append(red_m if is_red else white_m)

# Ground
bpy.ops.mesh.primitive_plane_add(size=100, location=(0,0,0))
ground = bpy.context.active_object
ground.data.materials.append(white_m)

# Lighting: Intentional hierarchy
bpy.ops.object.light_add(type='SUN', location=(15, -10, 25))
sun = bpy.context.active_object
sun.data.energy = 6
sun.rotation_euler = (math.radians(60), 0, math.radians(35)) # Deeper shadows

# High-quality perspective
cam_pos = (COLS * 2.5, -COLS * 1.5, COLS * 2)
bpy.ops.object.camera_add(location=cam_pos)
cam = bpy.context.active_object
cam.data.type = 'PERSP' # Reverted to Perspective for depth
# Look at center
direction = Vector((COLS/2, ROWS/2, 0)) - Vector(cam_pos)
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# Render Settings (Elevated for v2)
scene = bpy.context.scene
scene.camera = cam
scene.render.filepath = "/data/.openclaw/workspace/art/renders/2026-02-15/vignelli_visual_score_v2.png"
scene.render.resolution_x = 1600
scene.render.resolution_y = 1600
scene.render.engine = 'CYCLES'
scene.cycles.samples = 256 # Double the quality
bpy.ops.render.render(write_still=True)
