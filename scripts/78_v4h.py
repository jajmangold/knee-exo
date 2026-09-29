# -*- coding: utf-8 -*-
"""v4h: single-shear knee plate (Z 108-120). Bracket 122-132. Rod clevis moved fully
OUTBOARD (eye 132-142, outer ear 142-152) so it never meets the yoke. Yoke arm shortened
clear of the carriage's lowest position."""
import math
FORK1=(108.0,120.0); SBR_Z=(122.0,132.0); ROD_Z=(132.0,142.0); EAR_Z=((122.0,132.0),(142.0,152.0))
globals().update(FORK1=FORK1,SBR_Z=SBR_Z,ROD_Z=ROD_Z,EAR_Z=EAR_Z)
# ---- yoke: one plate ----
yk = cz(40.,*FORK1).fuse(bar((40.,20.),(0.,0.),26.,22.,*FORK1))
yk = yk.fuse(bx(*EXT_X,EXT_Y[0],34.,EXT_Z[1],FORK1[1]))
yk = yk.cut(cy(SCREW_R+3.,EXT_Y[0]-2,75.,XE,SCREW_Z))
yk = yk.cut(cz(6.15,FORK1[0]-2,FORK1[1]+2))
for x in (20.,60.): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK1[1]+1,x,22.))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
print("yoke reaches Y=%.1f ; carriage lowest Y=%.1f"%(yk.BoundBox.YMax, carr(-2.0)-34))
# ---- bracket ----
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
sb = bar((0.,0.),D0,22.,16.,*SBR_Z).fuse(bar(D0,(0.,-205.),16.,16.,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
sb = sb.fuse(cz(15.,SBR_Z[0],EAR_Z[1][1],*D0))                    # boss spans out to the outer ear
sb = sb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,52.,b0,b1,*ROD_Z,r_in=11.5))
sb = sb.cut(cz(4.1,SBR_Z[0]-2,EAR_Z[1][1]+2,*D0)).cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+.5))
for p in ((0.,-120.),(0.,-160.),(0.,-185.)): sb=sb.cut(cz(7.,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
doc.getObject("P2_ShankBracket_ALU").Shape=sb
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-34.,s+34.,*CAR_Z).fuse(cz(16.,CAR_Z[1],EAR_Z[1][1],XE,s))
    c=c.cut(cz(11.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=11.5))
    c=c.cut(cz(4.1,CAR_Z[1]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
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
print("P1 %.1f  P2 %.1f cm3 single closed solids"%(yk.Volume/1000,sb.Volume/1000))
