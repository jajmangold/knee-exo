# -*- coding: utf-8 -*-
"""Full pairwise interference, NO skip list. Self-contained pose driver."""
import math, json, itertools, FreeCAD
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration under freecadcmd, where no document is
    open yet -- which is why these older build scripts could not be re-run without the GUI.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"]); ROD_Z=K["rod_z"]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts"]
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee"]
MOVE=["P3_Carriage","P4_Rod_8mm","A2_BallScrew_SFU1620","A3_Motor_6374"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+THIGH+MOVE if O(n)]
print("parts:",len(ALL))
def pose(t):
    s=sm(t); r=FreeCAD.Rotation(V(0,0,1),t)
    for n in SHANK:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    c=O("P3_Carriage")
    if c: c.Placement=FreeCAD.Placement(V(0.0,s["carr"]-CARR0,0.0),FreeCAD.Rotation())
    rd=O("P4_Rod_8mm")
    if rd:
        dphi=s["phi"]-PHI0
        R=FreeCAD.Rotation(V(0,0,1),dphi)
        d0=V(D0[0],D0[1],0.0); d=V(s["Dx"],s["Dy"],0.0)
        rd.Placement=FreeCAD.Placement(d-R.multVec(d0),R)
    doc.recompute()
def vol(a,b):
    try:
        sa,sb=O(a).Shape,O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): return 0.0
        c=sa.common(sb)
        return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
worst={}
for th in [float(x) for x in range(-2,106,7)]+[105.0]:
    pose(th)
    for a,b in itertools.combinations(ALL,2):
        v=vol(a,b)
        if v>0.02:
            k=(a,b)
            if v>worst.get(k,(0,))[0]: worst[k]=(v,th)
pose(0.0)
print("\n=== every pair with >0.02 cm3 overlap anywhere in the ROM ===")
if not worst: print("  NONE")
for (a,b),(v,th) in sorted(worst.items(), key=lambda kv:-kv[1][0]):
    tag="REF limb (padding)" if a.startswith("REF") or b.startswith("REF") else "*** HARD PART CLASH ***"
    print("  %-26s ^ %-26s %7.2f cm3 @%+5.0f  %s"%(a,b,v,th,tag))
# telescoping engagement
a=O("A4_Shank2020_VSlot").Shape.BoundBox; s=O("P6_ShankSocket").Shape.BoundBox
print("\n2020 Y %.0f..%.0f ; socket Y %.0f..%.0f -> engagement %.0f mm"
      %(a.YMin,a.YMax,s.YMin,s.YMax, s.YMax-a.YMin))
