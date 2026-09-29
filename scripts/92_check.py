# -*- coding: utf-8 -*-
import FreeCAD
doc=FreeCAD.getDocument("KneeExo_v4")
A=doc.getObject("P2a_KneeHingePlate").Shape
B=doc.getObject("A4_Shank2020_VSlot").Shape
for n,s in (("P2a_KneeHingePlate",A),("A4_Shank2020_VSlot",B)):
    bb=s.BoundBox
    print("%-24s X[%7.1f,%7.1f] Y[%7.1f,%7.1f] Z[%7.1f,%7.1f]"
          %(n,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
c=A.common(B)
if c.isNull() or c.Volume<1e-6:
    print("\nCLEAR - no interpenetration")
else:
    bb=c.BoundBox
    print("\n*** INTERPENETRATION %.2f cm3 ***"%(c.Volume/1000))
    print("   overlap X[%7.1f,%7.1f] Y[%7.1f,%7.1f] Z[%7.1f,%7.1f]"
          %(bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
    print("   = %.0f%% of the plate's volume"%(c.Volume/A.Volume*100))
# also re-check every pair I put in the SKIP list
print("\n=== other pairs I had skipped ===")
PAIRS=[("A4_Shank2020_VSlot","P2b_RodClevisBlock"),("A4_Shank2020_VSlot","P6_ShankSocket"),
       ("P6_ShankSocket","P7_ShankCuff"),("P1_KneeYoke","A1_Extrusion_20x60_VSlot"),
       ("P5_ThighCuff","A1_Extrusion_20x60_VSlot"),("P2a_KneeHingePlate","P1_KneeYoke")]
for a,b in PAIRS:
    oa,ob=doc.getObject(a),doc.getObject(b)
    if not oa or not ob: print("  %-42s missing"%(a+"^"+b)); continue
    cc=oa.Shape.common(ob.Shape)
    v=0.0 if cc.isNull() else cc.Volume/1000
    print("  %-26s ^ %-26s %8.2f cm3 %s"%(a,b,v,"" if v<0.01 else "<-- overlap"))
