# -*- coding: utf-8 -*-
"""Sign fix: local -X maps to GLOBAL POSTERIOR, so anterior needs +80.
Seat check applies to THIGH-borne parts over the seated contact span only (Y 60..300);
the shank hangs off the front edge of the seat and is irrelevant to it."""
import math
MOT_OFF = +80.0                      # local +X  ->  global anterior
def build_drive(th):
    plc,L=_plc(th); p=L-T_TUBE
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    d = cz(11.0,101.0,115.0).fuse(cyl(7.5,8.0,BLK[0]+2.0)).fuse(cyl(20.0,*BLK))
    d = d.fuse(bx(-20.0, 88.0, BLK[0]+6.0, BLK[1], 94.0, 122.0))     # belt cover -> anterior
    d = d.fuse(cyl(10.0,*THREAD)).fuse(cyl(23.0,p,p+55.0))
    d = d.fuse(cyl(13.0,p+55.0,L-TANG))
    d = d.fuse(bx(-8.0,8.0,L-TANG,L,101.0,115.0)).fuse(cz(11.0,101.0,115.0,0.0,L))
    m = cyl(31.5, BLK[0], BLK[0]+74.0, x=MOT_OFF)                     # 6374 -> anterior
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
def xmax_in_span(shape, y0, y1):
    """max posterior X restricted to the seated contact span"""
    clip = bx(-400.0, 400.0, y0, y1, -50.0, 250.0)
    c = shape.common(clip)
    return None if c.isNull() or c.Volume < 1 else c.BoundBox.XMax
print("=== SEATED: thigh-borne parts over the seat contact span Y 60..300 ===")
print("    (thigh skin at X=+78; cuff shell legitimately sits at 88)")
worst = -999; name=""
for th in (85.0, 90.0, 95.0):
    pose(th)
    for n in ("P8_Motor_6374","P7_Actuator_ENVELOPE","P9_GasSpring",
              "P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"):
        xm = xmax_in_span(O(n).Shape, 60.0, 300.0)
        if xm is None: continue
        if xm > worst: worst, name = xm, "%s @%.0fdeg" % (n, th)
        if th == 90.0:
            print("   %-26s XMax %6.1f  %s" % (n, xm, "clear" if xm <= 88.5 else "PROUD %.0f mm"%(xm-78)))
print("   worst over 85-95 deg: %.1f  (%s)" % (worst, name))
print("   verdict:", "SEAT CLEAR - nothing but the padded cuff shell touches" if worst<=88.5 else "STILL BLOCKED")
print()
print("=== motor vs limb (anterior side) ===")
pose(90.0)
for l in ("REF_Thigh","REF_Knee"):
    c = O("P8_Motor_6374").Shape.common(O(l).Shape)
    print("   motor ^ %-10s %s" % (l, "clear" if (c.isNull() or c.Volume<1) else "OVERLAP %.2f cm3"%(c.Volume/1000)))
c = O("P8_Motor_6374").Shape.common(O("P3_ThighCuff").Shape)
print("   motor ^ ThighCuff  %s" % ("clear" if (c.isNull() or c.Volume<1) else "OVERLAP %.2f cm3"%(c.Volume/1000)))
pose(0.0); doc.recompute()
