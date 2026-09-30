# -*- coding: utf-8 -*-
"""STAGE 1 of the one-screw rebuild: spine, screw, belt loop, idler, gantry.

Geometry decided in 390_onescrew_section.py. Summary of what changes:

  A1   20x60 -> 20x40 V-slot, X +/-20, Z 88..108, Y 56..207 (was 227 mm, now 151)
  A2   ONE SFU1610 RH screw, moved X -58 -> -62 so the nut clears the return strand
  A5*  the belt becomes a CLOSED LOOP: knee wrap, -X strand below the clamp, +X strand
       running the full length, -X return strand above the clamp, idler wrap
  A6   NEW: a second 29T HTD-8M pulley on the centreline at X = 0, Y = 255
  P3   the printed twin carriage becomes ONE aluminium V-wheel gantry
  P10* NEW: 4 solid V-wheels at the |X| 20 corners

  DELETED: A2c, A2d (LH screw + nut), P3b (carriage B), A9, A9b (MGN7 rails),
           P10a-d (MGN7 blocks), P11 (sprung anchor), A8 (spring), P13 (Hall)

Kinematics:  Y_clamp = A0 - R*theta,  A0 = 161,  theta -2..104 deg

Send with:  python tools/fcsend.py scripts/391_onescrew_build.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

# ---------------------------------------------------------------- constants
TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)          # 36.924 pitch radius
BIN, BOUT = R - 1.372, R + 4.2             # 35.552 .. 41.124 belt band
PUL_R = BIN                                # pulley body outer radius
BZ = (96.0, 126.0)                         # belt Z band

RX = (-20.0, 20.0)                         # 2040
RZ = (88.0, 108.0)
# The idler is a 71 mm pulley on the centreline, so the rail CANNOT run under it: at
# X +/-20, Z 96..108 the extrusion would be inside the pulley. The rail therefore ends
# just short of it, and the idler hangs off the drive bracket instead (393).
RY = (56.0, 207.0)
OUT_SLOT = (-10.0, 10.0)                   # a 2040's 40 mm face has slots at +/-10
SIDE_Z = (95.0, 101.0)

SCR_X = -62.0
SCR_Z = 106.0
SCR_R = 7.9
SCR_Y = (70.0, 302.0)
NUT_R = 18.0
NUT_HALF = 21.0

A0 = 161.0
PLATE_HALF = 35.0
WHEEL_Y = 25.0                             # wheel centres at clamp +/- 25
WHEEL_R = 23.89 / 2.0
WHEEL_Z = (103.0, 113.0)
DECK_Z = (113.0, 131.0)
ARM_X = (-84.0, -45.0)
GAP_X = (-45.0, -33.0)                     # belt passes through here
IDL_Y = 255.0

THETA = [float(i) for i in range(-2, 105)]
YC = [A0 - R * math.radians(t) for t in THETA]
YC_MIN, YC_MAX = min(YC), max(YC)


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cz(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def put(name, label, shape, group=None):
    o = doc.getObject(name)
    if o is None:
        o = doc.addObject("Part::Feature", name)
        if group is not None:
            g = doc.getObject(group)
            if g is not None:
                g.addObject(o)
    o.Shape = shape
    o.Label = label
    return o


def one(shape, who):
    assert len(shape.Solids) == 1, "%s: solids=%d" % (who, len(shape.Solids))
    assert shape.isValid(), "%s: invalid" % who
    return shape


print("clamp Y %.2f .. %.2f  (stroke %.2f)" % (YC_MIN, YC_MAX, YC_MAX - YC_MIN))
print("gantry plate Y %.2f .. %.2f ; rail Y %.1f..%.1f"
      % (YC_MIN - PLATE_HALF, YC_MAX + PLATE_HALF, RY[0], RY[1]))
print("nut Y %.2f .. %.2f" % (YC_MIN - NUT_HALF, YC_MAX + NUT_HALF))
print("idler at Y %.1f, belt wrap reaches Y %.2f" % (IDL_Y, IDL_Y + BOUT))
# The rail has to exist wherever a WHEEL touches it, which is the wheel footprint
# (clamp +/- WHEEL_Y, +/- WHEEL_R), not the plate outline. The plate may overhang.
WH_LO, WH_HI = YC_MIN - WHEEL_Y - WHEEL_R, YC_MAX + WHEEL_Y + WHEEL_R
print("wheel footprint Y %.2f .. %.2f" % (WH_LO, WH_HI))
assert WH_LO >= RY[0], "wheels run off the distal end of the rail by %.2f" % (RY[0] - WH_LO)
assert WH_HI <= RY[1], "wheels run off the proximal end of the rail by %.2f" % (WH_HI - RY[1])
assert IDL_Y - PUL_R > RY[1], "the rail runs into the idler pulley"
assert IDL_Y - BOUT > YC_MAX + PLATE_HALF, "idler wrap fouls the gantry at full extension"

# ------------------------------------------------------------------ deletes
GONE = ["A2c_BallScrew_LH", "A2d_BallNut_LH", "P3b_CarriageB",
        "A9_RailMGN9_A", "A9b_RailMGN9_B",
        "P10a_Slider_Delrin", "P10b_Slider_Delrin",
        "P10c_Slider_Delrin", "P10d_Slider_Delrin",
        "P11_SprungAnchor", "A8_TensionSpring", "P13_HallTension"]
for nm in GONE:
    if doc.getObject(nm) is not None:
        doc.removeObject(nm)
        print("deleted %s" % nm)

# --------------------------------------------------------------- A1  20x40
r = bx(RX[0], RX[1], RY[0], RY[1], RZ[0], RZ[1])
for cx in OUT_SLOT:
    r = r.cut(bx(cx - 3., cx + 3., RY[0] - 1, RY[1] + 1, RZ[1] - 4., RZ[1] + 1))
    r = r.cut(bx(cx - 3., cx + 3., RY[0] - 1, RY[1] + 1, RZ[0] - 1, RZ[0] + 4.))
    r = r.cut(cy(4.0, RY[0] - 1, RY[1] + 1, cx, (RZ[0] + RZ[1]) / 2))
r = r.cut(bx(RX[0] - 1, RX[0] + 4., RY[0] - 1, RY[1] + 1, *SIDE_Z))
r = r.cut(bx(RX[1] - 4., RX[1] + 1, RY[0] - 1, RY[1] + 1, *SIDE_Z))
one(r, "A1")
o = doc.getObject("A1_Extrusion_20x60_VSlot")
o.Shape = r
o.Label = "A1_Extrusion_20x40_VSlot"
print("A1 2040  X %.0f..%.0f Z %.0f..%.0f Y %.0f..%.0f  ~%.0f g"
      % (RX[0], RX[1], RZ[0], RZ[1], RY[0], RY[1], 1.05 * (RY[1] - RY[0])))

# ------------------------------------------------------- A2 / A2b screw+nut
s = cy(SCR_R, SCR_Y[0], SCR_Y[1], SCR_X, SCR_Z)
put("A2_BallScrew_SFU1620", "A2_BallScrew_SFU1610_RH", one(s, "A2"))

n = cy(NUT_R, A0 - NUT_HALF, A0 + NUT_HALF, SCR_X, SCR_Z)
n = n.cut(cy(8.5, A0 - NUT_HALF - 1, A0 + NUT_HALF + 1, SCR_X, SCR_Z))
for k in range(4):
    aa = math.radians(45 + 90 * k)
    n = n.cut(cz(2.1, SCR_Z + NUT_R - 3., SCR_Z + NUT_R + 1.,
                 SCR_X + 9. * math.cos(aa), A0 - NUT_HALF + 6. + k * 9.))
n = n.removeSplitter()
put("A2b_BallNut_SFU1620", "A2b_BallNut_SFU1610", one(n, "A2b"))
print("A2 screw X %.0f Z %.0f ; nut OD %.0f spans X %.1f..%.1f (belt inner %.2f, gap %.2f)"
      % (SCR_X, SCR_Z, 2 * NUT_R, SCR_X - NUT_R, SCR_X + NUT_R, -BOUT,
         -BOUT - (SCR_X + NUT_R)))

# ------------------------------------------------------------ A6 29T idler
i = cz(PUL_R, BZ[0], BZ[1], 0.0, IDL_Y)
put("A6_Idler29T", "A6_Idler_29T_HTD8M", one(i, "A6"), group="C_Drive")
print("A6 idler 29T at X 0, Y %.0f, r %.3f, Z %.0f..%.0f" % (IDL_Y, PUL_R, *BZ))

# ------------------------------------------------------------- A5* the loop
# knee wrap: distal half annulus about the knee axis (0,0)
w = cz(BOUT, BZ[0], BZ[1]).cut(cz(BIN, BZ[0] - 1, BZ[1] + 1))
w = w.cut(bx(-BOUT - 1, BOUT + 1, 0.0, BOUT + 1, BZ[0] - 1, BZ[1] + 1))
put("A5_Belt_HTD8M", "A5_Belt_WrapKnee_180", one(w, "A5"))

# idler wrap: proximal half annulus about (0, IDL_Y)
w2 = cz(BOUT, BZ[0], BZ[1], 0.0, IDL_Y).cut(cz(BIN, BZ[0] - 1, BZ[1] + 1, 0.0, IDL_Y))
w2 = w2.cut(bx(-BOUT - 1, BOUT + 1, IDL_Y - BOUT - 1, IDL_Y, BZ[0] - 1, BZ[1] + 1))
put("A5d_Belt_WrapIdler", "A5d_Belt_WrapIdler_180", one(w2, "A5d"), group="C_Drive")

# -X strand below the clamp, at the pose the model is parked at (A0)
put("A5b_Belt_DriveRun", "A5b_Belt_StrandLower",
    one(bx(-BOUT, -BIN, 0.0, A0, BZ[0], BZ[1]), "A5b"))
# -X strand above the clamp, up to the idler
put("A5e_Belt_Return", "A5e_Belt_StrandUpper",
    one(bx(-BOUT, -BIN, A0, IDL_Y, BZ[0], BZ[1]), "A5e"), group="C_Drive")
# +X strand, the full length, capstan to idler
put("A5c_Belt_TakeRun", "A5c_Belt_StrandFar",
    one(bx(BIN, BOUT, 0.0, IDL_Y, BZ[0], BZ[1]), "A5c"))
print("A5 loop: strands at X +/-%.3f..%.3f, length 2*pi*R + 2*Y_i = %.0f mm"
      % (BIN, BOUT, 2 * math.pi * R + 2 * IDL_Y))
print("    rail ends Y %.0f, idler pulley starts Y %.2f -- %.2f mm clear"
      % (RY[1], IDL_Y - PUL_R, IDL_Y - PUL_R - RY[1]))

# ------------------------------------------------------------- P3 gantry
Y0, Y1 = A0 - PLATE_HALF, A0 + PLATE_HALF
deck = bx(GAP_X[1], 32.0, Y0, Y1, DECK_Z[0], DECK_Z[1])          # inboard deck
arm = bx(ARM_X[0], ARM_X[1], Y0, Y1, 89.0, DECK_Z[1])            # nut arm
bridge = bx(GAP_X[0], GAP_X[1], Y0, Y1, 89.0, BZ[0] - 1.0)       # under the belt
clamp = bx(GAP_X[0], GAP_X[1], A0 - 9.0, A0 + 9.0, 89.0, DECK_Z[1])
g = deck.fuse(arm).fuse(bridge).fuse(clamp)
# the belt passes through: slot it out everywhere except where the clamp grips
g = g.cut(bx(-BOUT - 0.4, -BIN + 0.4, Y0 - 1, A0 - 9.0, BZ[0] - 0.4, DECK_Z[1] + 1))
g = g.cut(bx(-BOUT - 0.4, -BIN + 0.4, A0 + 9.0, Y1 + 1, BZ[0] - 0.4, DECK_Z[1] + 1))
# nut pocket
g = g.cut(cy(NUT_R + 0.2, A0 - NUT_HALF - 1, A0 + NUT_HALF + 1, SCR_X, SCR_Z))
# clear the extrusion and the wheels
g = g.cut(bx(RX[0] - 2.0, RX[1] + 2.0, Y0 - 1, Y1 + 1, RZ[0] - 1, DECK_Z[0] - 0.5))
g = g.removeSplitter()
put("P3_Carriage", "P3_GantryPlate_Alu", one(g, "P3"))
print("P3 gantry  X %.0f..%.0f  Z %.0f..%.0f  %.1f cm3"
      % (g.BoundBox.XMin, g.BoundBox.XMax, g.BoundBox.ZMin, g.BoundBox.ZMax,
         g.Volume / 1000.))

# ------------------------------------------------------------- P10* V-wheels
for k, (sx, dy) in enumerate([(RX[0], -WHEEL_Y), (RX[0], WHEEL_Y),
                              (RX[1], -WHEEL_Y), (RX[1], WHEEL_Y)]):
    wh = cz(WHEEL_R, WHEEL_Z[0], WHEEL_Z[1], sx, A0 + dy)
    wh = wh.cut(cz(4.0, WHEEL_Z[0] - 1, WHEEL_Z[1] + 1, sx, A0 + dy))
    nm = "P10%s_VWheel" % "abcd"[k]
    put(nm, "P10%s_VWheel_Solid" % "abcd"[k], one(wh, nm), group="C_Drive")
print("4 solid V-wheels r %.3f at |X| %.0f, reach |X| %.2f (belt inner %.2f, gap %.2f)"
      % (WHEEL_R, RX[1], RX[1] + WHEEL_R, BIN, BIN - RX[1] - WHEEL_R))

doc.recompute()
print("STAGE 1 DONE -- objects now %d" % len(doc.Objects))
