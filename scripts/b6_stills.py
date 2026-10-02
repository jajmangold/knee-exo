# -*- coding: utf-8 -*-
"""Render the presentation stills. Runs inside Blender, after b1_scene and b2_look.

    KX_SRC=C:/Users/Josh/KneeExo_render/p00 KX_OUT=C:/Users/Josh/KneeExo_render/out_p00 \
        blender -b -P scripts/b1_scene.py -P scripts/b2_look.py -P scripts/b6_stills.py

WHY THIS FILE EXISTS, AND WHY IT HAS SIX SHOTS AND NOT EIGHT. renders/extended_0deg and
renders/flexed_40deg each hold eight stills -- 01_hero_clad through 08_shank_clad -- and no script
in this repository produced them. They were framed by hand in a Blender session, which means the
eight camera angles exist nowhere: not in a file, not in a comment, not in the images themselves.
When the drive cover was reworked and the part numbers were engraved, those images could not be
regenerated, and they are now the oldest artefacts in the project.

The only camera direction the repository does record is (0.62, -0.76, 0.20) in b3_frame.py, with
near-identical values in b5_reframe.py and anim_common.py. So that is what this renders: the hero
direction, clad and open, at whichever pose KX_SRC points at -- framed on the whole device, on the
knee, and on the drive end. Six images per pose, each of them reproducible.

Framing a subset is not inventing a viewpoint, which is why the knee and drive shots are allowed:
same direction, different crop. The drive earns its own pair because it is the part that changed
most -- the image the README carried showed the 190 mm box cap that 399 replaced with a loft.

Guessing the other seven angles would have been easy and wrong -- a render is a claim about what
the thing looks like, and eight invented viewpoints replacing eight stale ones is not an
improvement, it is the same problem with a newer timestamp. If more angles are wanted, add them
here with a reason, and they will survive the next rework.

The technical views -- coronal, sagittal, the differential pair, the knee and drive details -- are
FreeCAD viewport captures instead (223_cad_shots.py -> renders/cad). Those are the model itself
rather than a lit interpretation of it, which is what you want when reading a shape off an image.
"""
import json
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
# KX_SHOTS=05,06 renders only those, so adding a shot does not mean re-rendering the set. At 512
# samples on a CPU each one is about twelve minutes, which is enough for that to matter.
ONLY = [x.strip() for x in os.environ.get("KX_SHOTS", "").split(",") if x.strip()]

# The cladding. Hiding these is what "open" means: the five shells that cover the drive and the
# limb-facing structure. The fairing MOUNTS and the two interface bosses stay -- they are structure
# that happens to be tagged FAIR by the exporter, and hiding them leaves the canopy floating.
SHELLS = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle",
          "P24_FairingShank"]
HERO = (0.62, -0.76, 0.20)      # the one direction this repository actually records

# Framing a subset is not the same as inventing a viewpoint: every shot below looks along the one
# direction this repository records, and differs only in what it is framed on and whether the
# cladding is shown. The README has a slot for a drive-end image (it is the part that changed most,
# and the old one shows the 190 mm box P22 that 399 replaced with a loft), so the drive gets the
# same treatment the knee does.
KNEE = ["P1_KneeYoke", "P2a_KneeHingePlate", "P20_KneeShroud", "P6_ShankSocket"]
DRIVE = ["P22_DriveCap", "P25_MotorNacelle", "A7_DriveBox", "A3_Motor_6374", "A6_Idler29T",
         "P30_InterfaceProx"]
SHOTS = [
    ("01_hero_clad", HERO, True, (1500, 2000), 1.22, None),
    ("02_hero_open", HERO, False, (1500, 2000), 1.22, None),
    # Same direction, tighter, landscape: the knee is where the mechanism is legible.
    ("03_knee_clad", HERO, True, (2000, 1500), 1.00, KNEE),
    ("04_knee_open", HERO, False, (2000, 1500), 1.00, KNEE),
    ("05_drive_clad", HERO, True, (2000, 1500), 1.05, DRIVE),
    ("06_drive_open", HERO, False, (2000, 1500), 1.05, DRIVE),
]


# WHAT GEOMETRY THIS IS A PICTURE OF. Recorded, because an image file that exists is not an image
# file that is current: the README carried six renders of a boxy P22 and non-conical cuffs for
# weeks, and nothing could have caught it. The fingerprint comes from the export (221 writes it
# beside the STLs), so it describes the geometry actually rendered rather than whatever the model
# happens to be now. 902_doc_audit.py compares it against the live model and fails if they differ.
def record(images):
    fpf = os.path.join(SRC, "fingerprint.txt")
    fp = open(fpf).read().strip() if os.path.exists(fpf) else "unknown"
    path = r"C:/Users/Josh/knee-exo/renders/manifest.json"
    man = {}
    if os.path.exists(path):
        try:
            man = json.load(open(path))
        except Exception:
            man = {}
    for rel in images:
        man[rel] = {"geometry": fp, "made": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "by": os.path.basename(__file__), "src": os.path.basename(SRC)}
    json.dump(man, open(path, "w"), indent=1, sort_keys=True)
    print("%s: recorded %d images against geometry %s" % (os.path.basename(__file__), len(images), fp))


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
for name, direction, clad, (rx, ry), margin, focus in SHOTS:
    if ONLY and not any(name.startswith(x) for x in ONLY):
        continue
    show(SHELLS, clad)
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    frame_cam(direction, margin, focus)
    sc.render.filepath = os.path.join(OUT, name + ".png")
    t = time.time()
    bpy.ops.render.render(write_still=True)
    print("STILLS: %-16s %4d x %-4d %s  %.1f s"
          % (name, rx, ry, "clad" if clad else "open", time.time() - t))
show(SHELLS, True)
print("STILLS: %d images in %.1f min" % (len(SHOTS), (time.time() - t0) / 60.0))
POSE = "flexed_40deg" if "p40" in SRC else "extended_0deg"
record(["renders/%s/%s.png" % (POSE, n) for n, _, _, _, _, _ in SHOTS
        if not ONLY or any(n.startswith(x) for x in ONLY)])
