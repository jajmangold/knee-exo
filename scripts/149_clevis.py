# -*- coding: utf-8 -*-
"""P2b clevis side-mounts to A4's posterior face and rises to the new rod plane.
Rod pivot bolts: the clevis end may protrude below (nothing there now that the yoke is
inboard and the fork is at X +/-24); the carriage end may not (the rail is under it)."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
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
s0=sm(0.0)["carr"]; Dy=D0[1]
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
bs=unwrap([math.degrees(math.atan2(sm(q)["carr"]-rot2(D0,q)[1],XE-rot2(D0,q)[0]))-q for q in ts])
MARG=5.0; b0,b1=min(bs)-MARG,max(bs)+MARG
ZM=124.0; SLOT_Z=(116.4,131.6); POCK=13.0; BAR_R=7.6; R_OUT=40.0; U_LO,U_HI=6.0,33.0
SH20_Z=(94.,114.); zc=104.0; EAR=(94.,140.); P2B_BOLTS=(-55.,-85.); TOP=140.0
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()
cb=bx(10.,26.,-97.5,-45.,*SH20_Z).fuse(bar((26.,Dy),D0,13.,18.,*EAR)).removeSplitter()
cb=cb.cut(relief(D0,b0,b1))
cb=cb.cut(cz(4.1,90.,146.,*D0))
for y in P2B_BOLTS: cb=cb.cut(cx(3.0,8.,30.,y,zc))
cb=cb.cut(bx(-5.,29.,-45.,20.,90.,150.))
assert len(cb.Solids)==1 and cb.isClosed() and cb.isValid(),"P2b solids=%d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
b=cb.BoundBox
print("P2b clevis X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cb.Volume/1000))
print("  cheeks %.1f (lower) / %.1f (upper) mm"%(SLOT_Z[0]-EAR[0],EAR[1]-SLOT_Z[1]))
# ---- rod pivot bolts ----
def bolt(x,y,z_bot,nut_bot=None):
    s=cz(4.0,z_bot,TOP,x,y).fuse(cz(6.5,TOP,TOP+5.2,x,y))
    if nut_bot is not None: s=s.fuse(cz(6.9,nut_bot,z_bot,x,y))
    return s.removeSplitter()
for name,(x,y),zb,nb,note in (("HW_PinD_M8_Clevis",D0,94.0,88.0,"nyloc below, nothing in the way"),
                              ("HW_PinC_M8_Carriage",(XE,s0),108.0,None,"heat-set insert, rail below")):
    s=bolt(x,y,zb,nb)
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=name; o.ViewObject.Visibility=True
    print("  %-22s Z %.1f..%.1f  grip %.1f mm  (%s)"%(name,s.BoundBox.ZMin,s.BoundBox.ZMax,TOP-zb,note))
doc.recompute(); doc.save()
