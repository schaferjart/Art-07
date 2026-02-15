#!/usr/bin/env python3
"""
Socrates' First 3D Art Piece
A dreamy cluster of floating orbs with dramatic lighting
"""
import bpy
import random
import math

# Clear the scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Remove default light and camera
for obj in bpy.data.objects:
    if obj.type in ('LIGHT', 'CAMERA'):
        bpy.data.objects.remove(obj, do_unlink=True)

# Create a metaball cluster (organic blobby shapes)
bpy.ops.object.metaball_add(type='BALL', radius=1.0, location=(0, 0, 0))
meta_obj = bpy.context.active_object
meta_obj.name = "BlobCluster"

meta_data = meta_obj.data
meta_data.resolution = 0.3  # Lower = smoother

# Add multiple metaball elements
positions = [
    (0, 0, 0, 1.5),
    (2, 1, 0.5, 0.8),
    (-1.5, 0.8, -0.3, 0.9),
    (0.5, -1.2, 0.8, 0.6),
    (-0.8, -0.5, 1.2, 0.7),
    (1.2, 0.3, -0.9, 0.5),
]

for x, y, z, radius in positions:
    elem = meta_data.elements.new()
    elem.co = (x, y, z)
    elem.radius = radius

# Give it a nice material
mat = bpy.data.materials.new(name="BlobMaterial")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links

# Clear default nodes
for node in nodes:
    nodes.remove(node)

# Add principled BSDF (Blender 4.x API)
bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
bsdf.location = (0, 0)
bsdf.inputs['Base Color'].default_value = (0.3, 0.6, 0.9, 1.0)  # Blue-ish
bsdf.inputs['Subsurface Weight'].default_value = 0.3
bsdf.inputs['Subsurface Radius'].default_value = (0.5, 0.2, 0.8)  # Purple subsurface
bsdf.inputs['Roughness'].default_value = 0.2
bsdf.inputs['IOR'].default_value = 1.45

# Output node
output = nodes.new(type='ShaderNodeOutputMaterial')
output.location = (300, 0)
links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

meta_obj.data.materials.append(mat)

# Add dramatic lighting
# Key light (warm)
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
key_light = bpy.context.active_object
key_light.data.energy = 5.0
key_light.data.color = (1.0, 0.95, 0.8)
key_light.rotation_euler = (math.radians(45), 0, math.radians(30))

# Fill light (cool)
bpy.ops.object.light_add(type='AREA', location=(-5, -3, 5))
fill_light = bpy.context.active_object
fill_light.data.energy = 2.0
fill_light.data.color = (0.7, 0.8, 1.0)
fill_light.data.size = 5.0

# Rim light (dramatic purple)
bpy.ops.object.light_add(type='SPOT', location=(0, -8, 2))
rim_light = bpy.context.active_object
rim_light.data.energy = 10.0
rim_light.data.color = (0.8, 0.3, 0.9)
rim_light.data.spot_size = math.radians(30)
rim_light.rotation_euler = (math.radians(80), 0, math.radians(180))

# Add ground plane for shadows
bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -2))
ground = bpy.context.active_object
ground.name = "Ground"

# Ground material (matte dark)
ground_mat = bpy.data.materials.new(name="GroundMaterial")
ground_mat.use_nodes = True
ground_nodes = ground_mat.node_tree.nodes
ground_bsdf = ground_nodes.get("Principled BSDF")
if ground_bsdf:
    ground_bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.08, 1.0)
    ground_bsdf.inputs['Roughness'].default_value = 0.9
ground.data.materials.append(ground_mat)

# Position camera
bpy.ops.object.camera_add(location=(6, -6, 4))
camera = bpy.context.active_object
camera.rotation_euler = (math.radians(60), 0, math.radians(45))

# Point camera at the center
bpy.ops.object.select_all(action='DESELECT')
camera.select_set(True)
bpy.context.view_layer.objects.active = camera
bpy.ops.object.constraint_add(type='TRACK_TO')
camera.constraints['Track To'].target = meta_obj

# Set render settings
scene = bpy.context.scene
scene.camera = camera
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 64  # Low for faster render
scene.render.resolution_x = 800
scene.render.resolution_y = 600
scene.render.resolution_percentage = 100

# Set output
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '/data/.openclaw/workspace/art/socrates_first_render.png'

print("🎨 Rendering Socrates' first masterpiece...")
print(f"   Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
print(f"   Samples: {scene.cycles.samples}")
print(f"   Engine: {scene.render.engine}")

# Render!
bpy.ops.render.render(write_still=True)

print(f"\n✅ Render complete!")
print(f"   Saved to: {scene.render.filepath}")
