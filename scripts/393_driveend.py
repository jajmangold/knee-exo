# -*- coding: utf-8 -*-
"""STAGE 3: the drive end -- bracket, idler support, motor, cap.

The idler cannot sit on the rail (a 71 mm pulley on a 40 mm extrusion puts the extrusion
inside the pulley), and it cannot be held from inboard either, for the same reason. So it
hangs in a yoke that reaches it from OUTBOARD of the belt band and from above and below
it: the only three places that are free at Z 96..126 are |X| > 41.124, Z < 96 and Z > 126.

  end plate  X +/-46.5 Y 207..217  Z  88..108  bolts to the rail's proximal end,
                                               slotted for the two belt strands
  bottom     X +/-46.5 Y 217..298  Z  88..92    under the belt; lower idler bearing
  top        X +/-46.5 Y 217..298  Z 126.3..130.3 over the belt; upper idler bearing
  cheeks     |X| 41.5..46.5        Z  88..130.3 outboard of the belt, ties them together
  screw boss X -84..-41.5 Y 286..298 Z 88..124  upper screw bearing
  motorplate X -84..48  Y 298..306  Z  78..144  bored for the motor and the screw

The motor faces PROXIMALLY with its shaft out the far end, so the 1:1 link belt sits at
Y 382..394 clear of everything, instead of fighting the idler wrap for the space at Y 300.

Send with:  python tools/fcsend.py scripts/393_driveend.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
BIN, BOUT = R - 1.372, R + 4.2
PUL_R = BIN
BZ = (96.0, 126.0)
RY = (56.0, 207.0)
SCR_X, SCR_Z, SCR_R = -62.0, 106.0, 7.9
NUT_R = 18.0
IDL_Y = 255.0

# Plate and cheek thicknesses come from 400_bracket_stress.py, not from what was
# convenient to fuse. The first version used 7.7 mm plates and 6.5 mm cheeks and ran at
# 18 MPa against 240 -- about 50x overbuilt. At 4 mm plates and 5 mm cheeks the worst
# stress is 28.6 MPa (axle bearing) and the worst deflection 0.0009 mm.
BR_X = 46.5
CHEEK = 41.5
END_Y = (207.0, 217.0)
BODY_Y = (217.0, 298.0)
BOT_Z = (88.0, 92.0)
TOP_Z = (126.3, 130.3)
MP_Y = (298.0, 306.0)
MP_Z = (78.0, 144.0)
BOSS_X = (-84.0, -CHEEK)
BOSS_Y = (286.0, 298.0)
MOT_R, MOT_Z0 = 31.5, 111.0
MOT_Y = (306.0, 380.0)
LINK_Y = (382.0, 394.0)
SCR_Y = (70.0, 396.0)


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


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


assert CHEEK > BOUT, "cheeks are inside the belt band"
assert BOT_Z[1] < BZ[0] and TOP_Z[0] > BZ[1], "bracket plates are inside the belt band"
assert BOSS_Y[0] > IDL_Y - PUL_R, "screw boss is beside the idler, check X"
assert MP_Y[0] > IDL_Y + BOUT, "motor plate fouls the idler wrap"

# ------------------------------------------------------------ A7 drive bracket
a = bx(-BR_X, BR_X, END_Y[0], END_Y[1], 88.0, 108.0)
for sgn in (-1.0, 1.0):
    a = a.cut(bx(sgn * BIN - 0.3 if sgn > 0 else -BOUT - 0.3,
                 sgn * BOUT + 0.3 if sgn > 0 else -BIN + 0.3,
                 END_Y[0] - 1, END_Y[1] + 1, BZ[0] - 0.3, BZ[1] + 0.3))
a = a.fuse(bx(-BR_X, BR_X, BODY_Y[0], BODY_Y[1], *BOT_Z))
a = a.fuse(bx(-BR_X, BR_X, BODY_Y[0], BODY_Y[1], *TOP_Z))
for sgn in (-1.0, 1.0):
    lo, hi = sorted((sgn * CHEEK, sgn * BR_X))
    a = a.fuse(bx(lo, hi, BODY_Y[0], BODY_Y[1], BOT_Z[0], TOP_Z[1]))
a = a.fuse(bx(BOSS_X[0], BOSS_X[1], BOSS_Y[0], BOSS_Y[1], 88.0, SCR_Z + NUT_R))
mp = bx(BOSS_X[0], BR_X, MP_Y[0], MP_Y[1], *MP_Z)
mp = mp.cut(cy(MOT_R + 1.0, MP_Y[0] - 1, MP_Y[1] + 1, 0.0, MOT_Z0))
a = a.fuse(mp)
a = a.cut(cy(SCR_R + 0.5, BOSS_Y[0] - 1, MP_Y[1] + 1, SCR_X, SCR_Z))
a = a.removeSplitter()
assert len(a.Solids) == 1, "A7 solids=%d" % len(a.Solids)
assert a.isValid(), "A7 invalid"
o = doc.getObject("A7_DriveBox")
o.Shape = a
o.Label = "A7_DriveBracket_Idler"
b = a.BoundBox
print("A7  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  %.1f cm3"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, a.Volume / 1000.))

# -------------------------------------------------------------------- A2 screw
s = cy(SCR_R, SCR_Y[0], SCR_Y[1], SCR_X, SCR_Z)
put("A2_BallScrew_SFU1620", "A2_BallScrew_SFU1610_RH", s)
print("A2 screw Y %.0f..%.0f (%.0f mm, order 400)" % (SCR_Y[0], SCR_Y[1],
                                                      SCR_Y[1] - SCR_Y[0]))

# -------------------------------------------------------------------- A3 motor
m = cy(MOT_R, MOT_Y[0], MOT_Y[1], 0.0, MOT_Z0)
put("A3_Motor_6374", "A3_Motor_C6374_170Kv", m)
print("A3 motor X %.1f..%.1f Z %.1f..%.1f Y %.0f..%.0f  (was X -89.5..-26.5, Z 86.5..149.5)"
      % (-MOT_R, MOT_R, MOT_Z0 - MOT_R, MOT_Z0 + MOT_R, *MOT_Y))

# ----------------------------------------------------------------- link belt
lk = bx(SCR_X - 18.0, 18.0, LINK_Y[0], LINK_Y[1], MOT_Z0 - 18.0, MOT_Z0 + 18.0)
put("A7b_LinkBelt", "A7b_LinkBelt_1to1_HTD5M", lk, group="C_Drive")
print("A7b 1:1 link belt X %.0f..%.0f at Y %.0f..%.0f" % (SCR_X - 18, 18, *LINK_Y))

# ------------------------------------------------------------------ P22 cap
CAP_X = (-90.0, 54.0)
CAP_Y = (292.0, 404.0)
CAP_Z = (72.0, 150.0)
c = bx(CAP_X[0], CAP_X[1], CAP_Y[0], CAP_Y[1], CAP_Z[0], CAP_Z[1])
c = c.cut(bx(CAP_X[0] + 3, CAP_X[1] - 3, CAP_Y[0] + 3, CAP_Y[1] + 1,
             CAP_Z[0] + 3, CAP_Z[1] - 3))
c = c.removeSplitter()
assert len(c.Solids) == 1, "P22 solids=%d" % len(c.Solids)
o = doc.getObject("P22_DriveCap")
o.Shape = c
o.Label = "P22_DriveCap"
print("P22 cap X %.0f..%.0f (%.0f mm wide, was 190) Z %.0f..%.0f  %.1f cm3"
      % (CAP_X[0], CAP_X[1], CAP_X[1] - CAP_X[0], CAP_Z[0], CAP_Z[1], c.Volume / 1000.))

doc.recompute()
print("STAGE 3 DONE -- objects now %d" % len(doc.Objects))
