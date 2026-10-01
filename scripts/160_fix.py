# -*- coding: utf-8 -*-
"""Three residuals:
 1 HW_JointBolts ran 2 mm past A4's inboard slot into solid extrusion -> stop at Z=98
 2 the clevis pin's nyloc (r=6.9 at X=32) overlapped the clevis base's X=26 edge
   -> base back to X=24, bolt head to X 24..29
 3 the fork web sweeps into the yoke's ARM at high flexion -> cut the swept annular
   sector out of the yoke (the arm still spans 29..99 deg so it stays connected)"""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration under freecadcmd, where no document is
    open yet -- which is why these older build scripts could not be re-run without the GUI.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
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
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
s0=sm(0.0)["carr"]; Dy=D0[1]; zc=104.0; P2A=(-90.,-110.,-125.); P2B=(-70.,-90.)
# ---- 1. bolts ----
bolts=None
for y in P2A:
    bb=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))
    bolts=bb if bolts is None else bolts.fuse(bb)
for y in P2B:
    bolts=bolts.fuse(cx(2.5,-2.,29.,y,zc).fuse(cx(4.6,24.,29.,y,zc)))
doc.getObject("HW_JointBolts").Shape=bolts
print("1. HW_JointBolts: hinge bolts now stop at Z=98 (A4 inboard slot is 94..98)")
# ---- 2. clevis base back to X=24 ----
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
b0,b1=min(bs)-5.,max(bs)+5.
ZM=146.0; SLOT_Z=(138.4,153.6); POCK=13.; BAR_R=7.6; R_OUT=40.; U_LO,U_HI=6.,33.
EAR=(114.,162.)
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()
cb=bx(10.,24.,-97.5,-60.,94.,114.).fuse(bar((26.,Dy),D0,13.,18.,*EAR)).removeSplitter()
cb=cb.cut(relief(D0,b0,b1))
cb=cb.cut(cz(4.1,104.,168.,*D0))
for y in P2B: cb=cb.cut(cx(3.0,8.,28.,y,zc))
assert len(cb.Solids)==1 and cb.isClosed() and cb.isValid(),"P2b solids=%d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
print("2. P2b base X 10..24 (pin nyloc starts at X %.1f -> %.1f mm clear)"%(32.-6.9,32.-6.9-24.))
# ---- 3. yoke relief for the fork web's sweep ----
yk=doc.getObject("P1_KneeYoke"); base=yk.Shape
assert yk.Placement.isIdentity(),"P1 must be at identity"
cut=sector_at((0.,0.),84.0,-106.0,30.0,74.0,90.0,r_in=43.0)
out=base.cut(cut).removeSplitter()
print("3. P1 yoke %.1f -> %.1f cm3 (removed %.2f); solids=%d closed=%s"%(
    base.Volume/1000,out.Volume/1000,(base.Volume-out.Volume)/1000,len(out.Solids),out.isClosed()))
assert len(out.Solids)==1 and out.isClosed() and out.isValid(),"P1 solids=%d"%len(out.Solids)
yk.Shape=out
doc.recompute(); doc.save()
