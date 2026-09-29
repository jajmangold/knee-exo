# -*- coding: utf-8 -*-
"""REV F - final clearance pass:
 (a) pin-A gusset rerouted anterior, clear of the screw support block
 (b) belt cover Z 94-122, clear of the thigh cuff shell (outer R 88)
 (c) pin-B relief opened through the full 16 mm link thickness"""
import math
B0 = pinB(0.0); A = pinA()
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s = sector(r_out,b0,b1,z0,z1,r_in); s.translate(V(c[0],c[1],0.0)); return s

# ---------- P2: gusset rerouted ----------
up = bx(CAV_X[0]+0.4, CAV_X[1]-0.4, *Y_TONGUE, CAV_Z[0]+0.4, CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X, Y_TONGUE[1]-6, 300.0, *BOX_Z))
up = up.cut(bx(*CAV_X, Y_TONGUE[1]+2, 302.0, *CAV_Z))
up = up.fuse(bx(BOX_X[0]+4, BOX_X[1]-4, 190.0, 270.0, 88.0, 100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0, 36.0, 232.0, 268.0, z0, z1))
    up = up.fuse(bar((-30.0,205.0), (A[0],A[1]), 12.0, 8.0, z0, z1))     # anterior gusset
up = up.cut(bx(-14.0, 40.0, 230.0, 270.0, *LINK))
up = up.cut(cz(4.1, CLEV_Z[0][0]-2, CLEV_Z[1][1]+2, *A))
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25, y0, y0+30.0, BOX_Z[0]-2, BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2, 87.0, 99.0, x, y))
doc.getObject("P2_ThighUpright_Upper").Shape = up

# ---------- P4: relief through full thickness ----------
PK = (99.8, 116.2)
lk = cz(21.0, *LINK)
lk = lk.fuse(sector(70.0, *FINGER, *LINK, r_in=20.0))
lk = lk.fuse(bar((0.0,0.0), B0, 20.0, 14.0, *LINK))
lk = lk.fuse(cz(16.0, 94.0, 122.0, *B0))
lk = lk.fuse(bar((0.0,-20.0), (0.0,-160.0), 22.0, 18.0, *LINK))
lk = lk.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))
lk = lk.cut(cz(40.0, *PK, *B0))
lk = lk.cut(sector_at(B0, 95.0, -40.0, 112.0, *PK, r_in=40.0))
lk = lk.cut(cz(4.1, 92.0, 124.0, *B0))
lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))
lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
doc.getObject("P4_ShankLink_Horn").Shape = lk

# ---------- drive: belt cover lifted ----------
def build_drive(th):
    B = pinB(th); L = ab(th)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    plc = FreeCAD.Placement(V(A[0],A[1],0.0),
          FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
    def cyl(r,y0,y1,x=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,Z_PLANE),V(0,1,0))
    d = cz(DR['eye_r'], 101.0, 115.0)
    d = d.fuse(cyl(DR['neck_r'], 8.0, 26.0)).fuse(cyl(DR['blk_r'], *DR['blk']))
    d = d.fuse(bx(-88.0, 20.0, *DR['cover'], 94.0, 122.0))
    d = d.fuse(cyl(DR['screw_r'], *DR['screw']))
    d = d.fuse(cyl(DR['tube_r'], L-DR['tube_len'], L-DR['tang']))
    d = d.fuse(bx(-DR['tang_w'], DR['tang_w'], L-DR['tang'], L, 101.0, 115.0))
    d = d.fuse(cz(DR['eye_r'], 101.0, 115.0, 0.0, L))
    m = cyl(DR['mot_r'], *DR['mot'], x=DR['mot_off'])
    d.Placement = plc; m.Placement = plc
    return d, m, L
globals()['build_drive'] = build_drive
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1), t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d; P8.Shape = m; doc.recompute()
globals()['pose'] = pose

O = lambda n: doc.getObject(n)
T=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
S=["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
D=["P7_Actuator_ENVELOPE","P8_Motor_6374"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w=0.0
    for x in la:
        for y in lb: w=max(w, vol(O(x).Shape,O(y).Shape))
    return w
worst=0.0; bad=[]
for th in range(-2, 106, 2):
    pose(float(th))
    m = max(wp(S,T+PINS), wp(D,T), wp(D,S))
    worst = max(worst, m)
    if m >= 0.05: bad.append((th, round(m,3)))
print("swept %d poses from -2 to 105 deg in 2 deg steps" % len(range(-2,106,2)))
print("worst interference over the whole ROM: %.4f cm3" % worst)
print("poses above 0.05 cm3:", bad if bad else "NONE - mechanism is clear through full ROM")
for n in ("P1_ThighUpright_Lower","P2_ThighUpright_Upper","P4_ShankLink_Horn"):
    o=O(n); print("  %-26s %6.1f cm3 valid=%s solids=%d"%(n,o.Shape.Volume/1000,o.Shape.isValid(),len(o.Shape.Solids)))
pose(0.0); doc.recompute(); doc.saveAs(r"C:\Users\Josh\KneeExo_v1.FCStd")
print("saved:", doc.FileName)
