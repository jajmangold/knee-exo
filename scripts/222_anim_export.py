# -*- coding: utf-8 -*-
"""Export a full flexion cycle as posed STLs, one directory per frame, for the Blender
animation. Same material-tag filename scheme as 221_render_export.py.

Frames follow theta = 52 - 52*cos(2*pi*i/N), so the cycle 0 -> 104 -> 0 is smooth and
loops seamlessly with no duplicated end frame. Meshing is coarser than the stills
(0.06/0.30) because the GIFs are 720 px wide and the sweep has to fit inside FreeCAD's
90 s GUI dispatch limit -- hence CHUNK, run 0..7.
"""
import os, math, json, FreeCAD, Part, Mesh, MeshPart
from FreeCAD import Vector as V

CHUNK = __CHUNK__
NFRAMES = 32
PER = 4

g = globals()
doc = FreeCAD.getDocument("KneeExo_v4")
t = g.get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
g["_kx_timer"] = None

K = json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
C0 = K["C0"]; C1 = K["C1"]; R = K["R"]
BZ = tuple(K["belt_z"]); BIN, BOUT = K["belt_x"][0] + 0.05, K["belt_x"][1]

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "HW_JointBolts"]
CA = ["P3_Carriage", "A2b_BallNut_SFU1620", "P10a_Slider_Delrin", "P10b_Slider_Delrin"]
CB = ["P3b_CarriageB", "A2d_BallNut_LH", "P10c_Slider_Delrin", "P10d_Slider_Delrin",
      "P11_SprungAnchor", "A8_TensionSpring", "P13_HallTension"]
STAT = ["A1_Extrusion_20x60_VSlot", "P1_KneeYoke", "P5_ThighCuff", "A2_BallScrew_SFU1620",
        "A2c_BallScrew_LH", "A3_Motor_6374", "A7_DriveBox", "HW_PinB_10", "A5_Belt_HTD8M",
        "P20_KneeShroud", "P21_ShellAnterior"]
RUN = ["A5b_Belt_DriveRun", "A5c_Belt_TakeRun"]

MAT = {}
for n in ("A1_Extrusion_20x60_VSlot", "A4_Shank2020_VSlot"):
    MAT[n] = "ALU"
for n in ("P1_KneeYoke", "P2a_KneeHingePlate", "P3_Carriage", "P3b_CarriageB",
          "P5_ThighCuff", "P6_ShankSocket", "P7_ShankCuff", "P11_SprungAnchor"):
    MAT[n] = "PETG"
for n in ("P20_KneeShroud", "P21_ShellAnterior", "P24_FairingShank"):
    MAT[n] = "FAIR"
for n in ("A2_BallScrew_SFU1620", "A2c_BallScrew_LH", "HW_PinB_10", "HW_JointBolts"):
    MAT[n] = "STEEL"
for n in ("A2b_BallNut_SFU1620", "A2d_BallNut_LH", "A8_TensionSpring"):
    MAT[n] = "NUT"
for n in ("A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun"):
    MAT[n] = "BELT"
for n in ("P10a_Slider_Delrin", "P10b_Slider_Delrin",
          "P10c_Slider_Delrin", "P10d_Slider_Delrin"):
    MAT[n] = "DELRIN"
MAT["A3_Motor_6374"] = "MOTOR"
MAT["A7_DriveBox"] = "DARK"
MAT["P13_HallTension"] = "PCB"

O = lambda n: doc.getObject(n)


def pose(th):
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    rad = math.radians(th)
    cA = C0 - R * rad
    cB = C1 + R * rad
    for n in SHANK:
        o = O(n)
        if o:
            o.Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in CA:
        o = O(n)
        if o:
            o.Placement = FreeCAD.Placement(V(0., cA - C0, 0.), FreeCAD.Rotation())
    for n in CB:
        o = O(n)
        if o:
            o.Placement = FreeCAD.Placement(V(0., cB - C1, 0.), FreeCAD.Rotation())
    O("A5b_Belt_DriveRun").Shape = Part.makeBox(BOUT - BIN, cA - 24., BZ[1] - BZ[0],
                                                V(-BOUT, 0., BZ[0]))
    O("A5c_Belt_TakeRun").Shape = Part.makeBox(BOUT - BIN, cB - 24., BZ[1] - BZ[0],
                                               V(BIN, 0., BZ[0]))
    return cA, cB


ROOT = r"C:/Users/Josh/KneeExo_render/anim"
if not os.path.isdir(ROOT):
    os.makedirs(ROOT)

for i in range(CHUNK * PER, min((CHUNK + 1) * PER, NFRAMES)):
    th = 52.0 - 52.0 * math.cos(2 * math.pi * i / NFRAMES)
    OUT = os.path.join(ROOT, "f%02d" % i)
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    for f in os.listdir(OUT):
        if f.endswith(".stl"):
            os.remove(os.path.join(OUT, f))
    cA, cB = pose(th)
    doc.recompute()
    cnt = tri = 0
    for n in SHANK + CA + CB + STAT + RUN:
        o = O(n)
        if not o:
            continue
        m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.06,
                                   AngularDeflection=0.30, Relative=False)
        Mesh.Mesh(m.Topology).write(os.path.join(OUT, "%s__%s.stl" % (MAT.get(n, "MISC"), n)))
        cnt += 1
        tri += m.CountFacets
    # runA + runB must stay constant -- this is the differential, checked every frame
    print("f%02d theta %6.2f  carrA %6.2f  carrB %6.2f  sum %7.2f  %d parts %d facets"
          % (i, th, cA, cB, (cA - 24.) + (cB - 24.), cnt, tri))

pose(0.)
doc.recompute()
print("chunk %d done" % CHUNK)
