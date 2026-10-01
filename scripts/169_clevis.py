# -*- coding: utf-8 -*-
"""New P2b: a low flat clevis on the 2020's OUTBOARD face (Z=114). The rod pivot drops
from Z=146 to Z=130, so the rod is skewed 6.7 deg and runs 153.77 mm instead of 152.71.
The planar pivot separation is unchanged, so the kinematics are identical.

Because the plate now lies in XY, the 25.4 N.m from the 32 mm X offset is IN-plane
(bolt shear) instead of prying, and the residual prying is only 20.6 N.m spread over a
70 mm bolt span. The relief is the swept envelope of a TILTED barrel."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration when no document is open, which
    surfaces from freecadcmd as the unhelpful "<unknown exception data>" -- and is why these
    older build scripts could not be re-run without the GUI at all.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace(chr(92), "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
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
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
b0,b1=min(bs)-5.,max(bs)+5.
ZM_S,ZM_C=130.0,148.0; PLANAR=152.71; TAN=(ZM_C-ZM_S)/PLANAR
SLOT=(123.0,141.5); EAR=(114.0,150.0); BASE_Z=(114.0,123.0)
POCK=13.; BAR_R=7.6; R_OUT=40.; U_LO,U_HI=6.,33.
BOLTS=(-50.,-85.,-120.); Dy=D0[1]
print("skew %.2f deg, 3D rod length %.2f mm (planar %.2f unchanged)"%(
    math.degrees(math.atan(TAN)),math.hypot(PLANAR,ZM_C-ZM_S),PLANAR))
def relief(c,zm,a0,a1):
    s=cz(POCK,*SLOT,*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT))
    m=math.sqrt(1.0+TAN*TAN)
    for a in (a0,a1):
        ca,sa=math.cos(math.radians(a)),math.sin(math.radians(a))
        d=(ca/m,sa/m,TAN/m)
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,zm+d[2]*U_LO),V(*d)))
    return s.removeSplitter()
cb=bx(-8.,16.,-125.,-45.,*BASE_Z)                       # bolt pad on the outboard face
cb=cb.fuse(bar((16.,Dy),D0,12.,20.,114.,141.))          # web out to the pivot
cb=cb.fuse(cz(20.,*EAR,*D0)).removeSplitter()           # clevis boss
cb=cb.cut(relief(D0,ZM_S,b0,b1))
cb=cb.cut(cz(4.1,112.,156.,*D0))
for y in BOLTS: cb=cb.cut(cz(2.6,113.,124.,0.,y))
assert len(cb.Solids)==1 and cb.isClosed() and cb.isValid(),"P2b solids=%d"%len(cb.Solids)
o=doc.getObject("P2b_RodClevisBlock") or doc.addObject("Part::Feature","P2b_RodClevisBlock")
o.Shape=cb; o.Label="P2b_RodClevis_Flat"; o.ViewObject.Visibility=True
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="B_Shank": gg.addObject(o)
b=cb.BoundBox
print("P2b flat clevis X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cb.Volume/1000))
print("  pad Z %.0f..%.0f on the outboard face; slot %.1f..%.1f; cheeks %.1f / %.1f mm"%(
    BASE_Z[0],BASE_Z[1],SLOT[0],SLOT[1],SLOT[0]-EAR[0],EAR[1]-SLOT[1]))
print("  entirely above Z=114, so it can never reach the rail (Z 88..108) at any flexion")
print("  bolt line at X=0 is clear of the web (web min X = %.0f)"%(16.-12.))
# ---- bolts: fork set + clevis set ----
bolts=None
for y in (-90.,-110.,-125.):
    bb=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))
    bolts=bb if bolts is None else bolts.fuse(bb)
for y in BOLTS:
    bolts=bolts.fuse(cz(2.5,110.,123.,0.,y).fuse(cz(4.6,123.,128.,0.,y)))
doc.getObject("HW_JointBolts").Shape=bolts
print("HW_JointBolts: 3 M5 down into the inboard slot (fork) + 3 M5 down into the outboard slot (clevis)")
doc.recompute(); doc.save()
