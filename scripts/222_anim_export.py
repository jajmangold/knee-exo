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
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration when no document is open, which
    surfaces from freecadcmd as the unhelpful "<unknown exception data>" -- and is why these
    older build scripts could not be re-run without the GUI at all.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace(chr(92), "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
t = g.get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
g["_kx_timer"] = None

# One-screw kinematics; kin_low.json is the two-screw file and its C0/C1 are meaningless
# here. R is the only thing that carries over and it is a constant.
R = 29 * 8.0 / (2 * math.pi)
A0 = 161.0

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "P31_InterfaceDist", "HW_JointBolts"]
# posed with the shank but never exported -- the renders leave the reference limb out
# One moving group. The belt is a closed loop whose strands and wraps are static, so
# nothing is rebuilt per frame.
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
STAT = ["A1_Extrusion_20x60_VSlot", "P1_KneeYoke", "P5_ThighCuff", "A2_BallScrew_SFU1620",
        "A3_Motor_6374", "A6_Idler29T", "A7_DriveBox", "A7b_LinkBelt", "HW_PinB_10",
        "A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler",
        "P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle",
        "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount"]
MAT = {}
for n in ("A1_Extrusion_20x60_VSlot", "A4_Shank2020_VSlot"):
    MAT[n] = "ALU"
for n in ("P1_KneeYoke", "P2a_KneeHingePlate", "A6_Idler29T",
          "P5_ThighCuff", "P6_ShankSocket", "P7_ShankCuff"):
    MAT[n] = "PETG"
for n in ("P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle", "P30_InterfaceProx", "P31_InterfaceDist", "P24_FairingShank",
          "P23a_FairingMount", "P23b_FairingMount",
          "P23c_FairingMount"):
    MAT[n] = "FAIR"
for n in ("A2_BallScrew_SFU1620", "HW_PinB_10", "HW_JointBolts"):
    MAT[n] = "STEEL"
for n in ("A2b_BallNut_SFU1620",):
    MAT[n] = "NUT"
for n in ("A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun",
          "A5d_Belt_WrapIdler", "A7b_LinkBelt"):
    MAT[n] = "BELT"
for n in ("P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"):
    MAT[n] = "DELRIN"
MAT["A3_Motor_6374"] = "MOTOR"
MAT["A7_DriveBox"] = "ALUM"
MAT["P3_Carriage"] = "ALUM"

O = lambda n: doc.getObject(n)


def pose(th):
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    rad = math.radians(th)
    dy = (A0 - R * rad) - A0
    for n in SHANK + POSED_REF:
        o = O(n)
        if o:
            o.Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in GANTRY:
        o = O(n)
        if o:
            o.Placement = FreeCAD.Placement(V(0., dy, 0.), FreeCAD.Rotation())
    return dy


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
    dy = pose(th)
    doc.recompute()
    cnt = tri = 0
    for n in SHANK + GANTRY + STAT:
        o = O(n)
        if not o:
            continue
        m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.06,
                                   AngularDeflection=0.30, Relative=False)
        Mesh.Mesh(m.Topology).write(os.path.join(OUT, "%s__%s.stl" % (MAT.get(n, "MISC"), n)))
        cnt += 1
        tri += m.CountFacets
    # The two-screw version printed runA + runB every frame to prove the differential
    # held. There is nothing to check now: one clamp on a closed loop cannot drift, the
    # invariant is structural rather than something two screws have to agree on.
    print("f%02d theta %6.2f  clamp Y %7.2f  %d parts %d facets"
          % (i, th, A0 + dy, cnt, tri))

pose(0.)
doc.recompute()
print("chunk %d done" % CHUNK)
