#!/usr/bin/env python3
"""
Vignelli Visual Score V4: Emergence
Response to Critic Session 03: "Computational paradox - color as data vs color as deception"

Key Evolution:
- Grid as foundation (Vignelli discipline) BUT with organic emergence
- Metaballs breaking through strict grid - system vs chaos
- Color temperature now indicates "life" - warmer = more emergent/organic
- Introduces temporal concept: what escapes the system?

Philosophy: The tension between design systems and living chaos
"""
import bpy
import math
import random
from mathutils import Vector

# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Grid parameters - tighter, more disciplined base
COLS = 16
ROWS = 16
MODULE_SIZE = 0.6
GUTTER = 0.15
FIB = [1, 2, 3, 5, 8, 13, 21]

# Seed for reproducible chaos
random.seed(42)

def color_from_state(state, intensity=1.0):
    """
    state: 0.0 (system/total order) → 1.0 (emergence/chaos)
    Color shifts from cool gray-blue (system) to warm organic amber (life)
    """
    system_color = Vector((0.25, 0.28, 0.35))  # Cool gray-blue
    emergent_color = Vector((0.95, 0.55, 0.15))  # Warm amber-orange
    
    color = system_color.lerp(emergent_color, state * intensity)
    return (*color, 1.0)

def create_material(name, color, roughness, metallic=0.0, emission=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Emission Strength'].default_value = emission
    if emission > 0:
        bsdf.inputs['Emission Color'].default_value = color
    
    return mat

# Calculate emergence points (where chaos breaks through)
emergence_centers = [
    Vector((8, 6, 0)),
    Vector((4, 12, 0)),
    Vector((12, 10, 0)),
]

def calculate_emergence(x, y):
    """Calculate how much 'life' emerges at this grid point"""
    pos = Vector((x, y, 0))
    max_emergence = 0.0
    
    for center in emergence_centers:
        dist = (pos - center).length
        # Gaussian falloff of emergence influence
        influence = math.exp(-(dist ** 2) / 8.0)
        max_emergence = max(max_emergence, influence)
    
    # Add subtle noise
    noise = (math.sin(x * 0.7) + math.cos(y * 0.6)) * 0.05
    return min(1.0, max(0.0, max_emergence + noise))

# Generate Grid with emergence
objects_for_metaball = []
center = Vector((COLS * (MODULE_SIZE + GUTTER) / 2, ROWS * (MODULE_SIZE + GUTTER) / 2))

for c in range(COLS):
    for r in range(ROWS):
        x = c * (MODULE_SIZE + GUTTER)
        y = r * (MODULE_SIZE + GUTTER)
        
        # Calculate emergence at this point
        emergence = calculate_emergence(x, y)
        
        # Grid "importance" based on position
        pos = Vector((x, y))
        dist_from_center = (pos - center).length
        is_grid_line_x = (c % 4 == 0)
        is_grid_line_y = (r % 4 == 0)
        
        # Height: emergence breaks the grid vertically
        if emergence > 0.6:
            # Chaotic height for emergent zones
            height = 2.0 + emergence * 3.0 + random.uniform(0, 1.0)
        elif is_grid_line_x and is_grid_line_y:
            # Structural nodes
            fib_index = (c + r) % len(FIB)
            height = FIB[fib_index] * 0.3
        else:
            # Background grid
            height = 0.2 + (emergence * 0.5)
        
        # Color based on emergence state
        color = color_from_state(emergence, intensity=1.2)
        
        # Material properties: emergent zones are glossier, more alive
        roughness = 0.8 - (emergence * 0.6)  # 0.8 → 0.2
        metallic = emergence * 0.3
        emission = emergence * 0.4  # Slight glow for emergent areas
        
        # Create block
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, height / 2))
        block = bpy.context.active_object
        block.scale = (MODULE_SIZE, MODULE_SIZE, height)
        
        mat = create_material(f"Block_{c}_{r}", color, roughness, metallic, emission)
        block.data.materials.append(mat)
        
        # Track positions where emergence is strong for metaball creation
        if emergence > 0.7:
            objects_for_metaball.append((x, y, height + 0.5, emergence))

# Create organic metaball emergence (the chaos breaking through)
if objects_for_metaball:
    bpy.ops.object.metaball_add(type='BALL', radius=0.5, location=(0, 0, 0))
    meta_obj = bpy.context.active_object
    meta_obj.name = "Emergence_Blob"
    
    meta_data = meta_obj.data
    meta_data.resolution = 0.25
    meta_data.render_resolution = 0.1
    
    # Material for metaball - warm, glowing, alive
    meta_mat = bpy.data.materials.new(name="Emergence_Material")
    meta_mat.use_nodes = True
    nodes = meta_mat.node_tree.nodes
    links = meta_mat.node_tree.links
    
    for node in nodes:
        nodes.remove(node)
    
    # Warm, subsurface, organic
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.98, 0.45, 0.12, 1.0)
    bsdf.inputs['Subsurface Weight'].default_value = 0.6
    bsdf.inputs['Subsurface Radius'].default_value = (1.0, 0.3, 0.1)
    bsdf.inputs['Roughness'].default_value = 0.15
    bsdf.inputs['Transmission Weight'].default_value = 0.2
    bsdf.inputs['Emission Strength'].default_value = 0.3
    bsdf.inputs['Emission Color'].default_value = (1.0, 0.6, 0.2, 1.0)
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (300, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    meta_obj.data.materials.append(meta_mat)
    
    # Add metaball elements at emergence points
    for x, y, z, strength in objects_for_metaball[:12]:  # Limit to strongest
        elem = meta_data.elements.new()
        elem.co = (x, y, z + random.uniform(0, 0.5))
        elem.radius = 0.4 + (strength * 0.6)
        elem.stiffness = 0.5

# Ground - neutral system gray
bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, 0))
ground = bpy.context.active_object
ground_mat = create_material("System_Ground", (0.12, 0.12, 0.14, 1.0), 0.9)
ground.data.materials.append(ground_mat)

# Lighting: Dramatic chiaroscuro to emphasize emergence
# Key light - warm, focused on center
bpy.ops.object.light_add(type='SUN', location=(10, -8, 20))
key = bpy.context.active_object
key.data.energy = 6.0
key.data.color = (1.0, 0.9, 0.75)
key.rotation_euler = (math.radians(55), 0, math.radians(40))

# Rim light - cool, from behind to silhouette emergence
bpy.ops.object.light_add(type='AREA', location=(-10, 15, 8))
rim = bpy.context.active_object
rim.data.energy = 4.0
rim.data.color = (0.6, 0.75, 0.9)
rim.data.size = 6.0
rim.rotation_euler = (math.radians(70), 0, math.radians(-30))

# Fill - very subtle warm
bpy.ops.object.light_add(type='AREA', location=(8, 8, 12))
fill = bpy.context.active_object
fill.data.energy = 1.5
fill.data.color = (0.9, 0.85, 0.8)
fill.data.size = 10.0

# Camera - dramatic angle emphasizing depth
angle = 35
cam_x = math.cos(math.radians(angle)) * 22
cam_y = -math.sin(math.radians(angle)) * 22
bpy.ops.object.camera_add(location=(cam_x, cam_y, 14))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(65), 0, math.radians(angle))

# Render
scene = bpy.context.scene
scene.camera = cam
scene.render.filepath = "/data/.openclaw/workspace/art/renders/2026-02-17/vignelli_visual_score_v4.png"
scene.render.resolution_x = 1800
scene.render.resolution_y = 1800
scene.render.engine = 'CYCLES'
scene.cycles.samples = 48
scene.cycles.device = 'CPU'

print("🎨 Rendering Vignelli V4: Emergence...")
print("   Theme: System vs Chaos - what escapes the grid?")
print(f"   Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"   Emergence points: {len(objects_for_metaball)}")

bpy.ops.render.render(write_still=True)

print(f"\n✅ S04 Render complete!")
print(f"   Saved to: {scene.render.filepath}")
print(f"   Next: Critique session to verify the paradox is resolved...")
