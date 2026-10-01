# -*- coding: utf-8 -*-
"""Merge P2b into P2a. The 794 N rod force and the knee pin reaction now live on ONE
part, so the load never crosses a bolted joint over the 75 mm that matters.

Key structural move: a vertical stiffening web at X 10..24 spanning Z 88..162 turns the
6 mm outer cheek into a deep L-beam. Without it the tower's 41 N.m would be out-of-plane
bending on a 6 mm plate (172 MPa - hopeless in PETG).

Two orthogonal bolt sets into A4, each taking the moment that is in-plane for it:
  3 x M5 along Z into the inboard slot  (takes the knee moment, in-plane for the cheek)
  3 x M5 along X into the posterior slot (takes Mx, in-plane for the vertical web)"""
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
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"]); Dy=D0[1]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
b0,b1=min(bs)-5.,max(bs)+5.
IN_Z=(70.,76.); OUT_Z=(88.,94.); PIN_R=5.15
WEB_X=(10.,24.); WEB_Y=(-125.,-45.); WEB_Z=(88.,162.)
EAR_Z=(114.,162.); ZM=146.0; SLOT_Z=(138.4,153.6); POCK=13.; BAR_R=7.6
R_OUT=40.; U_LO,U_HI=6.,33.; zc=104.0
BOLT_Z=(-85.,-110.,-135.); BOLT_X=(-60.,-90.,-120.)
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()
p =bar((0.,0.),(0.,-80.),24.,14.,*IN_Z)                    # inner fork cheek
p =p.fuse(bar((0.,0.),(0.,-135.),24.,14.,*OUT_Z))          # outer fork cheek
p =p.fuse(bx(-10.,10.,-80.,-45.,IN_Z[0],OUT_Z[1]))         # fork web
p =p.fuse(bx(WEB_X[0],WEB_X[1],WEB_Y[0],WEB_Y[1],*WEB_Z))  # vertical stiffening web
p =p.fuse(bar((24.,Dy),D0,16.,18.,*EAR_Z)).removeSplitter()# rod clevis ear
p =p.cut(cz(PIN_R,IN_Z[0]-2,OUT_Z[1]+2))                   # knee pin bore
p =p.cut(relief(D0,b0,b1))                                 # rod-end swing relief
p =p.cut(cz(4.1,112.,168.,*D0))                            # rod pivot bolt
for y in BOLT_Z: p=p.cut(cz(2.6,OUT_Z[0]-1,OUT_Z[1]+1,0.,y))
for y in BOLT_X: p=p.cut(cx(2.6,8.,26.,y,zc))
assert len(p.Solids)==1 and p.isClosed() and p.isValid(),"P2a solids=%d"%len(p.Solids)
old=doc.getObject("P2a_KneeHingePlate").Shape.Volume/1000
doc.getObject("P2a_KneeHingePlate").Shape=p
doc.getObject("P2a_KneeHingePlate").Label="P2a_KneeHinge_RodClevis"
b=p.BoundBox
print("P2a merged  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
print("  %.1f cm3  (was P2a %.1f + P2b 46.2 = %.1f -> saved %.1f cm3)"%(
    p.Volume/1000,old,old+46.2,old+46.2-p.Volume/1000))
print("  vertical web X %.0f..%.0f spanning Z %.0f..%.0f makes the 6 mm cheek a deep L-beam"%(
    WEB_X[0],WEB_X[1],WEB_Z[0],WEB_Z[1]))
# sweep check: the web overlaps the rail's Z band, so how far proximal does it reach?
mx=-1e9; who=None
for q in [x/2.0 for x in range(-4,209)]:
    for pt in ((WEB_X[0],WEB_Y[0]),(WEB_X[1],WEB_Y[0]),(WEB_X[0],WEB_Y[1]),(WEB_X[1],WEB_Y[1])):
        y=rot2(pt,q)[1]
        if y>mx: mx,who=y,(pt,q)
print("  max Y reached by the vertical web: %.1f at %s theta=%.0f  (rail starts at 58.0)"%(
    mx,who[0],who[1]))
# ---- bolts ----
bolts=None
for y in BOLT_Z:
    bb=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))
    bolts=bb if bolts is None else bolts.fuse(bb)
for y in BOLT_X:
    bolts=bolts.fuse(cx(2.5,-2.,30.,y,zc).fuse(cx(4.6,25.,30.,y,zc)))
doc.getObject("HW_JointBolts").Shape=bolts
print("HW_JointBolts: 3 M5 along Z (inboard slot) + 3 M5 along X (posterior slot)")
# ---- retire P2b ----
if doc.getObject("P2b_RodClevisBlock"):
    doc.removeObject("P2b_RodClevisBlock"); print("retired P2b_RodClevisBlock")
doc.recompute(); doc.save()
