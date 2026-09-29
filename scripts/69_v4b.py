# -*- coding: utf-8 -*-
"""v4b: rod pivot pulled in to |D|=72 mm so it clears the seat. Shorter travel -> shorter
extrusion -> much better hip clearance. Motor moved beyond the rail's end."""
import math
D0=(25.0,-67.5); S0=40.0
LROD=math.hypot(XE-D0[0], S0-D0[1])
g=globals(); g.update(D0=D0,LROD=LROD)
def carr(t):
    D=rot2(D0,t); dd=LROD*LROD-(XE-D[0])**2
    assert dd>0; return D[1]+math.sqrt(dd)
def armv(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1])
    return abs(D[0]*(C[1]-D[1])/L - D[1]*(C[0]-D[0])/L)
g.update(carr=carr,armv=armv)
TRAV=carr(105.0)-carr(-2.0); CTOP=carr(105.0)
EXT_Y=(10.0, CTOP+42.0+55.0)                       # rail ends above the carriage + nut/bearing
MOT_Y=(EXT_Y[1]+4.0, EXT_Y[1]+78.0)
SCR_Y=(15.0, EXT_Y[1]-2.0)
g.update(EXT_Y=EXT_Y,MOT_Y=MOT_Y,SCR_Y=SCR_Y)
print("rod %.1f mm | carriage %.1f..%.1f (travel %.1f) | rail to Y=%.0f | motor %.0f..%.0f = %.0f%% thigh"
      %(LROD,carr(-2.0),CTOP,TRAV,EXT_Y[1],*MOT_Y,MOT_Y[1]/429*100))
KT=8.27/190.0; FA=2*math.pi*0.9*KT/0.020
print("%5s %8s %9s %7s %9s"%("flex","arm mm","F@25N.m","amps","tau@40A"))
for t in (0,30,60,90,105):
    a=armv(float(t)); print("%5d %8.1f %8.0f N %6.1f %8.1f N.m"%(t,a,25000/a,25000/a/FA,FA*40*a/1000))
n60=(armv(60.0)/1000)/0.020*2*math.pi
print("swing inertia +%.0f%% of limb (v3 was +30%%)"%(2.5e-4*n60*n60/0.29*100))
# ---- rebuild extrusion / screw / motor ----
ext=bx(*EXT_X,*EXT_Y,*EXT_Z)
for xo in (20.0,40.0,60.0):
    ext=ext.cut(bx(EXT_X[0]+xo-3.0,EXT_X[0]+xo+3.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[0]-1,EXT_Z[0]+4.0))
    ext=ext.cut(bx(EXT_X[0]+xo-3.0,EXT_X[0]+xo+3.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[1]-4.0,EXT_Z[1]+1))
ext=ext.cut(cy(7.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_X[0]+15.0,98.0)).cut(cy(7.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_X[0]+45.0,98.0))
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=ext
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCREW_R,*SCR_Y,XE,SCREW_Z)
doc.getObject("A3_Motor_6374").Shape=cy(31.5,*MOT_Y,XE,SCREW_Z)
# ---- P1 knee yoke (shorter reach) ----
yk = bar((40.0,42.0),(0.0,0.0),32.0,28.0,FORK_Z[0][0],FORK_Z[1][1])
yk = yk.cut(cz(70.0,SBR_Z[0]-2.0,SBR_Z[1]+2.0))
yk = yk.fuse(bx(EXT_X[0],EXT_X[1],EXT_Y[0],75.0,EXT_Z[1],FORK_Z[0][1]))
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))
for x in (20.0,60.0):
    for y in (24.0,58.0): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,y))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
# ---- P2 shank bracket ----
sb = bar((0.0,0.0),D0,24.0,19.0,*SBR_Z).fuse(bar(D0,(0.0,-205.0),19.0,18.0,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
sb = sb.fuse(cz(19.0,EAR_Z[0][0],EAR_Z[1][1],*D0))
sb = sb.cut(cz(13.0,*ROD_Z,*D0))
bs=[(math.degrees(math.atan2(carr(t)-rot2(D0,t)[1], XE-rot2(D0,t)[0]))-t)%360 for t in (-2,0,30,60,90,105)]
b0,b1=min(bs)-14.0,max(bs)+14.0
sb = sb.cut(sector_at(D0,58.0,b0,b1,*ROD_Z,r_in=13.0))
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
sb = sb.cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-0.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+0.5))
for p in ((0.0,-120.0),(0.0,-160.0),(0.0,-185.0)): sb=sb.cut(cz(8.0,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
doc.getObject("P2_ShankBracket_ALU").Shape=sb
print("rod sweeps %.0f..%.0f deg in the bracket frame; slot cut %.0f..%.0f"%(min(bs),max(bs),b0,b1))
pose(0.0); doc.recompute(); doc.save()
print("P1 %.1f  P2 %.1f cm3 single closed solids"%(yk.Volume/1000,sb.Volume/1000))
