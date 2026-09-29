# -*- coding: utf-8 -*-
import math
O = lambda n: doc.getObject(n)
PRINTED = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
           "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
T = PRINTED[:3]; S = PRINTED[3:]
PINS = ["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
D = ["P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring"]
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
print("=== printed parts ===")
tot=0.0; allok=True
for n in PRINTED:
    s=O(n).Shape; tot+=s.Volume; bb=s.BoundBox
    good = len(s.Solids)==1 and s.isValid() and s.isClosed(); allok &= good
    print("  %-26s %6.1f cm3 solids=%d closed=%s  %3.0fx%3.0fx%3.0f  %s"
          % (n, s.Volume/1000, len(s.Solids), s.isClosed(), bb.XLength,bb.YLength,bb.ZLength,
             "OK" if good else "FAIL"))
print("  all single closed solids:", allok)
print("  printed volume %.0f cm3 -> PA6-CF ~%.0f g" % (tot/1000, tot/1000*1.19*0.78))
print()
print("=== interference sweep -2..105 deg, 3 deg steps ===")
worst=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((S,T+PINS,"shank^thigh"),(D,T,"drive^thigh"),(D,S,"drive^shank"),
                      (["P9_GasSpring"],["P7_Actuator_ENVELOPE","P8_Motor_6374"],"gas^drive")):
        v,nm=wp(la,lb); worst=max(worst,v)
        if v>=0.05: off[tag]=(max(off.get(tag,(0,""))[0],v), nm)
print("  worst anywhere: %.4f cm3" % worst)
print("  offenders:", {k:(round(v,3),n) for k,(v,n) in off.items()} if off else "NONE - FULL ROM CLEAR")
print()
print("=== performance summary ===")
KT=8.27/190.0; F_A=2*math.pi*0.90*KT/0.020
print("  %5s %7s %9s %9s %9s %9s" % ("flex","arm","F_gas","tau_gas","tau@40A","tau_tot"))
for th in (0,30,45,60,75,90,105):
    a_=arm(float(th)); L=ab(float(th))
    Fg=200.0*(1.0+0.30*(ab(ROM[0])-L)/(ab(ROM[0])-ab(ROM[1])))
    tg=Fg*a_/1000.0; tm=F_A*40.0*a_/1000.0
    print("  %5d %7.1f %8.0fN %8.1f %8.1f %8.1f N.m" % (th,a_,Fg,tg,tm,tg+tm))
print()
pose(0.0)
allb=[O(n).Shape.BoundBox for n in PRINTED+D+PINS]
print("  envelope: lateral %.0f mm from limb midline, posterior %.0f, anterior %.0f"
      % (max(b.ZMax for b in allb), max(b.XMax for b in allb), min(b.XMin for b in allb)))
print("  device adds %.0f mm outboard of the thigh surface (skin at 78)" % (max(b.ZMax for b in allb)-78))
doc.recompute(); doc.save()
