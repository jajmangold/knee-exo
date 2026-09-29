# -*- coding: utf-8 -*-
import math
O = lambda n: doc.getObject(n)
T = ["P1_ThighUpright_Lower","P2_ThighUpright_Upright" if False else "P2_ThighUpright_Upper","P3_ThighCuff"]
PINS = ["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
S = ["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
D = ["P7_Actuator_ENVELOPE","P8_Motor_6374"]
LIMB = ["REF_Thigh","REF_Knee","REF_Shank"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c = a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w,nm = 0.0,"-"
    for x in la:
        for y in lb:
            v = vol(O(x).Shape,O(y).Shape)
            if v>w: w,nm = v,"%s/%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
print("th    | shank^thigh   | drive^thigh   | drive^shank   | ALL^limb(flesh)")
print("------+---------------+---------------+---------------+-----------------")
acc={}
for th in [-2,0,5,15,30,45,60,75,90,100,105]:
    pose(float(th))
    a,an = wp(S, T+PINS); b,bn = wp(D, T); c,cn = wp(D, S); d,dn = wp(T+S+D, LIMB)
    print("%5.0f | %6.2f %-7s| %6.2f %-7s| %6.2f %-7s| %6.2f %s"%(th,a,an,b,bn,c,cn,d,dn))
    for k,v in (("shank^thigh",a),("drive^thigh",b),("drive^shank",c),("all^limb",d)): acc[k]=max(acc.get(k,0),v)
print("\nWORST OVER ROM (cm3):", {k:round(v,3) for k,v in acc.items()})
pose(0.0)
for k in ("drive^thigh","drive^shank"):
    pass
# where does anything still touch the limb?
pose(0.0)
for t in T+S+D:
    for l in LIMB:
        v = vol(O(t).Shape,O(l).Shape)
        if v>0.5:
            c = O(t).Shape.common(O(l).Shape); bb=c.BoundBox
            print("  limb contact %s^%s %.2f cm3  X[%.0f,%.0f] Y[%.0f,%.0f] Z[%.0f,%.0f]"
                  %(t.split('_')[0],l,v,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
