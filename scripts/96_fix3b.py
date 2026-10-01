# -*- coding: utf-8 -*-
"""a) carriage screw bore was cut along Z; the screw runs along Y -> re-cut along Y
   b) screw at Z=115 (r8 -> bottom 107) dipped 1 mm into the rail face at Z=108 -> Z=117
   c) hinge-plate disc r=28 clipped the rod (closest approach 24.2 mm) -> r=22, arm reshaped"""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
CAR_Z=(108.0,122.0); EAR_Z=((120.0,128.0),(144.0,152.0)); ROD_Z=(128.0,144.0)
SCREW_R=8.0; SCREW_Z=117.0; HINGE_Z=(122.0,134.0)
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
cs=unwrap([math.degrees(math.atan2(rot2(D0,t)[1]-sm(t)["carr"],rot2(D0,t)[0]-XE)) for t in ts])
c0,c1=min(cs)-15.,max(cs)+15.
# ---- a) carriage with a Y-axis screw bore ----
s0=sm(0.0)["carr"]
c=bx(4.,76.,s0-36.,s0+36.,*CAR_Z).fuse(cz(17.,EAR_Z[0][0],EAR_Z[1][1],XE,s0))
c=c.cut(cz(15.5,*ROD_Z,XE,s0)).cut(sector_at((XE,s0),52.,c0,c1,*ROD_Z,r_in=15.5))
c=c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s0))
c=c.cut(cy(SCREW_R+1.5, s0-40., s0+40., XE, SCREW_Z))      # <-- along Y now
assert len(c.Solids)==1 and c.isClosed(),"carriage %d"%len(c.Solids)
doc.getObject("P3_Carriage").Shape=c
# ---- b) screw + motor raised clear of the rail face ----
sb=doc.getObject("A2_BallScrew_SFU1620").Shape.BoundBox
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCREW_R,sb.YMin,sb.YMax,XE,SCREW_Z)
mb=doc.getObject("A3_Motor_6374").Shape.BoundBox
doc.getObject("A3_Motor_6374").Shape=cy(31.5,mb.YMin,mb.YMax,XE,SCREW_Z)
# ---- c) hinge plate: smaller disc, arm reshaped to stay anterior of X=-10 ----
hp=cz(22.0,*HINGE_Z).fuse(bar((-16.0,-13.0),(-30.0,-125.0),9.0,9.0,*HINGE_Z))
hp=hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp=hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-55.,-80.,-108.): hp=hp.cut(Part.makeCylinder(2.6,44.,V(-40.,y,128.),V(1,0,0)))
assert len(hp.Solids)==1 and hp.isClosed(),"plate %d"%len(hp.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=hp
doc.recompute()
Zsec=12.0*18.0**2/6.0
print("hinge plate arm 18 mm wide x 12 mm: %.1f MPa at 22.4 N.m -> SF %.1f on 276 MPa yield"
      %(22400/Zsec, 276/(22400/Zsec)))
print("screw Z=%.0f (r%.0f -> bottom %.0f, rail face 108)"%(SCREW_Z,SCREW_R,SCREW_Z-SCREW_R))
doc.save()
