# -*- coding: utf-8 -*-
O = lambda n: doc.getObject(n)
PAIRS = [(a,b) for a in ("P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring")
               for b in ("P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
                         "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff")]
PAIRS += [(a,b) for a in ("P4_ShankLink_Horn","P5_ShankSlideHousing")
                for b in ("P1_ThighUpright_Lower","P2_ThighUpright_Upper",
                          "HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg")]
seen = {}
for th in (-2.0, 30.0, 60.0, 90.0, 105.0):
    pose(th)
    for a,b in PAIRS:
        sa, sb = O(a).Shape, O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): continue
        c = sa.common(sb)
        if c.isNull() or c.Volume < 40: continue
        k = (a,b); bb = c.BoundBox
        if c.Volume <= seen.get(k,(0,))[0]: continue
        seen[k] = (c.Volume, th, bb)
for (a,b),(v,th,bb) in sorted(seen.items(), key=lambda kv:-kv[1][0]):
    print("%-22s ^ %-22s %6.3f cm3 @%+5.0f  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]"
          % (a.split('_')[0]+"_"+a.split('_')[1], b.split('_')[1], v/1000, th,
             bb.XMin,bb.XMax, bb.YMin,bb.YMax, bb.ZMin,bb.ZMax))
pose(0.0)
