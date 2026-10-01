# -*- coding: utf-8 -*-
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
O=lambda n: doc.getObject(n)
SH=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket","P7_ShankCuff","REF_Shank","HW_PinB_10"]
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for n in SH:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.recompute()
# find the worst pose and the overlap region in the BLOCK'S OWN frame
worst=(0,None,None)
for t in [float(x) for x in range(90,106)]:
    pose(float(t))
    c=O("P2b_RodClevisBlock").Shape.common(O("A2_BallScrew_SFU1620").Shape)
    if not c.isNull() and c.Volume>worst[0]:
        cc=c.copy(); cc.Placement=FreeCAD.Placement()      # keep world coords
        inv=FreeCAD.Rotation(V(0,0,1),-t)
        loc=c.copy(); loc.rotate(V(0,0,0),V(0,0,1),-t)     # into the block's local frame
        worst=(c.Volume,t,loc.BoundBox)
v,t,bb=worst
print("worst %.3f cm3 at theta=%+.0f"%(v/1000,t))
print("in block-local frame: X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
pose(0.0)
# scallop with 1.5 mm margin all round
cb=O("P2b_RodClevisBlock").Shape
cut=Part.makeBox(bb.XLength+3, bb.YLength+3, bb.ZLength+3,
                 V(bb.XMin-1.5, bb.YMin-1.5, bb.ZMin-1.5))
cb2=cb.cut(cut)
print("block %.1f -> %.1f cm3, solids=%d"%(cb.Volume/1000, cb2.Volume/1000, len(cb2.Solids)))
assert len(cb2.Solids)==1 and cb2.isClosed()
O("P2b_RodClevisBlock").Shape=cb2
doc.recompute(); doc.save()
