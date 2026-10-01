# -*- coding: utf-8 -*-
"""What can the LIMB actually see? An occlusion test, not an interference test.

Every check in this repository asks "do two solids overlap". None of them asks the
question that matters for a worn device: standing at the skin and looking outward, is
there a line of sight to something that moves?

So: fire rays radially outward from just off the leg's surface, across the device's
angular span and along its length, and for each one compare the first radius at which it
meets any STATIC part with the first radius at which it meets a MOVING one. If the
moving part comes first, that ray is an opening with a moving part behind it.

Run at three poses, because the gantry sweeps 152 mm and a gap that is covered at full
extension may not be at full flexion.

This test has now earned its keep twice. It found the two windows onto the idler that the
user had already found by hand ("I can still touch A6_Idler_29T_HTD8M") while the pairwise
sweep reported the whole device clean; and it killed an attempt to merge P22 and P25 into
one lofted shell, which looked better and scored 16 exposed rays against 0 because the
bigger section's floor fell inside the limb cut and was deleted. Both failures are of the
same kind: a surface that is not there. An interference sweep cannot see those, because a
missing wall is an absence, not an overlap.

Send with:  python tools/fcsend.py scripts/406_coverage.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")
R_CAP = 29 * 8.0 / (2 * math.pi)
A0 = 161.0
LEG_R = 84.9

# BLOCKERS are everything STATIC, not just the fairings. A first pass listed only
# cladding and duly reported the idler and a V-wheel as "exposed" -- but the extrusion
# and the drive bracket stand between them and the limb, and a static aluminium part
# shields a finger exactly as well as a printed cover does. That was a flaw in the test,
# not in the device.
BLOCK = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle", "P24_FairingShank",
         "P1_KneeYoke", "P5_ThighCuff", "P7_ShankCuff",
         "P6_ShankSocket", "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount",
         "A1_Extrusion_20x60_VSlot", "A7_DriveBox", "A4_Shank2020_VSlot",
         "P2a_KneeHingePlate", "P30_InterfaceProx", "P31_InterfaceDist"]
# The screw and the motor can are in here too: a ball screw turns at 1160 rpm and an
# outrunner's CASE spins. Neither pinches, but neither is something to leave against skin.
MOVING = ["P3_Carriage", "A2b_BallNut_SFU1620", "A2_BallScrew_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel",
          "A5b_Belt_DriveRun", "A5c_Belt_TakeRun", "A5_Belt_HTD8M",
          "A5d_Belt_WrapIdler", "A6_Idler29T", "A3_Motor_6374", "A7b_LinkBelt"]
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]

O = lambda n: doc.getObject(n)


def shapes(names):
    """Parts as a LIST, deliberately not fused.

    The first version fused each group into one solid. Fusing 14 moving parts -- two of
    them half-annulus belt wraps -- silently produced a shape whose common() always came
    back empty, so every ray reported 'no moving part here' and the whole test returned a
    confident all-clear while the idler was reachable through two windows. A test that
    passes when its own input is broken is worse than no test, so: no fuse, and a hard
    check that each group is non-empty."""
    out = [(n, O(n).Shape) for n in names if O(n) is not None]
    assert out, "empty part group -- names wrong?"
    return out


def pose(th):
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    dy = (A0 - R_CAP * math.radians(th)) - A0
    # This tuple is the SHANK group and it is separate from BLOCK, so a part can be listed
    # as an occluder and still never get posed. P31_InterfaceDist was: it sat at identity
    # while the shank rotated, 88 mm from its host, and blocked rays from where it was not.
    for n in ("A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket",
              "P7_ShankCuff", "P24_FairingShank", "P31_InterfaceDist", "HW_JointBolts"):
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in GANTRY:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, dy, 0), FreeCAD.Rotation())


def first_r(parts, y, ang):
    """smallest radius at which a ray leaving the leg surface meets any of `parts`."""
    d = V(math.sin(math.radians(ang)), 0.0, math.cos(math.radians(ang)))
    a = V(d.x * (LEG_R + 0.5), y, d.z * (LEG_R + 0.5))
    b = V(d.x * 260.0, y, d.z * 260.0)
    ray = Part.makeCylinder(0.8, (b - a).Length, a, (b - a).normalize())
    best, who = None, None
    for n, sh in parts:
        if not ray.BoundBox.intersect(sh.BoundBox):
            continue
        c = ray.common(sh)
        if c.isNull() or c.Volume < 0.5:
            continue
        r = min(math.hypot(v.Point.x, v.Point.z) for v in c.Vertexes)
        if best is None or r < best:
            best, who = r, n
    return best, who


# One pose per call: fusing 12 cladding solids and firing a grid of rays through them
# blows past the 90 s GUI dispatch limit if all three are done together.
THETA = __THETA__
ANGLES = list(range(-70, 75, 14))
STATIONS = list(range(40, 332, 18))
print("=" * 78)
print("LIMB'S-EYE COVERAGE -- rays out from r %.1f, %d angles x %d stations x 3 poses"
      % (LEG_R + 0.5, len(ANGLES), len(STATIONS)))
print("   angle 0 = straight out laterally (+Z); negative = anterior (-X)")
print()
rows = []
pose(THETA)
doc.recompute()
cl, mv = shapes(BLOCK), shapes(MOVING)
exposed = 0
for y in STATIONS:
    for a in ANGLES:
        rm, mwho = first_r(mv, float(y), float(a))
        if rm is None:
            continue
        rc, cwho = first_r(cl, float(y), float(a))
        if rc is None or rc > rm + 0.5:
            exposed += 1
            rows.append((y, a, rm, rc, mwho))
print("   theta %+6.1f : %3d of %d rays reach a moving part first"
      % (THETA, exposed, len(ANGLES) * len(STATIONS)))
for y, a, rm, rc, mwho in rows:
    print("     OPEN  Y %3d  angle %+4d deg   %s at r %.1f, first blocker %s"
          % (y, a, mwho, rm, "NONE" if rc is None else "r %.1f" % rc))

pose(0.0)
doc.recompute()
print("=" * 78)
