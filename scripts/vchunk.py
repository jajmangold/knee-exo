# -*- coding: utf-8 -*-
"""Chunked pairwise sweep. Accumulates worst-case overlaps into a JSON file across
several synchronous calls so no single call exceeds the 90 s GUI dispatch limit."""
import math, json, itertools, os, FreeCAD
from FreeCAD import Vector as V
I0=__I0__; I1=__I1__
ACC=r"C:/Users/Josh/KneeExo_anim/clash.json"
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
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
acc={"worst":{},"env":{"lo":1e9,"hi":-1e9,"loN":"","hiN":"","khi":-1e9,"khiN":"","n":0}}
if os.path.exists(ACC):
    try: acc=json.load(open(ACC))
    except Exception: pass
W=acc["worst"]; E=acc["env"]
for i in range(I0,min(I1,len(S))):
    s=S[i]; pose(s)
    for a,b in itertools.combinations(ALL,2):
        sa,sb=O(a).Shape,O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): continue
        try: c=sa.common(sb)
        except Exception: continue
        if c.isNull(): continue
        v=c.Volume/1000.0
        if v<=0.02: continue
        k=a+"^"+b
        if v>W.get(k,[0])[0]: W[k]=[v,s["theta"]]
    for n in ALL:
        if n.startswith("REF"): continue
        bb=O(n).Shape.BoundBox
        if bb.ZMin<E["lo"]: E["lo"],E["loN"]=bb.ZMin,n
        if bb.ZMax>E["hi"]: E["hi"],E["hiN"]=bb.ZMax,n
        if bb.YMin<150.0 and bb.ZMax>E["khi"]: E["khi"],E["khiN"]=bb.ZMax,n
    E["n"]+=1
pose(BASE)
json.dump(acc,open(ACC,"w"))
print("chunk %d..%d done; poses accumulated=%d; pairs tracked=%d"%(I0,I1,E["n"],len(W)))
