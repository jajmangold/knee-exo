# -*- coding: utf-8 -*-
"""Relieve P2b's lower cheek where it sweeps past the ball screw at high flexion.
The screw is static and P2b rotates with the shank, so in P2b's local frame the screw
sweeps an arc. Built as fresh analytic cylinders on rotated axes (no transformGeometry,
which would turn the cylinder into a spline surface)."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]
p2b=doc.getObject("P2b_RodClevisBlock")
base=p2b.Shape                     # placement is identity -> this IS local geometry
assert p2b.Placement.isIdentity(),"P2b placement must be identity before editing"
SCR_X, SCR_Z, SCR_R = 40.0, 117.0, 9.0       # r=8 screw + 1.0 mm clearance
def rz(p,a):
    c,s=math.cos(a),math.sin(a); return (p[0]*c-p[1]*s, p[0]*s+p[1]*c, p[2])
acc=None; hits=[]
for s in S:
    th=s["theta"]
    if th < 70.0: continue                   # only high flexion can reach the screw
    a=-math.radians(th)                      # world -> P2b local
    b=rz((SCR_X,40.0,SCR_Z),a); d=rz((0.0,1.0,0.0),a)
    cyl=Part.makeCylinder(SCR_R,260.0,V(*b),V(d[0],d[1],0.0))
    if not cyl.BoundBox.intersect(base.BoundBox): continue
    c=base.common(cyl)
    if c.isNull() or c.Volume<1.0: continue
    hits.append((th,c.Volume/1000.0))
    acc=cyl if acc is None else acc.fuse(cyl)
print("poses where the screw reaches P2b: %d"%len(hits))
for th,v in hits: print("   th=%+6.1f  raw overlap %.4f cm3"%(th,v))
if acc is None:
    print("nothing to relieve")
else:
    acc=acc.removeSplitter()
    out=base.cut(acc).removeSplitter()
    print("P2b %.3f -> %.3f cm3 (removed %.3f)  solids=%d closed=%s valid=%s"%(
        base.Volume/1000,out.Volume/1000,(base.Volume-out.Volume)/1000,
        len(out.Solids),out.isClosed(),out.isValid()))
    assert len(out.Solids)==1 and out.isClosed() and out.isValid(),"P2b solids=%d"%len(out.Solids)
    p2b.Shape=out
    doc.recompute(); doc.save()
