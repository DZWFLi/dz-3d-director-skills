import argparse
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd):
    subprocess.run(cmd, check=True)


def find_blender(explicit):
    if explicit:
        candidate = Path(explicit)
        if candidate.is_file():
            return str(candidate.resolve())
        raise SystemExit("The --blender executable does not exist.")
    found = shutil.which("blender")
    if found:
        return found
    raise SystemExit("Blender executable not found. Pass --blender.")


def choose_asset(asset):
    path = Path(asset)
    if path.is_file():
        return path
    files = list(path.rglob("*"))
    for suffix in (".obj", ".fbx", ".glb", ".gltf"):
        matches = [p for p in files if p.suffix.lower() == suffix]
        if matches:
            return sorted(matches, key=lambda p: p.stat().st_size, reverse=True)[0]
    raise SystemExit(f"No OBJ/FBX/GLB/GLTF found in {path}")


def write_blender_script(script_path, asset_path, out_dir, lens, frames, render_video, width, height):
    code = f'''
import math
from pathlib import Path
import bpy
from mathutils import Matrix, Vector

ASSET = Path({str(asset_path)!r})
OUT = Path({str(out_dir)!r})
LENS = {lens}
FRAMES = {frames}
RENDER_VIDEO = {str(render_video)}
OUT.mkdir(parents=True, exist_ok=True)

def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

def import_asset():
    before = set(bpy.data.objects)
    ext = ASSET.suffix.lower()
    if ext == ".obj":
        bpy.ops.wm.obj_import(filepath=str(ASSET))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(ASSET))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(ASSET))
    else:
        raise RuntimeError("Unsupported asset")
    imported = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in imported if o.type == "MESH"]
    if not meshes:
        raise RuntimeError("No mesh imported")
    return imported, meshes

def bbox(meshes):
    pts = []
    for obj in meshes:
        pts.extend(obj.matrix_world @ Vector(c) for c in obj.bound_box)
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx

def normalize(imported, meshes):
    for obj in meshes:
        world = obj.matrix_world.copy()
        if obj.data.users > 1:
            obj.data = obj.data.copy()
        obj.data.transform(world)
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        obj.location = (0, 0, 0)
        obj.rotation_euler = (0, 0, 0)
        obj.scale = (1, 1, 1)
        obj.data.update()
    bpy.context.view_layer.update()
    mn, mx = bbox(meshes)
    center = (mn + mx) * 0.5
    size = mx - mn
    longest = max(size.x, size.y, size.z)
    if longest <= 0:
        raise RuntimeError("Imported mesh has no measurable size")
    scale = 5.2 / longest
    for obj in meshes:
        obj.data.transform(Matrix.Translation(-center))
        obj.data.transform(Matrix.Scale(scale, 4))
        obj.data.update()
    bpy.context.view_layer.update()
    mn, mx = bbox(meshes)
    for obj in meshes:
        obj.data.transform(Matrix.Translation((0, 0, -mn.z)))
        obj.hide_set(False)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.data.update()
    root = bpy.data.objects.new("Subject_Root", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in meshes:
        obj.parent = root
    bpy.context.view_layer.update()
    return bbox(meshes)

def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def setup_scene(mn, mx):
    size = mx - mn
    center = (mn + mx) * 0.5
    floor_size = max(12, max(size.x, size.y) * 3)
    bpy.ops.mesh.primitive_plane_add(size=floor_size, location=(0, 0, 0))
    floor = bpy.context.object
    floor.name = "Studio_Floor"
    mat = bpy.data.materials.new("Studio_Floor_Mat")
    mat.diffuse_color = (0.7, 0.7, 0.66, 1)
    floor.data.materials.append(mat)
    for name, loc, energy, area in [
        ("Key_Area", (-4.5, -5.5, 5), 1800, 5.5),
        ("Rim_Area", (4.5, 3, 3), 550, 3),
    ]:
        bpy.ops.object.light_add(type="AREA", location=loc)
        l = bpy.context.object
        l.name = name
        l.data.energy = energy
        l.data.size = area
    bpy.context.scene.world.color = (0.08, 0.085, 0.09)
    return center, size

def animate_camera(center, size):
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = FRAMES
    scene.render.fps = 24
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "CAM_push_orbit_handheld"
    cam.data.lens = LENS
    scene.camera = cam
    target = Vector((center.x, center.y, max(0.8, size.z * 0.48)))
    r0 = max(size.x, size.y) * 0.95 + 2.6
    r1 = max(size.x, size.y) * 0.65 + 1.8
    a0 = math.radians(-18)
    a1 = math.radians(28)
    for frame in range(1, FRAMES + 1):
        t = (frame - 1) / max(1, FRAMES - 1)
        s = t * t * (3 - 2 * t)
        r = r0 + (r1 - r0) * s
        a = a0 + (a1 - a0) * s
        cam.location = (
            center.x + math.sin(a) * r + math.sin(frame * 0.33) * 0.018,
            center.y - math.cos(a) * r + math.cos(frame * 0.29) * 0.014,
            target.z + math.sin(frame * 0.21) * 0.010,
        )
        look_at(cam, target)
        cam.keyframe_insert("location", frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)
    return cam

def render_outputs():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = {width}
    scene.render.resolution_y = {height}
    scene.view_settings.view_transform = "Standard"
    for frame, name in [(1, "preview_001.png"), ((FRAMES + 1) // 2, "preview_mid.png")]:
        scene.frame_set(frame)
        scene.render.filepath = str(OUT / name)
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "scene.blend"))
    bpy.ops.export_scene.gltf(filepath=str(OUT / "scene.glb"), export_format="GLB")
    if RENDER_VIDEO:
        frames_dir = OUT / "video_frames"
        frames_dir.mkdir(exist_ok=True)
        scene.render.filepath = str(frames_dir / "frame_")
        scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)

clear()
imported, meshes = import_asset()
mn, mx = normalize(imported, meshes)
center, size = setup_scene(mn, mx)
animate_camera(center, size)
render_outputs()
print("DONE", OUT)
'''
    script_path.write_text(code, encoding="utf-8")


def encode_video(out_dir):
    frames_dir = Path(out_dir) / "video_frames"
    if not frames_dir.exists():
        return
    try:
        import imageio_ffmpeg
    except Exception:
        raise SystemExit("MP4 requested: install imageio-ffmpeg. PNG frames are available.")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    run([
        ffmpeg, "-y", "-framerate", "24",
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
        str(Path(out_dir) / "camera_move.mp4"),
    ])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--blender")
    ap.add_argument("--lens", type=float, default=30)
    ap.add_argument("--frames", type=int, default=120)
    ap.add_argument("--render-video", action="store_true")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    args = ap.parse_args()

    if args.frames < 2 or args.lens <= 0 or min(args.width, args.height) <= 0:
        ap.error("frames must be >= 2; lens and dimensions must be positive")
    if args.render_video and (args.width % 2 or args.height % 2):
        ap.error("MP4 width and height must be even")
    if args.render_video:
        try:
            import imageio_ffmpeg
        except ImportError:
            ap.error("--render-video needs imageio-ffmpeg")
    blender = find_blender(args.blender)
    asset = choose_asset(args.asset)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    script = out / "_generate_camera_move_blender.py"
    write_blender_script(script, asset.resolve(), out.resolve(), args.lens, args.frames, args.render_video, args.width, args.height)
    run([blender, "--background", "--factory-startup", "--python-exit-code", "1", "--python", str(script.resolve())])
    if args.render_video:
        encode_video(out)
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
