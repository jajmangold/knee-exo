# -*- coding: utf-8 -*-
"""v4d: carriage range raised (s0=75) so the screw clears the bracket's sweep; knee yoke
gets a bridge confined to bearings the bracket never visits, plus a screw channel."""
import math
S0=75.0
LROD=math.hypot(XE-D0[0], S0-D0[1]); globals()['LROD']=LROD
def carr(t):
    D=rot2(D0,t); dd=LROD*LROD-(XE-D[0])**2
    assert dd>0; return D[1]+math.sqrt(dd)
def armv(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s); L=math.hypot(C[0]-D[0],C[1]-D[1])
    return abs(D[0]*(C[1]-D[1])/L - D[1]*(C[0]-D[0])/L)
globals().update(carr=carr,armv=armv)
CBOT,CTOP=carr(-2.0),carr(105.0)
EXT_Y=(10.0, CTOP+36.0+55.0); SCR_Y=(48.0, EXT_Y[1]-2.0); MOT_Y=(EXT_Y[1]+4.0, EXT_Y[1]+78.0)
globals().update(EXT_Y=EXT_Y,SCR_Y=SCR_Y,MOT_Y=MOT_Y)
print("rod %.1f | carriage %.1f..%.1f (travel %.1f) | rail->%.0f | motor->%.0f = %.0f%% thigh"
      %(LROD,CBOT,CTOP,CTOP-CBOT,EXT_Y[1],MOT_Y[1],MOT_Y[1]/429*100))
# ---- extrusion / screw / motor ----
ext=bx(*EXT_X,*EXT_Y,*EXT_Z)
for xo in (20.0,40.0,60.0):
    ext=ext.cut(bx(EXT_X[0]+xo-3.,EXT_X[0]+xo+3.,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[0]-1,EXT_Z[0]+4.))
    ext=ext.cut(bx(EXT_X[0]+xo-3.,EXT_X[0]+xo+3.,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[1]-4.,EXT_Z[1]+1))
ext=ext.cut(cy(7.,EXT_Y[0]-1,EXT_Y[1]+1,25.,98.)).cut(cy(7.,EXT_Y[0]-1,EXT_Y[1]+1,55.,98.))
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=ext
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCREW_R,*SCR_Y,XE,SCREW_Z)
doc.getObject("A3_Motor_6374").Shape=cy(31.5,*MOT_Y,XE,SCREW_Z)
# ---- P1 yoke: two fork plates + rail flange + bridge clear of the bracket sweep ----
yk = bar((40.,42.),(0.,0.),32.,28.,*FORK_Z[0]).fuse(bar((40.,42.),(0.,0.),32.,28.,*FORK_Z[1]))
yk = yk.fuse(bx(*EXT_X,EXT_Y[0],78.,EXT_Z[1],FORK_Z[0][1]))          # flange on the rail face
yk = yk.fuse(bx(*EXT_X,50.,112.,FORK_Z[0][1],FORK_Z[1][0]))          # bridge (bearings 35..85)
yk = yk.fuse(bx(*EXT_X,50.,112.,*FORK_Z[1]))
yk = yk.cut(cy(SCREW_R+3.0,EXT_Y[0]-2,120.,XE,SCREW_Z))              # screw clearance channel
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))                  # knee pivot
for x in (20.,60.):
    for y in (22.,60.): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,y))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
# ---- P2 bracket (slot bearings recomputed for the new s0) ----
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(carr(t)-rot2(D0,t)[1], XE-rot2(D0,t)[0]))-t for t in ts])
cs=unwrap([math.degrees(math.atan2(rot2(D0,t)[1]-carr(t), rot2(D0,t)[0]-XE)) for t in ts])
b0,b1=min(bs)-15.,max(bs)+15.; c0,c1=min(cs)-12.,max(cs)+12.
sb = bar((0.,0.),D0,24.,19.,*SBR_Z).fuse(bar(D0,(0.,-205.),19.,18.,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z'])).fuse(cz(19.,EAR_Z[0][0],EAR_Z[1][1],*D0))
sb = sb.cut(cz(13.,*ROD_Z,*D0)).cut(sector_at(D0,58.,b0,b1,*ROD_Z,r_in=13.))
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0)).cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+.5))
for p in ((0.,-120.),(0.,-160.),(0.,-185.)): sb=sb.cut(cz(8.,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
doc.getObject("P2_ShankBracket_ALU").Shape=sb
def build_carriage(t):
    s=carr(t)
    c=bx(EXT_X[0]-6.,EXT_X[1]+6.,s-36.,s+36.,*CAR_Z).fuse(cz(19.,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c=c.cut(cz(13.,*ROD_Z,XE,s)).cut(sector_at((XE,s),58.,c0,c1,*ROD_Z,r_in=13.))
    c=c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
globals()['build_carriage']=build_carriage
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals()['pose']=pose
pose(0.0); doc.recompute(); doc.save()
print("P1 %.1f  P2 %.1f cm3 single closed solids"%(yk.Volume/1000,sb.Volume/1000))
KT=8.27/190.; FA=2*math.pi*.9*KT/.020
print("%5s %8s %9s %7s %9s"%("flex","arm","F@25N.m","amps","tau@40A"))
for t in (0,30,60,90,105):
    a=armv(float(t)); print("%5d %8.1f %8.0f N %6.1f %8.1f"%(t,a,25000/a,25000/a/FA,FA*40*a/1000))
