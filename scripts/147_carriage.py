# -*- coding: utf-8 -*-
"""P3 carriage rebuilt: V-wheels on the rail's X-face slots (nothing below Z=86, so it
never meets the yoke), a mount plate for the SFU1620 nut flange, and the rod ear dropped
to Z 108..140 now that the screw is no longer stacked under the rod pivot."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
s0=sm(0.0)["carr"]
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
cs=unwrap([math.degrees(math.atan2(rot2(D0,q)[1]-sm(q)["carr"],rot2(D0,q)[0]-XE)) for q in ts])
MARG=5.0; c0,c1=min(cs)-MARG,max(cs)+MARG
ZM=124.0; SLOT_Z=(116.4,131.6); POCK=13.0; BAR_R=7.6; R_OUT=40.0; U_LO,U_HI=6.0,33.0
EAR=(108.0,140.0); TOP=(108.0,120.0); SCR_X,SCR_Z=-18.0,117.0
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()
ca=bx(-42.,78.,s0-36.,s0+36.,*TOP)                              # top plate
ca=ca.fuse(bx(2.,10.,s0-36.,s0+36.,92.,108.))                   # anterior wheel cheek
ca=ca.fuse(bx(70.,78.,s0-36.,s0+36.,92.,108.))                  # posterior wheel cheek
for xa,xb in ((-2.,12.),(68.,82.)):                             # 4 V-wheels, OD 24 at Z=98
    for dy in (-24.,24.): ca=ca.fuse(cx(12.,xa,xb,s0+dy,98.))
ca=ca.fuse(bx(-42.,6.,74.,84.,93.,141.))                        # ball-nut mount plate
ca=ca.fuse(cz(17.,*EAR,XE,s0)).removeSplitter()                 # rod ear
ca=ca.cut(cy(9.0,s0-40.,s0+40.,SCR_X,SCR_Z))                    # screw channel
ca=ca.cut(cy(14.5,73.,85.,SCR_X,SCR_Z))                         # pass the nut body
for k in range(4):                                              # nut flange bolts, PCD 38
    a=math.radians(45+90*k)
    ca=ca.cut(cy(3.3,73.,85.,SCR_X+19.*math.cos(a),SCR_Z+19.*math.sin(a)))
ca=ca.cut(relief((XE,s0),c0,c1))
ca=ca.cut(cz(4.1,106.,146.,XE,s0))                              # rod pivot bolt
assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"P3 solids=%d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
b=ca.BoundBox
print("P3 carriage X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000))
print("  rod ear Z %.0f..%.0f, slot %.1f..%.1f, cheeks %.1f / %.1f mm"%(
    EAR[0],EAR[1],SLOT_Z[0],SLOT_Z[1],SLOT_Z[0]-EAR[0],EAR[1]-SLOT_Z[1]))
print("  nothing below Z=86 (wheel OD) -> clear of the yoke at Z 76..88")
doc.recompute(); doc.save()
