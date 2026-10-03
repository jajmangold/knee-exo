# -*- coding: utf-8 -*-
"""Turn the motor over so its shaft points down the limb, and take 90 mm out of the ball screw.

Asked at the bench: "wouldn't it make more sense to invert the motor upside down and shorten the
screw a bunch". Measured before building, and yes:

    screw as drawn              Y 57..314 = 257 mm
    thread the nut actually uses   Y 73..183
    shaft above the nut's travel          131 mm, carrying torque and nothing else

The screw is that long only because the link belt sits on TOP of the drive, at Y 302..314, so the
screw has to reach up past the motor to meet it. Turn the motor over and the belt moves to the
motor's other end, below it, and the screw stops just above the nut.

THE STACK, FROM THE BOTTOM, AND WHY EACH NUMBER IS WHAT IT IS

    Y 203     the carriage's proximal end at rest. It only ever retreats from here, so this is
              the hard floor for anything fixed to the frame.
    Y 208-220 the link belt and both pulleys, 12 mm wide, 5 mm clear of the carriage
    Y 220-228 the motor's mounting plate: the shaft passes through it into the pulley
    Y 228-302 the motor, turned over. Its body does not grow the envelope -- it was Y 217..291
    Y 302+    the motor's free shaft end, where the magnet goes, in the space the belt vacated.
              434_odrive_mount.py puts the controller there, which is the only place it can go.

    screw     Y 57..224, with the 608 at Y 190..197 and the 20T pulley at 208..220
              167 mm instead of 257: 90 mm less screw, about 150 g of steel

WHAT THIS DOES NOT DO. P22_DriveCap runs to Y 334 and P25_MotorNacelle to Y 326, both sized to
cover a link belt that is no longer up there. There is roughly 30 mm of shell to come off once the
controller's envelope is known, and that is a cladding job for after the board is measured.

    freecadcmd.exe scripts/433_drive_flip.py
"""
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

M5 = 5.2
MOT_X, MOT_Z, MOT_R = -104.0, 62.0, 31.5
SCREW_X, SCREW_Z = -62.0, 106.0
MOTOR_Y = (228.0, 302.0)
PLATE_Y = (220.0, 228.0)
BELT_Y = (208.0, 220.0)
# THE 608 GOES IN THE MOTOR'S PLATE, not in a boss of its own. A boss at Y 190 -- just above the
# nut's travel, which is where it wants to be -- attaches to nothing: the bracket is empty until
# Y 206. The plate carries the screw's axis anyway (its section spans X -135..+46), it is 8 mm
# thick and a 608 is 7 mm wide, and this is what the original bracket did at Y 291..299: one
# plate holding the motor and the screw's upper bearing.
BRG_Y = (220.0, 227.0)          # the 608, seated in the motor plate
SCREW_Y = (57.0, 232.0)
R_BODY, R_END = 7.90, 4.00
# thread to Y 204, then dia 8 through the pulley (208..220) and the bearing (220..227). The nut
# needs thread to Y 183 at the top of its stroke, so 204 clears it by 21 mm.
JOURNAL = (71.0, 204.0)
MOT_BOLT = 12.5                 # the 25 mm square, as 428 assumed -- measure the motor
CARRIAGE_LIMIT = 203.0

a3 = doc.getObject("A3_Motor_6374")
a7 = doc.getObject("A7_DriveBox")
a7b = doc.getObject("A7b_LinkBelt")
a2 = doc.getObject("A2_BallScrew_SFU1620")
assert a3 and a7 and a7b and a2, "missing the motor, bracket, link belt or screw"
mirrored = a7.Shape.BoundBox.ZMax < 0
sgn = -1.0 if mirrored else 1.0


def z(v):
    return sgn * v


def zspan(lo, hi):
    a, b = z(lo), z(hi)
    return (min(a, b), max(a, b))


print("=" * 98)
print("DRIVE FLIPPED  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)
car = doc.getObject("P3_Carriage")
if car is not None:
    top = car.Shape.BoundBox.YMax
    print("  the carriage's proximal end is at Y %.1f; the belt starts at Y %.0f, %.0f mm clear"
          % (top, BELT_Y[0], BELT_Y[0] - top))
    assert BELT_Y[0] > top + 2.0, "the link belt would foul the carriage"

# ---------------------------------------------------------------- the motor, turned over
b3 = a3.Shape.BoundBox
a3.Shape = Part.makeCylinder(MOT_R, MOTOR_Y[1] - MOTOR_Y[0], V(MOT_X, MOTOR_Y[0], z(MOT_Z)),
                             V(0, 1, 0))
print("  motor Y %.0f..%.0f -> %.0f..%.0f, shaft now out of the DISTAL face at Y %.0f"
      % (b3.YMin, b3.YMax, MOTOR_Y[0], MOTOR_Y[1], MOTOR_Y[0]))

# ---------------------------------------------------------------- the link belt follows it
bb = a7b.Shape.BoundBox
moved = a7b.Shape.copy()
moved.translate(V(0, BELT_Y[0] - bb.YMin, 0))
a7b.Shape = moved
print("  belt  Y %.0f..%.0f -> %.0f..%.0f" % (bb.YMin, bb.YMax, BELT_Y[0], BELT_Y[1]))

# ---------------------------------------------------------------- the screw, 90 mm shorter
was = a2.Shape.Volume / 1000.0
oldlen = a2.Shape.BoundBox.YLength
shaft = Part.makeCylinder(R_END, JOURNAL[0] - SCREW_Y[0], V(SCREW_X, SCREW_Y[0], z(SCREW_Z)),
                          V(0, 1, 0))
shaft = shaft.fuse(Part.makeCylinder(R_BODY, JOURNAL[1] - JOURNAL[0],
                                     V(SCREW_X, JOURNAL[0], z(SCREW_Z)), V(0, 1, 0)))
shaft = shaft.fuse(Part.makeCylinder(R_END, SCREW_Y[1] - JOURNAL[1],
                                     V(SCREW_X, JOURNAL[1], z(SCREW_Z)), V(0, 1, 0)))
tidy = shaft.removeSplitter()
try:
    tidy.check(True)
    shaft = tidy
except Exception:
    pass
assert len(shaft.Solids) == 1, "the screw came out as %d solids" % len(shaft.Solids)
a2.Shape = shaft
a2.Label = "A2_BallScrew_SFU1610"
print("  screw Y %.0f..%.0f, %.0f mm instead of %.0f -- %.0f mm and about %.0f g of steel out"
      % (SCREW_Y[0], SCREW_Y[1], SCREW_Y[1] - SCREW_Y[0], oldlen,
         oldlen - (SCREW_Y[1] - SCREW_Y[0]), (was - shaft.Volume / 1000.0) * 7.85))

# ---------------------------------------------------------------- the bracket
sh = a7.Shape
v0 = sh.Volume
# section the old motor plate now, while it still exists: the motor's new envelope is about to
# cut straight through it
_sec0 = a7.Shape.slice(V(0, 1, 0), 295.0)
# clear the motor's new envelope, which swallows the old top plate at Y 291..299
sh = sh.cut(Part.makeCylinder(MOT_R + 1.0, (MOTOR_Y[1] + 4.0) - MOTOR_Y[0],
                              V(MOT_X, MOTOR_Y[0], z(MOT_Z)), V(0, 1, 0)))
# clear the old screw boss at Y 286..298
# Z 84..128, not 92..120: the first box stopped 2 mm short of the boss's top and left a
# 0.25 cm3 wafer floating at Z 120..122, which is a second solid and an invalid part.
_bz = zspan(SCREW_Z - 22.0, SCREW_Z + 22.0)
sh = sh.cut(Part.makeBox(34.0, 14.0, _bz[1] - _bz[0], V(SCREW_X - 17.0, 285.0, _bz[0])))
# and a window for the belt to run through. NOT a box across the bracket: a full-height slice at
# the belt's Y separates everything distal of it from everything proximal and the bracket falls
# into four pieces. Cut what the belt and its two pulleys actually sweep -- the belt's own solid
# plus a cylinder at each pulley -- which is bounded and is the real clearance anyway.
R32, R20 = 50.9 / 2.0 + 4.0, 31.8 / 2.0 + 4.0      # HTD-5M 32T and 20T pitch radii, plus belt
win = a7b.Shape.copy()
win.translate(V(0, BELT_Y[0] - win.BoundBox.YMin, 0))
win = win.fuse(Part.makeCylinder(R32, (BELT_Y[1] - BELT_Y[0]) + 4.0,
                                 V(MOT_X, BELT_Y[0] - 2.0, z(MOT_Z)), V(0, 1, 0)))
win = win.fuse(Part.makeCylinder(R20, (BELT_Y[1] - BELT_Y[0]) + 4.0,
                                 V(SCREW_X, BELT_Y[0] - 2.0, z(SCREW_Z)), V(0, 1, 0)))
sh = sh.cut(win)
print("  brkt  motor envelope, old screw boss and a belt window cut: -%.1f cm3"
      % ((v0 - sh.Volume) / 1000.0))

# the motor's mounting plate, at the end the shaft now comes out of
v1 = sh.Volume
# THE MOTOR'S PLATE IS THE OLD PLATE, MOVED -- not a box invented at the new Y. The bracket is a
# U-channel living at X >= -45; everything outboard of that, the motor included, hangs off a
# cantilevered plate, and the only one was at Y 291..299. A box drawn to the motor's own
# footprint floats: it never reaches X -45 and fuses to nothing, which is why this came out as
# three solids. Take that plate's own section and put it where the shaft now is.
_sec = _sec0
assert _sec, "no section at the old motor plate's Y -- has the bracket changed?"
_fs = [Part.Face(w) for w in _sec]
_outer = max(_fs, key=lambda f: f.Area)
_prof = _outer
for _f in _fs:
    if _f is not _outer:
        _prof = _prof.cut(_f)
_prof = _prof if _prof.ShapeType == "Face" else _prof.Faces[0]
_prof.translate(V(0, PLATE_Y[0] - 295.0, 0))
plate = _prof.extrude(V(0, PLATE_Y[1] - PLATE_Y[0], 0))
sh = sh.fuse(plate)
tidy = sh.removeSplitter()
try:
    tidy.check(True)
    sh = tidy
except Exception:
    pass
# the shaft's clearance and the four bolts
sh = sh.cut(Part.makeCylinder(6.0, (PLATE_Y[1] - PLATE_Y[0]) + 4.0,
                              V(MOT_X, PLATE_Y[0] - 2.0, z(MOT_Z)), V(0, 1, 0)))
for dx in (-MOT_BOLT, MOT_BOLT):
    for dz in (-MOT_BOLT, MOT_BOLT):
        sh = sh.cut(Part.makeCylinder(M5 / 2.0, (PLATE_Y[1] - PLATE_Y[0]) + 4.0,
                                      V(MOT_X + dx, PLATE_Y[0] - 2.0, z(MOT_Z + dz)), V(0, 1, 0)))
print("  brkt  motor plate at Y %.0f..%.0f with the shaft bore and 4 x M5 on a %.0f mm square: "
      "+%.1f cm3" % (PLATE_Y[0], PLATE_Y[1], 2 * MOT_BOLT, (sh.Volume - v1) / 1000.0))

# the screw's upper bearing, seated straight into the motor's plate
v1 = sh.Volume
sh = sh.cut(Part.makeCylinder(11.0, BRG_Y[1] - BRG_Y[0], V(SCREW_X, BRG_Y[0], z(SCREW_Z)),
                              V(0, 1, 0)))
sh = sh.cut(Part.makeCylinder(4.6, 16.0, V(SCREW_X, BRG_Y[0] - 4.0, z(SCREW_Z)), V(0, 1, 0)))
sh.check(True)
assert len(sh.Solids) == 1, "the bracket came out as %d solids" % len(sh.Solids)
a7.Shape = sh
print("  brkt  608 seated in the motor plate at Y %.0f..%.0f, pulley below it: %+.1f cm3"
      % (BRG_Y[0], BRG_Y[1], (sh.Volume - v1) / 1000.0))
print("  brkt  %.1f -> %.1f cm3" % (v0 / 1000.0, sh.Volume / 1000.0))

# ---------------------------------------------------------------- the cladding yields
# The belt's new plane runs through P25_MotorNacelle and P22_DriveCap, and the motor plate
# clips both. Same rule as everywhere else here: the shell gives way to the mechanism. Cut the
# belt's swept envelope plus the plate, not a box -- a box across the shell severs it.
# relieve against the bracket AS BUILT, not against the plate I fused into it: the plate is cut
# about afterwards and the bracket picks up the 608 seat, so an approximation of it leaves
# slivers -- 0.040 cm3 of bracket inside the nacelle, which the sweep finds and this would not.
relief = win.copy()
relief = relief.fuse(a7.Shape)
for nm in ("P25_MotorNacelle", "P22_DriveCap"):
    cl = doc.getObject(nm)
    if cl is None:
        continue
    v = cl.Shape.Volume
    cut = cl.Shape.cut(relief)
    if len(cut.Solids) == 1:
        cut.check(True)
        cl.Shape = cut
        print("  clad  %-18s relieved against the belt and the motor plate: -%.2f cm3"
              % (nm, (v - cut.Volume) / 1000.0))
        continue
    # THE NACELLE IS CUT IN TWO by the belt's new plane: the belt runs through where the shell's
    # distal end used to wrap the motor, because the motor now starts 11 mm further up. Relieving
    # it leaves a 7.6 cm3 fragment hanging below the cut. So trim the shell back to clear the
    # belt instead of perforating it, and let 406_coverage.py say whether anything down there is
    # then reachable from the skin -- it is the check that decides whether cladding is needed,
    # and it is what retired P24_FairingShank.
    cb = cl.Shape.BoundBox
    trim = cl.Shape.cut(Part.makeBox(cb.XLength + 8.0, (BELT_Y[1] + 2.0) - (cb.YMin - 4.0),
                                     cb.ZLength + 8.0,
                                     V(cb.XMin - 4.0, cb.YMin - 4.0, cb.ZMin - 4.0)))
    assert len(trim.Solids) == 1, "trimming %s gave %d solids" % (nm, len(trim.Solids))
    # and still relieve it against the bracket: trimming only clears the belt's plane, and the
    # motor plate clips the shell 2 mm further up, which is a 0.04 cm3 clash the sweep reports
    # and nothing else would
    again = trim.cut(relief)
    if len(again.Solids) == 1:
        trim = again
    trim.check(True)
    cl.Shape = trim
    print("  clad  %-18s could not be perforated without splitting, so trimmed to Y %.0f: -%.2f cm3"
          % (nm, BELT_Y[1] + 2.0, (v - trim.Volume) / 1000.0))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- verify
print()
print("  VERIFICATION")
fail = []
pairs = [("A7b_LinkBelt", "P25_MotorNacelle"), ("A7b_LinkBelt", "P22_DriveCap"),
         ("A7_DriveBox", "P25_MotorNacelle"), ("A7_DriveBox", "P22_DriveCap"),
         ("A3_Motor_6374", "A7_DriveBox"), ("A3_Motor_6374", "A7b_LinkBelt"),
         ("A2_BallScrew_SFU1620", "A7_DriveBox"), ("A7b_LinkBelt", "A7_DriveBox"),
         ("A7b_LinkBelt", "P3_Carriage"), ("A3_Motor_6374", "P25_MotorNacelle"),
         ("A2_BallScrew_SFU1620", "A2b_BallNut_SFU1620")]
for n1, n2 in pairs:
    o1, o2 = doc.getObject(n1), doc.getObject(n2)
    if o1 is None or o2 is None:
        continue
    c = o1.Shape.common(o2.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    ok = v <= 0.02 or n2 == "A2b_BallNut_SFU1620"
    print("     %-26s vs %-22s %7.3f cm3 %s"
          % (n1, n2, v, "" if ok else "<-- CLASH"))
    if not ok:
        fail.append("%s overlaps %s by %.3f cm3" % (n1, n2, v))
# the nut must still have thread under it over the whole stroke
nut = doc.getObject("A2b_BallNut_SFU1620")
if nut is not None:
    nb = nut.Shape.BoundBox
    need = (nb.YMin - 68.3, nb.YMax)
    ok = JOURNAL[0] <= need[0] and need[1] <= JOURNAL[1]
    print("     %-26s needs thread Y %.0f..%.0f, the body runs %.0f..%.0f  %s"
          % ("nut over its stroke", need[0], need[1], JOURNAL[0], JOURNAL[1], "" if ok else "<--"))
    if not ok:
        fail.append("the nut runs off the thread")
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  the motor drives downward into a belt below it, and the screw stops just above the")
    print("  nut. The space above the motor is now free for the controller.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
