# -*- coding: utf-8 -*-
import FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
A4=doc.getObject("A4_Shank2020_VSlot").Shape
P2a=doc.getObject("P2a_KneeHingePlate").Shape
print("plate bolt holes (axis along X):")
for f in P2a.Faces:
    if isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-2.6)<0.01:
        c=f.Surface.Center; print("   r2.6 at Y=%.0f Z=%.0f"%(c.y,c.z))
print("\ndoes the 2020 have matching holes? look for r~2.6 cylinders:")
found=[f for f in A4.Faces if isinstance(f.Surface,Part.Cylinder) and 2.0<f.Surface.Radius<3.5]
print("   found %d"%len(found))
for f in found[:5]:
    c=f.Surface.Center; print("     r%.2f at X=%.0f Y=%.0f Z=%.0f"%(f.Surface.Radius,c.x,c.y,c.z))
print("\n2020 cylinders present (any radius):")
seen=set()
for f in A4.Faces:
    if isinstance(f.Surface,Part.Cylinder):
        r=round(f.Surface.Radius,2)
        if r in seen: continue
        seen.add(r); c=f.Surface.Center
        print("     r%.2f at X=%.1f Z=%.1f"%(r,c.x,c.z))
print("\nface-to-face gap plate<->2020: %.2f mm"%P2a.distToShape(A4)[0])
bb=P2a.BoundBox; print("plate posterior edge X=%.1f ; 2020 anterior face X=%.1f"%(bb.XMax,-10.0))
# where is the plate's arm posterior edge, down the length?
for y in (-55.,-80.,-108.):
    sl=P2a.common(Part.makeBox(60,4,20,V(-45,y-2,120)))
    if not sl.isNull() and sl.Volume>1:
        print("   at Y=%4.0f arm spans X %.1f..%.1f"%(y,sl.BoundBox.XMin,sl.BoundBox.XMax))
