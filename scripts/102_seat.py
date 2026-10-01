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
cb=doc.getObject("P2b_RodClevisBlock").Shape
A4=doc.getObject("A4_Shank2020_VSlot").Shape
bb=cb.BoundBox
# slide the block inboard by its residual gap so it seats on the 2020 face
gap=cb.distToShape(A4)[0]
cb2=cb.copy(); cb2.translate(V(-gap,0,0))
print("P2b shifted %.3f mm -> gap now %.3f mm"%(gap, cb2.distToShape(A4)[0]))
assert len(cb2.Solids)==1 and cb2.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb2
doc.recompute(); doc.save()
