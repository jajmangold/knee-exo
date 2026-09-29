# -*- coding: utf-8 -*-
"""Anterior motor + screw at pin A means the belt must clear the upright (X -50..-2,
Z 88..128). Move the belt plane OUTBOARD to Z 130-154, motor to Z 140 / anterior 115,
and push the gas spring out to Z 163-177 to make room."""
import math
MOT_OFF, MOT_Z = 115.0, 140.0
GAS_PL, GAS_Z  = 170.0, (163.0, 177.0)
CLEV2_Z = ((156.0,163.0),(177.0,184.0))
COVER_Z = (130.0, 154.0)
A = pinA()
print("clearance arithmetic:")
print("  motor axis X=%.1f (upright anterior face -50) -> %.1f mm clear"
      % (A[0]-MOT_OFF, abs(A[0]-MOT_OFF+31.5+50.0)))
print("  motor<->gas axis separation %.1f mm (need %.1f)"
      % (math.hypot(MOT_OFF, GAS_PL-MOT_Z), 31.5+14.0))
print("  motor to limb axis %.1f mm (thigh R 78, cuff 88)"
      % (math.hypot(A[0]-MOT_OFF, MOT_Z)-31.5))
def build_drive(th):
    plc,L=_plc(th); p=L-T_TUBE
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z if z is not None else Z_PLANE),V(0,1,0))
    d = cz(11.0,101.0,115.0).fuse(cyl(7.5,8.0,BLK[0]+2.0)).fuse(cyl(20.0,*BLK))
    d = d.fuse(cyl(16.0, BLK[0]+4.0, BLK[1], 0.0, 140.0))              # outboard pulley on screw
    d = d.fuse(bx(-20.0, 147.0, BLK[0]+6.0, BLK[1], *COVER_Z))         # belt cover, outboard
    d = d.fuse(cyl(10.0,*THREAD)).fuse(cyl(23.0,p,p+55.0))
    d = d.fuse(cyl(13.0,p+55.0,L-TANG))
    d = d.fuse(bx(-8.0,8.0,L-TANG,L,101.0,115.0)).fuse(cz(11.0,101.0,115.0,0.0,L))
    m = cyl(31.5, BLK[0], BLK[0]+74.0, x=MOT_OFF, z=MOT_Z)
    d.Placement=plc; m.Placement=plc; return d,m,L
def build_gas(th):
    plc,L=_plc(th)
    def gc(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(11.0,*GAS_Z).fuse(gc(6.5,8.0,28.0)).fuse(gc(14.0,28.0,28.0+STROKE+50.0))
    s = s.fuse(gc(4.5,28.0+STROKE+50.0,L-14.0)).fuse(cz(11.0,*GAS_Z,0.0,L))
    s.Placement=plc; return s
globals().update(build_drive=build_drive, build_gas=build_gas, GAS_PL=GAS_PL, GAS_Z=GAS_Z)
# --- P2: move the gas clevis plates outboard to match ---
CLEV_Z=((94.0,101.0),(115.0,122.0)); CUFF_TH=[(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
Ya,Yb = A[1]-18.0, A[1]+19.0; Y_TOP=340.0
Y_TONGUE=(70.0,178.0)
up = bx(CAV_X[0]+0.4,CAV_X[1]-0.4,*Y_TONGUE,CAV_Z[0]+0.4,CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X,Y_TONGUE[1]-6,Y_TOP,*BOX_Z)).cut(bx(*CAV_X,Y_TONGUE[1]+2,Y_TOP+2,*CAV_Z))
up = up.fuse(bx(BOX_X[0]+4,BOX_X[1]-4,190.0,270.0,88.0,100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1))
    gus = bar((-30.0,A[1]-84.0),(A[0],A[1]),12.0,8.0,z0,z1)
    up = up.fuse(gus.common(bx(-60.0,4.0,A[1]-92.0,A[1]+4.0,z0,z1)))
up = up.fuse(bx(-14.0,6.0,Ya,Yb,122.0,184.0))                      # web out to the gas clevis
for z0,z1 in CLEV2_Z: up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1))
up = up.cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*LINK))
up = up.cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*GAS_Z))
up = up.cut(cz(5.15,92.0,190.0,*A))
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25,y0,y0+30.0,BOX_Z[0]-2,BOX_Z[1]+2))
for x,y in CUFF_TH: up = up.cut(cz(3.2,87.0,99.0,x,y))
assert len(up.Solids)==1 and up.isValid(), "P2 %d solids"%len(up.Solids)
doc.getObject("P2_ThighUpright_Upper").Shape = up
# --- P4: gas pocket follows outboard ---
B0 = pinB(0.0)
lk = doc.getObject("P4_ShankLink_Horn").Shape
lk = lk.fuse(cz(16.0,164.0,184.0,*B0))
lk = lk.cut(cz(13.0,*GAS_Z,*B0)).cut(sector_at(B0,52.0,-46.0,126.0,*GAS_Z,r_in=13.0))
lk = lk.cut(cz(5.15,92.0,190.0,*B0))
assert len(lk.Solids)==1 and lk.isValid(), "P4 %d solids"%len(lk.Solids)
doc.getObject("P4_ShankLink_Horn").Shape = lk
print("P2 %.1f  P4 %.1f cm3, single solids" % (up.Volume/1000, lk.Volume/1000))
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_=build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape=d
    doc.getObject("P8_Motor_6374").Shape=m
    doc.getObject("P9_GasSpring").Shape=build_gas(t)
    doc.recompute()
globals()['pose']=pose
pose(0.0); doc.recompute(); doc.save(); print("saved")
