# -*- coding: utf-8 -*-
"""Clevis slots were 16 mm tall (sized for a bare pin eye) but the rod is a 20 mm 2020,
so its socket cannot enter. Open both slots to 20 mm; ears go 8 -> 6 mm.
6 mm ear on an 8 mm pin = 984/(8*6) = 20.5 MPa bearing - fine in 6061."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
SLOT_Z=(125.8,146.2)          # was (128,144)
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(sm(t)["carr"]-rot2(D0,t)[1],XE-rot2(D0,t)[0]))-t for t in ts])
cs=unwrap([math.degrees(math.atan2(rot2(D0,t)[1]-sm(t)["carr"],rot2(D0,t)[0]-XE)) for t in ts])
b0,b1=min(bs)-18.,max(bs)+18.; c0,c1=min(cs)-15.,max(cs)+15.
# open the clevis slots
cb=doc.getObject("P2b_RodClevisBlock").Shape
cb=cb.cut(cz(15.7,*SLOT_Z,*D0)).cut(sector_at(D0,52.,b0,b1,*SLOT_Z,r_in=15.7))
assert len(cb.Solids)==1 and cb.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb
s0=sm(0.0)["carr"]
ca=doc.getObject("P3_Carriage").Shape
ca=ca.cut(cz(15.7,*SLOT_Z,XE,s0)).cut(sector_at((XE,s0),52.,c0,c1,*SLOT_Z,r_in=15.7))
assert len(ca.Solids)==1 and ca.isClosed()
doc.getObject("P3_Carriage").Shape=ca
print("slots opened to Z %.1f..%.1f (%.1f mm); ears now %.1f mm"%(SLOT_Z[0],SLOT_Z[1],SLOT_Z[1]-SLOT_Z[0],SLOT_Z[0]-120.0))
print("clevis %.1f cm3   carriage %.1f cm3"%(cb.Volume/1000,ca.Volume/1000))
doc.recompute(); doc.save()
