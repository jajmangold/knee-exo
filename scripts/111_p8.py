# -*- coding: utf-8 -*-
import FreeCAD
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
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
