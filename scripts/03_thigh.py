# -*- coding: utf-8 -*-
"""Thigh assembly: upright (lower fork + upper), ROM stop pins, thigh cuff."""
# --- revised clearance-driven values (supersede 02) ---
R_HUB, R_PLATE, PLATE_SEC = 32.0, 76.0, (74.0, 252.0)
R_PIN, D_PIN = 60.0, 12.0
FLEX_HOLES = [(238,105),(228,95),(218,85),(208,75),(198,65),(188,55)]
EXT_HOLES  = [(99.6,0),(109.6,10),(119.6,20)]
FINGER     = (107.3, 127.3)          # stop-finger bearings at theta=0, r 50..70
BOX_X, BOX_Z, WALL = (-34.0, 14.0), (88.0, 128.0), 5.0
CAV_X, CAV_Z = (-29.0, 9.0), (93.0, 123.0)
Y_SLEEVE  = (25.0, 170.0)            # lower box (outer sleeve)
Y_TONGUE  = (70.0, 178.0)            # upper tongue (inner)
CLEV_Z    = ((94.0,101.0), (115.0,122.0))
g = globals()

A = pinA()

# ================= P1  ThighUprightLower  (fork + sleeve) =================
def fork_plate(z0, z1):
    s = sector(R_PLATE, PLATE_SEC[0], PLATE_SEC[1], z0, z1)
    return s.fuse(cz(R_HUB, z0, z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
low = low.fuse(bx(*BOX_X, *Y_SLEEVE, *BOX_Z))                       # sleeve
low = low.cut(bx(*CAV_X, Y_SLEEVE[0]+4, Y_SLEEVE[1]+2, *CAV_Z))     # hollow
# lighten the fork plates
for z0, z1 in (FORK_IN, FORK_OUT):
    for b in (95, 130, 165, 200, 235):
        p = pol(54, b); low = low.cut(cz(11, z0-1, z1+1, *p))
# pivot bore (M12 shoulder bolt, slip fit)
low = low.cut(cz(6.15, FORK_IN[0]-2, FORK_OUT[1]+2))
# ROM stop-pin holes (12 mm dowels, span both plates)
for b, lab in FLEX_HOLES + EXT_HOLES:
    p = pol(R_PIN, b); low = low.cut(cz(D_PIN/2+0.1, FORK_IN[0]-2, FORK_OUT[1]+2, *p))
# telescope clamp bolts (M5 through both sleeve walls)
for y in (95.0, 145.0):
    low = low.cut(cz(2.75, BOX_Z[0]-2, BOX_Z[1]+2, -12.0, y))
P1 = add("P1_ThighUpright_Lower", low, (0.20,0.42,0.75), G_TH)

# ================= P2  ThighUprightUpper =================
up = bx(CAV_X[0]+0.4, CAV_X[1]-0.4, *Y_TONGUE, CAV_Z[0]+0.4, CAV_Z[1]-0.4)   # tongue
up = up.fuse(bx(*BOX_X, Y_TONGUE[1]-6, 300.0, *BOX_Z))                       # box
up = up.cut(bx(*CAV_X, Y_TONGUE[1]+2, 302.0, *CAV_Z))                        # hollow
up = up.fuse(bx(-30.0, 10.0, 190.0, 270.0, 88.0, 100.0))                     # cuff-mount boss
# pin-A clevis plates + gussets (gussets only in the plate Z bands -> eye gap stays clear)
for z0, z1 in CLEV_Z:
    up = up.fuse(bx(2.0, 36.0, 232.0, 268.0, z0, z1))
    up = up.fuse(bar((6.0,212.0), (A[0],A[1]), 14.0, 10.0, z0, z1))
up = up.cut(bx(-1.0, 40.0, 230.0, 270.0, *LINK))        # 16 mm eye gap (Z 100-116)
up = up.cut(cz(4.1, CLEV_Z[0][0]-2, CLEV_Z[1][1]+2, *A)) # 8 mm pin A bore
# telescope adjust slots (+/-15 mm)
for y0 in (80.0, 130.0):
    up = up.cut(bx(-14.75, -9.25, y0, y0+30.0, BOX_Z[0]-2, BOX_Z[1]+2))
# cuff mount inserts (M5 heat-set, bored from Z=88 outward)
CUFF_TH_PTS = [(-24.0,195.0),(4.0,195.0),(-24.0,265.0),(4.0,265.0)]
for x, y in CUFF_TH_PTS:
    up = up.cut(cz(3.2, 87.0, 99.0, x, y))
P2 = add("P2_ThighUpright_Upper", up, (0.25,0.50,0.85), G_TH)

# ================= P3  ThighCuff =================
ri, ro = R_TH + PAD, R_TH + PAD + SHELL      # 84 / 88
cuff = arc_shell(ri, ro, *Y_THC)
cuff = cuff.fuse(bx(-30.0, 10.0, Y_THC[0]+5, Y_THC[1]-5, 76.0, 88.0))   # lateral pad
for x, y in CUFF_TH_PTS:
    cuff = cuff.cut(cz(2.75, 74.0, 90.0, x, y))                          # M5 through
# strap slots (38 mm webbing) near both free edges, 2 heights
for b in (256.0, 64.0):
    for y in (Y_THC[0]+22, Y_THC[1]-22):
        sl = bx(-2.6, 2.6, y-20.0, y+20.0, ri-6.0, ro+6.0)
        sl.rotate(V(0,0,0), V(0,1,0), -(b-270.0))
        cuff = cuff.cut(sl)
P3 = add("P3_ThighCuff", cuff, (0.95,0.62,0.10), G_TH)

# ================= hardware: ROM dowels + pivot bolt =================
pf = pol(R_PIN, FLEX_HOLES[0][0]); pe = pol(R_PIN, EXT_HOLES[0][0])
add("HW_ROMpin_flexion_105deg", cz(D_PIN/2, 84.0, 132.0, *pf), (0.55,0.55,0.58), G_HW)
add("HW_ROMpin_extension_0deg", cz(D_PIN/2, 84.0, 132.0, *pe), (0.55,0.55,0.58), G_HW)
add("HW_PivotBolt_M12x90",      cz(6.0, 80.0, 140.0),          (0.40,0.40,0.44), G_HW)

doc.recompute()
for o in (P1,P2,P3):
    print("%-26s vol=%8.1f cm3  bbox %s" % (o.Name, o.Shape.Volume/1000,
          " x ".join("%.0f"%v for v in (o.Shape.BoundBox.XLength,o.Shape.BoundBox.YLength,o.Shape.BoundBox.ZLength))))
print("solid?", [o.Shape.isValid() for o in (P1,P2,P3)])
