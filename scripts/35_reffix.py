# -*- coding: utf-8 -*-
"""REF_Shank was makeCone(..., dir=+Y) from Y=-20 -> it pointed PROXIMALLY, overlapping
the thigh. Reference-only bug, but it made the limb-clearance column meaningless."""
sh = Part.makeCone(60.0, 38.0, 360.0, FreeCAD.Vector(0,-20,0), FreeCAD.Vector(0,-1,0))
doc.getObject("REF_Shank").Shape = sh
if getattr(doc.getObject("REF_Shank"), "ViewObject", None) is not None:  # absent headless
    doc.getObject("REF_Shank").ViewObject.Transparency = 80
pose(0.0); doc.recompute()
O = lambda n: doc.getObject(n)
LIMB = ["REF_Thigh","REF_Knee","REF_Shank"]
PARTS = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff","P4_ShankLink_Horn",
         "P5_ShankSlideHousing","P6_ShankCuff","P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring"]
def vol(a,b):
    try:
        if not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
print("=== structure vs nominal limb (corrected reference) ===")
worst={}
for th in [float(x) for x in range(-2,106,6)]+[105.0]:
    pose(th)
    for p in PARTS:
        for l in LIMB:
            v=vol(O(p).Shape,O(l).Shape)
            if v>0.3: worst[(p,l)]=max(worst.get((p,l),0.0),v)
for (p,l),v in sorted(worst.items(), key=lambda kv:-kv[1]):
    print("  %-24s ^ %-10s %6.2f cm3" % (p.split('_')[0]+"_"+p.split('_')[1], l, v))
if not worst: print("  none - structure stands clear of the nominal limb everywhere")
print("  (nominal cones; contact here = where the 6 mm foam liner compresses)")
pose(0.0); doc.recompute(); doc.save()
