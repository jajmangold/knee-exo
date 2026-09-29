# -*- coding: utf-8 -*-
"""P2a back to the bare knee fork -- the tower and its vertical stiffening web go away,
because the rod pivot now lands on the 2020's OUTBOARD face instead of 32 mm above it."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
IN_Z=(70.,76.); OUT_Z=(88.,94.); PIN_R=5.15; FORK_BOLTS=(-90.,-110.,-125.)
p =bar((0.,0.),(0.,-80.),24.,14.,*IN_Z)
p =p.fuse(bar((0.,0.),(0.,-135.),24.,14.,*OUT_Z))
p =p.fuse(bx(-10.,10.,-80.,-45.,IN_Z[0],OUT_Z[1])).removeSplitter()
p =p.cut(cz(PIN_R,IN_Z[0]-2,OUT_Z[1]+2))
for y in FORK_BOLTS: p=p.cut(cz(2.6,OUT_Z[0]-1,OUT_Z[1]+1,0.,y))
assert len(p.Solids)==1 and p.isClosed() and p.isValid(),"P2a solids=%d"%len(p.Solids)
was=doc.getObject("P2a_KneeHingePlate").Shape.Volume/1000
doc.getObject("P2a_KneeHingePlate").Shape=p
doc.getObject("P2a_KneeHingePlate").Label="P2a_KneeHingeFork"
b=p.BoundBox
print("P2a bare fork  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
print("  %.1f cm3  (was %.1f with the tower+web -> %.1f cm3 back out)"%(
    p.Volume/1000,was,was-p.Volume/1000))
doc.recompute(); doc.save()
