# -*- coding: utf-8 -*-
import math
O = lambda n: doc.getObject(n)
THIGH = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff","REF_Thigh","REF_Knee"]
PINS  = ["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
MOV   = ["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff","REF_Shank"]

def vol(a, b):
    try:
        if a.isNull() or b.isNull(): return 0.0
        if not a.BoundBox.intersect(b.BoundBox): return 0.0
        c = a.common(b)
        return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0

print("theta |  mov/thigh   mov/pins  act/thigh  act/shank |  arm_geo arm_fml  pin-pin")
print("------+----------------------------------------------+-------------------------")
worst = {}
for th in [-2,0,5,15,30,45,60,75,90,100,104,105]:
    pose(float(th))
    act = O("P7_Actuator_ENVELOPE").Shape
    c1 = max(vol(O(m).Shape, O(t).Shape) for m in MOV for t in THIGH)
    c2 = max(vol(O(m).Shape, O(p).Shape) for m in MOV for p in PINS)
    c3 = max(vol(act, O(t).Shape) for t in THIGH)
    c4 = max(vol(act, O(m).Shape) for m in MOV if m != "REF_Shank")
    Bp, Ap = pinB(float(th)), pinA()
    dx, dy = Bp[0]-Ap[0], Bp[1]-Ap[1]; L = math.hypot(dx,dy)
    arm_geo = abs(dx*(0-Ap[1]) - dy*(0-Ap[0]))/L
    print("%5.0f | %10.2f %10.2f %10.2f %10.2f | %7.1f %7.1f %8.1f"
          % (th, c1,c2,c3,c4, arm_geo, arm(float(th)), L))
    for k,v in (("mov/thigh",c1),("mov/pins",c2),("act/thigh",c3),("act/shank",c4)):
        worst[k] = max(worst.get(k,0.0), v)
print("\nworst intersection (cm3):", {k:round(v,3) for k,v in worst.items()})
for th, lab in ((-2.0,"extension"), (105.0,"flexion")):
    pose(th)
    for p in PINS:
        v = vol(O("P4_ShankLink_Horn").Shape, O(p).Shape)
        if v > 0.001: print("  %s stop engaged: finger vs %s = %.2f cm3" % (lab, p, v))
pose(0.0)
