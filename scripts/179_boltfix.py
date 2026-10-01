# -*- coding: utf-8 -*-
"""HW_JointBolts still carried the 3 clevis bolts (Z 110..128) from the rigid-rod
design. P2b is retired, and their heads sat inside the belt corridor (Z 116..146).
Only the 3 fork-to-2020 bolts remain."""
import FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
bolts=None
for y in (-90.,-110.,-125.):
    b=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))
    bolts=b if bolts is None else bolts.fuse(b)
bolts=bolts.removeSplitter()
doc.getObject("HW_JointBolts").Shape=bolts
bb=bolts.BoundBox
print("HW_JointBolts  Z %.1f..%.1f  solids=%d  vol %.2f cm3  (was Z 82..128)"%(
    bb.ZMin,bb.ZMax,len(bolts.Solids),bolts.Volume/1000))
print("  3 x M5 up into A4's inboard slot (94..98), heads under the outer cheek")
doc.recompute(); doc.save()
