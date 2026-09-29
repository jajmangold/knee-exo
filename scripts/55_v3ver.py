# -*- coding: utf-8 -*-
import math
O=lambda n: doc.getObject(n)
PRN=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
     "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
THI=PRN[:3]; SHA=PRN[3:]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
DRV=["P7_Drive_Coaxial","P8_Motor_6374"]; LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
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
    c=s.common(bx(-400.0,400.0,y0,y1,-60.0,300.0))
    return None if c.isNull() or c.Volume<1 else c.BoundBox.XMax
print("=== printed parts ===")
tot=0.0; ok=True
for n in PRN:
    s=O(n).Shape; tot+=s.Volume; bb=s.BoundBox
    good=len(s.Solids)==1 and s.isValid() and s.isClosed(); ok&=good
    print("  %-26s %6.1f cm3 solids=%d closed=%s %3.0fx%3.0fx%3.0f %s"
          %(n,s.Volume/1000,len(s.Solids),s.isClosed(),bb.XLength,bb.YLength,bb.ZLength,"OK" if good else "FAIL"))
print("  all single closed:",ok,"  %.0f cm3 -> %.0f g PA6-CF"%(tot/1000,tot/1000*1.19*0.78))
print()
print("=== SEATED (thigh-borne, Y 60..340) ===")
worst=-999
for th in (80.,85.,90.,95.,100.):
    pose(th)
    for n in DRV+THI:
        xm=xmax_span(O(n).Shape,60.0,340.0)
        if xm is not None and xm>worst: worst,wn=xm,n
pose(90.0)
for n in DRV+THI:
    xm=xmax_span(O(n).Shape,60.0,340.0)
    if xm is not None: print("  %-24s %6.1f  %s"%(n,xm,"clear" if xm<=88.5 else "PROUD %.0f"%(xm-78)))
print("  worst %.1f (%s) -> %s"%(worst,wn,"SEAT CLEAR" if worst<=88.5 else "BLOCKED"))
print()
print("=== full-ROM interference, 3 deg steps ===")
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHA,THI+PINS,"shank^thigh"),(DRV,THI,"drive^thigh"),(DRV,SHA,"drive^shank"),
                      (DRV+THI+SHA,LIMB,"struct^limb")):
        v,nm=wp(la,lb); w=max(w,v)
        if v>=0.05: off[tag]=(round(max(off.get(tag,(0,""))[0],v),3),nm)
print("  worst %.4f cm3"%w)
print("  offenders:",off if off else "NONE")
pose(0.0)
allb=[O(n).Shape.BoundBox for n in PRN+DRV+PINS]
LAT=max(b.ZMax for b in allb)
print()
print("  WIDTH: lateral %.0f mm from midline = %.0f mm outboard of thigh skin"%(LAT,LAT-78))
print("         (v1 posterior-motor build was 164; anterior-belt build was 184)")
doc.recompute(); doc.saveAs(r"C:\Users\Josh\KneeExo_v3.FCStd")
print("saved",doc.FileName)
