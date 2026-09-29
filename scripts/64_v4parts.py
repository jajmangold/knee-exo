# -*- coding: utf-8 -*-
"""v4 parts. Z stack: extrusion 88-108 | carriage 108-122 | screw 115 | rod 121-133
   knee fork 108-120 & 134-146 | shank bracket 122-132 (ALU).  Max lateral 146.5."""
import math
EXT_Z=(88.0,108.0); CAR_Z=(108.0,122.0); SCREW_Z=115.0
ROD_Z=(121.0,133.0); EAR_Z=((115.0,121.0),(133.0,139.0))
FORK_Z=((108.0,120.0),(134.0,146.0)); SBR_Z=(122.0,132.0)
TONG=dict(x=(-13.0,13.0),y=(-200.0,-153.0),z=(122.0,132.0))
Y_THC=(150.0,260.0)          # cuff pulled down so the motor clears it
g=globals(); g.update(EXT_Z=EXT_Z,CAR_Z=CAR_Z,SCREW_Z=SCREW_Z,ROD_Z=ROD_Z,EAR_Z=EAR_Z,
                      FORK_Z=FORK_Z,SBR_Z=SBR_Z,TONG=TONG,Y_THC=Y_THC)
# ---------- P1 knee yoke (printed PA6-CF) ----------
yk = bar((40.0,45.0),(0.0,0.0),34.0,30.0,FORK_Z[0][0],FORK_Z[1][1])
yk = yk.cut(cz(72.0,SBR_Z[0]-2.0,SBR_Z[1]+2.0))                     # gap for the shank bracket
yk = yk.fuse(bx(EXT_X[0],EXT_X[1],15.0,80.0,EXT_Z[1],FORK_Z[0][1])) # flange onto the rail face
yk = yk.cut(cz(6.15,FORK_Z[0][0]-2,FORK_Z[1][1]+2))                 # knee pivot bore
for x in (20.0,60.0):
    for y in (28.0,62.0): yk=yk.cut(cz(2.6,EXT_Z[1]-1,FORK_Z[0][1]+1,x,y))   # M5 into T-slots
for p in ((18.0,20.0),(46.0,26.0)): yk=yk.cut(cz(9.0,FORK_Z[0][0]-1,FORK_Z[0][1]+1,*p))
assert len(yk.Solids)==1 and yk.isValid() and yk.isClosed(),"P1 %d"%len(yk.Solids)
add("P1_KneeYoke",yk,(0.20,0.42,0.75),G_T)
# ---------- P2 shank bracket (ALUMINIUM 10 mm) ----------
sb = bar((0.0,0.0),D0,26.0,20.0,*SBR_Z)
sb = sb.fuse(bar(D0,(0.0,-205.0),20.0,18.0,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
for z0,z1 in EAR_Z: sb = sb.fuse(cz(18.0,z0,z1,*D0))                # rod clevis ears
sb = sb.cut(cz(13.0,*ROD_Z,*D0))                                    # rod eye pocket
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))                # 8 mm rod pin
sb = sb.cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))                         # knee pivot
sb = sb.cut(cz(10.6,SBR_Z[0]-0.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+0.5))
for p in ((14.0,-52.0),(22.0,-88.0),(0.0,-150.0),(0.0,-180.0)):
    sb = sb.cut(cz(8.0,SBR_Z[0]-1,SBR_Z[1]+1,*p))
sb = sb.cut(cz(3.1,TONG['z'][0]-2,TONG['z'][1]+2,0.0,-181.0))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
add("P2_ShankBracket_ALU",sb,(0.70,0.72,0.75),G_S)
# ---------- P3 carriage + rod clevis ----------
def build_carriage(t):
    s=carr(t)
    c = bx(EXT_X[0]-6.0,EXT_X[1]+6.0,s-38.0,s+38.0,*CAR_Z)          # gantry plate
    c = c.fuse(bx(30.0,50.0,s-26.0,s+26.0,CAR_Z[1],EAR_Z[1][1]))    # clevis body
    c = c.cut(bx(28.0,52.0,s-28.0,s+28.0,*ROD_Z))                   # rod eye gap
    c = c.fuse(cz(14.0,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c = c.cut(cz(13.0,*ROD_Z,XE,s)).cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s))
    c = c.cut(cz(SCREW_R+1.0,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))           # screw passes through
    return c
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    r = Part.makeCylinder(4.0,L,V(D[0],D[1],(ROD_Z[0]+ROD_Z[1])/2),V(ux,uy,0.0))
    r = r.fuse(cz(11.0,*ROD_Z,*D)).fuse(cz(11.0,*ROD_Z,*C))
    return r
def build_screw(t):
    return cy(SCREW_R,20.0,300.0,XE,SCREW_Z)
def build_motor(t):
    return cy(31.5,302.0,376.0,XE,SCREW_Z)
add("P3_Carriage",build_carriage(0.0),(0.30,0.32,0.36),G_D)
add("P4_Rod_8mm",build_rod(0.0),(0.85,0.85,0.88),G_D)
add("A2_BallScrew_SFU1620",build_screw(0.0),(0.55,0.57,0.60),G_D)
add("A3_Motor_6374",build_motor(0.0),(0.15,0.15,0.18),G_D)
# ---------- cuffs + slide housing ----------
def cuff(ri,ro,ys,pts,padz):
    c=arc_shell(ri,ro,*ys).fuse(bx(-30.0,30.0,ys[0]+5,ys[1]-5,padz[0],padz[1]))
    for x,y in pts: c=c.cut(cz(2.75,padz[0]-2,padz[1]+2,x,y))
    for b in (256.0,64.0):
        for y in (ys[0]+22,ys[1]-22):
            sl=bx(-2.6,2.6,y-20.0,y+20.0,ri-6.0,ro+6.0)
            sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); c=c.cut(sl)
    return c
CUFF_TH=[(20.0,Y_THC[0]+22),(60.0,Y_THC[0]+22),(20.0,Y_THC[1]-22),(60.0,Y_THC[1]-22)]
tc=arc_shell(R_TH+PAD,R_TH+PAD+SHELL,*Y_THC)
tc=tc.fuse(bx(EXT_X[0],EXT_X[1],Y_THC[0]+5,Y_THC[1]-5,76.0,EXT_Z[0]))   # pad up to the rail
for x,y in CUFF_TH: tc=tc.cut(cz(2.6,74.0,EXT_Z[0]+1,x,y))
for b in (256.0,64.0):
    for y in (Y_THC[0]+18,Y_THC[1]-18):
        sl=bx(-2.6,2.6,y-18.0,y+18.0,R_TH+PAD-6.0,R_TH+PAD+SHELL+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); tc=tc.cut(sl)
assert len(tc.Solids)==1
add("P5_ThighCuff",tc,(0.95,0.62,0.10),G_T)
SOCK=dict(x=(-22.0,22.0),y=(-218.0,-148.0),z=(117.0,137.0))
hs=bx(*SOCK['x'],*SOCK['y'],*SOCK['z'])
hs=hs.cut(bx(TONG['x'][0]-0.4,TONG['x'][1]+0.4,-219.0,-160.0,TONG['z'][0]-0.4,TONG['z'][1]+0.4))
hs=hs.cut(bx(-3.0,3.0,-193.0,-168.0,134.0,139.0))
hs=hs.fuse(bx(-30.0,30.0,-273.0,-163.0,68.0,78.0)).fuse(bx(-8.0,8.0,-262.0,-174.0,76.0,119.0))
for xa,xb in ((14.0,22.0),(-22.0,-14.0)): hs=hs.fuse(bx(xa,xb,-258.0,-178.0,70.0,119.0))
CUFF_SH=[(-22.0,-190.0),(22.0,-190.0),(-22.0,-246.0),(22.0,-246.0)]
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.0,79.0,x,y))
assert len(hs.Solids)==1
add("P6_ShankSlideHousing",hs,(0.85,0.35,0.15),G_S)
add("P7_ShankCuff",cuff(R_SH+PAD,R_SH+PAD+SHELL,Y_SHC,CUFF_SH,(56.0,68.0)),(0.95,0.62,0.10),G_S)
# ---------- pose ----------
SHANK=[doc.getObject(n) for n in ("P2_ShankBracket_ALU","P6_ShankSlideHousing","P7_ShankCuff","REF_Shank")]
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
g.update(pose=pose,build_carriage=build_carriage,build_rod=build_rod,SHANK=SHANK)
pose(0.0); doc.recompute()
print("v4 parts built.")
for n in ("P1_KneeYoke","P2_ShankBracket_ALU","P5_ThighCuff","P6_ShankSlideHousing","P7_ShankCuff"):
    s=doc.getObject(n).Shape
    print("  %-26s %6.1f cm3 solids=%d closed=%s"%(n,s.Volume/1000,len(s.Solids),s.isClosed()))
