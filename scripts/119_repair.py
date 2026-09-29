# -*- coding: utf-8 -*-
"""STOP the animation first, reset all placements, then rebuild the parts whose
geometry got an animation pose baked into it."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
g=globals()
t=g.get("_kx_timer")
if t is not None:
    try: t.stop(); print("animation timer stopped")
    except Exception as e: print("timer stop:",e)
doc=FreeCAD.getDocument("KneeExo_v4")
for o in doc.Objects:
    if o.TypeId=="Part::Feature": o.Placement=FreeCAD.Placement()
doc.recompute()
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
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
cs=unwrap([math.degrees(math.atan2(rot2(D0,q)[1]-sm(q)["carr"],rot2(D0,q)[0]-XE)) for q in ts])
b0,b1=min(bs)-18.,max(bs)+18.; c0,c1=min(cs)-15.,max(cs)+15.
SLOT_Z=(125.8,146.2); EAR=(120.0,152.0); CAR_Z=(108.0,122.0); SCREW_Z=117.0
Dy=D0[1]; s0=sm(0.0)["carr"]
# ---- P2b ----
cb=bx(10.0,26.0,Dy-30.0,Dy+30.0,121.0,128.0)
cb=cb.fuse(bar((26.0,Dy),D0,13.0,18.0,*EAR))
cb=cb.cut(cz(15.7,*SLOT_Z,*D0)).cut(sector_at(D0,52.0,b0,b1,*SLOT_Z,r_in=15.7))
cb=cb.cut(cz(4.1,118.0,154.0,*D0))
for y in (-55.0,-85.0): cb=cb.cut(cx(3.0,8.0,30.0,y,131.0))
cb=cb.cut(bx(-5.0,29.0,-45.0,20.0,115.0,160.0))
assert len(cb.Solids)==1 and cb.isClosed(),"P2b %d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
# ---- P3 carriage ----
ca=bx(4.0,76.0,s0-36.0,s0+36.0,*CAR_Z).fuse(cz(17.0,*EAR,XE,s0))
ca=ca.cut(cz(15.7,*SLOT_Z,XE,s0)).cut(sector_at((XE,s0),52.0,c0,c1,*SLOT_Z,r_in=15.7))
ca=ca.cut(cz(4.1,118.0,154.0,XE,s0)).cut(cy(9.5,s0-40.0,s0+40.0,XE,SCREW_Z))
assert len(ca.Solids)==1 and ca.isClosed(),"P3 %d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
# ---- P4 integral rod ----
ROD_Z=(128.0,144.0); BAR_Z=(126.0,146.0); INSET=28.0
D=(D0[0],D0[1]); C=(XE,s0)
L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L; nx,ny=-uy,ux
r=cz(14.0,*ROD_Z,*D).fuse(cz(14.0,*ROD_Z,*C))
p0=(D[0]+ux*INSET,D[1]+uy*INSET); p1=(C[0]-ux*INSET,C[1]-uy*INSET)
pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),(p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
w=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
r=r.fuse(Part.Face(w).extrude(V(0,0,BAR_Z[1]-BAR_Z[0])))
r=r.removeSplitter()
r=r.cut(cz(4.1,124.0,148.0,*D)).cut(cz(4.1,124.0,148.0,*C))
print("rod solids=%d closed=%s vol=%.1f"%(len(r.Solids),r.isClosed(),r.Volume/1000))
doc.getObject("P4_Rod_8mm").Shape=r
for n in ("P2b_RodClevisBlock","P3_Carriage","P4_Rod_8mm"):
    s=doc.getObject(n).Shape; bb=s.BoundBox
    print("  %-24s X[%7.1f,%7.1f] Y[%7.1f,%7.1f] vol %6.1f"%(n,bb.XMin,bb.XMax,bb.YMin,bb.YMax,s.Volume/1000))
doc.recompute(); doc.save()
