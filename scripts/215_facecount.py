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
tot=0
rows=[]
for o in doc.Objects:
    if not hasattr(o,"Shape") or o.Shape.isNull(): continue
    if o.isDerivedFrom("App::DocumentObjectGroup"): continue
    n=len(o.Shape.Faces); tot+=n; rows.append((n,o.Name))
for n,nm in sorted(rows,reverse=True)[:10]: print("  %5d faces  %s"%(n,nm))
print("  total faces in the document: %d"%tot)
