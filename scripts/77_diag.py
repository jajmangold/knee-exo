# -*- coding: utf-8 -*-
O=lambda n: doc.getObject(n)
seen={}
for th in [float(x) for x in range(-2,106,3)]:
    pose(th)
    for a,b in (("P2_ShankBracket_ALU","P1_KneeYoke"),("P3_Carriage","P1_KneeYoke")):
        sa,sb=O(a).Shape,O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): continue
        c=sa.common(sb)
        if c.isNull() or c.Volume<50: continue
        if c.Volume<=seen.get((a,b),(0,))[0]: continue
        seen[(a,b)]=(c.Volume,th,c.BoundBox)
for (a,b),(v,th,bb) in seen.items():
    print("%-22s ^ %-12s %6.2f cm3 @%+5.0f  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]"
          %(a.split('_')[0],b.split('_')[1],v/1000,th,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
print()
print("yoke Z bands: fork %s %s ; bridge %.0f..%.0f ; flange %.0f..%.0f"
      %(FORK_Z[0],FORK_Z[1],FORK_Z[0][1],FORK_Z[1][0],EXT_Z[1],FORK_Z[0][1]))
print("bracket Z %s ; carriage Z %s ; ears %s"%(SBR_Z,CAR_Z,EAR_Z))
print("carriage lowest Y = %.1f - 34 = %.1f ; yoke flange to Y=34, arm cap to Y=70"%(carr(-2.0),carr(-2.0)-34))
pose(0.0)
