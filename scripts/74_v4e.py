# -*- coding: utf-8 -*-
"""The rod sweeps X 25..59 over the ROM, so the yoke's Z-bridge must cross anterior of it."""
import math
yk = bar((40.,42.),(0.,0.),32.,28.,*FORK_Z[0]).fuse(bar((40.,42.),(0.,0.),32.,28.,*FORK_Z[1]))
yk = yk.fuse(bx(*EXT_X,EXT_Y[0],78.,EXT_Z[1],FORK_Z[0][1]))      # flange on the rail face
yk = yk.fuse(bx(8.,22.,38.,112.,FORK_Z[0][1],FORK_Z[1][0]))      # bridge, anterior of the rod
yk = yk.fuse(bx(8.,22.,38.,112.,*FORK_Z[1]))
yk = yk.cut(cy(SCREW_R+3.,EXT_Y[0]-2,120.,XE,SCREW_Z))
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))
for x in (20.,60.):
    for y in (22.,60.): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,y))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
pose(0.0); doc.recompute()
# sweep the rod's X envelope to confirm the bridge is clear
xs=[]
for t in [float(x) for x in range(-2,106,3)]:
    D=rot2(D0,t); s=carr(t)
    xs += [D[0]-4,D[0]+4,XE-4,XE+4]
print("rod X envelope over the ROM: %.1f .. %.1f   bridge at X 8..22 -> %s"
      %(min(xs),max(xs),"clear" if min(xs)>22 else "CHECK"))
print("P1 %.1f cm3 single closed solid"%(yk.Volume/1000))
doc.save()
