# -*- coding: utf-8 -*-
"""STAGE 5: the four things the first sweep caught, and one it caught by accident.

1. THE MOTOR WAS INSIDE THE LEG. I put it at Z centre 111 to save lateral protrusion;
   at r 31.5 that reaches Z 79.5 and REF_Thigh's surface is at Z 85. The two-screw build
   had it at Z centre 118 for exactly this reason and I moved it without asking why it was
   there. Back to 118. Same for the motor plate, and it moves to Y 300..308 so it clears
   REF_Thigh's proximal end at Y 300 as well.

2. THE V-WHEEL MODEL WAS WRONG, AND OPTIMISTIC. 320_rail_section.py puts the wheel centre
   ON the corner, so half the wheel is inside the aluminium -- which is why every wheel
   flagged 0.727 cm3 against the extrusion. A V groove straddles the corner: the corner
   apex sits at the bottom of the groove, so the centre stands off along the 45 deg
   bisector by groove_minor/2. That pushes the OUTER edge further out than 320 assumed:

     solid V, OD 23.89, groove minor ~15.9 -> centre |X| 25.6, outer 37.5  FOULS the belt
     mini  V, OD 15.23, groove minor ~9.5  -> centre |X| 23.4, outer 31.0  clears by 4.6

   So on a 2040 only the MINI wheel fits, and 320's table saying both fit is wrong.
   Modelled with the rail cut out of the wheel, which is what the groove does.

3. THE LINK BELT ENVELOPE SWALLOWED THE SCREW. Modelling artefact -- the screw carries one
   of its pulleys. Bored.

4. THE DRIVE CAP WAS A CLOSED BOX. Its distal wall sat across the bracket, the screw and
   the idler wrap, and its floor at Z 72 was inside the thigh. Open at the distal end,
   floor up to Z 86, and it starts at Y 300 past REF_Thigh.

Send with:  python tools/fcsend.py scripts/396_fixes.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
BIN, BOUT = R - 1.372, R + 4.2
BZ = (96.0, 126.0)
RX = (-20.0, 20.0)
RZ = (88.0, 108.0)
SCR_X, SCR_Z, SCR_R = -62.0, 106.0, 7.9
NUT_R = 18.0
A0 = 161.0
MOT_R, MOT_Z0 = 31.5, 118.0
MOT_Y = (308.0, 382.0)
MP_Y = (300.0, 308.0)
MP_Z = (MOT_Z0 - MOT_R - 2.0, MOT_Z0 + MOT_R + 2.0)
LINK_Y = (384.0, 396.0)
SCR_Y = (70.0, 398.0)
WHEEL_Y = 25.0
# mini V-wheel: OD 15.23, groove minor ~9.5, so the centre stands off the corner by
# (9.5/2)/sqrt(2) in each of X and Z.
W_OD, W_GROOVE = 15.23, 9.5
W_OFF = (W_GROOVE / 2.0) / math.sqrt(2.0)
W_R = W_OD / 2.0
W_CX = RX[1] + W_OFF
W_CZ = RZ[1] + W_OFF
WEB_A_X = (-34.5, -32.5)


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def cz(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


print("wheel: OD %.2f groove %.1f -> centre |X| %.2f Z %.2f, outer |X| %.2f"
      % (W_OD, W_GROOVE, W_CX, W_CZ, W_CX + W_R))
print("       belt inner %.3f -> clears by %.2f mm ; web A at X %.1f clears by %.2f"
      % (BIN, BIN - (W_CX + W_R), WEB_A_X[1], abs(WEB_A_X[1]) - (W_CX + W_R)))
assert W_CX + W_R < BIN, "wheel fouls the belt"
assert abs(WEB_A_X[1]) > W_CX + W_R, "web A fouls the wheel (392 builds it)"
assert abs(WEB_A_X[0]) < BIN, "web A fouls the belt"

# ------------------------------------------------------------------ 1. motor
m = cy(MOT_R, MOT_Y[0], MOT_Y[1], 0.0, MOT_Z0)
doc.getObject("A3_Motor_6374").Shape = m
print("A3 motor Z %.1f..%.1f (thigh surface is Z 85), Y %.0f..%.0f"
      % (MOT_Z0 - MOT_R, MOT_Z0 + MOT_R, *MOT_Y))
REF = doc.getObject("REF_Thigh").Shape


def vs_leg(shape, who):
    """The only honest test for 'is it inside the leg' is against REF_Thigh itself.
    A bounding-box Z test cannot tell a plate at Z 82 beyond the thigh's proximal end
    from one at Z 82 buried in the middle of it."""
    c = shape.common(REF)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("    %-22s vs REF_Thigh: %.3f cm3" % (who, v))
    assert v < 0.02, "%s intrudes into the leg by %.3f cm3" % (who, v)


vs_leg(m, "A3_Motor")

# ------------------------------------------------------------- 2. the wheels
rail = doc.getObject("A1_Extrusion_20x60_VSlot").Shape
for k, (sgn, dy) in enumerate([(-1, -WHEEL_Y), (-1, WHEEL_Y), (1, -WHEEL_Y), (1, WHEEL_Y)]):
    wh = cz(W_R, W_CZ - 5.1, W_CZ + 5.1, sgn * W_CX, A0 + dy)
    wh = wh.cut(cz(3.0, W_CZ - 6, W_CZ + 6, sgn * W_CX, A0 + dy))
    wh = wh.cut(rail)                      # the V groove straddles the corner
    wh = wh.removeSplitter()
    o = doc.getObject("P10%s_VWheel" % "abcd"[k])
    o.Shape = wh
    o.Label = "P10%s_VWheel_Mini" % "abcd"[k]

# --------------------------------------------------------------- 3. link belt
s = cy(SCR_R, SCR_Y[0], SCR_Y[1], SCR_X, SCR_Z)
doc.getObject("A2_BallScrew_SFU1620").Shape = s
lk = bx(SCR_X - 18.0, 18.0, LINK_Y[0], LINK_Y[1], MOT_Z0 - 18.0, MOT_Z0 + 18.0)
lk = lk.cut(cy(SCR_R + 0.3, LINK_Y[0] - 1, LINK_Y[1] + 1, SCR_X, SCR_Z))
lk = lk.removeSplitter()
doc.getObject("A7b_LinkBelt").Shape = lk

# -------------------------------------------------- 1b. bracket's motor plate
a = doc.getObject("A7_DriveBox").Shape
a = a.cut(bx(-90.0, 54.0, 296.0, 320.0, 70.0, 160.0))            # old motor plate
mp = bx(-84.0, 48.0, MP_Y[0], MP_Y[1], *MP_Z)
mp = mp.cut(cy(MOT_R + 1.0, MP_Y[0] - 1, MP_Y[1] + 1, 0.0, MOT_Z0))
mp = mp.cut(cy(SCR_R + 0.5, MP_Y[0] - 1, MP_Y[1] + 1, SCR_X, SCR_Z))
for x0, x1 in ((-80.0, -54.0), (36.0, 46.0)):
    for z0, z1 in ((MP_Z[0] + 2, MP_Z[0] + 14), (MP_Z[1] - 14, MP_Z[1] - 2)):
        mp = mp.cut(bx(x0, x1, MP_Y[0] - 1, MP_Y[1] + 1, z0, z1))
# tie the plate back to the bracket body with two webs, outboard of the belt
for sgn in (-1.0, 1.0):
    lo, hi = sorted((sgn * 41.5, sgn * 48.0))
    a = a.fuse(bx(lo, hi, 295.0, MP_Y[0] + 0.1, 88.0, 134.0))  # 295: the cut above
    # ended the bracket body at Y 296, so the web must start inside it, not at 298
a = a.fuse(mp)
a = a.removeSplitter()
assert len(a.Solids) == 1, "A7 solids=%d" % len(a.Solids)
doc.getObject("A7_DriveBox").Shape = a
b = a.BoundBox
print("A7  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  %.1f cm3 -> %.0f g"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax,
         a.Volume / 1000., a.Volume / 1000. * 2.70))
vs_leg(a, "A7_DriveBracket")

# ------------------------------------------------------------------- 4. cap
CAP_X = (-90.0, 54.0)
CAP_Y = (300.0, 406.0)
CAP_Z = (82.0, 154.0)
c = bx(CAP_X[0], CAP_X[1], CAP_Y[0], CAP_Y[1], *CAP_Z)
c = c.cut(bx(CAP_X[0] + 3, CAP_X[1] - 3, CAP_Y[0] - 1, CAP_Y[1] - 3,
             CAP_Z[0] + 3, CAP_Z[1] - 3))
c = c.removeSplitter()
assert len(c.Solids) == 1, "P22 solids=%d" % len(c.Solids)
vs_leg(c, "P22_DriveCap")
doc.getObject("P22_DriveCap").Shape = c
print("P22 cap X %.0f..%.0f (%.0f wide, was 190) Y %.0f..%.0f Z %.0f..%.0f, open distally"
      % (CAP_X[0], CAP_X[1], CAP_X[1] - CAP_X[0], *CAP_Y, *CAP_Z))

doc.recompute()
doc.save()
print("STAGE 5 DONE, saved.")
