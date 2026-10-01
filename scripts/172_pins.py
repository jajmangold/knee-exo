# -*- coding: utf-8 -*-
"""Rod pivot bolts for the skewed layout. Shank end can protrude below (nothing under it
now the clevis sits above Z=114); carriage end still stops on the cheek above the screw."""
import json, math, FreeCAD, Part
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
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
spec=(("HW_PinD_M8_Clevis",   D0,      114.0,150.0,108.0,"clevis cheeks 9.0 / 8.5, nyloc under"),
      ("HW_PinC_M8_Carriage",(XE,s0),  131.5,163.4,None, "threads the 7.0 mm cheek over the screw"))
for name,(x,y),zb,top,nb,note in spec:
    s=cz(4.0,zb,top,x,y).fuse(cz(6.5,top,top+5.2,x,y))
    if nb is not None: s=s.fuse(cz(6.9,nb,zb,x,y))
    s=s.removeSplitter()
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=name; o.ViewObject.Visibility=True
    print("  %-22s Z %.1f..%.1f  grip %.1f mm  (%s)"%(name,s.BoundBox.ZMin,s.BoundBox.ZMax,top-zb,note))
F=794.0
print("\n  pin unsupported span at the shank end: slot 18.5 mm, eye 12 mm -> use 2 x 3 mm")
print("  spacer washers to centre the eye, or accept %.0f MPa of bolt bending"%(
    F*18.5/8/(math.pi*8**3/32)))
doc.recompute(); doc.save()
