# -*- coding: utf-8 -*-
"""Stop the live timer and zero every placement BEFORE any geometry edit.
This is the step whose omission baked animation poses into P2b and P3 last time."""
import FreeCAD
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
    try:
        t.stop(); print("timer stopped")
    except Exception as e: print("timer stop failed: %s"%e)
else:
    print("no _kx_timer in globals (already clear)")
g["_kx_timer"]=None; g["_kx_runner"]=None
ident=FreeCAD.Placement()
moved=[]
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity():
        moved.append(o.Name); o.Placement=ident
doc.recompute()
print("placements zeroed: %d -> %s"%(len(moved),moved))
bad=[o.Name for o in doc.Objects if hasattr(o,"Placement") and not o.Placement.isIdentity()]
print("non-identity remaining:", bad or "none")
doc.save()
