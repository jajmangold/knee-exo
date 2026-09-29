# -*- coding: utf-8 -*-
"""Parallel elastic element: 200 N gas spring on the SAME pin A / pin B axes, outboard
at Z 136-150. AB shortens with flexion, so the spring compresses as the knee bends ->
assist force RISES exactly where stair/sit-to-stand demand peaks. Pin A/B go to 10 mm."""
import math
B0 = pinB(0.0); A = pinA()
GAS_Z   = (136.0, 150.0)          # gas-spring eye lugs
GAS_PL  = 143.0                   # gas-spring centre plane
CLEV2_Z = ((129.0,136.0), (150.0,157.0))
GAS = dict(eye=11.0, dead=104.0, tube_r=14.0, rod_r=4.5, F0=200.0, prog=0.30)
L_EXT, L_RET = ab(ROM[0]), ab(ROM[1])
print("gas spring: stroke %.1f mm, %.1f compressed .. %.1f extended, dead length %.1f"
      % (L_EXT-L_RET, L_RET, L_EXT, L_RET-(L_EXT-L_RET)))

# ---------- P2: two more clevis plates outboard + 10 mm pin A ----------
up = doc.getObject("P2_ThighUpright_Upper").Shape
for z0, z1 in CLEV2_Z:
    up = up.fuse(bx(-10.0, 36.0, 232.0, 268.0, z0, z1))
    up = up.fuse(bar((-30.0,205.0), (A[0],A[1]), 12.0, 8.0, z0, z1))
up = up.cut(bx(-14.0, 40.0, 230.0, 270.0, *GAS_Z))        # gas eye gap
up = up.cut(cz(5.15, 92.0, 160.0, *A))                     # 10 mm pin A through everything
doc.getObject("P2_ThighUpright_Upper").Shape = up
print("P2 %.1f cm3 solids=%d valid=%s" % (up.Volume/1000, len(up.Solids), up.isValid()))

# ---------- P4: extend the pin-B boss outboard, slot for the gas eye ----------
lk = doc.getObject("P4_ShankLink_Horn").Shape
lk = lk.fuse(cz(16.0, 122.0, 157.0, *B0))                  # boss extension
lk = lk.cut(cz(12.5, *GAS_Z, *B0))                         # gas eye pocket
lk = lk.cut(sector_at(B0, 44.0, -40.0, 120.0, *GAS_Z, r_in=12.5))   # its swing fan
lk = lk.cut(cz(5.15, 92.0, 160.0, *B0))                    # 10 mm pin B
n = len(lk.Solids)
print("P4 %.1f cm3 solids=%d valid=%s" % (lk.Volume/1000, n, lk.isValid()))
assert n == 1 and lk.isValid(), "P4 fragmented by the gas-spring pocket (%d)" % n
doc.getObject("P4_ShankLink_Horn").Shape = lk

# ---------- P9: gas spring envelope ----------
def build_gas(th):
    B = pinB(th); L = ab(th)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    plc = FreeCAD.Placement(V(A[0],A[1],0.0),
          FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
    def cyl(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(GAS['eye'], *GAS_Z)
    s = s.fuse(cyl(GAS['tube_r'], 14.0, 14.0+GAS['dead']-14.0))
    s = s.fuse(cyl(GAS['rod_r'], GAS['dead'], L-14.0))
    s = s.fuse(cz(GAS['eye'], *GAS_Z, 0.0, L))
    s.Placement = plc
    return s
P9 = doc.getObject("P9_GasSpring") or doc.addObject("Part::Feature","P9_GasSpring")
P9.Shape = build_gas(0.0); P9.ViewObject.ShapeColor = (0.10,0.55,0.35)
doc.getObject("C_Actuator").addObject(P9)
globals()['build_gas'] = build_gas; globals()['P9'] = P9; globals()['GAS_Z']=GAS_Z
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d
    doc.getObject("P8_Motor_6374").Shape = m
    P9.Shape = build_gas(t)
    doc.recompute()
globals()['pose'] = pose

print()
print("%5s %8s %9s %9s %11s %11s %9s" % ("flex","arm mm","AB mm","F_gas N","tau_gas","tau_needed","motor A"))
F_PER_A = 2*math.pi*0.90*(8.27/190.0)/0.020
for th in (0,15,30,45,60,75,90,105):
    L = ab(float(th)); F = GAS['F0']*(1.0+GAS['prog']*(L_EXT-L)/(L_EXT-L_RET))
    a_ = arm(float(th)); tg = F*a_/1000.0
    need = max(0.0, 25.0-tg)
    print("%5d %8.1f %9.1f %9.0f %10.1f %10.1f %9.1f"
          % (th, a_, L, F, tg, need, need*1000/a_/F_PER_A))
doc.recompute(); doc.save(); print("\nsaved")
