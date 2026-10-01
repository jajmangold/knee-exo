# -*- coding: utf-8 -*-
"""Recess the knee pin head into the hub so it is FLUSH at Z=126 instead of standing
proud to 132. Less to snag, and it drops the whole knee's lateral envelope by 6 mm."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
g=globals()
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
t=g.get("_kx_timer")
if t is not None:
    try: t.stop(); print("timer stopped")
    except Exception: pass
g["_kx_timer"]=None
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
assert not [o for o in doc.Objects if hasattr(o,"Placement") and not o.Placement.isIdentity()]
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
p2=doc.getObject("P2a_KneeHingePlate"); s=p2.Shape
s=s.cut(cz(10.0,113.,126.5))                       # counterbore for the recessed head
assert len(s.Solids)==1 and s.isClosed() and s.isValid(),"P2a solids=%d"%len(s.Solids)
p2.Shape=s
pin=cz(6.0,68.,113.).fuse(cz(9.5,113.,126.)).fuse(cz(10.,62.,68.)).removeSplitter()
assert len(pin.Solids)==1 and pin.isClosed(),"pin"
doc.getObject("HW_PinB_10").Shape=pin
print("HW_PinB M12: head now recessed Z 113..126, flush with the hub (was proud to 132)")
print("P2a %.1f cm3 with the counterbore"%(s.Volume/1000))
doc.recompute(); doc.save()
