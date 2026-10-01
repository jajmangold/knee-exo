# -*- coding: utf-8 -*-
"""Restore the rod to the integral form that verified clean, and mark the detailed
printed housings as manufacturing-only (not assembly geometry)."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
ROD_Z=(128.0,144.0); BAR_Z=(126.0,146.0); INSET=28.0
s0=sm(0.0); D=(D0[0],D0[1]); C=(XE,s0["carr"])
L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L; nx,ny=-uy,ux
r=cz(14.0,*ROD_Z,*D).fuse(cz(14.0,*ROD_Z,*C))
p0=(D[0]+ux*INSET,D[1]+uy*INSET); p1=(C[0]-ux*INSET,C[1]-uy*INSET)
pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),(p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
w=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
r=r.fuse(Part.Face(w).extrude(V(0,0,BAR_Z[1]-BAR_Z[0])))
r=r.cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*D)).cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*C))
assert len(r.Solids)==1 and r.isClosed()
o=doc.getObject("P4_Rod_8mm"); o.Placement=FreeCAD.Placement(); o.Shape=r
o.Label="P4_RodAssembly"
for n in ("P8_RodEndHousing_PETG","P8b_RodEndHousing_Carriage"):
    h=doc.getObject(n)
    if h:
        h.Placement=FreeCAD.Placement()
        h.ViewObject.Visibility=False
        h.Label=n.replace("P8","MFG_P8")
print("rod restored integral: %.1f cm3"%(r.Volume/1000))
print("housings hidden (manufacturing detail, geometry duplicated inside the rod)")
doc.recompute(); doc.save()
