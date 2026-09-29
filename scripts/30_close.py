# -*- coding: utf-8 -*-
"""Last two clashes:
 (1) screw support block started at local y=12 -> Y=287, inside the pin-A clevis. -> y=20
 (2) gas cylinder (r14 @Z143) vs ball-nut housing (r23 @Z108): 35 mm apart, needs 37.
     -> gas plane 143 -> 150, clevis plates follow."""
import math
A = pinA(); B0 = pinB(0.0)
L_RET, L_EXT = ab(ROM[1]), ab(ROM[0]); STROKE = L_EXT-L_RET
NUT, TANG, T_TUBE = 50.0, 35.0, 190.0
THREAD = (L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0)
BLK = (20.0, 56.0)
GAS_PL, GAS_Z = 150.0, (143.0, 157.0)
CLEV_Z, CLEV2_Z = ((94.0,101.0),(115.0,122.0)), ((136.0,143.0),(157.0,164.0))
CUFF_TH_PTS = [(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
Ya, Yb = A[1]-18.0, A[1]+19.0
Y_TOP = 340.0
print("gas plane %.0f vs drive plane %.0f -> gap %.0f (need r23+r14=37)" % (GAS_PL, Z_PLANE, GAS_PL-Z_PLANE))
assert GAS_PL-Z_PLANE >= 37.0 and THREAD[0] >= BLK[1]-2

# ---- P4 full rebuild (fork horn + gas pocket at the new plane) ----
SLOT_Z, CHEEK_Z, R_CHEEK = (99.8,116.2), (94.0,122.0), (34.0,80.0)
ann_cheek = cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot  = cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk = cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk = lk.fuse(cz(16.0,*CHEEK_Z,*B0)).fuse(cz(16.0,122.0,164.0,*B0))
lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk = lk.fuse(bx(*TONGUE['x'],*TONGUE['y'],*TONGUE['z']))
slot = cz(22.0,*SLOT_Z,*B0).fuse(sector_at(B0,44.0,-40.0,120.0,*SLOT_Z,r_in=22.0))
lk = lk.cut(slot.common(ann_slot)).cut(cz(12.5,*SLOT_Z,*B0))
lk = lk.cut(cz(12.5,*GAS_Z,*B0)).cut(sector_at(B0,44.0,-40.0,120.0,*GAS_Z,r_in=12.5))
lk = lk.cut(cz(5.15,92.0,168.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk = lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk = lk.cut(cz(3.1,TONGUE['z'][0]-2,TONGUE['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid(), "P4 %d solids" % len(lk.Solids)
doc.getObject("P4_ShankLink_Horn").Shape = lk
print("P4 %.1f cm3 solids=1" % (lk.Volume/1000))

# ---- P2 rebuild with clevis plates at the new gas plane ----
up = bx(CAV_X[0]+0.4,CAV_X[1]-0.4,*Y_TONGUE,CAV_Z[0]+0.4,CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X,Y_TONGUE[1]-6,Y_TOP,*BOX_Z)).cut(bx(*CAV_X,Y_TONGUE[1]+2,Y_TOP+2,*CAV_Z))
up = up.fuse(bx(BOX_X[0]+4,BOX_X[1]-4,190.0,270.0,88.0,100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1)).fuse(bar((-30.0,A[1]-84.0),(A[0],A[1]),12.0,8.0,z0,z1))
up = up.fuse(bx(-14.0,6.0,Ya,Yb,122.0,164.0))
for z0,z1 in CLEV2_Z: up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1))
up = up.cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*LINK))
up = up.cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*GAS_Z))
up = up.cut(cz(5.15,92.0,168.0,*A))
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25,y0,y0+30.0,BOX_Z[0]-2,BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2,87.0,99.0,x,y))
assert len(up.Solids)==1 and up.isValid(), "P2 %d solids" % len(up.Solids)
doc.getObject("P2_ThighUpright_Upper").Shape = up
print("P2 %.1f cm3 solids=1" % (up.Volume/1000))

def _plc(th):
    B=pinB(th); L=ab(th); ux,uy=(B[0]-A[0])/L,(B[1]-A[1])/L
    return FreeCAD.Placement(V(A[0],A[1],0.0),FreeCAD.Rotation(V(0,0,1),math.degrees(math.atan2(-ux,uy)))), L
def build_drive(th):
    plc,L=_plc(th); p=L-T_TUBE
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    d = cz(11.0,101.0,115.0).fuse(cyl(7.5,8.0,BLK[0]+2.0)).fuse(cyl(20.0,*BLK))
    d = d.fuse(bx(-88.0,20.0,BLK[0]+6.0,BLK[1],94.0,122.0)).fuse(cyl(10.0,*THREAD))
    d = d.fuse(cyl(23.0,p,p+55.0)).fuse(cyl(13.0,p+55.0,L-TANG))
    d = d.fuse(bx(-8.0,8.0,L-TANG,L,101.0,115.0)).fuse(cz(11.0,101.0,115.0,0.0,L))
    m = cyl(31.5,BLK[0],BLK[0]+74.0,x=-62.0)
    d.Placement=plc; m.Placement=plc; return d,m,L
def build_gas(th):
    plc,L=_plc(th)
    def gc(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(11.0,*GAS_Z).fuse(gc(6.5,8.0,28.0)).fuse(gc(14.0,28.0,28.0+STROKE+50.0))
    s = s.fuse(gc(4.5,28.0+STROKE+50.0,L-14.0)).fuse(cz(11.0,*GAS_Z,0.0,L))
    s.Placement=plc; return s
globals().update(build_drive=build_drive,build_gas=build_gas,GAS_PL=GAS_PL,GAS_Z=GAS_Z)
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_=build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape=d
    doc.getObject("P8_Motor_6374").Shape=m
    doc.getObject("P9_GasSpring").Shape=build_gas(t)
    doc.recompute()
globals()['pose']=pose
doc.getObject("HW_PinA_M8x40").Shape = cz(5.0,92.0,168.0,*A)
doc.getObject("HW_PinB_M8x36_quickpull").Shape = cz(5.0,92.0,168.0,*B0)
pose(0.0); doc.recompute(); doc.save(); print("saved")
