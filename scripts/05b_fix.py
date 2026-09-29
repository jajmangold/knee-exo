# -*- coding: utf-8 -*-
"""Actuator envelope must physically fit inside the RETRACTED pin-to-pin length."""
L_RET, L_EXT = ab(ROM[1]), ab(ROM[0])
EYE, ROD_MIN = 11.0, 10.0
BODY_MAX = L_RET - 2*EYE - ROD_MIN
ACT.update(body_len=165.0, eye=EYE)
assert ACT['body_len'] <= BODY_MAX, "body too long"
print("retracted eye-to-eye      %.1f mm" % L_RET)
print("max body length allowed   %.1f mm  -> using %.1f mm" % (BODY_MAX, ACT['body_len']))
print("rod exposed: %.1f mm (flexed) .. %.1f mm (extended)  = stroke %.1f mm"
      % (L_RET-EYE-ACT['body_len']-EYE+EYE, L_EXT-EYE-ACT['body_len'], L_EXT-L_RET))

def build_actuator(th_deg):
    B = pinB(th_deg); L = ab(th_deg)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    def seg(d, s0, s1):
        assert s1 > s0, "zero/negative actuator segment at %.1f deg" % th_deg
        return Part.makeCylinder(d/2, s1-s0, V(A[0]+ux*s0, A[1]+uy*s0, Z_PLANE), V(ux,uy,0.0))
    s = seg(ACT['body_d'], EYE, EYE+ACT['body_len'])
    s = s.fuse(seg(ACT['rod_d'], EYE+ACT['body_len'], L-EYE))
    s = s.fuse(seg(22.0, L-EYE-8.0, L)); s = s.fuse(seg(22.0, 0.0, EYE))
    return s, L
globals()['build_actuator'] = build_actuator

def pose(th_deg):
    r = FreeCAD.Rotation(V(0,0,1), th_deg)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    doc.getObject("P7_Actuator_ENVELOPE").Shape = build_actuator(th_deg)[0]
    doc.recompute()
globals()['pose'] = pose
pose(0.0); print("ok")
