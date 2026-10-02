# -*- coding: utf-8 -*-
"""Render the presentation stills. Runs inside Blender, after b1_scene and b2_look.

    KX_SRC=C:/Users/Josh/KneeExo_render/p00 KX_OUT=C:/Users/Josh/KneeExo_render/out_p00 \
        blender -b -P scripts/b1_scene.py -P scripts/b2_look.py -P scripts/b6_stills.py

WHY THIS FILE EXISTS, AND WHY IT HAS FOUR SHOTS AND NOT EIGHT. renders/extended_0deg and
renders/flexed_40deg each hold eight stills -- 01_hero_clad through 08_shank_clad -- and no script
in this repository produced them. They were framed by hand in a Blender session, which means the
eight camera angles exist nowhere: not in a file, not in a comment, not in the images themselves.
When the drive cover was reworked and the part numbers were engraved, those images could not be
regenerated, and they are now the oldest artefacts in the project.

The only camera direction the repository does record is (0.62, -0.76, 0.20) in b3_frame.py, with
near-identical values in b5_reframe.py and anim_common.py. So that is what this renders: the hero
direction, clad and open, at whichever pose KX_SRC points at. Four images per pose, each of them
reproducible.

Guessing the other seven angles would have been easy and wrong -- a render is a claim about what
the thing looks like, and eight invented viewpoints replacing eight stale ones is not an
improvement, it is the same problem with a newer timestamp. If more angles are wanted, add them
here with a reason, and they will survive the next rework.

The technical views -- coronal, sagittal, the differential pair, the knee and drive details -- are
FreeCAD viewport captures instead (223_cad_shots.py -> renders/cad). Those are the model itself
rather than a lit interpretation of it, which is what you want when reading a shape off an image.
"""
import math
import os
import time

import bpy
import mathutils as mu

SRC = os.environ.get("KX_SRC", r"C:/Users/Josh/KneeExo_render/p00")
OUT = os.environ.get("KX_OUT", r"C:/Users/Josh/KneeExo_render/out")
SAMPLES = int(os.environ.get("KX_SAMPLES", "512"))
SCALE = int(os.environ.get("KX_SCALE", "100"))       # 25 for a quick look
DEVICE = os.environ.get("KX_DEVICE", "CPU")          # this machine has no NVIDIA card

# The cladding. Hiding these is what "open" means: the five shells that cover the drive and the
# limb-facing structure. The fairing MOUNTS and the two interface bosses stay -- they are structure
# that happens to be tagged FAIR by the exporter, and hiding them leaves the canopy floating.
SHELLS = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle",
          "P24_FairingShank"]
HERO = (0.62, -0.76, 0.20)      # the one direction this repository actually records

SHOTS = [
    ("01_hero_clad", HERO, True, (1500, 2000), 1.22),
    ("02_hero_open", HERO, False, (1500, 2000), 1.22),
    # Same direction, tighter, landscape: the knee is where the mechanism is legible.
    ("03_knee_clad", HERO, True, (2000, 1500), 1.00),
    ("04_knee_open", HERO, False, (2000, 1500), 1.00),
]
KNEE = ["P1_KneeYoke", "P2a_KneeHingePlate", "P20_KneeShroud", "P6_ShankSocket"]


def bbox(names=None):
    pts = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == 'Ground' or o.hide_render:
            continue
        if names and o.name not in names:
            continue
        pts += [o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn = mu.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mu.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx, (mn + mx) / 2


def frame_cam(dir_vec, margin=1.22, names=None):
    """Same arithmetic as b3_frame, kept here so a still does not depend on b3 having run (b3
    ends by firing a test render, which is not something a batch wants)."""
    mn, mx, ctr = bbox(names)
    cam = bpy.data.objects['Cam']
    d = cam.data
    radius = max((mx - mn).x, (mx - mn).y, (mx - mn).z) / 2 * margin
    vfov = 2 * math.atan(d.sensor_height / (2 * d.lens))
    dist = radius / math.tan(vfov / 2)
    v = mu.Vector(dir_vec).normalized()
    for n in ('CamTarget', 'CamPivot'):
        if n in bpy.data.objects:
            bpy.data.objects[n].location = ctr
    cam.location = v * dist
    return ctr, dist, radius


def show(names, on):
    for n in names:
        o = bpy.data.objects.get(n)
        if o is not None:
            o.hide_render = not on
            o.hide_viewport = not on


sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = DEVICE
sc.cycles.samples = SAMPLES
sc.render.resolution_percentage = SCALE
sc.render.image_settings.file_format = 'PNG'
if not os.path.isdir(OUT):
    os.makedirs(OUT)

# ground under the lowest point, and the reference limb almost gone: it is context, and at any
# real opacity it hides the device it is there to give scale to
mn, mx, _ = bbox()
if 'Ground' in bpy.data.objects:
    bpy.data.objects['Ground'].location = (0, 0, mn.z - 0.015)
if 'Limb' in bpy.data.materials:
    bpy.data.materials['Limb'].node_tree.nodes['Principled BSDF'] \
        .inputs['Alpha'].default_value = 0.06

print("STILLS: %s -> %s, %d samples at %d%%, %s"
      % (os.path.basename(SRC), OUT, SAMPLES, SCALE, DEVICE))
print("STILLS: assembly %.0f x %.0f x %.0f mm"
      % ((mx.x - mn.x) * 1000, (mx.y - mn.y) * 1000, (mx.z - mn.z) * 1000))
t0 = time.time()
for name, direction, clad, (rx, ry), margin in SHOTS:
    show(SHELLS, clad)
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    frame_cam(direction, margin, KNEE if "knee" in name else None)
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("STILLS: %-16s %4d x %-4d %s  %.1f s"
          % (name, rx, ry, "clad" if clad else "open", time.time() - t))
show(SHELLS, True)
print("STILLS: %d images in %.1f min" % (len(SHOTS), (time.time() - t0) / 60.0))
