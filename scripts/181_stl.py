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
PRINTED=["P1_KneeYoke","P2a_KneeHingePlate","P3_Carriage","P5_ThighCuff",
         "P6_ShankSocket","P7_ShankCuff","P12_SpringBracket"]
MACHINED=["P10a_Slider_Delrin","P10b_Slider_Delrin"]
tot=0.0
for n in PRINTED+MACHINED:
    o=doc.getObject(n)
    if not o: print("  %-24s MISSING"%n); continue
    assert len(o.Shape.Solids)==1 and o.Shape.isClosed(), n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT,n+".stl"))
    if n in PRINTED: tot+=o.Shape.Volume/1000
    print("  %-24s %6.1f cm3  %6d facets  %s"%(
        n,o.Shape.Volume/1000,m.CountFacets,"PETG" if n in PRINTED else "Delrin"))
print("printed total %.1f cm3 -> ~%.0f g PETG (100%% infill upper bound)"%(tot,tot*1.27))
# retire STLs for parts that no longer exist
for dead in ("P2b_RodClevisBlock","P4_Rod_M8","P8_RodEndHousing_PETG","P8b_RodEndHousing_Carriage"):
    p=os.path.join(OUT,dead+".stl")
    if os.path.exists(p): os.remove(p); print("  removed stale %s.stl"%dead)
