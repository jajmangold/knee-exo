# -*- coding: utf-8 -*-
"""Animate the current mechanism and render the GIF frames. Runs after b1_scene and b2_look.

    KX_SRC=C:/Users/Josh/KneeExo_render/p00 KX_OUT=C:/Users/Josh/KneeExo_render/anim \
        blender -b -P scripts/b1_scene.py -P scripts/b2_look.py -P scripts/b7_anim.py

This replaces b4_anim.py, which animates an architecture that no longer exists. b4 reads
KneeExo_anim/kinematics.json -- dated September, carrying rod_len, Dx/Dy and phi -- and keyframes a
rod end, a clevis and a slider-crank through them. The rod linkage was replaced by a belt over a
capstan, and b4's part lists still name P2b_RodClevisBlock and P4_Rod_8mm while omitting every piece
of cladding added since: the fairings, the two-part drive wall, the three mounts and both interface
bosses would have stood still while the leg bent.

The motion it replaces all that with is two lines, because that is what the current mechanism is:

    the shank side rotates by theta about the knee axis, which is the model's Z through the origin
    the gantry slides by (A0 - R*theta) - A0 along the limb axis, R being the 29T capstan radius

Those are the same two expressions in 406_coverage.py, 601_verify_fast.py and 221_render_export.py.
The part lists are 601's, which are the ones the interference sweep uses -- so if a part is added to
the sweep it is animated too, rather than a sixth hand-maintained pose list drifting on its own.
(The README's "a part can be in a check's list and never be posed" is exactly this failure: five
pose lists, each maintained separately from the part list beside it.)

Object-local transforms are model coordinates here: b1_scene parents every mesh to RIG with an
identity parent inverse, and the STL import preserves absolute coordinates, so an object's origin is
the model origin -- which is the knee axis. Rotating an object about its own Z is therefore rotating
it about the knee axis, with no axis bookkeeping at all.
"""
import json
import math
import os
import time

import bpy

SRC = os.environ.get("KX_SRC", r"C:/Users/Josh/KneeExo_render/p00")
OUT = os.environ.get("KX_OUT", r"C:/Users/Josh/KneeExo_render/anim")
SAMPLES = int(os.environ.get("KX_SAMPLES", "96"))
NFRAMES = int(os.environ.get("KX_FRAMES", "32"))
DEVICE = os.environ.get("KX_DEVICE", "CPU")

# 601_verify_fast.py's lists, verbatim: what moves with the shank, and what rides the screw.
# 601's list minus REF_Shank: 221_render_export.py has no material tag for the reference limbs, so
# they are not in a render export at all. Listed here anyway would print a "not in the scene"
# warning on every run, which trains people to ignore the warning that matters.
SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "P31_InterfaceDist", "HW_JointBolts"]
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
SHELLS = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle",
          "P24_FairingShank"]
KNEE = ["P1_KneeYoke", "P2a_KneeHingePlate", "P20_KneeShroud", "P6_ShankSocket"]

R_CAP = 29 * 8.0 / (2 * math.pi)        # 29T HTD-8M capstan pitch radius, mm
A0 = 161.0                              # gantry clamp Y at theta = 0
HERO = (0.62, -0.78, 0.13)              # anim_common.py's direction, the one that is recorded

# theta = 52 - 52 cos(2 pi i / N): starts and ends at 0, peaks at 104, and loops with no
# duplicated end frame. Same law the published GIFs used.
THETA = [52.0 - 52.0 * math.cos(2.0 * math.pi * i / NFRAMES) for i in range(NFRAMES)]

SHOTS = [("hero_clad", True, (560, 747), 1.22, None),
         ("hero_open", False, (560, 747), 1.22, None),
         ("knee_open", False, (560, 420), 1.00, KNEE)]


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


def keyframe():
    """One keyframe per rendered frame, LINEAR: the motion is the mechanism's, and Blender's
    default Bezier easing would make the knee accelerate out of each keyframe -- a smooth lie
    about a constant-ratio transmission.

    Set through preferences rather than by walking the f-curves afterwards: Blender 5.x moved
    them into slotted Actions, so action.fcurves raises AttributeError, and the version-proof
    way to get linear keys is to insert them linear in the first place.
    """
    try:
        bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
    except Exception:
        pass
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, NFRAMES
    for i, th in enumerate(THETA):
        f = i + 1
        dy = (A0 - R_CAP * math.radians(th)) - A0        # mm
        for n in SHANK:
            o = bpy.data.objects.get(n)
            if o is None:
                continue
            o.rotation_euler = (0.0, 0.0, math.radians(th))
            o.keyframe_insert("rotation_euler", frame=f)
        for n in GANTRY:
            o = bpy.data.objects.get(n)
            if o is None:
                continue
            o.location = (0.0, dy / 1000.0, 0.0)          # metres
            o.keyframe_insert("location", frame=f)


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
sc.render.resolution_percentage = 100
sc.render.image_settings.file_format = 'PNG'

missing = [n for n in SHANK + GANTRY if bpy.data.objects.get(n) is None]
if missing:
    print("ANIM: NOT IN THE SCENE, so not animated: %s" % ", ".join(missing))
keyframe()
print("ANIM: %d frames, theta %.0f..%.0f deg, %d samples, %s"
      % (NFRAMES, min(THETA), max(THETA), SAMPLES, DEVICE))

# camera framed on the WIDEST pose, then left alone: a camera that refits per frame makes the
# device appear to breathe, and the whole point of the loop is to show one thing moving.
sc.frame_set(1 + NFRAMES // 2)
bpy.context.view_layer.update()

import mathutils as mu                                              # noqa: E402


def frame_cam(dir_vec, margin, names):
    pts = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.name == 'Ground' or o.hide_render:
            continue
        if names and o.name not in names:
            continue
        pts += [o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn = mu.Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = mu.Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (mn + mx) / 2
    cam = bpy.data.objects['Cam']
    radius = max((mx - mn).x, (mx - mn).y, (mx - mn).z) / 2 * margin
    vfov = 2 * math.atan(cam.data.sensor_height / (2 * cam.data.lens))
    cam.location = mu.Vector(dir_vec).normalized() * (radius / math.tan(vfov / 2))
    for n in ('CamTarget', 'CamPivot'):
        if n in bpy.data.objects:
            bpy.data.objects[n].location = ctr
    return mn


t0 = time.time()
for name, clad, (rx, ry), margin, focus in SHOTS:
    show(SHELLS, clad)
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    mn = frame_cam(HERO, margin, focus)
    if 'Ground' in bpy.data.objects:
        bpy.data.objects['Ground'].location = (0, 0, mn.z - 0.015)
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)
    sc.render.filepath = os.path.join(d, "f")
    t = time.time()
    bpy.ops.render.render(animation=True)
    print("ANIM: %-12s %3d x %-3d %-5s %d frames in %.1f min"
          % (name, rx, ry, "clad" if clad else "open", NFRAMES, (time.time() - t) / 60.0))
show(SHELLS, True)
print("ANIM: done in %.1f min -- assemble with tools/gif.py" % ((time.time() - t0) / 60.0))
record(["renders/anim/%s.gif" % n for n, _, _, _, _ in SHOTS])
