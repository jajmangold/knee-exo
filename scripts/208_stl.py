import os, FreeCAD, Mesh, MeshPart
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
OUT=r"C:/Users/Josh/KneeExo_v6_STL"
STRUCT=["P1_KneeYoke","P2a_KneeHingePlate","P3_Carriage","P3b_CarriageB","P5_ThighCuff",
        "P6_ShankSocket","P7_ShankCuff","P11_SprungAnchor"]
SHROUD=["P20_KneeShroud","P21_ShellAnterior","P22_ShellPosterior","P23_DriveCover"]
MACH=["P10a_Slider_Delrin","P10b_Slider_Delrin","P10c_Slider_Delrin","P10d_Slider_Delrin"]
ts=th=0.
for n in STRUCT+SHROUD+MACH:
    o=doc.getObject(n)
    if not o: print("  %-22s MISSING"%n); continue
    assert len(o.Shape.Solids)==1 and o.Shape.isClosed(), n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT,n+".stl"))
    v=o.Shape.Volume/1000
    if n in STRUCT: ts+=v
    if n in SHROUD: th+=v
    tag="PETG struct" if n in STRUCT else ("PETG shroud" if n in SHROUD else "Delrin")
    print("  %-22s %6.1f cm3  %s"%(n,v,tag))
print("\nstructural %.1f cm3 (~%.0f g) + shrouds %.1f cm3 (~%.0f g) = %.1f cm3 (~%.0f g) PETG"%(
    ts,ts*1.27,th,th*1.27,ts+th,(ts+th)*1.27))
print("shrouds could print at low infill/2-wall -> nearer %.0f g"%(th*0.55))
