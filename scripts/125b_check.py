import FreeCAD
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
for o in doc.Objects:
    if not hasattr(o,"Shape") or o.Shape.isNull(): print("%-26s NULL"%o.Name); continue
    b=o.Shape.BoundBox; s=o.Shape
    print("%-26s X %7.1f..%7.1f Y %7.1f..%7.1f Z %7.1f..%7.1f  sol=%d vol=%6.1f"%(
        o.Name,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,len(s.Solids),s.Volume/1000))
