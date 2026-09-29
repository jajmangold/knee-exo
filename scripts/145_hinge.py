# -*- coding: utf-8 -*-
"""P2a becomes a FORK straddling the yoke: inner cheek Z 70..76, outer cheek Z 88..94,
web joining them at Y<-45 where the yoke's r=40 disc has ended. The knee pin then works
in DOUBLE shear instead of single -- the varus/valgus weakness flagged earlier.
A4 shank 2020 moves outboard of the outer cheek to Z 94..114."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
SH20_X=(-10.,10.); SH20_Y=(-300.,-45.); SH20_Z=(94.,114.)
IN_Z=(70.,76.); OUT_Z=(88.,94.); PIN_R=5.15
P2A_BOLTS=(-60.,-90.,-120.); P2B_BOLTS=(-55.,-85.)
# ---- A4 shank 2020 at its new Z ----
zc=(SH20_Z[0]+SH20_Z[1])/2
s=bx(*SH20_X,*SH20_Y,*SH20_Z)
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4))     # inboard slot
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4,SH20_Z[1]+1))     # outboard slot
s=s.cut(bx(SH20_X[0]-1,SH20_X[0]+4,SH20_Y[0]-1,SH20_Y[1]+1,zc-3,zc+3))
s=s.cut(bx(SH20_X[1]-4,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,zc-3,zc+3))
s=s.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.,zc))                        # central bore
for y in P2B_BOLTS: s=s.cut(cx(2.6,-12.,12.,y,zc))
assert len(s.Solids)==1 and s.isClosed() and s.isValid(),"A4"
doc.getObject("A4_Shank2020_VSlot").Shape=s
print("A4 shank 2020  Z %.1f..%.1f (was 121..141)  %.1f cm3"%(SH20_Z[0],SH20_Z[1],s.Volume/1000))
# ---- P2a fork ----
inner=bar((0.,0.),(0.,-80.),24.,14.,*IN_Z)
outer=bar((0.,0.),(0.,-130.),24.,14.,*OUT_Z)
web  =bx(-10.,10.,-80.,-45.,IN_Z[0],OUT_Z[1])
hp=inner.fuse(outer).fuse(web).removeSplitter()
hp=hp.cut(cz(PIN_R,IN_Z[0]-2,OUT_Z[1]+2))                             # knee pin bore
for y in P2A_BOLTS: hp=hp.cut(cz(2.6,OUT_Z[0]-1,OUT_Z[1]+1,0.,y))     # M5 into A4's inboard slot
assert len(hp.Solids)==1 and hp.isClosed() and hp.isValid(),"P2a solids=%d"%len(hp.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=hp
b=hp.BoundBox
print("P2a fork  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,hp.Volume/1000))
print("  cheeks %.0f mm (Z %.0f..%.0f) and %.0f mm (Z %.0f..%.0f), yoke %.0f..%.0f between them"%(
    IN_Z[1]-IN_Z[0],IN_Z[0],IN_Z[1],OUT_Z[1]-OUT_Z[0],OUT_Z[0],OUT_Z[1],76.,88.))
# ---- bolts: P2a into A4's inboard slot, P2b into A4's posterior slot ----
bolts=None
for y in P2A_BOLTS:
    bb=cz(2.5,66.,100.,0.,y).fuse(cz(4.6,66.,71.,0.,y))
    bolts=bb if bolts is None else bolts.fuse(bb)
for y in P2B_BOLTS:
    bolts=bolts.fuse(cx(2.5,-2.,30.,y,zc).fuse(cx(4.6,25.,30.,y,zc)))
doc.getObject("HW_JointBolts").Shape=bolts
print("HW_JointBolts: %d M5 (3 hinge-to-2020 along Z, 2 clevis-to-2020 along X)"%(
    len(P2A_BOLTS)+len(P2B_BOLTS)))
doc.recompute(); doc.save()
