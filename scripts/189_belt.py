# -*- coding: utf-8 -*-
"""Belt for the differential. NO SPRING -- both ends are positively driven, so BOTH runs
have a length that varies and both are rebuilt per pose. Only the 180 deg wrap is static.
A printed cover protects the runs (the C-Beam channel cannot: the runs are 71.3 mm apart
and 30 mm wide, the channel is ~40 x 20)."""
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
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_diff.json"))
R=K["R"]; C0=K["C0"]; C1=K["C1"]; S=K["samples"]; BZ=tuple(K["belt_z"])
BIN,BOUT=R-1.372+0.05,R+4.2
w=Part.makeCylinder(BOUT,BZ[1]-BZ[0],V(0,0,BZ[0]),V(0,0,1),180.0)
w.rotate(V(0,0,0),V(0,0,1),180.0)
w=w.cut(cz(BIN,BZ[0]-1,BZ[1]+1)).removeSplitter()
assert len(w.Solids)==1 and w.isValid(),"wrap"
o=doc.getObject("A5_Belt_HTD8M") or doc.addObject("Part::Feature","A5_Belt_HTD8M")
o.Shape=w; o.Label="A5_Belt_Wrap180"; o.ViewObject.Visibility=True
print("A5  wrap 180 deg, distal side, Z %.0f..%.0f -- static at every angle (14 of 28 teeth)"%BZ)
for nm,sgn,C in (("A5b_Belt_DriveRun",-1.,C0),("A5c_Belt_TakeRun",1.,C1)):
    x0,x1=sorted((sgn*BIN,sgn*BOUT))
    d=bx(x0,x1,0.,C-24.,*BZ)
    ob=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
    ob.Shape=d; ob.Label=nm; ob.ViewObject.Visibility=True
    print("  %-20s X %6.1f..%6.1f  length %.1f mm at theta=0 (varies)"%(nm,x0,x1,C-24.))
a=[s["carrA"]-24 for s in S]; b=[s["carrB"]-24 for s in S]
print("  run A %.1f..%.1f mm, run B %.1f..%.1f mm, sum %.2f constant"%(
    min(a),max(a),min(b),max(b),a[0]+b[0]))
# retire the spring
for dead in ("A6_Spring_ConstForce","P12_SpringBracket"):
    if doc.getObject(dead): doc.removeObject(dead); print("retired %s"%dead)
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObject(doc.getObject("A5c_Belt_TakeRun"))
doc.recompute(); doc.save()
