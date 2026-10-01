# -*- coding: utf-8 -*-
"""Coherent rebuild of the shank subassembly. Key change: the shared through-bolts move
from Z=131 to Z=124, below the rod housing (Z 128..144), which was the only free band --
the housing occupies Y -81.5..-53.5 so there isn't room to dodge it in Y."""
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
b0,b1=min(bs)-24.,max(bs)+24.; c0,c1=min(cs)-20.,max(cs)+20.
SH20_X=(-10.,10.); SH20_Y=(-300.,-45.); SH20_Z=(121.,141.)
SLOT_Z=(125.8,146.2); EAR=(120.,152.); CAR_Z=(108.,122.); SCREW_Z=117.
HINGE_Z=(122.,134.); BZ=124.0; TZ=131.0            # shared-bolt Z, T-nut Z
SHARED=(-55.,-85.); TNUT=(-115.,); Dy=D0[1]; s0=sm(0.)["carr"]
# --- 2020 ---
s=bx(*SH20_X,*SH20_Y,*SH20_Z)
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4))
s=s.cut(bx(-3,3,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4,SH20_Z[1]+1))
s=s.cut(bx(SH20_X[0]-1,SH20_X[0]+4,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(bx(SH20_X[1]-4,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,128,134))
s=s.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.,131.))
for y in SHARED: s=s.cut(cx(2.6,-12.,12.,y,BZ))
assert len(s.Solids)==1 and s.isClosed(),"A4"
doc.getObject("A4_Shank2020_VSlot").Shape=s
# --- hinge plate ---
hp=cz(22.,*HINGE_Z).fuse(bx(-28.,-10.,-130.,-10.,*HINGE_Z))
hp=hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp=hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in SHARED: hp=hp.cut(cx(2.6,-30.,-8.,y,BZ))
for y in TNUT:   hp=hp.cut(cx(2.6,-30.,-8.,y,TZ))
assert len(hp.Solids)==1 and hp.isClosed(),"P2a"
doc.getObject("P2a_KneeHingePlate").Shape=hp
# --- clevis ---
cb=bx(10.,26.,-97.5,-45.,121.,128.).fuse(bar((26.,Dy),D0,13.,18.,*EAR))
cb=cb.cut(cz(15.7,*SLOT_Z,*D0)).cut(sector_at(D0,60.,b0,b1,*SLOT_Z,r_in=15.7))
cb=cb.cut(cz(4.1,118.,154.,*D0))
for y in SHARED: cb=cb.cut(cx(3.0,8.,30.,y,BZ))
cb=cb.cut(bx(-5.,29.,-45.,20.,115.,160.))
assert len(cb.Solids)==1 and cb.isClosed(),"P2b"
doc.getObject("P2b_RodClevisBlock").Shape=cb
# --- carriage ---
ca=bx(4.,76.,s0-36.,s0+36.,*CAR_Z).fuse(cz(17.,*EAR,XE,s0))
ca=ca.cut(cz(15.7,*SLOT_Z,XE,s0)).cut(sector_at((XE,s0),60.,c0,c1,*SLOT_Z,r_in=15.7))
ca=ca.cut(cz(4.1,118.,154.,XE,s0)).cut(cy(9.5,s0-40.,s0+40.,XE,SCREW_Z))
assert len(ca.Solids)==1 and ca.isClosed(),"P3"
doc.getObject("P3_Carriage").Shape=ca
# --- bolts ---
bolts=None
for y in SHARED:
    b=cx(2.5,-34.,25.7,y,BZ).fuse(cx(4.6,-34.,-29.,y,BZ))
    bolts=b if bolts is None else bolts.fuse(b)
for y in TNUT:
    bolts=bolts.fuse(cx(2.5,-34.,-6.,y,TZ).fuse(cx(4.6,-34.,-29.,y,TZ)))
doc.getObject("HW_JointBolts").Shape=bolts
doc.recompute()
print("rebuilt: shared bolts Z=%.0f (rod housing is Z 128..144), T-nut Z=%.0f"%(BZ,TZ))
print("fans widened to r=60, bearings %.0f..%.0f (clevis) / %.0f..%.0f (carriage)"%(b0,b1,c0,c1))
doc.save()
