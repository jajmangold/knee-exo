# -*- coding: utf-8 -*-
import FreeCAD, Part
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
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
SLOT_Z=131.0; SHARED=(-55.0,-85.0); TNUT=(-115.0,)
cb=doc.getObject("P2b_RodClevisBlock").Shape
# X extent of the BOLTING ROOT only: slice well below the rod-eye boss centre
sl=cb.common(Part.makeBox(60,6,10,V(0,-118.0,SLOT_Z-5)))
root_x = sl.BoundBox.XMax if not sl.isNull() and sl.Volume>1 else 26.0
# safer: measure at each bolt station, taking the first solid span from X=10
print("clevis bbox X %.1f..%.1f (includes the rod-eye boss)"%(cb.BoundBox.XMin,cb.BoundBox.XMax))
END = 25.7
bolts=None
for y in SHARED:
    b=cx(2.5,-34.0,END,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z))
    bolts=b if bolts is None else bolts.fuse(b)
for y in TNUT:
    bolts=bolts.fuse(cx(2.5,-34.0,-6.0,y,SLOT_Z).fuse(cx(4.6,-34.0,-29.0,y,SLOT_Z)))
doc.getObject("HW_JointBolts").Shape=bolts
doc.recompute()
B=doc.getObject("HW_JointBolts").Shape
print("bolts now X %.1f..%.1f"%(B.BoundBox.XMin,B.BoundBox.XMax))
for n in ("P2b_RodClevisBlock","P2a_KneeHingePlate","A4_Shank2020_VSlot"):
    c=B.common(doc.getObject(n).Shape)
    print("  vs %-26s %.3f cm3"%(n, 0.0 if c.isNull() else c.Volume/1000))
doc.save()
