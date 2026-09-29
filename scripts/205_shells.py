# -*- coding: utf-8 -*-
"""Drive shells + coupling cover.

Outer wall and top flange only -- no bottom flange, because the bottom faces the limb and
the thigh cuff, which already close it (and a bottom flange on the posterior side would
foul the cuff, which reaches X=88 at Z<=88).

Mounting tongues go into the rail's SIDE slot at Y positions that side's carriage never
reaches: carriage A travels Y 61..231 so shell A mounts at Y 238..278; carriage B travels
Y 112..283 so shell B mounts at Y 64..104."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def rng(a,b): return (min(a,b),max(a,b))
WALL=(76.,80.); TOP=(131.,135.); WZ=(85.,135.); SHELL_Y=(60.,289.)
SLOT_Z=(95.2,100.8); RISER_X=(30.,33.5); TONGUE_X=(26.,30.)
SPEC=(("P21_ShellAnterior",-1.,(238.,258.,278.)),
      ("P22_ShellPosterior", 1.,( 64., 84.,104.)))
for nm,g,tys in SPEC:
    s=bx(*rng(g*WALL[0],g*WALL[1]),SHELL_Y[0],SHELL_Y[1],*WZ)        # outer wall
    s=s.fuse(bx(*rng(g*WALL[1],g*33.),SHELL_Y[0],SHELL_Y[1],*TOP))   # top flange
    for ty in tys:
        s=s.fuse(bx(*rng(g*RISER_X[0],g*RISER_X[1]),ty-6.,ty+6.,SLOT_Z[0],TOP[1]))
        s=s.fuse(bx(*rng(g*TONGUE_X[0],g*TONGUE_X[1]),ty-6.,ty+6.,*SLOT_Z))
    s=s.removeSplitter()
    for ty in tys: s=s.cut(cz(2.6,SLOT_Z[0]-1,TOP[1]+1,g*31.75,ty))   # T-nut screws
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),"%s solids=%d"%(nm,len(s.Solids))
    o=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
    o.Shape=s; o.Label=nm; o.ViewObject.Visibility=True
    b=s.BoundBox
    print("%-19s X %6.1f..%6.1f Y %5.1f..%5.1f Z %.0f..%.0f  %5.1f cm3  tongues at Y %s"%(
        nm,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,s.Volume/1000,tys))
# ---- P23 coupling cover over the twin-screw drive box ----
c=bx(-76.,76.,288.,313.,94.,132.)
c=c.cut(bx(-72.,72.,291.,314.,90.,128.))
for sx in (-58.,58.): c=c.cut(cy(9.0,286.,293.,sx,106.))            # screw pass-throughs
c=c.removeSplitter()
assert len(c.Solids)==1 and c.isClosed() and c.isValid(),"P23 solids=%d"%len(c.Solids)
o=doc.getObject("P23_DriveCover") or doc.addObject("Part::Feature","P23_DriveCover")
o.Shape=c; o.Label="P23_DriveCover"; o.ViewObject.Visibility=True
b=c.BoundBox
print("P23_DriveCover      X %6.1f..%6.1f Y %5.1f..%5.1f Z %.0f..%.0f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,c.Volume/1000))
print("  4 mm walls, open bottom, bored for both screws at X +/-58")
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([doc.getObject(n) for n in ("P21_ShellAnterior","P22_ShellPosterior","P23_DriveCover")])
doc.recompute(); doc.save()
