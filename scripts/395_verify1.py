# -*- coding: utf-8 -*-
"""Full pairwise interference sweep of the ONE-SCREW build, all 107 poses.

Supersedes 231_verify.py. Differences beyond the part list:

  * One moving carriage, not two. Y_clamp = A0 - R*theta.
  * NOTHING about the belt is rebuilt per pose. In the closed-loop topology both straight
    strands and both wraps are static geometry; only the clamp slides along the -X strand.
    The two-screw build had to rebuild two runs every pose because the runs ENDED at the
    carriages.

Run in chunks -- the GUI dispatch dies at 90 s and then keeps working in the background,
which silently corrupts the accumulator:

  for i in 0 12 24 36 48 60 72 84 96; do ... I0=$i I1=$((i+12)) ; done

Send with:  python tools/fcsend.py <rendered copy>
"""
import math
import json
import itertools
import os
import FreeCAD
import Part
from FreeCAD import Vector as V

I0 = __I0__
I1 = __I1__
ACC = r"C:/Users/Josh/KneeExo_anim/clash1.json"
doc = FreeCAD.getDocument("KneeExo_v4")

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
A0 = 161.0
THETA = [float(i) for i in range(-2, 105)]

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "REF_Shank", "HW_JointBolts"]
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
STAT = ["A1_Extrusion_20x60_VSlot", "P1_KneeYoke", "P5_ThighCuff", "REF_Thigh", "REF_Knee",
        "A2_BallScrew_SFU1620", "A3_Motor_6374", "A6_Idler29T", "A7_DriveBox",
        "A7b_LinkBelt", "HW_PinB_10",
        "A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler",
        "P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap",
        "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount",
        "P25_MotorNacelle"]

O = lambda n: doc.getObject(n)
ALL = [n for n in SHANK + GANTRY + STAT if O(n)]
MISSING = [n for n in SHANK + GANTRY + STAT if not O(n)]


def pose(th):
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    for n in SHANK:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    dy = (A0 - R * math.radians(th)) - A0
    for n in GANTRY:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, dy, 0), FreeCAD.Rotation())


acc = {"worst": {}, "env": {"lo": 1e9, "hi": -1e9, "loN": "", "hiN": "",
                            "khi": -1e9, "khiN": "", "ax": 1e9, "px": -1e9, "n": 0}}
if os.path.exists(ACC):
    try:
        acc = json.load(open(ACC))
    except Exception:
        pass
W = acc["worst"]
E = acc["env"]

for i in range(I0, min(I1, len(THETA))):
    th = THETA[i]
    pose(th)
    for a, b in itertools.combinations(ALL, 2):
        sa, sb = O(a).Shape, O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox):
            continue
        try:
            c = sa.common(sb)
        except Exception:
            continue
        if c.isNull():
            continue
        v = c.Volume / 1000.0
        if v <= 0.02:
            continue
        k = a + "^" + b
        if v > W.get(k, [0])[0]:
            W[k] = [v, th]
    for n in ALL:
        if n.startswith("REF"):
            continue
        bb = O(n).Shape.BoundBox
        if bb.ZMin < E["lo"]:
            E["lo"], E["loN"] = bb.ZMin, n
        if bb.ZMax > E["hi"]:
            E["hi"], E["hiN"] = bb.ZMax, n
        if bb.XMin < E["ax"]:
            E["ax"] = bb.XMin
        if bb.XMax > E["px"]:
            E["px"] = bb.XMax
        if bb.YMin < 150.0 and bb.ZMax > E["khi"]:
            E["khi"], E["khiN"] = bb.ZMax, n
    E["n"] += 1

pose(0.0)
json.dump(acc, open(ACC, "w"))
print("chunk %d..%d done; poses=%d; parts=%d; pairs flagged=%d"
      % (I0, I1, E["n"], len(ALL), len(W)))
if MISSING:
    print("MISSING FROM THE DOCUMENT: %s" % ", ".join(MISSING))
