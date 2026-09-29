import FreeCAD
doc=FreeCAD.getDocument("KneeExo_v4")
for o in doc.Objects:
    if not hasattr(o,"Shape") or o.Shape.isNull(): print("%-26s NULL"%o.Name); continue
    b=o.Shape.BoundBox; s=o.Shape
    print("%-26s X %7.1f..%7.1f Y %7.1f..%7.1f Z %7.1f..%7.1f  sol=%d vol=%6.1f"%(
        o.Name,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,len(s.Solids),s.Volume/1000))
