import json
import bpy
from mathutils import Vector

scene = bpy.context.scene
meshes = [obj for obj in scene.objects if obj.type == 'MESH']
points = [obj.matrix_world @ Vector(corner) for obj in meshes for corner in obj.bound_box]
report = {
    'mesh_count': len(meshes),
    'hidden_in_render': [obj.name for obj in meshes if obj.hide_render],
    'frame_range': [scene.frame_start, scene.frame_end],
    'fps': scene.render.fps,
    'resolution': [scene.render.resolution_x, scene.render.resolution_y],
}
if points:
    report['world_bbox'] = [[min(p[axis] for p in points) for axis in range(3)],
                            [max(p[axis] for p in points) for axis in range(3)]]
if scene.camera:
    report['camera'] = {'name': scene.camera.name,
                        'world_position': list(scene.camera.matrix_world.translation),
                        'lens_mm': scene.camera.data.lens}
print(json.dumps(report, indent=2))
