# -*- coding: utf-8 -*-
import math
O=lambda n: doc.getObject(n)
PRN=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
     "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
THI=PRN[:3]; SHA=PRN[3:]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
DRV=["P7_Actuator_ENVELOPE","P8_Motor_6374","P9_GasSpring"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w=0.0
    for x in la:
        for y in lb: w=max(w,vol(O(x).Shape,O(y).Shape))
    return w
w=0.0
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    w=max(w, wp(SHA,THI+PINS), wp(DRV,THI), wp(DRV,SHA),
          wp(["P9_GasSpring"],["P7_Actuator_ENVELOPE","P8_Motor_6374"]))
print("worst real interference over full ROM (motor<->its own belt cover excluded): %.4f cm3"%w)
print()
KT=8.27/190.0; F_A=2*math.pi*0.90*KT/0.020
print("%5s %7s %9s %9s %9s | %s"%("flex","arm mm","F_gas N","tau_gas","tau@40A","total"))
for th in (0,30,45,60,75,90,105):
    a_=arm(float(th)); L=ab(float(th))
    Fg=200.0*(1.0+0.30*(L_EXT-L)/STROKE); tg=Fg*a_/1000.0; tm=F_A*40.0*a_/1000.0
    print("%5d %7.1f %9.0f %9.1f %9.1f | %.1f N.m"%(th,a_,Fg,tg,tm,tg+tm))
pose(0.0); doc.recompute(); doc.save()
print("\nsaved", doc.FileName)
