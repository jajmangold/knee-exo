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
    try: t.stop(); print("timer stopped")
    except Exception as e: print("stop: %s"%e)
g["_kx_timer"]=None
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
print("non-identity:", [o.Name for o in doc.Objects if hasattr(o,"Placement") and not o.Placement.isIdentity()] or "none")
for n in ("HW_PinB_10","P5_ThighCuff","P7_ShankCuff","A3_Motor_6374","P6_ShankSocket"):
    o=doc.getObject(n)
    if not o: print("  %-20s MISSING"%n); continue
    b=o.Shape.BoundBox
    print("  %-20s X %7.1f..%7.1f  Y %8.1f..%8.1f  Z %7.1f..%7.1f  vol %6.1f"%(
        n,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,o.Shape.Volume/1000))
doc.save()
