# -*- coding: utf-8 -*-
O = lambda n: doc.getObject(n)
for th in (-2.0, 60.0, 105.0):
    pose(th)
    for a in ("P7_Actuator_ENVELOPE","P8_Motor_6374"):
        for b in ("P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
                  "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"):
            sa, sb = O(a).Shape, O(b).Shape
            if not sa.BoundBox.intersect(sb.BoundBox): continue
            c = sa.common(sb)
            if c.isNull() or c.Volume < 20: continue
            bb = c.BoundBox
            print("th=%+5.0f %s^%s V=%5.3f cm3  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]"
                  % (th, a.split('_')[0], b.split('_')[0], c.Volume/1000,
                     bb.XMin,bb.XMax, bb.YMin,bb.YMax, bb.ZMin,bb.ZMax))
    print()
pose(0.0)
