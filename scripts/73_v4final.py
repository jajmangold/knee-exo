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
      ("P5_ThighCuff","A1_Extrusion_20x60_VSlot"),("A3_Motor_6374","A2_BallScrew_SFU1620")}
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
print("=== full-ROM interference, 3 deg ===")
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHK,THIGH,"shank^thigh"),(DRV,THIGH,"drive^thigh"),
                      (DRV,SHK,"drive^shank"),(THIGH+DRV,LIMB,"thighside^limb")):
        v,nm=wp(la,lb); w=max(w,v)
        if v>=0.05: off[tag]=(round(max(off.get(tag,(0,""))[0],v),3),nm)
print("  worst %.4f cm3 ; offenders: %s"%(w,off if off else "NONE - full ROM clear"))
print()
def Rth(y): return 62.0+(85.0-62.0)*max(0.0,min(y,300.0))/300.0
print("=== SEATED: thigh-borne parts + the rod, over the seat contact span ===")
SEATP=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","P3_Carriage",
       "A2_BallScrew_SFU1620","A3_Motor_6374","P4_Rod_8mm"]
worst=-999; wn=""
for th in (80.,85.,90.,95.,100.,105.):
    pose(th)
    for n in SEATP:
        bb=O(n).Shape.BoundBox
        for i in range(16):
            y=max(60.0,bb.YMin)+ (max(bb.YMax,60.0)-max(60.0,bb.YMin))*i/15.0
            if y<60.0 or y>380.0: continue
            sl=O(n).Shape.common(bx(-400.,400.,y-2.,y+2.,-60.,300.))
            if sl.isNull() or sl.Volume<1: continue
            p=sl.BoundBox.XMax-Rth(y)
            if p>worst: worst,wn=p,"%s @%.0f Y%.0f"%(n.split('_')[0],th,y)
print("  worst protrusion past the thigh underside: %+.1f mm (%s)"%(worst,wn))
print("  -> %s"%("SEAT CLEAR (cuff shell only)" if worst<=11.0 else "FOULS SEAT"))
pose(0.0)
allb=[O(n).Shape.BoundBox for n in THIGH+SHK+DRV]
LAT=max(b.ZMax for b in allb); TOP=max(b.YMax for b in allb)
print()
print("=== envelope / mass ===")
print("  lateral %.0f mm (%.0f outboard of thigh skin) | top Y=%.0f (%.0f%% thigh) | travel %.0f"
      %(LAT,LAT-78,TOP,TOP/429*100,carr(105.0)-carr(-2.0)))
PR=["P1_KneeYoke","P5_ThighCuff","P6_ShankSlideHousing","P7_ShankCuff"]
tot=sum(O(n).Shape.Volume for n in PR)
print("  printed %.0f cm3 -> %.0f g PA6-CF   |  ALU bracket %.0f g  |  extrusion %.0f g"
      %(tot/1000,tot/1000*1.19*.78, O("P2_ShankBracket_ALU").Shape.Volume/1000*2.70,
        (275-10)/1000*1.6*1000/1000*1000/1000))
for n in PR+["P2_ShankBracket_ALU"]:
    s=O(n).Shape
    print("    %-26s %6.1f cm3 solids=%d closed=%s"%(n,s.Volume/1000,len(s.Solids),s.isClosed()))
doc.recompute(); doc.save(); print("\nsaved",doc.FileName)
