# -*- coding: utf-8 -*-
"""The two rod pivot bolts were never modelled. M8 shoulder bolts in DOUBLE SHEAR
through the clevis cheeks -- this is the detail that makes 'bolt the eye flat to the
plate' unnecessary: the ears already exist on both ends."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def bolt(x,y):
    s=cz(4.0,116.0,156.0,x,y)                  # M8 shoulder, spans both cheeks
    s=s.fuse(cz(6.5,152.0,157.2,x,y))          # head above the upper cheek
    s=s.fuse(cz(6.9,114.8,120.0,x,y))          # nyloc below the lower cheek
    return s.removeSplitter()
made=[]
for name,(x,y) in (("HW_PinD_M8_Clevis",D0),("HW_PinC_M8_Carriage",(XE,s0))):
    s=bolt(x,y)
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=name; o.ViewObject.Visibility=True; made.append(o)
    print("  %-22s at (%.1f,%.1f) vol %.2f cm3"%(name,x,y,s.Volume/1000))
grp=None
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and any(m.Name=="P2b_RodClevisBlock" for m in gg.Group):
        grp=gg; break
if grp: grp.addObjects(made); print("added to group %s"%grp.Name)
doc.recompute(); doc.save()
print("grip length: cheek %.1f + eye 12.0 + cheek %.1f = %.1f mm, double shear both ends"%(8.4,8.4,28.8))
