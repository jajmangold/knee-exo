# -*- coding: utf-8 -*-
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
for n in ("P2b_RodClevisBlock","P3_Carriage","P4_Rod_8mm","A2_BallScrew_SFU1620"):
    o=doc.getObject(n)
    if not o: print("%-28s MISSING"%n); continue
    s=o.Shape; bb=s.BoundBox
    print("%-28s solids=%d closed=%-5s valid=%-5s vol=%7.1f cm3"%(n,len(s.Solids),s.isClosed(),s.isValid(),s.Volume/1000))
    print("     bbox X[%7.1f,%7.1f] Y[%7.1f,%7.1f] Z[%7.1f,%7.1f]  placement=%s"
          %(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax,o.Placement.Base))
print()
a=doc.getObject("P2b_RodClevisBlock").Shape; b=doc.getObject("P3_Carriage").Shape
c=a.common(b)
if not c.isNull() and c.Volume>1:
    bb=c.BoundBox
    print("P2b^carriage overlap X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.1f,%.1f]"%(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
