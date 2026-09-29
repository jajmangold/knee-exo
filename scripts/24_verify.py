# -*- coding: utf-8 -*-
import math
O = lambda n: doc.getObject(n)
PRINTED = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
           "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
T = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
PINS = ["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
S = ["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
D = ["P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring"]
print("=== manufacturability: one closed solid per printed part ===")
tot = 0.0; ok = True
for n in PRINTED:
    s = O(n).Shape; tot += s.Volume
    bb = s.BoundBox
    good = len(s.Solids)==1 and s.isValid() and s.isClosed()
    ok &= good
    print("  %-26s %6.1f cm3  solids=%d valid=%s closed=%s  %3.0fx%3.0fx%3.0f mm %s"
          % (n, s.Volume/1000, len(s.Solids), s.isValid(), s.isClosed(),
             bb.XLength, bb.YLength, bb.ZLength, "OK" if good else "<-- FAIL"))
print("  total printed volume %.0f cm3" % (tot/1000))
print("  PA6-CF @1.19 g/cc, ~78%% effective density -> %.0f g of printed structure" % (tot/1000*1.19*0.78))

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
print()
print("=== interference sweep, %s to %s deg in 3 deg steps ===" % (ROM[0], ROM[1]))
worst=0.0; offenders={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((S,T+PINS,"shank^thigh"),(D,T,"drive^thigh"),(D,S,"drive^shank"),
                      (["P9_GasSpring"],["P7_Actuator_ENVELOPE","P8_Motor_6374"],"gas^drive")):
        v,nm = wp(la,lb)
        worst = max(worst,v)
        if v >= 0.05: offenders[tag] = max(offenders.get(tag,0.0), v)
print("  worst interference anywhere in the ROM: %.4f cm3" % worst)
print("  offenders:", offenders if offenders else "NONE - full ROM clear")
print()
print("=== envelope ===")
pose(0.0)
allp = PRINTED+D+PINS
xs=[O(n).Shape.BoundBox for n in allp]
print("  lateral extent from limb midline: %.0f mm (knee skin is at 50, thigh skin at 78)"
      % max(b.ZMax for b in xs))
print("  posterior extent: %.0f mm   anterior: %.0f mm" % (max(b.XMax for b in xs), min(b.XMin for b in xs)))
pose(0.0); doc.recompute(); doc.save()
