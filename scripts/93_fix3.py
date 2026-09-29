# -*- coding: utf-8 -*-
"""Three real interpenetrations my SKIP list hid:
 1 P2a hinge plate ran THROUGH the 2020 -> reroute its arm anterior of X=-10
 2 P2b clevis arm's end cap reached X=-1 -> start the arm further posterior
 3 the socket bore stopped 14 mm short of its own front face, so the 2020 stabbed
   into solid material instead of sliding in -> open the bore and lengthen the 2020"""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
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
SH20_X=(-10.0,10.0); SH20_Z=(121.0,141.0); SH20_Y=(-300.0,-45.0)   # 2020 lengthened
HINGE_Z=(122.0,134.0); D0=(32.0,-67.5)
ROD_Z=(128.0,144.0); EAR_Z=((120.0,128.0),(144.0,152.0))
# ---- 1. shank 2020, longer so it actually engages the socket ----
s=bx(*SH20_X,*SH20_Y,*SH20_Z)
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4))
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4,SH20_Z[1]+1))
s=s.cut(bx(SH20_X[0]-1,SH20_X[0]+4,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(bx(SH20_X[1]-4,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.0,131.0))
assert len(s.Solids)==1 and s.isClosed()
doc.getObject("A4_Shank2020_VSlot").Shape=s
# ---- 2. hinge plate: arm kept anterior of the 2020 face (X=-10) ----
hp=cz(28.0,*HINGE_Z).fuse(bar((-20.0,-18.0),(-30.0,-125.0),10.0,10.0,*HINGE_Z))
hp=hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp=hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-55.,-80.,-108.): hp=hp.cut(Part.makeCylinder(2.6,44.,V(-40.,y,128.),V(1,0,0)))
assert len(hp.Solids)==1 and hp.isClosed()
doc.getObject("P2a_KneeHingePlate").Shape=hp
# ---- 3. rod clevis: arm starts further posterior so its cap clears X=10 ----
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
import json
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json")); S=K["samples"]; XE=K["XE"]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,sn=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*sn,p[0]*sn+p[1]*c)
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(sm(t)["carr"]-rot2(D0,t)[1],XE-rot2(D0,t)[0]))-t for t in ts])
b0,b1=min(bs)-18.,max(bs)+18.
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
cb=bx(10.3,26.0,D0[1]-30.0,D0[1]+30.0,SH20_Z[0],EAR_Z[0][1])
cb=cb.fuse(bar((26.0,D0[1]),D0,13.0,18.0,EAR_Z[0][0],EAR_Z[1][1]))
cb=cb.cut(cz(15.5,*ROD_Z,*D0)).cut(sector_at(D0,52.0,b0,b1,*ROD_Z,r_in=15.5))
cb=cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-20.,20.): cb=cb.cut(Part.makeCylinder(2.6,44.,V(-4.,D0[1]+dy,131.),V(1,0,0)))
assert len(cb.Solids)==1 and cb.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb
# ---- 4. socket: bore opened through its own front face ----
hs=bx(-20.,20.,-318.,-248.,SH20_Z[0]-9,SH20_Z[1]+9)
hs=hs.cut(bx(SH20_X[0]-0.3,SH20_X[1]+0.3,-319.,-246.,SH20_Z[0]-0.3,SH20_Z[1]+0.3))
hs=hs.fuse(bx(-30.,30.,-318.,-208.,68.,78.))
hs=hs.fuse(bx(-8.,8.,-314.,-218.,76.,SH20_Z[0]-6))
for xa,xb in ((14.,22.),(-22.,-14.)): hs=hs.fuse(bx(xa,xb,-310.,-222.,70.,SH20_Z[0]-6))
hs=hs.cut(bx(-3.,3.,-292.,-270.,SH20_Z[1]+3,SH20_Z[1]+11))
for x,y in [(-22.,-233.),(22.,-233.),(-22.,-293.),(22.,-293.)]: hs=hs.cut(cz(3.2,67.,79.,x,y))
assert len(hs.Solids)==1 and hs.isClosed()
doc.getObject("P6_ShankSocket").Shape=hs
doc.recompute()
print("2020 now Y %.0f..%.0f ; socket bore open to Y=-246"%SH20_Y)
print("telescoping engagement: %.0f mm, travel reserve %.0f mm"%(-248.0-SH20_Y[0]+0.0+(-1)*0+ (248-300)*-1 -52+52, 319-300))
