# -*- coding: utf-8 -*-
"""Re-cut P2b and P3 for the SI8 rod ends.

Slot 20.4 -> 15.2 mm tall, pocket r 15.7 -> 13.0. Instead of a constant-angle fan
(which was sized for the old r=14 housings and under-cuts near the pocket) the relief
is the EXACT swept envelope of the r=7 barrel: sector(theta_min..theta_max) fused with
the barrel cylinder at each extreme. Any intermediate angle's overhang lies inside one
of those two, so 2 fuses give an exact envelope -- no 27-shape union."""
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
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
cs=unwrap([math.degrees(math.atan2(rot2(D0,q)[1]-sm(q)["carr"],rot2(D0,q)[0]-XE)) for q in ts])
MARG=5.0
b0,b1=min(bs)-MARG,max(bs)+MARG; c0,c1=min(cs)-MARG,max(cs)+MARG

ZM=140.0; SLOT_Z=(132.4,147.6); POCK=13.0
BAR_R=7.6; U_LO,U_HI=6.0,33.0; R_OUT=40.0        # barrel r=7 +0.6 clearance
SH20_X=(-10.,10.); EAR=(120.,156.); CAR_Z=(108.,122.); SCREW_Z=117.
BZ=124.0; SHARED=(-55.,-85.); Dy=D0[1]; s0=sm(0.)["carr"]

def relief(c,a0,a1):
    """exact swept envelope of the rod-end barrel about pivot c, angles a0..a1"""
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c)
    s=s.fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()

# --- clevis P2b ---
cb=bx(10.,26.,-97.5,-45.,121.,128.).fuse(bar((26.,Dy),D0,13.,18.,*EAR))
cb=cb.cut(relief(D0,b0,b1))
cb=cb.cut(cz(4.1,118.,158.,*D0))
for y in SHARED: cb=cb.cut(cx(3.0,8.,30.,y,BZ))
cb=cb.cut(bx(-5.,29.,-45.,20.,115.,160.))
print("P2b solids=%d closed=%s vol=%.2f cm3  cheeks %.1f / %.1f mm"%(
    len(cb.Solids),cb.isClosed(),cb.Volume/1000,SLOT_Z[0]-EAR[0],EAR[1]-SLOT_Z[1]))
assert len(cb.Solids)==1 and cb.isClosed() and cb.isValid(),"P2b solids=%d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb

# --- carriage P3 ---
ca=bx(4.,76.,s0-36.,s0+36.,*CAR_Z).fuse(cz(17.,*EAR,XE,s0))
ca=ca.cut(relief((XE,s0),c0,c1))
ca=ca.cut(cz(4.1,118.,158.,XE,s0)).cut(cy(8.6,s0-40.,s0+40.,XE,SCREW_Z))
print("P3  solids=%d closed=%s vol=%.2f cm3  boss wall %.1f mm"%(
    len(ca.Solids),ca.isClosed(),ca.Volume/1000,17.0-POCK))
assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"P3 solids=%d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
doc.recompute(); doc.save()
print("slot %.1f..%.1f (%.1f mm) for a 12 mm eye; swing %.1f..%.1f (clevis) %.1f..%.1f (carriage)"%(
    SLOT_Z[0],SLOT_Z[1],SLOT_Z[1]-SLOT_Z[0],b0,b1,c0,c1))
