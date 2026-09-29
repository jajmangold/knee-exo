# -*- coding: utf-8 -*-
import FreeCAD
doc=FreeCAD.getDocument("KneeExo_v4")
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
