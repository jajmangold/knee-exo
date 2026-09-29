# -*- coding: utf-8 -*-
import math
O=lambda n: doc.getObject(n)
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff"]
SHK=["P2_ShankBracket_ALU","P6_ShankSlideHousing","P7_ShankCuff"]
DRV=["P3_Carriage","P4_Rod_8mm","A2_BallScrew_SFU1620","A3_Motor_6374"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb,skip=()):
    w,nm=0.0,"-"
    for x in la:
        for y in lb:
            if (x,y) in skip or (y,x) in skip: continue
            v=vol(O(x).Shape,O(y).Shape)
            if v>w: w,nm=v,"%s^%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
SKIP={("P3_Carriage","A2_BallScrew_SFU1620"),("P3_Carriage","A1_Extrusion_20x60_VSlot"),
      ("P4_Rod_8mm","P3_Carriage"),("P4_Rod_8mm","P2_ShankBracket_ALU")}   # designed contacts
print("=== full-ROM interference, 3 deg steps ===")
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHK,THIGH,"shank^thigh"),(DRV,THIGH,"drive^thigh"),
                      (DRV,SHK,"drive^shank"),(THIGH+SHK+DRV,LIMB,"struct^limb")):
        v,nm=wp(la,lb,SKIP); w=max(w,v)
        if v>=0.05: off[tag]=(round(max(off.get(tag,(0,""))[0],v),3),nm)
print("  worst %.4f cm3"%w)
print("  offenders:",off if off else "NONE - full ROM clear")
print()
print("=== SEATED (thigh-borne parts, Y 60..380; thigh skin +78) ===")
def xmax_span(s,y0,y1):
    c=s.common(bx(-400.0,400.0,y0,y1,-60.0,300.0))
    return None if c.isNull() or c.Volume<1 else c.BoundBox.XMax
worst=-999
for th in (80.,85.,90.,95.,100.):
    pose(th)
    for n in THIGH+DRV:
        xm=xmax_span(O(n).Shape,60.0,380.0)
        if xm is not None and xm>worst: worst,wn=xm,n
pose(90.0)
for n in THIGH+DRV:
    xm=xmax_span(O(n).Shape,60.0,380.0)
    if xm is not None: print("  %-28s %6.1f  %s"%(n,xm,"clear" if xm<=88.5 else "PROUD %.0f"%(xm-78)))
print("  worst %.1f (%s) -> %s"%(worst,wn,"SEAT CLEAR" if worst<=88.5 else "BLOCKED"))
print()
pose(0.0)
allb=[O(n).Shape.BoundBox for n in THIGH+SHK+DRV]
LAT=max(b.ZMax for b in allb); TOPY=max(b.YMax for b in allb)
print("=== envelope ===")
print("  lateral %.0f mm from midline = %.0f mm outboard of thigh skin"%(LAT,LAT-78))
print("  highest point Y=%.0f = %.0f%% up a 429 mm thigh (hip clearance)"%(TOPY,TOPY/429*100))
print("  carriage travel %.1f -> %.1f mm"%(carr(-2.0),carr(105.0)))
print()
KT=8.27/190.0; FA=2*math.pi*0.9*KT/0.020; J=2.5e-4
print("=== performance ===")
print("  %5s %9s %9s %8s %9s"%("flex","arm mm","F@25N.m","amps","tau@40A"))
for t in (0,30,60,90,105):
    a=armv(float(t)); print("  %5d %9.1f %8.0f N %7.1f %8.1f N.m"%(t,a,25000/a,25000/a/FA,FA*40*a/1000))
n60=(armv(60.0)/1000)/0.020*2*math.pi
print("  swing inertia at 60 deg: +%.0f%% of limb"%(J*n60*n60/0.29*100))
doc.recompute(); doc.save()
