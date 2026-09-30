# -*- coding: utf-8 -*-
"""Close what can be closed, without a fin on the knee.

An earlier pass covered the whole 106 deg swept fan with a static lateral cheek grown
off P20 (r 40..108, Z 127..132). Geometrically it worked -- zero interference across the
ROM -- but it is a 216 mm flat plate standing off the side of the knee, which is both
ugly and a snag hazard in its own right. The thing it was covering is bare *structural
plate*, not mechanism: there is no pinch hazard out there, only cosmetics. Trading a
cosmetic gap for a fin that catches door frames is a bad deal, so it is gone.

What is here instead:

  P24_FairingShank  += tapered proximal tip, Y -100 -> -66
  P21_ShellAnterior  = trimmed back to Y = 290
  P22_DriveCap       = new part, Y 290..399, over the drive box and the motor

The shank tip tapers in WIDTH so its radius from the knee axis shrinks and it clears the
knee shroud through the swing. A constant-section shell only reaches Y = -80; tapered,
-66 is clean. That takes the moving gap from 55 mm to 20 mm (P20 already reaches Y = -46),
which a fabric gaiter covers -- standard orthotic practice, and it looks better than a
plate. Tapering the Z band as well buys nothing, because the swing is a rotation about Z
and Z is invariant under it.

Run 217_fairing.py first: this script assumes the stock fairings.

Axes: +Y proximal, Z is the knee axis so Z is medial-lateral (a lateral upright),
+X posterior -- the shank swings toward +X in flexion.
"""
import math, FreeCAD, Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

t = globals().get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
globals()["_kx_timer"] = None

for o in doc.Objects:                      # Shape bakes the placement in
    if o.TypeId.startswith("Part::"):
        o.Placement = FreeCAD.Placement()
doc.recompute()

O = lambda n: doc.getObject(n)
N_EXP, N_PTS = 5.5, 40


def need(sh, label, solids=1):
    assert sh.isValid(), "%s invalid" % label
    assert len(sh.Solids) == solids, "%s solids=%d (want %d)" % (label, len(sh.Solids), solids)
    assert sh.isClosed(), "%s not closed" % label
    return sh


def sell(y, xc, a, b, zc):
    pts = []
    for i in range(N_PTS + 1):
        th = 2.0 * math.pi * i / N_PTS
        c, s = math.cos(th), math.sin(th)
        pts.append(V(xc + a * math.copysign(abs(c) ** (2.0 / N_EXP), c), y,
                     zc + b * math.copysign(abs(s) ** (2.0 / N_EXP), s)))
    pts[-1] = pts[0]
    return Part.Wire(Part.makePolygon(pts))


def loft(st):
    return Part.makeLoft([sell(*s) for s in st], True, True)


# ------------------------------------------------- shank fairing, proximal tip
# P24's own section at Y=-100 is a=24, b=25, zc=100 truncated at Z=96. The tip carries
# that up to a=14, Z 101..117 at Y=-66. A superellipse is strictly inside the rectangle
# of the same half-dimensions, and the rectangular version of this tip was swept clean,
# so this is the conservative case -- but 231_verify.py re-runs the whole sweep anyway.
# The swing is a rotation about Z, so Z is INVARIANT under it: only the X,Y footprint --
# the radius from the knee axis -- decides sweep clearance. An earlier version tapered the
# Z band too (zc 100 -> 109, b 25 -> 8), which bought nothing and drove the tip's lower
# wall straight through A4_Shank2020_VSlot, which runs at Z 94..114 out to Y = -70.
# So: keep P24's own Z band and taper the WIDTH only.
#            y      xc     a     b     zc
TIP_O = [(-100.0, 0.0, 24.0, 25.0, 100.0),
         (-88.0,  0.0, 21.0, 25.0, 100.0),
         (-80.0,  0.0, 18.0, 25.0, 100.0),
         (-72.0,  0.0, 15.5, 25.0, 100.0),
         (-66.0,  0.0, 14.0, 25.0, 100.0)]
# inner overruns the DISTAL end and must also run past A4's proximal end at Y = -70, or
# the solid tip cap closes over the rail
TIP_I = [(-102.0, 0.0, 21.0, 22.0, 100.0),
         (-88.0,  0.0, 18.0, 22.0, 100.0),
         (-80.0,  0.0, 15.0, 22.0, 100.0),
         (-68.0,  0.0, 11.5, 22.0, 100.0)]

tip = need(loft(TIP_O), "shank tip outer").cut(need(loft(TIP_I), "shank tip inner"))
tip = tip.cut(Part.makeBox(80., 60., 60., V(-40., -102., 40.)))   # open below Z=96, as P24 is
tip = need(tip.removeSplitter(), "shank tip")

p24 = O("P24_FairingShank")
if p24.Shape.BoundBox.YMax < -95.0:
    fused = need(p24.Shape.fuse(tip).removeSplitter(), "P24 + tip")
    p24.Shape = fused
    b = fused.BoundBox
    print("P24_FairingShank  %.1f cm3  Y %+.1f..%+.1f  X %+.1f..%+.1f  Z %+.1f..%+.1f"
          % (fused.Volume / 1000., b.YMin, b.YMax, b.XMin, b.XMax, b.ZMin, b.ZMax))
    print("  moving gap now Y %+.1f..%+.1f = %.0f mm (was 55) -> fabric gaiter"
          % (b.YMax, -46.0, -46.0 - b.YMax))
else:
    print("P24 already extended (YMax %.1f)" % p24.Shape.BoundBox.YMax)

# A4 runs at Z 94..114 out to Y = -70, inside the tip. Both move with the shank, so any
# overlap is CONSTANT across the sweep -- the signature of a static error. Check it here
# rather than three chunks into a 107-pose run.
_a4 = O("A4_Shank2020_VSlot").Shape.common(O("P24_FairingShank").Shape).Volume / 1000.
print("  A4 vs P24 (must be 0): %.3f cm3 %s" % (_a4, "" if _a4 < 0.01 else "<-- FAIL"))

# ------------------------------------------------------------- the drive cap
JOIN = 290.0
p21 = O("P21_ShellAnterior")
if p21.Shape.BoundBox.YMax > JOIN + 0.5:
    trimmed = need(p21.Shape.cut(Part.makeBox(400., 60., 200., V(-200., JOIN, 40.)))
                   .removeSplitter(), "P21 trimmed")
    p21.Shape = trimmed
    print("P21_ShellAnterior trimmed to Y <= %.0f  (%.1f cm3)" % (JOIN, trimmed.Volume / 1000.))
else:
    print("P21_ShellAnterior already trimmed")

# The motor is a 63 mm can at X = -58, Z = 118, needing X = -89.5 and Z = 149.5. A
# symmetric section that wide would be a 200 mm pod, mostly empty posteriorly, so the
# section centre walks to xc = -20. Two constraints time that walk: going negative early
# pulls the posterior wall into the drive box (X = +70 until Y = 311), and necking down
# early puts the motor through the wall -- so the section stays full until Y = 389.
#           y      xc     a     b     zc
OUTER = [(JOIN,    0.0, 84.0, 23.0, 115.0),      # matches P21's section
         (300.0,  -2.0, 86.0, 28.0, 116.0),
         (308.0,  -4.0, 88.0, 35.0, 117.5),
         (312.0,  -8.0, 90.0, 39.0, 118.5),
         (317.0, -14.0, 90.0, 41.0, 118.5),
         (324.0, -20.0, 86.0, 41.0, 118.5),
         (348.0, -20.0, 82.0, 40.0, 118.5),
         (375.0, -20.0, 80.0, 39.5, 118.5),
         (389.0, -19.0, 79.0, 39.0, 118.5),
         (394.0, -18.0, 62.0, 30.0, 118.5),
         (399.0, -17.0, 36.0, 17.0, 118.5)]
W = 3.5
INNER = [(st[0], st[1], st[2] - W, st[3] - W, st[4]) for st in OUTER[:-1]]
INNER[0] = (JOIN - 2.0, 0.0, 84.0 - W, 23.0 - W, 115.0)

o_ = need(loft(OUTER), "cap outer")
cap = need(loft(OUTER), "cap outer").cut(need(loft(INNER), "cap inner"))
# Open the medial face only as far as the drive box. P21's convention -- open below
# Z=92, because that side lies against the limb -- is right for the thigh canopy and
# wrong over an outrunner: the whole bell rotates, and leaving it open exposed a 5.5 mm
# band of spinning case at Z 86.5..92 pointing at the leg. From Y=310 the cap closes
# right round. That makes it a clamshell to assemble, which is noted in the BOM.
cap = cap.cut(Part.makeBox(400., 310.0 - (JOIN - 4.0), 40.0, V(-200., JOIN - 4.0, 52.0)))
cap = need(cap.removeSplitter(), "P22_DriveCap")

p22 = O("P22_DriveCap") or doc.addObject("Part::Feature", "P22_DriveCap")
p22.Label = "P22_DriveCap"
p22.Shape = cap
b = cap.BoundBox
print("P22_DriveCap      %.1f cm3  X %+.1f..%+.1f  Y %+.1f..%+.1f  Z %+.1f..%+.1f"
      % (cap.Volume / 1000., b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

# --------------------------------------------------------------- static checks
medial = Part.makeBox(500., 200., 60., V(-250., JOIN - 10., 32.))
ok = True
for n in ("A3_Motor_6374", "A7_DriveBox", "A2_BallScrew_SFU1620", "A2c_BallScrew_LH",
          "P3_Carriage", "P3b_CarriageB", "REF_Thigh", "P21_ShellAnterior",
          "A1_Extrusion_20x60_VSlot"):
    o = O(n)
    if o and cap.BoundBox.intersect(o.Shape.BoundBox):
        v = cap.common(o.Shape).Volume / 1000.
        if v > 0.01:
            ok = False
            print("  FAIL %s pierces the cap wall by %.2f cm3" % (n, v))
for n in ("A3_Motor_6374", "A7_DriveBox"):
    v = O(n).Shape.cut(o_).cut(medial).Volume / 1000.
    if v > 0.05:
        ok = False
        print("  FAIL %s %.2f cm3 outside the cap envelope above Z=92" % (n, v))
print("  static checks: %s" % ("all clear" if ok else "SEE FAILURES ABOVE"))
print("  P20_KneeCap left alone at %.1f cm3 -- no cheek" % (O("P20_KneeShroud").Shape.Volume / 1000.))

doc.recompute()
doc.save()
print("done")
