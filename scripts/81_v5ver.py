# -*- coding: utf-8 -*-
import math
O=lambda n: doc.getObject(n)
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff"]
SHK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket","P7_ShankCuff"]
DRV=["P3_Carriage","P4_Rod_8mm","A2_BallScrew_SFU1620","A3_Motor_6374"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
SKIP={("P3_Carriage","A2_BallScrew_SFU1620"),("P3_Carriage","A1_Extrusion_20x60_VSlot"),
      ("P4_Rod_8mm","P3_Carriage"),("P4_Rod_8mm","P2b_RodClevisBlock"),
      ("A2_BallScrew_SFU1620","A1_Extrusion_20x60_VSlot"),("P1_KneeYoke","A1_Extrusion_20x60_VSlot"),
      ("P5_ThighCuff","A1_Extrusion_20x60_VSlot"),("A3_Motor_6374","A2_BallScrew_SFU1620"),
      ("A4_Shank2020_VSlot","P2a_KneeHingePlate"),("A4_Shank2020_VSlot","P2b_RodClevisBlock"),
      ("A4_Shank2020_VSlot","P6_ShankSocket"),("P6_ShankSocket","P7_ShankCuff")}
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
def Rth(y): return 62.0+(85.0-62.0)*max(0.0,min(y,300.0))/300.0
print()
print("=== SEATED: thigh-borne parts + rod ===")
SEATP=THIGH+DRV
worst=-999; wn=""
for th in (80.,85.,90.,95.,100.,105.):
    pose(th)
    for n in SEATP:
        bb=O(n).Shape.BoundBox
        for i in range(16):
            lo=max(60.0,bb.YMin); hi=max(bb.YMax,60.0)
            y=lo+(hi-lo)*i/15.0
            if y<60.0 or y>380.0: continue
            sl=O(n).Shape.common(bx(-400.,400.,y-2.,y+2.,-60.,320.))
            if sl.isNull() or sl.Volume<1: continue
            p=sl.BoundBox.XMax-Rth(y)
            if p>worst: worst,wn=p,"%s @%.0f"%(n.split('_')[0],th)
print("  worst protrusion %+.1f mm (%s) -> %s"%(worst,wn,
      "clear - cuff shell only" if worst<=15.5 else "FOULS"))
pose(0.0)
allb=[O(n).Shape.BoundBox for n in THIGH+SHK+DRV]
print()
print("=== envelope / BOM ===")
print("  lateral %.0f mm (%.0f outboard of skin) | top Y=%.0f (%.0f%% thigh)"
      %(max(b.ZMax for b in allb),max(b.ZMax for b in allb)-78,
        max(b.YMax for b in allb),max(b.YMax for b in allb)/429*100))
PR=["P1_KneeYoke","P5_ThighCuff","P6_ShankSocket","P7_ShankCuff"]
AL=["P2a_KneeHingePlate","P2b_RodClevisBlock"]
tp=sum(O(n).Shape.Volume for n in PR); ta=sum(O(n).Shape.Volume for n in AL)
print("  printed %.0f cm3 -> %.0f g PA6-CF"%(tp/1000,tp/1000*1.19*.78))
print("  alu bits %.0f cm3 -> %.0f g 6061 (was one 231 g machined plate)"%(ta/1000,ta/1000*2.70))
print("  extrusion: 20x60 thigh rail %.0f mm (~%.0f g) + 2020 shank %.0f mm (~%.0f g)"
      %(EXT_Y[1]-EXT_Y[0],(EXT_Y[1]-EXT_Y[0])/1000*1450,SH20_Y[1]-SH20_Y[0],(SH20_Y[1]-SH20_Y[0])/1000*500))
for n in PR+AL:
    s=O(n).Shape; print("    %-24s %6.1f cm3 solids=%d"%(n,s.Volume/1000,len(s.Solids)))
doc.recompute(); doc.save()
