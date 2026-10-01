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

4. (The drive cap used to be rebuilt here as a box. It is a loft now and lives in
   399_drivecap.py; this file no longer touches it.)

Send with:  python tools/fcsend.py scripts/396_fixes.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
BIN, BOUT = R - 1.372, R + 4.2
BZ = (96.0, 126.0)
RX = (-20.0, 20.0)
RZ = (88.0, 108.0)
SCR_X, SCR_Z, SCR_R = -62.0, 106.0, 7.9
NUT_R = 18.0
A0 = 161.0
WHEEL_Y = 35.0
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

# The motor, screw, link belt and motor mount all moved into 393_driveend.py when the
# motor went anterior (402_motor_anterior.py). This file used to rebuild them here and
# would now undo that, so those blocks are gone. It keeps the V-wheel geometry and the
# leg checks.
vs_leg(doc.getObject('A3_Motor_6374').Shape, 'A3_Motor')
vs_leg(doc.getObject('A7_DriveBox').Shape, 'A7_DriveBracket')

# P22 is built by 399_drivecap.py as a loft, not here as a box. The box version that
# used to live here drove 0.485 cm3 into the thigh once the cap's Y range moved.

doc.recompute()
doc.save()
print("STAGE 5 DONE, saved.")
