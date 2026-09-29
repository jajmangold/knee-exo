# -*- coding: utf-8 -*-
"""Bar inset 28 mm vs r=14 housings left a 14 mm gap -> 3 loose solids.
Overlap them so the rod is one body."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
ROD_Z=(128.0,144.0); BAR_Z=(126.0,146.0); INSET=6.0
s0=sm(0.0)["carr"]; D=(D0[0],D0[1]); C=(XE,s0)
L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L; nx,ny=-uy,ux
r=cz(14.0,*ROD_Z,*D).fuse(cz(14.0,*ROD_Z,*C))
p0=(D[0]+ux*INSET,D[1]+uy*INSET); p1=(C[0]-ux*INSET,C[1]-uy*INSET)
pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),(p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
w=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
r=r.fuse(Part.Face(w).extrude(V(0,0,BAR_Z[1]-BAR_Z[0]))).removeSplitter()
r=r.cut(cz(4.1,124.0,148.0,*D)).cut(cz(4.1,124.0,148.0,*C))
print("rod: solids=%d closed=%s valid=%s vol=%.1f cm3"%(len(r.Solids),r.isClosed(),r.isValid(),r.Volume/1000))
assert len(r.Solids)==1 and r.isClosed()
doc.getObject("P4_Rod_8mm").Shape=r
doc.recompute(); doc.save()
