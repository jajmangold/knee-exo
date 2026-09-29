# -*- coding: utf-8 -*-
"""Clevis root's top corner is inside the bar's swept fan, and the screw scallop was
lost in an earlier rebuild. Trim the root to Y<=-45 (both shared bolts at -55/-85 stay
on it) and re-cut the screw relief."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
cb=doc.getObject("P2b_RodClevisBlock")
before=cb.Shape.Volume/1000
# 1) trim the root's top corner out of the bar's sweep
sh=cb.Shape.cut(bx(-5.0,29.0,-45.0,0.0,115.0,160.0))
# 2) re-cut the screw relief at full flexion, measured not guessed
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for n in ("A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
              "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts"):
        o=doc.getObject(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.recompute()
cb.Shape=sh; doc.recompute()
scr=doc.getObject("A2_BallScrew_SFU1620").Shape
worst=(0.0,None,None)
for t in [float(x) for x in range(40,106,2)]:
    pose(float(t))
    c=cb.Shape.common(scr)
    if not c.isNull() and c.Volume>worst[0]:
        loc=c.copy(); loc.rotate(V(0,0,0),V(0,0,1),-t)
        worst=(c.Volume,t,loc.BoundBox)
pose(0.0)
if worst[1] is not None:
    v,t,bb=worst
    print("screw relief needed: %.3f cm3 at theta=%+.0f"%(v/1000,t))
    sh=cb.Shape.cut(bx(bb.XMin-1.5,bb.XMax+1.5,bb.YMin-1.5,bb.YMax+1.5,bb.ZMin-1.5,bb.ZMax+1.5))
    cb.Shape=sh
assert len(cb.Shape.Solids)==1 and cb.Shape.isClosed()
print("clevis %.1f -> %.1f cm3"%(before,cb.Shape.Volume/1000))
doc.recompute(); doc.save()
