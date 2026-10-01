# -*- coding: utf-8 -*-
"""Make the plate-to-2020 joint real:
 - P2a gets a STRAIGHT lap section seated flat on the 2020's anterior face (X=-10)
 - its bolts line up with the 2020's ANTERIOR SLOT (Z=131) -> T-nuts, no drilling
 - P2b seated flat on the posterior face (X=+10), through-bolted -> matching holes in the 2020
 - bolts modelled so the joint reads as fastened"""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
HINGE_Z=(122.0,134.0); SLOT_Z=131.0           # centre of the 2020's anterior slot
LAP_X=(-28.0,-10.0)                            # seats flat on the 2020 face at X=-10
PB=(-35.0,-65.0,-95.0)                         # plate bolt stations
# ---- P2a: disc + straight lap ----
hp=cz(22.0,*HINGE_Z).fuse(bx(LAP_X[0],LAP_X[1],-120.0,-10.0,*HINGE_Z))
hp=hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp=hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in PB: hp=hp.cut(cx(2.6,LAP_X[0]-2,LAP_X[1]+2,y,SLOT_Z))
assert len(hp.Solids)==1 and hp.isClosed(),"P2a %d"%len(hp.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=hp
# ---- P2b: seat flat on the posterior face, and drill the 2020 to match ----
cb=doc.getObject("P2b_RodClevisBlock").Shape
cb=cb.cut(bx(-30.0,10.0,-200.0,0.0,110.0,160.0))      # trim anything inboard of X=10
bbc=cb.BoundBox
CBOLT=[(bbc.YMin+18.0),(bbc.YMax-18.0)]
A4=doc.getObject("A4_Shank2020_VSlot").Shape
for y in CBOLT:
    hole=cx(2.6,-12.0,30.0,y,SLOT_Z)
    cb=cb.cut(hole); A4=A4.cut(hole)                   # through-bolt: drill both
assert len(cb.Solids)==1 and cb.isClosed(),"P2b %d"%len(cb.Solids)
assert len(A4.Solids)==1 and A4.isClosed(),"A4 %d"%len(A4.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
doc.getObject("A4_Shank2020_VSlot").Shape=A4
# ---- visible fasteners ----
bolts=None
for y in PB:                                            # M5 into the anterior slot (T-nut)
    b=cx(2.5,LAP_X[0]-9.0,-11.0,y,SLOT_Z).fuse(cx(4.6,LAP_X[0]-9.0,LAP_X[0]-4.0,y,SLOT_Z))
    bolts=b if bolts is None else bolts.fuse(b)
for y in CBOLT:                                         # M5 through-bolts + nut
    b=cx(2.5,-13.0,26.0,y,SLOT_Z).fuse(cx(4.6,-18.0,-13.0,y,SLOT_Z)).fuse(cx(4.6,26.0,30.0,y,SLOT_Z))
    bolts=bolts.fuse(b)
o=doc.getObject("HW_JointBolts") or doc.addObject("Part::Feature","HW_JointBolts")
o.Shape=bolts; o.ViewObject.ShapeColor=(0.45,0.45,0.50)
grp=doc.getObject("B_Shank")
if grp and o not in grp.Group: grp.addObject(o)
doc.recompute()
P=doc.getObject("P2a_KneeHingePlate").Shape
print("P2a %.1f cm3 (%.0f g 6061); gap to 2020 = %.3f mm"%(P.Volume/1000,P.Volume/1000*2.7,P.distToShape(A4)[0]))
print("P2b %.1f cm3; gap to 2020 = %.3f mm"%(cb.Volume/1000, cb.distToShape(A4)[0]))
print("bolts: %d M5 (3 T-nut into anterior slot, 2 through-bolt)"%(len(PB)+len(CBOLT)))
doc.save()
