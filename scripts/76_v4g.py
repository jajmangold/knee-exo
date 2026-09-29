# -*- coding: utf-8 -*-
"""Bracket reaches X=-12.6 anterior at worst, so the bridge goes to X -44..-26.
Yoke arm's end cap reaches Y=70 at X=40, so the screw channel must run to Y=75."""
import math
def plate(z0,z1): return cz(44.,z0,z1).fuse(bar((40.,40.),(0.,0.),30.,26.,z0,z1))
yk = plate(*FORK_Z[0]).fuse(plate(*FORK_Z[1]))
yk = yk.fuse(bx(*EXT_X,EXT_Y[0],34.,EXT_Z[1],FORK_Z[0][1]))
yk = yk.fuse(bx(-44.,-26.,-24.,24.,FORK_Z[0][1],FORK_Z[1][0]))     # bridge, clear of the bracket
yk = yk.cut(cy(SCREW_R+3.,EXT_Y[0]-2,75.,XE,SCREW_Z))              # screw channel through the arm
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))
for x in (20.,60.): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,22.))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
xs=[]
for t in [float(x) for x in range(-2,106,3)]:
    D=rot2(D0,t)
    e=22.0*math.cos(math.radians(20.0+t))
    xs.append(min(e,D[0]-15.0))
print("bracket most-anterior reach over ROM: X=%.1f ; bridge at X -44..-26 -> %s"
      %(min(xs),"clear" if min(xs)>-26 else "CHECK"))
pose(0.0); doc.recompute(); doc.save()
print("P1 %.1f cm3"%(yk.Volume/1000))
