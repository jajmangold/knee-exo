# -*- coding: utf-8 -*-
"""v4f consolidated:
 - s0=85 so the screw starts above the bracket's rod boss
 - rod boss r 19->15
 - yoke: disc fork plates + SHORT rail flange (below the carriage) + ANTERIOR Z-bridge
   at X -34..-12, a bearing the shank bracket never sweeps (it sweeps 243..82)."""
import math
S0=85.0
LROD=math.hypot(XE-D0[0], S0-D0[1]); globals()['LROD']=LROD
def carr(t):
    D=rot2(D0,t); dd=LROD*LROD-(XE-D[0])**2
    assert dd>0; return D[1]+math.sqrt(dd)
def armv(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s); L=math.hypot(C[0]-D[0],C[1]-D[1])
    return abs(D[0]*(C[1]-D[1])/L - D[1]*(C[0]-D[0])/L)
globals().update(carr=carr,armv=armv)
CBOT,CTOP=carr(-2.0),carr(105.0)
EXT_Y=(10.0,CTOP+36.0+55.0); SCR_Y=(CBOT-26.0,EXT_Y[1]-2.0); MOT_Y=(EXT_Y[1]+4.0,EXT_Y[1]+78.0)
globals().update(EXT_Y=EXT_Y,SCR_Y=SCR_Y,MOT_Y=MOT_Y)
print("carriage %.1f..%.1f (travel %.1f) | screw from %.0f | rail->%.0f | motor->%.0f (%.0f%% thigh)"
      %(CBOT,CTOP,CTOP-CBOT,SCR_Y[0],EXT_Y[1],MOT_Y[1],MOT_Y[1]/429*100))
ext=bx(*EXT_X,*EXT_Y,*EXT_Z)
for xo in (20.,40.,60.):
    ext=ext.cut(bx(10.+xo-3.,10.+xo+3.,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[0]-1,EXT_Z[0]+4.))
    ext=ext.cut(bx(10.+xo-3.,10.+xo+3.,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[1]-4.,EXT_Z[1]+1))
ext=ext.cut(cy(7.,EXT_Y[0]-1,EXT_Y[1]+1,25.,98.)).cut(cy(7.,EXT_Y[0]-1,EXT_Y[1]+1,55.,98.))
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=ext
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCREW_R,*SCR_Y,XE,SCREW_Z)
doc.getObject("A3_Motor_6374").Shape=cy(31.5,*MOT_Y,XE,SCREW_Z)
# ---- yoke ----
def plate(z0,z1): return cz(44.,z0,z1).fuse(bar((40.,40.),(0.,0.),30.,26.,z0,z1))
yk = plate(*FORK_Z[0]).fuse(plate(*FORK_Z[1]))
yk = yk.fuse(bx(*EXT_X,EXT_Y[0],34.,EXT_Z[1],FORK_Z[0][1]))          # short flange
yk = yk.fuse(bx(-38.,-12.,-24.,24.,FORK_Z[0][1],FORK_Z[1][0]))       # anterior Z-bridge
yk = yk.cut(cy(SCREW_R+3.,EXT_Y[0]-2,SCR_Y[0]+6.,XE,SCREW_Z))
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))
for x in (20.,60.): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,22.))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
# ---- bracket (boss r=15) ----
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
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z'])).fuse(cz(15.,EAR_Z[0][0],EAR_Z[1][1],*D0))
sb = sb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,52.,b0,b1,*ROD_Z,r_in=11.5))
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0)).cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+.5))
for p in ((0.,-120.),(0.,-160.),(0.,-185.)): sb=sb.cut(cz(7.,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
doc.getObject("P2_ShankBracket_ALU").Shape=sb
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
print("P1 %.1f  P2 %.1f cm3 single closed solids"%(yk.Volume/1000,sb.Volume/1000))
