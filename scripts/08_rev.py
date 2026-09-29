# -*- coding: utf-8 -*-
"""REV B:  drive = 6374 + SFU2020 ball screw + ODrive (replaces COTS linear actuator)
Fixes: (1) stop finger fouled the sleeve box -> twin plates below Y=80
       (2) drive fouled the upright -> box shifted anterior to X[-50,-2]
       (3) pin-B rod-eye pocket was a plain rectangle -> proper radiused pocket"""
import math
BOX_X, CAV_X = (-50.0, -2.0), (-45.0, -7.0)
CUFF_TH_PTS  = [(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
Y_TWIN, Y_CLOSED = (25.0, 84.0), 75.0
LEAD, ETA, KT = 20.0, 0.90, 8.27/190.0
A = pinA()

# ---------- P1 rebuilt ----------
def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
for z0,z1 in (FORK_IN, FORK_OUT):                      # twin plates keep the gap open
    low = low.fuse(bx(*BOX_X, *Y_TWIN, z0, z1))
low = low.fuse(bx(*BOX_X, Y_CLOSED, 170.0, *BOX_Z))    # closed sleeve above the finger
low = low.cut(bx(*CAV_X, Y_CLOSED+4, 172.0, *CAV_Z))
for z0,z1 in (FORK_IN, FORK_OUT):
    for b in (95,130,165,200,235):
        low = low.cut(cz(11.0, z0-1, z1+1, *pol(54.0,b)))
low = low.cut(cz(6.15, FORK_IN[0]-2, FORK_OUT[1]+2))
for b,_ in FLEX_HOLES + EXT_HOLES:
    low = low.cut(cz(D_PIN/2+0.1, FORK_IN[0]-2, FORK_OUT[1]+2, *pol(R_PIN,b)))
for y in (110.0, 150.0): low = low.cut(cz(2.75, BOX_Z[0]-2, BOX_Z[1]+2, -26.0, y))
doc.getObject("P1_ThighUpright_Lower").Shape = low

# ---------- P2 rebuilt ----------
up = bx(CAV_X[0]+0.4, CAV_X[1]-0.4, *Y_TONGUE, CAV_Z[0]+0.4, CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X, Y_TONGUE[1]-6, 300.0, *BOX_Z))
up = up.cut(bx(*CAV_X, Y_TONGUE[1]+2, 302.0, *CAV_Z))
up = up.fuse(bx(BOX_X[0]+4, BOX_X[1]-4, 190.0, 270.0, 88.0, 100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0, 36.0, 232.0, 268.0, z0, z1))
    up = up.fuse(bar((-16.0,212.0), (A[0],A[1]), 14.0, 10.0, z0, z1))
up = up.cut(bx(-14.0, 40.0, 230.0, 270.0, *LINK))
up = up.cut(cz(4.1, CLEV_Z[0][0]-2, CLEV_Z[1][1]+2, *A))
for y0 in (80.0, 130.0): up = up.cut(bx(-28.75,-23.25, y0, y0+30.0, BOX_Z[0]-2, BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2, 87.0, 99.0, x, y))
doc.getObject("P2_ThighUpright_Upper").Shape = up

# ---------- P3 pad follows the new box ----------
ri, ro = R_TH+PAD, R_TH+PAD+SHELL
cuff = arc_shell(ri, ro, *Y_THC).fuse(bx(BOX_X[0]+4, BOX_X[1]-4, Y_THC[0]+5, Y_THC[1]-5, 76.0, 88.0))
for x,y in CUFF_TH_PTS: cuff = cuff.cut(cz(2.75, 74.0, 90.0, x, y))
for b in (256.0, 64.0):
    for y in (Y_THC[0]+22, Y_THC[1]-22):
        sl = bx(-2.6,2.6, y-20.0, y+20.0, ri-6.0, ro+6.0)
        sl.rotate(V(0,0,0), V(0,1,0), -(b-270.0)); cuff = cuff.cut(sl)
doc.getObject("P3_ThighCuff").Shape = cuff

# ---------- P4: proper radiused clevis pocket at pin B ----------
B0 = pinB(0.0)
lk = cz(34.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=30.0))
lk = lk.fuse(bar((0.0,0.0), B0, 20.0, 14.0, *LINK)).fuse(cz(16.0, 94.0, 122.0, *B0))
lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0), 22.0, 18.0, *LINK))
lk = lk.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))
lk = lk.cut(cz(12.0, 100.4, 115.6, *B0))                                  # radiused pocket
lk = lk.cut(bx(B0[0]-12.0, B0[0]+12.0, B0[1], B0[1]+30.0, 100.4, 115.6))  # entry channel
lk = lk.cut(cz(4.1, 92.0, 124.0, *B0))
lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))
lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(8.0, LINK[0]-1, LINK[1]+1, *pol(36.0,310.0)))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
doc.getObject("P4_ShankLink_Horn").Shape = lk

# ---------- REV B drive: screw + nut tube + block/belt + 6374 ----------
DR = dict(eye=11.0, blk=(11.0,46.0), blk_r=22.0, screw=(46.0,200.0), screw_r=10.0,
          tube_len=150.0, tube_r=17.0, mot_off=-62.0, mot_r=31.5, mot=(11.0,85.0))
def build_drive(th):
    B = pinB(th); L = ab(th)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    phi = math.degrees(math.atan2(-ux, uy))
    plc = FreeCAD.Placement(V(A[0], A[1], 0.0), FreeCAD.Rotation(V(0,0,1), phi))
    def cyl(r, y0, y1, x=0.0):   # local: +Y = A->B, local -X = posterior
        return Part.makeCylinder(r, y1-y0, V(x, y0, Z_PLANE), V(0,1,0))
    d = cz(DR['eye'], 101.0, 115.0)                                  # rear eye at pin A
    d = d.fuse(cyl(DR['blk_r'], *DR['blk']))                         # bearing/pulley block
    d = d.fuse(bx(-88.0, 20.0, 14.0, 44.0, 85.0, 131.0))             # belt cover
    d = d.fuse(cyl(DR['screw_r'], *DR['screw']))                     # SFU2020 screw
    d = d.fuse(cyl(DR['tube_r'], L-DR['tube_len'], L))               # nut tube (moving)
    d = d.fuse(cz(DR['eye'], 101.0, 115.0, 0.0, L))                  # pin-B clevis lug
    m = cyl(DR['mot_r'], *DR['mot'], x=DR['mot_off'])                # 6374 can
    d.Placement = plc; m.Placement = plc
    return d, m, L
dv, mo, L0 = build_drive(0.0)
doc.getObject("P7_Actuator_ENVELOPE").Shape = dv
doc.getObject("P7_Actuator_ENVELOPE").Label = "P7_BallscrewDrive_SFU2020"
P8 = add("P8_Motor_6374", mo, (0.15,0.15,0.18), G_ACT)
globals()['P8'] = P8; globals()['build_drive'] = build_drive

def pose(t):
    r = FreeCAD.Rotation(V(0,0,1), t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    d, m, _ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d; P8.Shape = m
    doc.recompute()
globals()['pose'] = pose
pose(0.0)
F_A = 2*math.pi*ETA*KT/(LEAD/1000.0)
print("REV B built.  force/amp = %.1f N/A" % F_A)
for nm in ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff","P4_ShankLink_Horn"]:
    o = doc.getObject(nm); print("  %-26s %7.1f cm3 valid=%s" % (nm, o.Shape.Volume/1000, o.Shape.isValid()))
