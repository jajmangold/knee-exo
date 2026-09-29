# -*- coding: utf-8 -*-
"""Eyes are flat lugs (15 mm wide in Z), not spheres of revolution. Re-sweep with
structure / actuator / limb separated."""
import math
EYE_W = (100.5, 115.5)          # rod-end / rear-eye width, fits the 16 mm clevis gap
def build_actuator(th_deg):
    B = pinB(th_deg); L = ab(th_deg)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    def seg(d, s0, s1):
        assert s1 > s0
        return Part.makeCylinder(d/2, s1-s0, V(A[0]+ux*s0, A[1]+uy*s0, Z_PLANE), V(ux,uy,0.0))
    s = seg(ACT['body_d'], EYE, EYE+ACT['body_len'])
    s = s.fuse(seg(ACT['rod_d'], EYE+ACT['body_len'], L-EYE))
    for p in (A, B):                                     # flat eye lugs
        s = s.fuse(cz(11.0, *EYE_W, *p))
    return s, L
globals()['build_actuator'] = build_actuator
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1), t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    doc.getObject("P7_Actuator_ENVELOPE").Shape = build_actuator(t)[0]
    doc.recompute()
globals()['pose'] = pose

O = lambda n: doc.getObject(n)
STRUCT_T = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
PINS     = ["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
STRUCT_S = ["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
LIMB     = ["REF_Thigh","REF_Knee","REF_Shank"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c = a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def worst_pair(la, lb):
    w, nm = 0.0, ""
    for x in la:
        for y in lb:
            v = vol(O(x).Shape, O(y).Shape)
            if v > w: w, nm = v, "%s/%s" % (x.split('_')[0], y.split('_')[0])
    return w, nm

print("theta | shank-vs-thigh | act-vs-thigh | act-vs-shank | struct-vs-LIMB(flesh)")
print("------+----------------+--------------+--------------+----------------------")
acc = {}
for th in [-2,0,5,15,30,45,60,75,90,100,105]:
    pose(float(th)); act = [ "P7_Actuator_ENVELOPE" ]
    a,an = worst_pair(STRUCT_S, STRUCT_T + PINS)
    b,bn = worst_pair(act, STRUCT_T)
    c,cn = worst_pair(act, STRUCT_S)
    d,dn = worst_pair(STRUCT_T + STRUCT_S + act, LIMB)
    print("%5.0f | %7.2f %-6s | %5.2f %-6s | %5.2f %-6s | %6.2f %s"
          % (th, a,an, b,bn, c,cn, d,dn))
    for k,v in (("shank/thigh",a),("act/thigh",b),("act/shank",c),("struct/limb",d)):
        acc[k] = max(acc.get(k,0.0), v)
print("\nWORST OVER FULL ROM (cm3):", {k:round(v,3) for k,v in acc.items()})
print("(limb bodies are nominal cones - contact there = where padding/relief is needed)")
pose(0.0)
