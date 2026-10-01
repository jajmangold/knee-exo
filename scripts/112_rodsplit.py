# -*- coding: utf-8 -*-
"""The rod is really 3 parts: 2020 bar + 2 printed housings (2x 608 each).
P4 had both housings integral AND P8 duplicated one of them statically.
Split properly so all three share the rod's transform."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"]); ROD_Z=tuple(K["rod_z"])
ROD_Z=(128.0,144.0); BAR_Z=(126.0,146.0); INSET=28.0
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0); D=(D0[0],D0[1]); C=(XE,s0["carr"])
L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L; nx,ny=-uy,ux
print("rod pin-to-pin %.1f mm, axis (%.3f,%.3f)"%(L,ux,uy))
def housing(P,sgn):
    """r14 body with two 608 seats, socketed over the 2020 (sgn=+1 socket toward the far pin)"""
    h=cz(14.0,*ROD_Z,*P).cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*P))
    h=h.cut(cz(11.1,ROD_Z[0]+1.0,ROD_Z[0]+8.0,*P))
    h=h.cut(cz(11.1,ROD_Z[1]-8.0,ROD_Z[1]-1.0,*P))
    a=(P[0]+ux*sgn*8.0, P[1]+uy*sgn*8.0); b=(P[0]+ux*sgn*30.0, P[1]+uy*sgn*30.0)
    def seg(w,z0,z1):
        pts=[(a[0]+nx*w,a[1]+ny*w),(b[0]+nx*w,b[1]+ny*w),(b[0]-nx*w,b[1]-ny*w),(a[0]-nx*w,a[1]-ny*w)]
        wi=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
        return Part.Face(wi).extrude(V(0,0,z1-z0))
    h=h.fuse(seg(14.0,BAR_Z[0]-2,BAR_Z[1]+2))
    a2=(P[0]+ux*sgn*11.0,P[1]+uy*sgn*11.0); b2=(P[0]+ux*sgn*32.0,P[1]+uy*sgn*32.0)
    pts=[(a2[0]+nx*10.2,a2[1]+ny*10.2),(b2[0]+nx*10.2,b2[1]+ny*10.2),
         (b2[0]-nx*10.2,b2[1]-ny*10.2),(a2[0]-nx*10.2,a2[1]-ny*10.2)]
    wi=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
    h=h.cut(Part.Face(wi).extrude(V(0,0,BAR_Z[1]-BAR_Z[0])))
    return h
hD=housing(D,+1); hC=housing(C,-1)
# bar between the sockets
p0=(D[0]+ux*INSET,D[1]+uy*INSET); p1=(C[0]-ux*INSET,C[1]-uy*INSET)
pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),(p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
wi=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
barr=Part.Face(wi).extrude(V(0,0,BAR_Z[1]-BAR_Z[0]))
barr=barr.cut(cz(4.2,BAR_Z[0]-1,BAR_Z[1]+1,(p0[0]+p1[0])/2,(p0[1]+p1[1])/2))
for sh,nm in ((barr,"P4_Rod_8mm"),(hD,"P8_RodEndHousing_PETG"),(hC,"P8b_RodEndHousing_Carriage")):
    assert len(sh.Solids)==1 and sh.isClosed(), "%s %d solids"%(nm,len(sh.Solids))
doc.getObject("P4_Rod_8mm").Shape=barr
doc.getObject("P4_Rod_8mm").Label="P4_Rod_2020"
doc.getObject("P8_RodEndHousing_PETG").Shape=hD
doc.getObject("P8_RodEndHousing_PETG").Placement=FreeCAD.Placement()
o=doc.getObject("P8b_RodEndHousing_Carriage") or doc.addObject("Part::Feature","P8b_RodEndHousing_Carriage")
o.Shape=hC; o.ViewObject.ShapeColor=(0.25,0.60,0.35)
doc.getObject("P8_RodEndHousing_PETG").ViewObject.ShapeColor=(0.25,0.60,0.35)
doc.recompute()
print("bar %.1f cm3 | housing D %.1f | housing C %.1f cm3 (%.0f g PETG each)"
      %(barr.Volume/1000,hD.Volume/1000,hC.Volume/1000,hD.Volume/1000*1.27))
print("bar^hD %.3f  bar^hC %.3f  hD^hC %.3f cm3"
      %(barr.common(hD).Volume/1000, barr.common(hC).Volume/1000, hD.common(hC).Volume/1000))
doc.save()
