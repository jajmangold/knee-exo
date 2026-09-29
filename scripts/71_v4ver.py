# -*- coding: utf-8 -*-
import math
O=lambda n: doc.getObject(n)
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff"]
SHK=["P2_ShankBracket_ALU","P6_ShankSlideHousing","P7_ShankCuff"]
DRV=["P3_Carriage","P4_Rod_8mm","A2_BallScrew_SFU1620","A3_Motor_6374"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
SKIP={("P3_Carriage","A2_BallScrew_SFU1620"),("P3_Carriage","A1_Extrusion_20x60_VSlot"),
      ("P4_Rod_8mm","P3_Carriage"),("P4_Rod_8mm","P2_ShankBracket_ALU"),
      ("A2_BallScrew_SFU1620","A1_Extrusion_20x60_VSlot"),("P1_KneeYoke","A1_Extrusion_20x60_VSlot"),
      ("P5_ThighCuff","A1_Extrusion_20x60_VSlot")}
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w,nm=0.0,"-"
    for x in la:
        for y in lb:
            if (x,y) in SKIP or (y,x) in SKIP: continue
            v=vol(O(x).Shape,O(y).Shape)
            if v>w: w,nm=v,"%s^%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
def Rth(y): return 62.0+(85.0-62.0)*max(0.0,min(y,300.0))/300.0
print("=== full-ROM interference, 3 deg ===")
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHK,THIGH,"shank^thigh"),(DRV,THIGH,"drive^thigh"),
                      (DRV,SHK,"drive^shank"),(THIGH+SHK+DRV,LIMB,"struct^limb")):
        v,nm=wp(la,lb); w=max(w,v)
        if v>=0.05: off[tag]=(round(max(off.get(tag,(0,""))[0],v),3),nm)
print("  worst %.4f cm3 ; offenders: %s"%(w,off if off else "NONE"))
print()
print("=== SEATED: protrusion past the seat plane (thigh underside) ===")
worst=-999; wn=""
for th in (80.,85.,90.,95.,100.,105.):
    pose(th)
    for n in THIGH+SHK+DRV:
        bb=O(n).Shape.BoundBox
        for y in [bb.YMin+ (bb.YLength*i/12.0) for i in range(13)]:
            if y<60.0: continue
            sl=O(n).Shape.common(bx(-400.,400.,y-2.,y+2.,-60.,300.))
            if sl.isNull() or sl.Volume<1: continue
            p=sl.BoundBox.XMax-Rth(y)
            if p>worst: worst,wn=p,"%s @%.0fdeg Y%.0f"%(n,th,y)
print("  worst protrusion %+.1f mm (%s) -> %s"%(worst,wn,"SEAT CLEAR" if worst<=10.0 else "FOULS SEAT"))
pose(0.0)
allb=[O(n).Shape.BoundBox for n in THIGH+SHK+DRV]
print()
print("  lateral %.0f mm (%.0f outboard of skin) | top Y=%.0f (%.0f%% thigh) | travel %.0f mm"
      %(max(b.ZMax for b in allb),max(b.ZMax for b in allb)-78,max(b.YMax for b in allb),
        max(b.YMax for b in allb)/429*100, carr(105.0)-carr(-2.0)))
doc.recompute(); doc.save()
