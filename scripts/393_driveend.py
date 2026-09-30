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
# MOTOR ON THE FRONT OF THE THIGH (402_motor_anterior.py). On the centreline it had to
# queue behind the idler's belt wrap and cost 74 mm of PROXIMAL length, which is the one
# budget that had run out -- Y 412 is past the hip on a 1.65 m patient. Anterior, it shares
# Y with the idler instead. It cannot go just "a bit forward": a 63 mm can has to clear the
# ball screw at X -62, which pushes it all the way to X -104.
# ...and TUCKED IN toward the leg rather than sticking straight out laterally. Since the
# motor is belted to the screw rather than coaxial with it, its position in the X-Z plane
# is free -- it only has to clear the leg, the screw and the belt band. At Z 118 it stood
# 188.8 mm from the leg axis, about 20 mm proud of the canopy's own 168.1. At Z 62 it sits
# on a 121.1 mm radius, 4.6 mm off the thigh, and its outermost point is 152.6 -- INSIDE
# the canopy. It stops contributing to the device's bulge at all.
MOT_X = -104.0
MOT_R, MOT_Z0 = 31.5, 62.0
MOT_Y = (217.0, 291.0)
# An outrunner face-mounts at its SHAFT end, and the shaft faces proximal, so the mount
# plate belongs at Y 291 -- not at Y 207 where a first attempt put it. That matters for
# more than correctness: a mount at 207 forces the cap to flare from P21's section out to
# X -142 in 13 mm, which looks exactly as bad as it sounds. At 291 the cap has 87 mm to
# do it in. The same plate carries the screw's upper bearing.
MP_Y = (291.0, 299.0)
ARM_X = (-90.0, -44.0)
ARM_Z = (80.0, 100.0)   # stays outside the leg: its inboard corner is at radius 91
END_X = 46.5                   # the rail-end plate stays small
LINK_Y = (302.0, 314.0)        # clear of the idler wrap (296.1) and the mount plate
# 1:1.6 OVERDRIVE, not 1:1 (404_link_ratio.py). A 32T motor pulley driving a 20T screw
# pulley puts the total ratio at 14.5:1 -- the number 390 wanted an SFU1616 for -- using
# the SFU1610 already specced. This belt sits on the motor side of the screw's own
# advantage, so it carries 85 N, not the 764 the capstan loop carries: gearing here is
# nearly free, where 403 showed gearing the idler is not.
LINK_T_MOT, LINK_T_SCR, LINK_PITCH = 32, 20, 5.0
LINK_R_MOT = LINK_T_MOT * LINK_PITCH / (2 * math.pi) + 2.0
LINK_R_SCR = LINK_T_SCR * LINK_PITCH / (2 * math.pi) + 2.0
SCR_Y = (70.0, 314.0)


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

assert MOT_X + MOT_R < SCR_X - SCR_R - 2.0, "motor can fouls the ball screw"
assert LINK_Y[0] > IDL_Y + BOUT and LINK_Y[0] >= MP_Y[1], "link belt fouls the wrap or the mount"
assert math.hypot(MOT_X, MOT_Z0) >= 85.0 + MOT_R + 3.0, "motor is inside the leg"
assert math.hypot(MOT_X - SCR_X, MOT_Z0 - SCR_Z) >= MOT_R + SCR_R + 2.5, "motor fouls the screw"

# ------------------------------------------------------------ A7 drive bracket
a = bx(-END_X, END_X, END_Y[0], END_Y[1], 88.0, 108.0)
for sgn in (-1.0, 1.0):
    a = a.cut(bx(sgn * BIN - 0.3 if sgn > 0 else -BOUT - 0.3,
                 sgn * BOUT + 0.3 if sgn > 0 else -BIN + 0.3,
                 END_Y[0] - 1, END_Y[1] + 1, BZ[0] - 0.3, BZ[1] + 0.3))
a = a.fuse(bx(-BR_X, BR_X, BODY_Y[0], BODY_Y[1], *BOT_Z))
a = a.fuse(bx(-BR_X, BR_X, BODY_Y[0], BODY_Y[1], *TOP_Z))
for sgn in (-1.0, 1.0):
    lo, hi = sorted((sgn * CHEEK, sgn * BR_X))
    a = a.fuse(bx(lo, hi, BODY_Y[0], BODY_Y[1], BOT_Z[0], TOP_Z[1]))
# Motor mount: a disc no bigger than the motor's own face (a 6374 bolts on a ~25 mm
# circle), because any flange larger than the can would reach back inside the thigh --
# the motor is only 4.6 mm off it. An arm carries the disc back to the yoke.
mp = cy(MOT_R, MP_Y[0], MP_Y[1], MOT_X, MOT_Z0)
mp = mp.cut(cy(6.0, MP_Y[0] - 1, MP_Y[1] + 1, MOT_X, MOT_Z0))
a = a.fuse(mp)
a = a.fuse(bx(ARM_X[0], ARM_X[1], MP_Y[0], MP_Y[1], *ARM_Z))
a = a.cut(cy(SCR_R + 0.5, END_Y[0] - 1, MP_Y[1] + 1, SCR_X, SCR_Z))
a = a.removeSplitter()
assert len(a.Solids) == 1, "A7 solids=%d" % len(a.Solids)
assert a.isValid(), "A7 invalid"
o = doc.getObject("A7_DriveBox")
o.Shape = a
o.Label = "A7_DriveBracket_Idler"
b = a.BoundBox
print("A7  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  %.1f cm3 -> %.0f g"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax,
         a.Volume / 1000., a.Volume / 1000. * 2.70))

# -------------------------------------------------------------------- A2 screw
s = cy(SCR_R, SCR_Y[0], SCR_Y[1], SCR_X, SCR_Z)
put("A2_BallScrew_SFU1620", "A2_BallScrew_SFU1610_RH", s)
print("A2 screw Y %.0f..%.0f (%.0f mm, order 400)" % (SCR_Y[0], SCR_Y[1],
                                                      SCR_Y[1] - SCR_Y[0]))

# -------------------------------------------------------------------- A3 motor
m = cy(MOT_R, MOT_Y[0], MOT_Y[1], MOT_X, MOT_Z0)
put("A3_Motor_6374", "A3_Motor_C6374_170Kv", m)
print("A3 motor X %.1f..%.1f Z %.1f..%.1f Y %.0f..%.0f -- anterior, sharing Y with the idler"
      % (MOT_X - MOT_R, MOT_X + MOT_R, MOT_Z0 - MOT_R, MOT_Z0 + MOT_R, *MOT_Y))

# ----------------------------------------------------------------- link belt
# stadium: a pulley at each end and the belt spanning between, not a bounding box --
# a box around this run would sit deep inside the leg.
def stadium(r1, r2, y0, y1):
    p1 = cy(r1, y0, y1, MOT_X, MOT_Z0)
    p2 = cy(r2, y0, y1, SCR_X, SCR_Z)
    dx, dz = SCR_X - MOT_X, SCR_Z - MOT_Z0
    L = math.hypot(dx, dz)
    r = max(r1, r2)
    mid = Part.makeBox(L, y1 - y0, 2 * r, V(0, y0, -r))
    mid.rotate(V(0, y0, 0), V(0, 1, 0), -math.degrees(math.atan2(dz, dx)))
    mid.translate(V(MOT_X, 0, MOT_Z0))
    return p1.fuse(p2).fuse(mid).removeSplitter()


lk = stadium(LINK_R_MOT, LINK_R_SCR, LINK_Y[0], LINK_Y[1])
# The screw carries one of this belt's pulleys, so it runs straight through the envelope.
# Bore it, or the sweep reports 2.35 cm3 of 'clash' that is really an assembly.
lk = lk.cut(cy(SCR_R + 0.3, LINK_Y[0] - 1, LINK_Y[1] + 1, SCR_X, SCR_Z)).removeSplitter()
put("A7b_LinkBelt", "A7b_LinkBelt_1to1_HTD5M", lk, group="C_Drive")
b = lk.BoundBox
print("A7b link belt %dT:%dT HTD-%gM = 1:%.2f OVERDRIVE -> total ratio %.1f:1"
      % (LINK_T_MOT, LINK_T_SCR, LINK_PITCH, LINK_T_MOT / float(LINK_T_SCR),
         2 * math.pi * R / 10.0 * LINK_T_SCR / float(LINK_T_MOT)))
print("    X %.0f..%.0f Z %.0f..%.0f at Y %.0f..%.0f, centre distance %.0f mm"
      % (b.XMin, b.XMax, b.ZMin, b.ZMax, LINK_Y[0], LINK_Y[1],
         math.hypot(MOT_X - SCR_X, MOT_Z0 - SCR_Z)))

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
