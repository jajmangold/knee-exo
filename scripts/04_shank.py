# -*- coding: utf-8 -*-
"""Shank assembly: link (hub+crank horn+strut+telescoping tongue), slide housing, cuff.
Plus the actuator envelope and a pose() driver for the whole 1-DOF mechanism."""
B0 = pinB(0.0); A = pinA()
TONGUE = dict(x=(-13.0,13.0), y=(-197.0,-150.0), z=(102.0,114.0))
SOCK   = dict(x=(-22.0, 22.0), y=(-215.0,-145.0), z=(97.0,119.0))

# ================= P4  ShankLink =================
lk = cz(34.0, *LINK)                                             # hub
lk = lk.fuse(sector(70.0, FINGER[0], FINGER[1], *LINK, r_in=30.0))  # ROM stop finger
lk = lk.fuse(bar((0.0,0.0), B0, 20.0, 14.0, *LINK))              # crank horn
lk = lk.fuse(cz(16.0, 94.0, 122.0, *B0))                         # horn tip boss (rod-end fork)
lk = lk.fuse(bar((0.0,-20.0), (0.0,-160.0), 22.0, 18.0, *LINK))  # shank strut
lk = lk.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))       # telescoping tongue
# rod-end slot + pin B bore
lk = lk.cut(bx(B0[0]-9.0, B0[0]+9.0, B0[1], B0[1]+26.0, 100.8, 115.2))
lk = lk.cut(cz(4.1, 92.0, 124.0, *B0))
# knee pivot: 12.5 through + 2x 6801-2RS (21x5) counterbores
lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))
lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)); lk = lk.cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
# lightening
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(8.0, LINK[0]-1, LINK[1]+1, *pol(36.0, 310.0)))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))   # M6 travel-limit screw
P4 = add("P4_ShankLink_Horn", lk, (0.75,0.20,0.22), G_SH)

# ================= P5  ShankSlideHousing =================
hs = bx(*SOCK['x'], *SOCK['y'], *SOCK['z'])
hs = hs.cut(bx(TONGUE['x'][0]-0.4, TONGUE['x'][1]+0.4, -216.0, -157.0,
               TONGUE['z'][0]-0.4, TONGUE['z'][1]+0.4))                 # socket, 59 deep
hs = hs.cut(bx(-3.0, 3.0, -190.0, -165.0, 116.0, 121.0))                # travel slot (15 mm)
hs = hs.fuse(bx(-30.0, 30.0, -273.0, -163.0, 68.0, 78.0))               # cuff flange
hs = hs.fuse(bx(-8.0, 8.0, -262.0, -174.0, 76.0, 99.0))                 # web
for xa, xb in ((14.0,22.0), (-22.0,-14.0)):
    hs = hs.fuse(bx(xa, xb, -258.0, -178.0, 70.0, 99.0))                # gussets
CUFF_SH_PTS = [(-22.0,-190.0),(22.0,-190.0),(-22.0,-246.0),(22.0,-246.0)]
for x, y in CUFF_SH_PTS: hs = hs.cut(cz(3.2, 67.0, 79.0, x, y))         # M5 inserts
P5 = add("P5_ShankSlideHousing", hs, (0.85,0.35,0.15), G_SH)

# ================= P6  ShankCuff =================
ri, ro = R_SH + PAD, R_SH + PAD + SHELL     # 64 / 68
sc = arc_shell(ri, ro, *Y_SHC)
sc = sc.fuse(bx(-30.0, 30.0, Y_SHC[0]+5, Y_SHC[1]-5, 56.0, 68.0))
for x, y in CUFF_SH_PTS: sc = sc.cut(cz(2.75, 54.0, 70.0, x, y))
for b in (256.0, 64.0):
    for y in (Y_SHC[0]+22, Y_SHC[1]-22):
        sl = bx(-2.6, 2.6, y-20.0, y+20.0, ri-6.0, ro+6.0)
        sl.rotate(V(0,0,0), V(0,1,0), -(b-270.0)); sc = sc.cut(sl)
P6 = add("P6_ShankCuff", sc, (0.95,0.62,0.10), G_SH)

# ================= reference limb =================
th = Part.makeCone(62.0, 85.0, 285.0, V(0,15,0), V(0,1,0))
kn = Part.makeSphere(52.0, V(0,0,0))
sh = Part.makeCone(60.0, 38.0, 360.0, V(0,-20,0), V(0,1,0))
for nm, s, grp in (("REF_Thigh",th,G_REF), ("REF_Knee",kn,G_REF), ("REF_Shank",sh,G_SH)):
    o = add(nm, s, (0.85,0.75,0.70), grp); o.ViewObject.Transparency = 72

# ================= actuator (rebuilt per pose) =================
ACT = dict(body_d=32.0, rod_d=12.0, eye=11.0, body_len=185.0)
def build_actuator(th_deg):
    B = pinB(th_deg); L = ab(th_deg)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    z0, z1 = ACT['body_d']/2, None
    def seg(d, s0, s1):
        p0 = V(A[0]+ux*s0, A[1]+uy*s0, Z_PLANE)
        return Part.makeCylinder(d/2, s1-s0, p0, V(ux, uy, 0.0))
    s = seg(ACT['body_d'], ACT['eye'], ACT['eye']+ACT['body_len'])
    s = s.fuse(seg(ACT['rod_d'], ACT['eye']+ACT['body_len'], L-ACT['eye']))
    s = s.fuse(seg(22.0, L-ACT['eye']-8.0, L))          # PU-bushed rod end at pin B
    s = s.fuse(seg(22.0, 0.0, ACT['eye']))              # rear eye at pin A
    return s, L
act_s, L0 = build_actuator(0.0)
P7 = add("P7_Actuator_ENVELOPE", act_s, (0.30,0.32,0.36), G_ACT)
add("HW_PinA_M8x40", cz(4.0, 92.0, 124.0, *A), (0.55,0.55,0.58), G_HW)
add("HW_PinB_M8x36_quickpull", cz(4.0, 92.0, 124.0, *B0), (0.85,0.75,0.20), G_HW)

# ================= pose driver =================
SHANK_OBJS = [P4, P5, P6, doc.getObject("REF_Shank"),
              doc.getObject("HW_PinB_M8x36_quickpull")]
def pose(th_deg):
    r = FreeCAD.Rotation(V(0,0,1), th_deg)
    for o in SHANK_OBJS:
        o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    P7.Shape = build_actuator(th_deg)[0]
    doc.recompute()
g['pose'] = pose; g['build_actuator'] = build_actuator; g['SHANK_OBJS'] = SHANK_OBJS

doc.recompute()
for o in (P4,P5,P6):
    print("%-24s vol=%7.1f cm3  valid=%s" % (o.Name, o.Shape.Volume/1000, o.Shape.isValid()))
tot = sum(doc.getObject(n).Shape.Volume for n in
          ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
           "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"])/1000
print("printed volume %.0f cm3 -> PA6-CF @1.19 g/cc x 0.55 infill-avg = %.0f g" % (tot, tot*1.19*0.78))
print("actuator eye-to-eye at 0 deg = %.1f mm" % L0)
