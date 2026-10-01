# -*- coding: utf-8 -*-
"""Stop the live timer and zero every placement BEFORE any geometry edit.
This is the step whose omission baked animation poses into P2b and P3 last time."""
import FreeCAD
g=globals()
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
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
