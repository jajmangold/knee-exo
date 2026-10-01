# -*- coding: utf-8 -*-
"""P2b clevis: base bolts to A4's posterior face over Y -97.5..-60 at Z 94..114, and the
ear rises from Z=114 so nothing of it is in the rail's Z band (88..108). That matters --
at 104 deg the clevis pivot swings to (57.8, 47.3), and the rail now starts at Y=58, so
low-Z clevis material would have clipped the rail's distal end."""
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
b0,b1=min(bs)-5.,max(bs)+5.
ZM=146.0; SLOT_Z=(138.4,153.6); POCK=13.; BAR_R=7.6; R_OUT=40.; U_LO,U_HI=6.,33.
EAR=(114.,162.); BASE_Z=(94.,114.); BASE_Y=(-97.5,-60.); zc=104.0; P2B=(-70.,-90.); TOP=162.0
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    for a in (a0,a1):
        d=(math.cos(math.radians(a)),math.sin(math.radians(a)))
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM),V(d[0],d[1],0.0)))
    return s.removeSplitter()
cb=bx(10.,26.,BASE_Y[0],BASE_Y[1],*BASE_Z).fuse(bar((26.,Dy),D0,13.,18.,*EAR)).removeSplitter()
cb=cb.cut(relief(D0,b0,b1))
cb=cb.cut(cz(4.1,104.,168.,*D0))
for y in P2B: cb=cb.cut(cx(3.0,8.,30.,y,zc))
assert len(cb.Solids)==1 and cb.isClosed() and cb.isValid(),"P2b solids=%d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
b=cb.BoundBox
print("P2b clevis X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cb.Volume/1000))
print("  base Z %.0f..%.0f only over Y %.1f..%.1f; ear starts at Z %.0f (rail tops out at 108)"%(
    BASE_Z[0],BASE_Z[1],BASE_Y[0],BASE_Y[1],EAR[0]))
print("  lower cheek %.1f mm, upper cheek %.1f mm"%(SLOT_Z[0]-EAR[0],EAR[1]-SLOT_Z[1]))
# sweep check: how far proximal does any low-Z clevis material reach?
mx=-1e9
for q in [x/2.0 for x in range(-4,209)]:
    for p in ((10.,BASE_Y[0]),(26.,BASE_Y[0]),(10.,BASE_Y[1]),(26.,BASE_Y[1])):
        y=rot2(p,q)[1]
        if y>mx: mx=y
print("  max Y reached by any clevis material below Z=114: %.1f  (rail starts at 58.0)"%mx)
# ---- rod pivot bolts ----
def bolt(x,y,z_bot,nut_bot=None):
    s=cz(4.0,z_bot,TOP,x,y).fuse(cz(6.5,TOP,TOP+5.2,x,y))
    if nut_bot is not None: s=s.fuse(cz(6.9,nut_bot,z_bot,x,y))
    return s.removeSplitter()
for name,(x,y),zb,nb,note in (("HW_PinD_M8_Clevis",D0,114.0,108.0,"nyloc below; clevis sweep stays under Y=58"),
                              ("HW_PinC_M8_Carriage",(XE,s0),131.5,None,"stops on the 7.4 mm cheek - the screw runs at Z=122")):
    s=bolt(x,y,zb,nb)
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=name; o.ViewObject.Visibility=True
    print("  %-22s Z %.1f..%.1f  grip %.1f mm  (%s)"%(name,s.BoundBox.ZMin,s.BoundBox.ZMax,TOP-zb,note))
doc.recompute(); doc.save()
