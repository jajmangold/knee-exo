# -*- coding: utf-8 -*-
"""Consistent fastener scheme. Constraints discovered:
 - the 2020 only exists below Y=-45, so every bolt must be below that
 - the hinge plate occupies the 2020's ANTERIOR face exactly where the clevis's
   through-bolts would exit -> share them: 2 M5 clamp clevis + 2020 + plate as a stack,
   plus 1 T-nut bolt into the anterior slot to stop the plate rotating."""
import FreeCAD, Part
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration under freecadcmd, where no document is
    open yet -- which is why these older build scripts could not be re-run without the GUI.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
HINGE_Z=(122.0,134.0); SLOT_Z=131.0; LAP_X=(-28.0,-10.0)
SHARED=(-55.0,-85.0)      # clamp clevis + 2020 + plate
TNUT=(-115.0,)            # plate only, into the anterior slot
A4=doc.getObject("A4_Shank2020_VSlot").Shape
bbA=A4.BoundBox
print("2020 spans Y %.0f..%.0f  -> all fasteners must sit below Y=%.0f"%(bbA.YMin,bbA.YMax,bbA.YMax))
assert all(y<bbA.YMax for y in SHARED+TNUT)
# ---- rebuild the 2020 clean, then drill only the shared holes ----
SH20_X=(-10.0,10.0); SH20_Z=(121.0,141.0); SH20_Y=(bbA.YMin,bbA.YMax)
s=bx(*SH20_X,*SH20_Y,*SH20_Z)
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4))
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4,SH20_Z[1]+1))
s=s.cut(bx(SH20_X[0]-1,SH20_X[0]+4,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(bx(SH20_X[1]-4,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(Part.makeCylinder(4.2,SH20_Y[1]-SH20_Y[0]+2,V(0,SH20_Y[0]-1,131),V(0,1,0)))
for y in SHARED: s=s.cut(cx(2.6,-12.0,12.0,y,SLOT_Z))
assert len(s.Solids)==1 and s.isClosed()
doc.getObject("A4_Shank2020_VSlot").Shape=s
# ---- hinge plate: lap reaches down past every bolt ----
hp=cz(22.0,*HINGE_Z).fuse(bx(LAP_X[0],LAP_X[1],-130.0,-10.0,*HINGE_Z))
hp=hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp=hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in SHARED+TNUT: hp=hp.cut(cx(2.6,LAP_X[0]-2,LAP_X[1]+2,y,SLOT_Z))
assert len(hp.Solids)==1 and hp.isClosed()
doc.getObject("P2a_KneeHingePlate").Shape=hp
# ---- clevis block: same two holes ----
cb=doc.getObject("P2b_RodClevisBlock").Shape
for f in list(cb.Faces):
    pass
cb=cb.cut(cx(3.0,8.0,30.0,SHARED[0],SLOT_Z)).cut(cx(3.0,8.0,30.0,SHARED[1],SLOT_Z))
assert len(cb.Solids)==1 and cb.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb
# ---- fasteners ----
bolts=None
for y in SHARED:                       # head on the plate side, nut on the clevis side
    b=cx(2.5,-34.0,28.0,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z)).fuse(cx(4.6,24.0,28.0,y,SLOT_Z))
    bolts=b if bolts is None else bolts.fuse(b)
for y in TNUT:
    b=cx(2.5,-34.0,-6.0,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z))
    bolts=bolts.fuse(b)
doc.getObject("HW_JointBolts").Shape=bolts
doc.recompute()
P=doc.getObject("P2a_KneeHingePlate").Shape; C=doc.getObject("P2b_RodClevisBlock").Shape
print("plate %.1f cm3 gap->2020 %.3f | clevis %.1f cm3 gap->2020 %.3f"
      %(P.Volume/1000,P.distToShape(s)[0],C.Volume/1000,C.distToShape(s)[0]))
print("fasteners: 2 shared M5 through clevis+2020+plate, 1 M5 T-nut into the anterior slot")
doc.save()
