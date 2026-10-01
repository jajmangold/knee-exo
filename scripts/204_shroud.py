# -*- coding: utf-8 -*-
"""P20 knee shroud: cowl over the 180 deg belt wrap and BOTH nip points -- the worst
pinch hazard in the machine (764 N belt converging onto a toothed pulley).

Spans 172..368 deg so it overhangs each nip by 8 deg. Legs at 175 and 5 deg land on the
yoke's new proximal lobe; at r=43..47 they sit OUTSIDE the belt runs (which are at
|X| 35.6..41.1), so they clear them by ~1.7 mm.

No inboard side plate: the gap there is only 2 mm (fork cheek tops out at Z=94, belt
starts at Z=96) and the pulley at r<=35.6 plus the cheek already close it."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def asect(ri,ro,a0,a1,z0,z1):
    q=Part.makeCylinder(ro,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    return q.cut(cz(ri,z0-1,z1+1))
RIM=(43.,46.5); SZ=(94.5,130.); ANG=(172.,368.)
PLATE_Z=(126.5,130.); PLATE_RI=22.
LEG_A=(175.,5.); LEG_R=(43.,47.); LEG_W=6.5; LEG_Z=(88.,130.)
BOLT_R=44.75
s=asect(RIM[0],RIM[1],ANG[0],ANG[1],*SZ)                    # outer rim over the wrap
s=s.fuse(asect(PLATE_RI,RIM[1],ANG[0],ANG[1],*PLATE_Z))     # outboard side plate
for a in LEG_A:
    s=s.fuse(asect(LEG_R[0],LEG_R[1],a-LEG_W,a+LEG_W,*LEG_Z))
s=s.removeSplitter()
for a in LEG_A:
    lx,ly=BOLT_R*math.cos(math.radians(a)),BOLT_R*math.sin(math.radians(a))
    s=s.cut(cz(2.6,86.,100.,lx,ly))
    s=s.cut(cz(4.6,96.,101.,lx,ly))                         # counterbore for the head
assert len(s.Solids)==1 and s.isClosed() and s.isValid(),"P20 solids=%d"%len(s.Solids)
o=doc.getObject("P20_KneeShroud") or doc.addObject("Part::Feature","P20_KneeShroud")
o.Shape=s; o.Label="P20_KneeShroud"; o.ViewObject.Visibility=True
b=s.BoundBox
print("P20 knee shroud X %.1f..%.1f Y %.1f..%.1f Z %.0f..%.0f  %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,s.Volume/1000))
print("  rim r %.0f..%.1f over %.0f..%.0f deg (wrap is 180..360) -> %.0f deg of overhang each nip"%(
    RIM[0],RIM[1],ANG[0],ANG[1],180.-ANG[0]))
print("  belt outer is r=41.12, so the rim stands %.2f mm clear of it"%(RIM[0]-41.12))
for a in LEG_A:
    lx=LEG_R[0]*math.cos(math.radians(a))
    print("  leg at %3.0f deg: inner face X %+7.2f vs belt run X %+.2f -> %.2f mm clear"%(
        a,lx,-41.12 if a>90 else 41.12,abs(lx)-41.12))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="B_Shank": gg.addObject(o)
doc.recompute(); doc.save()
