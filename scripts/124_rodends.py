import FreeCAD as App
doc=App.getDocument("KneeExo_v4")
for n in ("P4_Rod_8mm","P2b_RodClevisBlock","P3_Carriage","A4_Shank2020_VSlot","P8_RodEndHousing_PETG"):
    o=doc.getObject(n)
    if not o: print(n,"MISSING"); continue
    b=o.Shape.BoundBox
    print("%-24s X %7.1f..%7.1f  Y %7.1f..%7.1f  Z %7.1f..%7.1f  vol %6.1f cm3"%(
        n,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,o.Shape.Volume/1000))
