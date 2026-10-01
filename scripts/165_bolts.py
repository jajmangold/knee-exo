# -*- coding: utf-8 -*-
"""Posterior bolts started at X=-2, but A4's posterior T-slot void is X 6..10 -- the
T-nut's thread begins at X=6, so the shank must start there, not inside the extrusion."""
import FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
BOLT_Z=(-85.,-110.,-135.); BOLT_X=(-60.,-90.,-120.); zc=104.0
bolts=None
for y in BOLT_Z:
    bb=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))       # into the inboard slot (94..98)
    bolts=bb if bolts is None else bolts.fuse(bb)
for y in BOLT_X:
    bolts=bolts.fuse(cx(2.5,6.,24.,y,zc).fuse(cx(4.6,18.,24.,y,zc)))
doc.getObject("HW_JointBolts").Shape=bolts
b=bolts.BoundBox
print("HW_JointBolts X %.1f..%.1f  Z %.1f..%.1f  solids=%d  vol %.2f cm3"%(
    b.XMin,b.XMax,b.ZMin,b.ZMax,len(bolts.Solids),bolts.Volume/1000))
print("  3 M5 along Z: shank 82..98 into the inboard slot (94..98)")
print("  3 M5 along X: shank 6..24 into the posterior slot (6..10), head 18..24 on the web face")
doc.recompute(); doc.save()
