# -*- coding: utf-8 -*-
import math, json, itertools, FreeCAD
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts"]
ROD=["P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage"]
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
       "A2_BallScrew_SFU1620","A3_Motor_6374"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+ROD+THIGH+["P3_Carriage"] if O(n)]
def pose(t):
    s=sm(t); r=FreeCAD.Rotation(V(0,0,1),t)
    for n in SHANK:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    O("P3_Carriage").Placement=FreeCAD.Placement(V(0,s["carr"]-CARR0,0),FreeCAD.Rotation())
    R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
    base=V(s["Dx"],s["Dy"],0)-R.multVec(V(D0[0],D0[1],0))
    for n in ROD:
        if O(n): O(n).Placement=FreeCAD.Placement(base,R)
def vol(a,b):
    try:
        sa,sb=O(a).Shape,O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): return 0.0
        c=sa.common(sb); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
worst={}
for th in [float(x) for x in range(-2,106,7)]+[105.0]:
    pose(th)
    for a,b in itertools.combinations(ALL,2):
        v=vol(a,b)
        if v>0.02 and v>worst.get((a,b),(0,))[0]: worst[(a,b)]=(v,th)
pose(0.0)
print("=== pairs >0.02 cm3 anywhere in the ROM (%d parts, no skips) ==="%len(ALL))
hard=0
for (a,b),(v,th) in sorted(worst.items(),key=lambda kv:-kv[1][0]):
    ref = a.startswith("REF") or b.startswith("REF")
    if not ref: hard+=1
    print("  %-30s ^ %-30s %7.2f cm3 @%+5.0f %s"%(a,b,v,th,"REF limb" if ref else "*** HARD ***"))
print("\nhard-part clashes: %d"%hard)
