# -*- coding: utf-8 -*-
"""LA 250 -> 300. Identical torque curve and stroke, +50 mm axial room at pin B so the
screw tip clears the tang. Only pin A moves, so P1/P3/P4/P5/P6 are untouched."""
import math
LA = 300.0; globals()['LA'] = LA
A = pinA(); globals()['A'] = A
L_RET, L_EXT = ab(ROM[1]), ab(ROM[0]); STROKE = L_EXT-L_RET
NUT, TANG, T_TUBE, BLK = 50.0, 35.0, 190.0, (12.0, 50.0)
THREAD = (L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0)
Y_TOP = 340.0
GAS_Z, GAS_PL = (136.0,150.0), 143.0
CLEV_Z, CLEV2_Z = ((94.0,101.0),(115.0,122.0)), ((129.0,136.0),(150.0,157.0))
CUFF_TH_PTS = [(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
Ya, Yb = A[1]-18.0, A[1]+19.0      # clevis Y span, centred on pin A
print("pin A = (%.1f, %.1f);  pin-pin %.1f..%.1f stroke %.1f" % (A[0],A[1],L_RET,L_EXT,STROKE))
print("thread %.1f..%.1f (%.1f mm); nut face %.1f..%.1f; screw tip %.1f vs tang start %.1f"
      % (*THREAD, THREAD[1]-THREAD[0], L_RET-T_TUBE, L_EXT-T_TUBE+NUT, THREAD[1], L_RET-TANG))
assert THREAD[0] >= BLK[1]-1 and THREAD[1] <= L_RET-TANG, "schedule does not close"

# ---------- P2 rebuilt at the new pin A ----------
up = bx(CAV_X[0]+0.4, CAV_X[1]-0.4, *Y_TONGUE, CAV_Z[0]+0.4, CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X, Y_TONGUE[1]-6, Y_TOP, *BOX_Z))
up = up.cut(bx(*CAV_X, Y_TONGUE[1]+2, Y_TOP+2, *CAV_Z))
up = up.fuse(bx(BOX_X[0]+4, BOX_X[1]-4, 190.0, 270.0, 88.0, 100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0, 36.0, Ya, Yb, z0, z1))
    up = up.fuse(bar((-30.0, A[1]-84.0), (A[0],A[1]), 12.0, 8.0, z0, z1))
up = up.fuse(bx(-14.0, 6.0, Ya, Yb, 122.0, 157.0))
for z0,z1 in CLEV2_Z: up = up.fuse(bx(-10.0, 36.0, Ya, Yb, z0, z1))
up = up.cut(bx(-14.0, 40.0, Ya-4.0, A[1]+7.0, *LINK))
up = up.cut(bx(-14.0, 40.0, Ya-4.0, A[1]+7.0, *GAS_Z))
up = up.cut(cz(5.15, 92.0, 160.0, *A))
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25, y0, y0+30.0, BOX_Z[0]-2, BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2, 87.0, 99.0, x, y))
assert len(up.Solids)==1 and up.isValid(), "P2 %d solids" % len(up.Solids)
doc.getObject("P2_ThighUpright_Upper").Shape = up
print("P2 %.1f cm3 solids=1  (box now runs to Y=%.0f)" % (up.Volume/1000, Y_TOP))

# ---------- drive + gas at LA=300 ----------
def _plc(th):
    B = pinB(th); L = ab(th)
    ux,uy = (B[0]-A[0])/L,(B[1]-A[1])/L
    return FreeCAD.Placement(V(A[0],A[1],0.0),
           FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy)))), L
def build_drive(th):
    plc, L = _plc(th)
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    p = L - T_TUBE                                      # nut proximal face
    d = cz(11.0, 101.0, 115.0)                          # rear eye lug
    d = d.fuse(cyl(7.5, 8.0, 26.0))                     # eye neck
    d = d.fuse(cyl(20.0, *BLK))                         # screw support block
    d = d.fuse(bx(-88.0, 20.0, 26.0, 50.0, 94.0, 122.0))# 1:1 belt cover
    d = d.fuse(cyl(10.0, *THREAD))                      # SFU2020 screw
    d = d.fuse(cyl(23.0, p, p+55.0))                    # ball-nut housing
    d = d.fuse(cyl(13.0, p+55.0, L-TANG))               # slim output tube
    d = d.fuse(bx(-8.0, 8.0, L-TANG, L, 101.0, 115.0))  # flat tang
    d = d.fuse(cz(11.0, 101.0, 115.0, 0.0, L))          # pin-B lug
    m = cyl(31.5, 20.0, 94.0, x=-62.0)                  # 6374 can
    d.Placement = plc; m.Placement = plc
    return d, m, L
def build_gas(th):
    plc, L = _plc(th)
    def gc(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(11.0, *GAS_Z).fuse(gc(6.5, 8.0, 28.0)).fuse(gc(14.0, 28.0, 28.0+STROKE+50.0))
    s = s.fuse(gc(4.5, 28.0+STROKE+50.0, L-14.0)).fuse(cz(11.0, *GAS_Z, 0.0, L))
    s.Placement = plc
    return s
globals().update(build_drive=build_drive, build_gas=build_gas, THREAD=THREAD, T_TUBE=T_TUBE, TANG=TANG)
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d
    doc.getObject("P8_Motor_6374").Shape = m
    doc.getObject("P9_GasSpring").Shape = build_gas(t)
    doc.recompute()
globals()['pose'] = pose
doc.getObject("HW_PinA_M8x40").Shape = cz(5.0, 92.0, 160.0, *A)
doc.getObject("HW_PinA_M8x40").Label = "HW_PinA_10x68"
doc.getObject("HW_PinB_M8x36_quickpull").Shape = cz(5.0, 92.0, 160.0, *pinB(0.0))
doc.getObject("HW_PinB_M8x36_quickpull").Label = "HW_PinB_10x68"
pose(0.0); doc.recompute(); doc.save(); print("saved")
