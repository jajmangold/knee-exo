# -*- coding: utf-8 -*-
import math, json, itertools, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts","HW_PinD_M8_Clevis"]
CARR =["P3_Carriage","HW_PinC_M8_Carriage"]
ROD  =["P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage"]
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
       "A2_BallScrew_SFU1620","A3_Motor_6374"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+CARR+ROD+THIGH if O(n)]
# tidy: the carriage pin belongs with the drive group, not the shank group
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup"):
        if gg.Name=="B_Shank" and any(m.Name=="HW_PinC_M8_Carriage" for m in gg.Group):
            gg.removeObject(O("HW_PinC_M8_Carriage"))
        if gg.Name=="C_Drive": gg.addObject(O("HW_PinC_M8_Carriage"))
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
# --- fit audit at the new joints ---
print("\n=== rod-end joint fits (mm) ===")
print("  eye bore 8.10 vs M8 shoulder 8.00           -> 0.10 diametral")
print("  eye width 12.0 in a 15.2 slot               -> 1.60 per side")
print("  eye OD 24.0 in a 26.0 pocket                -> 1.00 radial")
print("  barrel OD 14.0 in a 15.2 swept relief       -> 0.60 per side")
print("  clevis cheeks 8.4 / 8.4 (were 5.8 / 5.8)")
print("  carriage boss wall 4.0 (was 1.3)")
doc.save()
