# -*- coding: utf-8 -*-
import math, json, itertools, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_JointBolts","HW_PinD_M8_Clevis"]
CARR =["P3_Carriage","HW_PinC_M8_Carriage","A2b_BallNut_SFU1620"]
ROD  =["P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage"]
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
       "A2_BallScrew_SFU1620","A3_Motor_6374","HW_PinB_10"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+CARR+ROD+THIGH if O(n)]
def pose(s):
    r=FreeCAD.Rotation(V(0,0,1),s["theta"])
    for n in SHANK:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CARR:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,s["carr"]-CARR0,0),FreeCAD.Rotation())
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
for s in S:
    pose(s)
    for a,b in itertools.combinations(ALL,2):
        v=vol(a,b)
        if v>0.02 and v>worst.get((a,b),(0,))[0]: worst[(a,b)]=(v,s["theta"])
pose(BASE)
print("=== %d parts, %d poses, NO skip list ==="%(len(ALL),len(S)))
hard=0
for (a,b),(v,th) in sorted(worst.items(),key=lambda kv:-kv[1][0]):
    ref = a.startswith("REF") or b.startswith("REF")
    if not ref: hard+=1
    print("  %-28s ^ %-28s %7.2f cm3 @%+6.1f %s"%(a,b,v,th,"REF limb" if ref else "*** HARD ***"))
print("\nhard-part clashes: %d"%hard)
# lateral envelope, swept over the whole ROM
lo=1e9; hi=-1e9; loN=hiN=""
knee_hi=-1e9; knee_hiN=""
for s in S:
    pose(s)
    for n in ALL:
        if n.startswith("REF"): continue
        b=O(n).Shape.BoundBox
        if b.ZMin<lo: lo,loN=b.ZMin,n
        if b.ZMax>hi: hi,hiN=b.ZMax,n
        if b.YMin<150.0 and b.ZMax>knee_hi: knee_hi,knee_hiN=b.ZMax,n
pose(BASE)
print("\n=== lateral envelope swept over the ROM ===")
print("  inboard  Z %.1f  (%s)"%(lo,loN))
print("  outboard Z %.1f  (%s)"%(hi,hiN))
print("  outboard below the hip (Y<150): Z %.1f  (%s)"%(knee_hi,knee_hiN))
print("  proud of the knee skin (Z=52): %.1f mm at the knee, %.1f mm overall"%(knee_hi-52,hi-52))
doc.save()
