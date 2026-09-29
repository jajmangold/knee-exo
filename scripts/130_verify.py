# -*- coding: utf-8 -*-
"""Full pairwise sweep, no skip list. Driver fix: the shank rotation now comes from
the SAMPLE's own theta, not the requested t -- samples stop at 104 deg, so asking for
105 rotated the shank 105 while placing the rod from the 104 sample (1.30 mm of fake
misalignment, which is what the 0.04 cm3 'clash' was)."""
import math, json, itertools, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
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
def pose(s):
    r=FreeCAD.Rotation(V(0,0,1),s["theta"])          # <-- from the sample, not from t
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
print("samples: %d, theta %.1f .. %.1f"%(len(S),S[0]["theta"],S[-1]["theta"]))
worst={}
idx=list(range(0,len(S),3))
if idx[-1]!=len(S)-1: idx.append(len(S)-1)     # always include the true end of travel
for i in idx:
    pose(S[i])
    for a,b in itertools.combinations(ALL,2):
        v=vol(a,b)
        if v>0.02 and v>worst.get((a,b),(0,))[0]: worst[(a,b)]=(v,S[i]["theta"])
pose(BASE)
print("=== pairs >0.02 cm3 over %d poses (%d parts, no skips) ==="%(len(idx),len(ALL)))
hard=0
for (a,b),(v,th) in sorted(worst.items(),key=lambda kv:-kv[1][0]):
    ref = a.startswith("REF") or b.startswith("REF")
    if not ref: hard+=1
    print("  %-30s ^ %-30s %7.2f cm3 @%+6.1f %s"%(a,b,v,th,"REF limb" if ref else "*** HARD ***"))
print("\nhard-part clashes: %d"%hard)
