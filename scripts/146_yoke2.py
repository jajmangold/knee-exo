# -*- coding: utf-8 -*-
"""P1 yoke moves from the rail's OUTBOARD face (Z 108..120) to its INBOARD face
(Z 76..88) -- same 3-slot 60 mm face, same T-nut pattern, same strength, but it lands
in the 36 mm of empty space that was already there instead of adding to the stack.
HW_PinB_10 (the knee pin) did not exist in the document at all; created here."""
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
YOKE_Z=(76.0,88.0); RAIL_X=(10.0,70.0); PIN_R=5.15
yk=cz(40.0,*YOKE_Z)
yk=yk.fuse(bar((0.,0.),(40.,70.),34.,30.,*YOKE_Z))
yk=yk.fuse(bx(16.0,64.0,46.0,112.0,*YOKE_Z)).removeSplitter()
# keep the yoke inboard of the carriage V-wheel paths (X<12 and X>68) for Y>44
yk=yk.cut(bx(-45.0,16.0,44.0,120.0,YOKE_Z[0]-2,YOKE_Z[1]+2))
yk=yk.cut(bx(64.0,85.0,44.0,120.0,YOKE_Z[0]-2,YOKE_Z[1]+2))
yk=yk.cut(cz(PIN_R,YOKE_Z[0]-2,YOKE_Z[1]+2))                       # knee pin bore
NBOLT=[]
for x in (20.,40.,60.):
    for y in (58.,100.):
        yk=yk.cut(cz(2.6,YOKE_Z[0]-1,YOKE_Z[1]+1,x,y)); NBOLT.append((x,y))
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
b=yk.BoundBox
print("P1 yoke  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,yk.Volume/1000))
print("  %d M5 T-nuts into the rail's inboard face at X 20/40/60, Y 58/100"%len(NBOLT))
# ---- HW_PinB_10: the knee pin, spanning the fork in double shear ----
p=cz(5.0,68.0,96.0).fuse(cz(8.0,96.0,102.0)).fuse(cz(8.5,62.0,68.0)).removeSplitter()
assert len(p.Solids)==1 and p.isClosed(),"PinB"
o=doc.getObject("HW_PinB_10") or doc.addObject("Part::Feature","HW_PinB_10")
o.Shape=p; o.Label="HW_PinB_10_KneePin"; o.ViewObject.Visibility=True
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="B_Shank": gg.addObject(o)
print("HW_PinB_10 M10 knee pin Z 62..102, shank 68..96 spans the fork (24 mm, double shear)")
print("  clearance to the knee at Z=62: %.1f mm (knee radius 52 on the pin axis)"%(62.0-52.0))
doc.recompute(); doc.save()
