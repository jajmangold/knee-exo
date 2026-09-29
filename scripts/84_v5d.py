# -*- coding: utf-8 -*-
"""Shank 2020 -> Z 121-141, just clear of the knee yoke (108-120)."""
import math
SH20_Z=(121.0,141.0); globals()['SH20_Z']=SH20_Z
s20=bx(*SH20_X,*SH20_Y,*SH20_Z)
s20=s20.cut(bx(-3.,3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4.))
s20=s20.cut(bx(-3.,3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4.,SH20_Z[1]+1))
s20=s20.cut(bx(SH20_X[0]-1,SH20_X[0]+4.,SH20_Y[0]-1,SH20_Y[1]+1,128.,134.))
s20=s20.cut(bx(SH20_X[1]-4.,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,128.,134.))
s20=s20.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.0,131.0))
doc.getObject("A4_Shank2020_VSlot").Shape=s20
hp = cz(26.0,*HINGE_Z).fuse(bar((0.0,-10.0),(-18.0,-120.0),22.0,15.0,*HINGE_Z))
hp = hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp = hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-60.,-85.,-110.): hp=hp.cut(Part.makeCylinder(2.6,40.,V(-30.,y,131.),V(1,0,0)))
assert len(hp.Solids)==1 and hp.isClosed()
doc.getObject("P2a_KneeHingePlate").Shape=hp
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(carr(t)-rot2(D0,t)[1],XE-rot2(D0,t)[0]))-t for t in ts])
b0,b1=min(bs)-15.,max(bs)+15.
cb = bx(10.0,20.0,D0[1]-28.0,D0[1]+28.0,SH20_Z[0],EAR_Z[0][1])
cb = cb.fuse(bar((16.0,D0[1]),D0,15.0,15.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,46.0,b0,b1,*ROD_Z,r_in=11.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-18.,18.): cb=cb.cut(Part.makeCylinder(2.6,40.,V(-4.,D0[1]+dy,131.),V(1,0,0)))
assert len(cb.Solids)==1 and cb.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb
hs = bx(-20.0,20.0,-318.0,-248.0,SH20_Z[0]-9.0,SH20_Z[1]+9.0)
hs = hs.cut(bx(SH20_X[0]-0.3,SH20_X[1]+0.3,-319.0,-262.0,SH20_Z[0]-0.3,SH20_Z[1]+0.3))
hs = hs.fuse(bx(-30.0,30.0,-318.0,-208.0,68.0,78.0))
hs = hs.fuse(bx(-8.0,8.0,-314.0,-218.0,76.0,SH20_Z[0]-6.0))
for xa,xb in ((14.,22.),(-22.,-14.)): hs=hs.fuse(bx(xa,xb,-310.,-222.,70.,SH20_Z[0]-6.0))
hs = hs.cut(bx(-3.,3.,-292.,-270.,SH20_Z[1]+3.,SH20_Z[1]+11.))
for x,y in [(-22.,-233.),(22.,-233.),(-22.,-293.),(22.,-293.)]: hs=hs.cut(cz(3.2,67.,79.,x,y))
assert len(hs.Solids)==1 and hs.isClosed()
doc.getObject("P6_ShankSocket").Shape=hs
pose(0.0); doc.recompute(); doc.save()
print("2020 Z %s | yoke 108-120 | gap %.0f mm"%(SH20_Z,SH20_Z[0]-120))
