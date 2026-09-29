# -*- coding: utf-8 -*-
"""Two changes that open the knee up for a proper static shroud:
  A4's proximal end -45 -> -70. Its inner corner swings at r=45 today, leaving only
  3.88 mm above the belt. At -70 that becomes r=70.7. Nothing needs the extra length --
  the fork bolts are at Y -90..-125 and the socket engages at Y -208..-318.
  The yoke gains a proximal lobe out to r=47 so the shroud legs have something to land on
  (it stays at r=30 on the distal side, where the belt wraps)."""
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
SH_X=(-10.,10.); SH_Y=(-300.,-70.); SH_Z=(94.,114.); zc=104.
P2B=(-70.,-90.)
s=bx(*SH_X,*SH_Y,*SH_Z)
s=s.cut(bx(-3,3,SH_Y[0]-1,SH_Y[1]+1,SH_Z[0]-1,SH_Z[0]+4))
s=s.cut(bx(-3,3,SH_Y[0]-1,SH_Y[1]+1,SH_Z[1]-4,SH_Z[1]+1))
s=s.cut(bx(SH_X[0]-1,SH_X[0]+4,SH_Y[0]-1,SH_Y[1]+1,zc-3,zc+3))
s=s.cut(bx(SH_X[1]-4,SH_X[1]+1,SH_Y[0]-1,SH_Y[1]+1,zc-3,zc+3))
s=s.cut(cy(4.2,SH_Y[0]-1,SH_Y[1]+1,0.,zc))
assert len(s.Solids)==1 and s.isClosed(),"A4"
doc.getObject("A4_Shank2020_VSlot").Shape=s
print("A4 now Y %.0f..%.0f ; inner corner radius %.1f mm (was %.1f)"%(
    SH_Y[0],SH_Y[1],math.hypot(10.,70.),math.hypot(10.,45.)))
# ---- yoke: proximal lobe to r=47, distal stays r=30 ----
YZ=(76.,88.); PIN_R=6.15
yk=cz(30.,*YZ)
yk=yk.fuse(cz(47.,*YZ).common(bx(-48.,48.,-9.,48.,YZ[0]-1,YZ[1]+1)))   # proximal lobe
yk=yk.fuse(bar((0.,0.),(0.,70.),28.,30.,*YZ))
yk=yk.fuse(bx(-30.,30.,58.,124.,*YZ)).removeSplitter()
yk=yk.cut(cz(PIN_R,YZ[0]-2,YZ[1]+2))
for x in (-20.,0.,20.):
    for y in (70.,112.): yk=yk.cut(cz(2.6,YZ[0]-1,YZ[1]+1,x,y))
hx,hy=25.*math.cos(math.radians(-60)),25.*math.sin(math.radians(-60))
yk=yk.cut(bx(hx-6.,hx+6.,hy-4.,hy+4.,YZ[1]-4.,YZ[1]+0.5))
for a in (175.,5.):                                                     # shroud leg bosses
    lx,ly=44.75*math.cos(math.radians(a)),44.75*math.sin(math.radians(a))
    yk=yk.cut(cz(2.1,YZ[1]-8.,YZ[1]+1,lx,ly))
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
b=yk.BoundBox
print("P1 yoke X %.1f..%.1f Y %.1f..%.1f Z %.0f..%.0f  %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,yk.Volume/1000))
print("  proximal lobe r=47 over Y>-9 gives the shroud legs at 175/5 deg a landing")
print("  (the lobe is at Z 76..88, the belt at Z 96..126 -> no interaction)")
doc.recompute(); doc.save()
