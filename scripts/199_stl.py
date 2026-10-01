import os, FreeCAD, Mesh, MeshPart
g=globals()
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
OUT=r"C:/Users/Josh/KneeExo_v6_STL"
PR=["P1_KneeYoke","P2a_KneeHingePlate","P3_Carriage","P3b_CarriageB","P5_ThighCuff",
    "P6_ShankSocket","P7_ShankCuff","P11_SprungAnchor"]
MA=["P10a_Slider_Delrin","P10b_Slider_Delrin","P10c_Slider_Delrin","P10d_Slider_Delrin"]
tot=0.
for n in PR+MA:
    o=doc.getObject(n)
    if not o: print("  %-24s MISSING"%n); continue
    assert len(o.Shape.Solids)==1 and o.Shape.isClosed(), n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT,n+".stl"))
    if n in PR: tot+=o.Shape.Volume/1000
    print("  %-24s %6.1f cm3  %s"%(n,o.Shape.Volume/1000,"PETG" if n in PR else "Delrin"))
print("printed %.1f cm3 -> ~%.0f g PETG (+ rail 351 g)"%(tot,tot*1.27))
