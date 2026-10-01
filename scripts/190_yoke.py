# -*- coding: utf-8 -*-
"""Yoke rebuilt for the C-Beam. It now bolts into the INBOARD slots of BOTH wings
(X=-30 and X=+30) instead of three bolts in one line -- a genuinely better joint, and
the C-Beam's channel void at X -20..+20 gives the yoke's arm free space."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
YZ=(76.,88.); RY0=58.0; BOLTS=(-30.,30.); BY=(70.,112.)
yk=cz(40.,*YZ)
yk=yk.fuse(bar((0.,0.),(0.,70.),34.,38.,*YZ))
yk=yk.fuse(bx(-40.,40.,RY0,124.,*YZ)).removeSplitter()
yk=yk.cut(cz(5.15,YZ[0]-2,YZ[1]+2))
for x in BOLTS:
    for y in BY: yk=yk.cut(cz(2.6,YZ[0]-1,YZ[1]+1,x,y))
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
b=yk.BoundBox
print("P1 yoke X %.0f..%.0f Y %.0f..%.0f Z %.0f..%.0f  %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,yk.Volume/1000))
print("  4 M5 into the wing inboard slots at X %s, Y %s -- a rectangle, not a line"%(BOLTS,BY))
doc.recompute(); doc.save()
