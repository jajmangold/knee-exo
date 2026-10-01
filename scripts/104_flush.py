# -*- coding: utf-8 -*-
"""Bolt heads live on the ANTERIOR (plate) side only; the clevis side is a tapped
blind hole so nothing protrudes into the rod's swept path. Also seat the clevis."""
import FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
SLOT_Z=131.0; SHARED=(-55.0,-85.0); TNUT=(-115.0,)
A4=doc.getObject("A4_Shank2020_VSlot").Shape
cb=doc.getObject("P2b_RodClevisBlock")
g=cb.Shape.distToShape(A4)[0]
if g>1e-4:
    t=cb.Shape.copy(); t.translate(V(-g,0,0)); cb.Shape=t
    print("clevis seated: gap %.3f -> %.3f"%(g, cb.Shape.distToShape(A4)[0]))
XOUT=cb.Shape.BoundBox.XMax
bolts=None
for y in SHARED:                      # head anterior, shank ends flush in the clevis
    b=cx(2.5,-34.0,XOUT-0.2,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z))
    bolts=b if bolts is None else bolts.fuse(b)
for y in TNUT:
    bolts=bolts.fuse(cx(2.5,-34.0,-6.0,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z)))
doc.getObject("HW_JointBolts").Shape=bolts
doc.recompute()
print("bolt shanks end at X=%.1f (clevis outer face %.1f) - nothing protrudes"%(XOUT-0.2,XOUT))
doc.save()
