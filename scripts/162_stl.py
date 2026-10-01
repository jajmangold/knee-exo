# -*- coding: utf-8 -*-
import os, FreeCAD, Mesh, MeshPart
g=globals()
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
t=g.get("_kx_timer")
if t is not None:
    try: t.stop(); print("timer stopped")
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
OUT=r"C:/Users/Josh/KneeExo_v6_STL"
if not os.path.isdir(OUT): os.makedirs(OUT)
PRINTED=["P1_KneeYoke","P2a_KneeHingePlate","P2b_RodClevisBlock","P3_Carriage",
         "P5_ThighCuff","P6_ShankSocket","P7_ShankCuff"]
MACHINED=["P10a_Slider_Delrin","P10b_Slider_Delrin"]
tot=0.0
for n in PRINTED+MACHINED:
    o=doc.getObject(n)
    if not o: print("  %-24s MISSING"%n); continue
    assert len(o.Shape.Solids)==1 and o.Shape.isClosed(), n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT,n+".stl"))
    tag="PETG" if n in PRINTED else "Delrin"
    if n in PRINTED: tot+=o.Shape.Volume/1000
    print("  %-24s %6.1f cm3  %6d facets  %s"%(n,o.Shape.Volume/1000,m.CountFacets,tag))
print("printed total %.1f cm3 -> ~%.0f g PETG at 1.27 g/cm3 (100%% infill upper bound)"%(tot,tot*1.27))
b=doc.getObject("P10a_Slider_Delrin").Shape.BoundBox
print("Delrin sliders: 2 off, %.1f x %.1f x %.1f mm bar (5.6 wide, 9.8 tall, 102 long)"%(
    b.XLength,b.ZLength,b.YLength))
print("  4 mm of the height sits in the rail slot; 3 x M3 retaining screws each")
