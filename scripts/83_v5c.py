# -*- coding: utf-8 -*-
"""Rod eye moved outboard of the yoke (127-137, ears 121-127 / 137-147); hinge-plate disc
trimmed to r=26 so the rod clears it. Max lateral now set by the motor (146.5)."""
import math
ROD_Z=(127.0,137.0); EAR_Z=((121.0,127.0),(137.0,147.0)); HINGE_Z=(122.0,134.0)
globals().update(ROD_Z=ROD_Z,EAR_Z=EAR_Z,HINGE_Z=HINGE_Z)
hp = cz(26.0,*HINGE_Z).fuse(bar((0.0,-10.0),(-18.0,-120.0),22.0,15.0,*HINGE_Z))
hp = hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp = hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-60.,-85.,-110.): hp=hp.cut(Part.makeCylinder(2.6,40.,V(-30.,y,128.),V(1,0,0)))
assert len(hp.Solids)==1 and hp.isValid() and hp.isClosed(),"P2a %d"%len(hp.Solids)
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
cs=unwrap([math.degrees(math.atan2(rot2(D0,t)[1]-carr(t),rot2(D0,t)[0]-XE)) for t in ts])
b0,b1=min(bs)-15.,max(bs)+15.; c0,c1=min(cs)-12.,max(cs)+12.
cb = bx(10.0,20.0,D0[1]-28.0,D0[1]+28.0,SH20_Z[0]+2.0,EAR_Z[0][1])
cb = cb.fuse(bar((16.0,D0[1]),D0,15.0,15.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,46.0,b0,b1,*ROD_Z,r_in=11.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-18.,18.): cb=cb.cut(Part.makeCylinder(2.6,40.,V(-4.,D0[1]+dy,118.),V(1,0,0)))
assert len(cb.Solids)==1 and cb.isValid() and cb.isClosed(),"P2b %d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-34.,s+34.,*CAR_Z).fuse(cz(16.,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c=c.cut(cz(11.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=11.5))
    c=c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    zc=(ROD_Z[0]+ROD_Z[1])/2
    return Part.makeCylinder(4.,L,V(D[0],D[1],zc),V(ux,uy,0.)).fuse(
           cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*D)).fuse(cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*C))
globals().update(build_carriage=build_carriage,build_rod=build_rod)
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals()['pose']=pose
pose(0.0); doc.recompute(); doc.save()
print("P2a %.1f  P2b %.1f cm3"%(hp.Volume/1000,cb.Volume/1000))
