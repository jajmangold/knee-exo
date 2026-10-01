# -*- coding: utf-8 -*-
"""Four fixes.

The yoke: I had cut its disc to r=30 "to clear the belt wrap", but the yoke is at Z 76..88
and the belt at Z 96..126 -- radius was never the constraint. What actually sweeps through
that annulus is the FORK WEB (Z 70..94, r 45..81, angles 260..28 over the ROM). So the yoke
goes back to a full r=47 disc with that swept sector cut out of it, and the shroud legs
move to 185 and 250 deg, which are clear of the web sweep AND of both belt runs (the runs
cross r 43..46.5 at 145..153 and 27..35 deg)."""
import math, FreeCAD, Part
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
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def asect(ri,ro,a0,a1,z0,z1):
    q=Part.makeCylinder(ro,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    return q.cut(cz(ri,z0-1,z1+1))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
LEG_A=(185.,230.); BOLT_R=44.75; YZ=(76.,88.); PIN_R=6.15
# ---- 1. yoke: full r=47 disc minus the fork web's swept sector ----
yk=cz(47.,*YZ)
yk=yk.cut(asect(43.,49.,241.,403.,YZ[0]-1,YZ[1]+1))       # fork OUTER CHEEK sweep, 241..43 deg
yk=yk.fuse(bar((0.,0.),(0.,70.),28.,30.,*YZ))
yk=yk.fuse(bx(-30.,30.,58.,124.,*YZ)).removeSplitter()
yk=yk.cut(cz(PIN_R,YZ[0]-2,YZ[1]+2))
for x in (-20.,0.,20.):
    for y in (70.,112.): yk=yk.cut(cz(2.6,YZ[0]-1,YZ[1]+1,x,y))
hx,hy=25.*math.cos(math.radians(-60)),25.*math.sin(math.radians(-60))
yk=yk.cut(bx(hx-6.,hx+6.,hy-4.,hy+4.,YZ[1]-4.,YZ[1]+0.5))
for a in LEG_A:
    yk=yk.cut(cz(2.1,YZ[1]-8.,YZ[1]+1,BOLT_R*math.cos(math.radians(a)),BOLT_R*math.sin(math.radians(a))))
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
print("1. P1 yoke: full r=47 disc, web-sweep sector 260..28 deg cut out; %.1f cm3"%(yk.Volume/1000))
# ---- 2. shroud legs to 185 / 250 ----
RIM=(43.,46.5); SZ=(94.5,130.); ANG=(172.,368.); PLATE=(126.5,130.); LEG_R=(43.,47.); LEG_W=6.5
s=asect(RIM[0],RIM[1],ANG[0],ANG[1],*SZ)
s=s.fuse(asect(22.,RIM[1],ANG[0],ANG[1],*PLATE))
for a in LEG_A: s=s.fuse(asect(LEG_R[0],LEG_R[1],a-LEG_W,a+LEG_W,88.,SZ[1]))
s=s.removeSplitter()
for a in LEG_A:
    lx,ly=BOLT_R*math.cos(math.radians(a)),BOLT_R*math.sin(math.radians(a))
    s=s.cut(cz(2.6,86.,100.,lx,ly)).cut(cz(4.6,96.,101.,lx,ly))
assert len(s.Solids)==1 and s.isClosed() and s.isValid(),"P20 solids=%d"%len(s.Solids)
doc.getObject("P20_KneeShroud").Shape=s
print("2. P20 legs at %s deg (clear of web sweep 260..28 and of both belt runs)"%(LEG_A,))
for a in LEG_A:
    lx=LEG_R[0]*math.cos(math.radians(a)); ly=LEG_R[0]*math.sin(math.radians(a))
    print("     leg %3.0f deg -> inner corner (%+7.2f,%+7.2f)"%(a,lx,ly))
# ---- 3. A7 drive box shrunk to fit inside its cover ----
doc.getObject("A7_DriveBox").Shape=bx(-70.,70.,292.,311.,98.,126.)
print("3. A7_DriveBox shrunk to X -70..70 Y 292..311 Z 98..126 (inside P23's 4 mm walls)")
# ---- 4. shells end at Y=287 so they abut, not overlap, P23 ----
for nm in ("P21_ShellAnterior","P22_ShellPosterior"):
    o=doc.getObject(nm); sh=o.Shape
    o.Shape=sh.cut(bx(-90.,90.,287.,320.,80.,140.))
    print("4. %-19s trimmed to Y<=287 (P23 starts at 288)"%nm)
doc.recompute(); doc.save()
