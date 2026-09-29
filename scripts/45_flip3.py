# -*- coding: utf-8 -*-
"""Motor anterior offset 100 mm: clears the cuff's lateral mounting pad (X -46..-6,
Z 76..88) and sits proud of the anterior thigh - on top of the front of the thigh."""
import math
MOT_OFF, MOT_Z = 100.0, 108.0
def build_drive(th):
    plc,L=_plc(th); p=L-T_TUBE
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    d = cz(11.0,101.0,115.0).fuse(cyl(7.5,8.0,BLK[0]+2.0)).fuse(cyl(20.0,*BLK))
    d = d.fuse(bx(-20.0, 132.0, BLK[0]+6.0, BLK[1], 94.0, 122.0))    # belt cover spans to motor
    d = d.fuse(cyl(10.0,*THREAD)).fuse(cyl(23.0,p,p+55.0))
    d = d.fuse(cyl(13.0,p+55.0,L-TANG))
    d = d.fuse(bx(-8.0,8.0,L-TANG,L,101.0,115.0)).fuse(cz(11.0,101.0,115.0,0.0,L))
    m = cyl(31.5, BLK[0], BLK[0]+74.0, x=MOT_OFF, z=MOT_Z)
    d.Placement=plc; m.Placement=plc; return d,m,L
globals()['build_drive']=build_drive
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_=build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape=d
    doc.getObject("P8_Motor_6374").Shape=m
    doc.getObject("P9_GasSpring").Shape=build_gas(t)
    doc.recompute()
globals()['pose']=pose
O=lambda n: doc.getObject(n)
THI=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
SHA=["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
DRV=["P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w,nm=0.0,"-"
    for x in la:
        for y in lb:
            v=vol(O(x).Shape,O(y).Shape)
            if v>w: w,nm=v,"%s^%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
def xmax_span(s,y0,y1):
    c=s.common(bx(-400.0,400.0,y0,y1,-50.0,250.0))
    return None if c.isNull() or c.Volume<1 else c.BoundBox.XMax
print("=== SEATED (thigh-borne, Y 60..300; skin +78, cuff shell 88) ===")
worst=-999
for th in (85.0,90.0,95.0):
    pose(th)
    for n in DRV+THI:
        xm=xmax_span(O(n).Shape,60.0,300.0)
        if xm is not None: worst=max(worst,xm)
pose(90.0)
for n in DRV+THI:
    xm=xmax_span(O(n).Shape,60.0,300.0)
    if xm is not None: print("   %-26s %6.1f  %s"%(n,xm,"clear" if xm<=88.5 else "PROUD"))
print("   worst %.1f -> %s"%(worst,"SEAT CLEAR" if worst<=88.5 else "BLOCKED"))
print()
print("=== full-ROM interference, 3 deg steps ===")
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHA,THI+PINS,"shank^thigh"),(DRV,THI,"drive^thigh"),
                      (DRV,SHA,"drive^shank"),(["P9_GasSpring"],["P7_Actuator_ENVELOPE","P8_Motor_6374"],"gas^drive"),
                      (DRV+THI+SHA,LIMB,"struct^limb")):
        v,nm=wp(la,lb); w=max(w,v)
        if v>=0.05: off[tag]=(round(max(off.get(tag,(0,""))[0],v),3),nm)
print("   worst %.4f cm3"%w)
print("   offenders:", off if off else "NONE - full ROM clear")
pose(0.0); doc.recompute(); doc.save()
print("saved")
