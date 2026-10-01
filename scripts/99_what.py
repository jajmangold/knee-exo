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
P=doc.getObject("P2a_KneeHingePlate"); s=P.Shape; bb=s.BoundBox
print("P2a_KneeHingePlate")
print("  bbox X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]  -> %.0f x %.0f x %.0f mm"
      %(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax,bb.XLength,bb.YLength,bb.ZLength))
print("  volume %.1f cm3 -> %.0f g in 6061"%(s.Volume/1000, s.Volume/1000*2.70))
# circular holes: radius + axis
seen=set()
for f in s.Faces:
    if isinstance(f.Surface,Part.Cylinder):
        r=round(f.Surface.Radius,2); c=f.Surface.Center
        key=(r,round(c.x,1),round(c.y,1))
        if key in seen: continue
        seen.add(key)
        print("   cyl r=%5.2f (d=%5.2f) at X=%7.1f Y=%7.1f"%(r,r*2,c.x,c.y))
print()
print("what it touches (gap <1.5 mm at pose 0):")
for n in ("P1_KneeYoke","A4_Shank2020_VSlot","P2b_RodClevisBlock","P6_ShankSocket",
          "A1_Extrusion_20x60_VSlot","P4_Rod_8mm","HW_PinB_10"):
    o=doc.getObject(n)
    if not o: continue
    d=s.distToShape(o.Shape)[0]
    print("   %-26s gap %6.2f mm %s"%(n,d,"<-- mates" if d<1.5 else ""))
