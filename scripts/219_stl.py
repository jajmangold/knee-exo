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
for f in os.listdir(OUT):
    if f.endswith(".stl"): os.remove(os.path.join(OUT,f))
STRUCT=["P1_KneeYoke","P2a_KneeHingePlate","P3_Carriage","P3b_CarriageB","P5_ThighCuff",
        "P6_ShankSocket","P7_ShankCuff","P11_SprungAnchor"]
FAIR=["P20_KneeShroud","P21_ShellAnterior","P24_FairingShank"]
MACH=["P10a_Slider_Delrin","P10b_Slider_Delrin","P10c_Slider_Delrin","P10d_Slider_Delrin"]
ts=tf=0.
for n in STRUCT+FAIR+MACH:
    o=doc.getObject(n)
    if not o: print("  %-22s MISSING"%n); continue
    assert len(o.Shape.Solids)==1, n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    Mesh.Mesh(m.Topology).write(os.path.join(OUT,o.Label+".stl"))
    v=o.Shape.Volume/1000
    if n in STRUCT: ts+=v
    if n in FAIR: tf+=v
    print("  %-24s %6.1f cm3  %s"%(o.Label,v,"PETG struct" if n in STRUCT else
          ("PETG fairing" if n in FAIR else "Delrin")))
print("\nstructural %.0f cm3 (~%.0f g) + fairings %.0f cm3 (~%.0f g at 2-wall/low infill)"%(
    ts,ts*1.27,tf,tf*0.55))
print("total ~%.0f g PETG + 351 g rail"%(ts*1.27+tf*0.55))
