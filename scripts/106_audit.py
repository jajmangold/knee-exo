# -*- coding: utf-8 -*-
"""Every joint that is SUPPOSED to be in contact - is it?"""
import FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
O=lambda n: doc.getObject(n)
MATES=[("P2a_KneeHingePlate","A4_Shank2020_VSlot","plate laps the 2020 anterior face"),
       ("P2b_RodClevisBlock","A4_Shank2020_VSlot","clevis on the 2020 posterior face"),
       ("P6_ShankSocket","A4_Shank2020_VSlot","sliding fit (0.3 mm by design)"),
       ("P1_KneeYoke","A1_Extrusion_20x60_VSlot","yoke flange on the rail face"),
       ("P5_ThighCuff","A1_Extrusion_20x60_VSlot","cuff pad to the rail"),
       ("P6_ShankSocket","P7_ShankCuff","socket arm to cuff pad"),
       ("HW_JointBolts","P2a_KneeHingePlate","bolt in clearance hole (want a gap)"),
       ("P2a_KneeHingePlate","P1_KneeYoke","hinge clearance (want ~2 mm)")]
bad=[]
for a,b,why in MATES:
    oa,ob=O(a),O(b)
    if not oa or not ob: print("  %-26s missing"%a); continue
    d=oa.Shape.distToShape(ob.Shape)[0]
    ok = (d<0.02) if "laps" in why or "posterior face" in why or "flange" in why else True
    flag="" if (d<0.02 or "design" in why or "want" in why or "pad" in why) else "  <-- NOT SEATED"
    if flag: bad.append((a,b,d))
    print("  %-26s ^ %-26s %6.3f mm   %s%s"%(a,b,d,why,flag))
if bad:
    print("\nseating the loose ones:")
    for a,b,d in bad:
        oa=O(a); t=oa.Shape.copy()
        # move along -X or +X toward the mate
        ba,bb=oa.Shape.BoundBox, O(b).Shape.BoundBox
        sgn = -1.0 if ba.XMin > bb.XMin else 1.0
        t.translate(V(sgn*d,0,0))
        nd=t.distToShape(O(b).Shape)[0]
        if nd<d: oa.Shape=t; print("   %s moved %+.3f -> gap %.3f"%(a,sgn*d,nd))
doc.recompute(); doc.save()
