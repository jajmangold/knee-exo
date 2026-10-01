# -*- coding: utf-8 -*-
"""Rod pivot bolts, entering from the TOP only. Nothing may protrude below the lower
cheek: the knee yoke sits under the clevis pivot (Z 108..120) and the ball screw sits
under the carriage pivot (Z 109..125). So the thread engages the lower cheek itself --
12.4 mm at the clevis (tap M8), 6.8 mm at the carriage (brass heat-set insert).
The bolt carries 794 N in DOUBLE SHEAR; the threads only hold preload."""
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
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
TOP=156.0
def bolt(x,y,z_bot):
    s=cz(4.0,z_bot,TOP,x,y).fuse(cz(6.5,TOP,TOP+5.2,x,y))
    return s.removeSplitter()
spec=(("HW_PinD_M8_Clevis",  D0,        120.0, 12.4, "tapped M8 in PETG"),
      ("HW_PinC_M8_Carriage",(XE,s0),   125.6,  6.8, "M8 brass heat-set insert"))
for name,(x,y),zb,cheek,note in spec:
    s=bolt(x,y,zb)
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=name; o.ViewObject.Visibility=True
    print("  %-22s at (%5.1f,%6.1f)  shank Z %.1f..%.1f  grip %.1f mm  lower cheek %.1f mm (%s)"%(
        name,x,y,zb,TOP,TOP-zb,cheek,note))
# shear check on the two bolts
F=794.0; A=math.pi*8.0**2/4
print("\n  M8 in double shear: %.0f N / (2 x %.1f mm2) = %.0f MPa; 8.8 shear allow ~370 MPa -> SF %.1f"%(
    F,A,F/(2*A),370.0/(F/(2*A))))
print("  bearing on the rod-end eye (8 dia x 12 wide): %.0f MPa"%(F/(8.0*12.0)))
doc.recompute(); doc.save()
