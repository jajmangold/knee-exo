# -*- coding: utf-8 -*-
import FreeCAD
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
O=lambda n: doc.getObject(n)
p8=O("P8_RodEndHousing_PETG"); rod=O("P4_Rod_8mm")
print("P8 exists:", p8 is not None, " visible:", p8.ViewObject.Visibility if p8 else "-")
print("P8 placement:", p8.Placement.Base, "angle %.1f"%(p8.Placement.Rotation.Angle*57.2958))
print("rod placement:", rod.Placement.Base, "angle %.1f"%(rod.Placement.Rotation.Angle*57.2958))
b8=p8.Shape.BoundBox; br=rod.Shape.BoundBox
print("P8 bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(b8.XMin,b8.XMax,b8.YMin,b8.YMax,b8.ZMin,b8.ZMax))
print("rod bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"%(br.XMin,br.XMax,br.YMin,br.YMax,br.ZMin,br.ZMax))
c=p8.Shape.common(rod.Shape)
print("P8 ^ rod overlap: %.2f cm3  (P8 is %.2f cm3)"%(0 if c.isNull() else c.Volume/1000, p8.Shape.Volume/1000))
print("\nobjects in the document:")
for o in doc.Objects:
    if o.TypeId=="Part::Feature":
        print("   %-28s vis=%-5s"%(o.Name,o.ViewObject.Visibility))
