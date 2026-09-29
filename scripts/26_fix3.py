# -*- coding: utf-8 -*-
"""(a) gas cylinder needs a neck (28 mm tube cannot pass the 14 mm clevis gap)
   (b) fork plate sector 74->84 deg: the extended horn cheeks reach bearing 77
   (c) identify which drive component still touches P4 at deep flexion"""
import math
A = pinA(); B0 = pinB(0.0)
GAS_Z, GAS_PL = (136.0,150.0), 143.0

# ---- (c) piecewise probe at theta=105 ----
pose(105.0)
L = ab(105.0); B = pinB(105.0)
ux,uy = (B[0]-A[0])/L, (B[1]-A[1])/L
plc = FreeCAD.Placement(V(A[0],A[1],0.0), FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
comps = {
 "rear_eye":  cz(DR['eye_r'],101.0,115.0),
 "neck":      cyl(DR['neck_r'],8.0,26.0),
 "blk":       cyl(DR['blk_r'],*DR['blk']),
 "cover":     bx(-88.0,20.0,*DR['cover'],94.0,122.0),
 "screw":     cyl(DR['screw_r'],*DR['screw']),
 "nut_tube":  cyl(DR['tube_r'], L-DR['tube_len'], L-DR['tang']),
 "tang":      bx(-DR['tang_w'],DR['tang_w'],L-DR['tang'],L,101.0,115.0),
 "pinB_lug":  cz(DR['eye_r'],101.0,115.0,0.0,L),
}
p4 = doc.getObject("P4_ShankLink_Horn").Shape
for k,s in comps.items():
    s.Placement = plc
    v = 0.0
    if s.BoundBox.intersect(p4.BoundBox):
        c = s.common(p4); v = 0.0 if c.isNull() else c.Volume/1000.0
    if v > 0.01: print("  (c) %-10s overlaps P4 by %.3f cm3" % (k, v))
print("  (c) probe done")

# ---- (a) gas spring with a neck ----
def build_gas(th):
    Bp = pinB(th); Lg = ab(th)
    gx,gy = (Bp[0]-A[0])/Lg, (Bp[1]-A[1])/Lg
    pg = FreeCAD.Placement(V(A[0],A[1],0.0), FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-gx,gy))))
    def gc(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(11.0, *GAS_Z)                          # eye lug, 14 mm wide
    s = s.fuse(gc(6.5, 8.0, 28.0))                # NECK - clears the clevis plates
    s = s.fuse(gc(14.0, 28.0, 104.0))             # cylinder body
    s = s.fuse(gc(4.5, 104.0, Lg-14.0))           # rod
    s = s.fuse(cz(11.0, *GAS_Z, 0.0, Lg))         # lower eye lug
    s.Placement = pg
    return s
globals()['build_gas'] = build_gas

# ---- (b) rebuild P1 with PLATE_SEC 84..252 ----
PLATE_SEC = (84.0, 252.0); globals()['PLATE_SEC'] = PLATE_SEC
Y_TWIN, Y_CLOSED = (25.0, 84.0), 75.0
FLEX_HOLES = [(238,105),(228,95),(218,85),(208,75),(198,65),(188,55)]
EXT_HOLES  = [(99.6,0),(109.6,10),(119.6,20)]
def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
for z0,z1 in (FORK_IN,FORK_OUT): low = low.fuse(bx(*BOX_X,*Y_TWIN,z0,z1))
low = low.fuse(bx(*BOX_X, Y_CLOSED, 170.0, *BOX_Z))
low = low.cut(bx(*CAV_X, Y_CLOSED+4, 172.0, *CAV_Z))
for z0,z1 in (FORK_IN,FORK_OUT):
    for b in (95,130,165,200,235): low = low.cut(cz(11.0,z0-1,z1+1,*pol(54.0,b)))
low = low.cut(cz(6.15, FORK_IN[0]-2, FORK_OUT[1]+2))
for b,_ in FLEX_HOLES+EXT_HOLES:
    low = low.cut(cz(D_PIN/2+0.1, FORK_IN[0]-2, FORK_OUT[1]+2, *pol(R_PIN,b)))
for y in (110.0,150.0): low = low.cut(cz(2.75, BOX_Z[0]-2, BOX_Z[1]+2, -26.0, y))
assert len(low.Solids)==1 and low.isValid(), "P1 broke: %d solids" % len(low.Solids)
doc.getObject("P1_ThighUpright_Lower").Shape = low
print("  (b) P1 rebuilt %.1f cm3 solids=1" % (low.Volume/1000))

def pose(t):
    r = FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d
    doc.getObject("P8_Motor_6374").Shape = m
    doc.getObject("P9_GasSpring").Shape = build_gas(t)
    doc.recompute()
globals()['pose'] = pose
pose(0.0); doc.recompute(); doc.save(); print("saved")
