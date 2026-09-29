# -*- coding: utf-8 -*-
import math, json, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
O=lambda n: doc.getObject(n)
def pose(t):
    s=sm(t); r=FreeCAD.Rotation(V(0,0,1),t)
    for n in ("A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
              "P7_ShankCuff","REF_Shank","HW_PinB_10"):
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    O("P3_Carriage").Placement=FreeCAD.Placement(V(0,s["carr"]-CARR0,0),FreeCAD.Rotation())
    R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
    O("P4_Rod_8mm").Placement=FreeCAD.Placement(V(s["Dx"],s["Dy"],0)-R.multVec(V(D0[0],D0[1],0)),R)
    doc.recompute()
for th,pairs in ((-2.0,[("P2a_KneeHingePlate","P4_Rod_8mm"),
                        ("A1_Extrusion_20x60_VSlot","A2_BallScrew_SFU1620")]),
                 (61.0,[("P3_Carriage","A2_BallScrew_SFU1620")])):
    pose(th)
    for a,b in pairs:
        c=O(a).Shape.common(O(b).Shape)
        if c.isNull() or c.Volume<1: continue
        bb=c.BoundBox
        print("@%+5.0f %-26s ^ %-24s %6.2f cm3  X[%6.1f,%6.1f] Y[%7.1f,%7.1f] Z[%6.1f,%6.1f]"
              %(th,a,b,c.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
sc=O("A2_BallScrew_SFU1620").Shape.BoundBox
print("\nscrew bbox X[%.1f,%.1f] Z[%.1f,%.1f]  (rail outer face Z=108)"%(sc.XMin,sc.XMax,sc.ZMin,sc.ZMax))
pose(0.0)
