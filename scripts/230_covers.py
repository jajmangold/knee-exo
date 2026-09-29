# -*- coding: utf-8 -*-
"""Close the two remaining holes in the cladding, both from the STATIC side.

The shank-side gap was never a reach problem, it was a sweep problem: a shank-mounted
shell has to swing past the static thigh fairing, which caps it at 34 of the 55 mm. A
thigh-mounted cover never sweeps -- it only has to clear the shank laterally in Z, and
nothing on the shank exceeds Z = 126 (hinge plate tops out there, the pin at 126, the
rail at 114). So Z >= 127 is free at ANY radius, and a static cheek can cover the whole
106 deg fan with no gap and no gaiter.

  P20_KneeShroud  += lateral cheek sector, r 40..108, Z 127..132, -100..+26 deg
  P21_ShellAnterior trimmed back to Y = 290
  P22_DriveCap     = new part, Y 290..396, over the drive box and the motor

P21 runs at a constant a=84, b=23, zc=115 and then closes from Y=300, while the motor
starts at Y=314 already needing Z 86.5..149.5. There is no room to flare between the two,
so the cap cannot simply butt onto P21's end face -- P21 gets trimmed to Y=290 and the cap
takes over the last 22 mm of canopy to have somewhere to put the shoulder.

Axes, because they are not guessable: +Y proximal, Z is the knee axis so Z is
medial-lateral (this is a lateral upright), +X posterior -- the shank swings to +X.
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

# geometry must be edited unposed -- obj.Shape bakes the placement in
for o in doc.Objects:
    if o.TypeId.startswith("Part::"):
        o.Placement = FreeCAD.Placement()
doc.recompute()

O = lambda n: doc.getObject(n)


def need(sh, label, solids=1):
    assert sh.isValid(), "%s invalid" % label
    assert len(sh.Solids) == solids, "%s solids=%d (want %d)" % (label, len(sh.Solids), solids)
    assert sh.isClosed(), "%s not closed" % label
    return sh


# ---------------------------------------------------------------- the cheek
R_IN, R_OUT = 40.0, 108.0
ZC0, ZC1 = 127.0, 132.0
A0, A1 = -100.0, 26.0          # from +X (posterior) toward +Y (proximal)

out = Part.makeCylinder(R_OUT, ZC1 - ZC0, V(0, 0, ZC0), V(0, 0, 1), A1 - A0)
out.rotate(V(0, 0, 0), V(0, 0, 1), A0)
inn = Part.makeCylinder(R_IN, ZC1 - ZC0 + 2, V(0, 0, ZC0 - 1), V(0, 0, 1))
cheek = need(out.cut(inn), "cheek sector")
ALREADY = O("P20_KneeShroud").Shape.BoundBox.XMax > 100.0   # re-runnable

# soften the outer rim so it does not read as a cut-off disc
try:
    rim = [e for e in cheek.Edges
           if abs(e.BoundBox.ZMax - e.BoundBox.ZMin) < 1e-6
           and abs(math.hypot(e.CenterOfMass.x, e.CenterOfMass.y) - R_OUT) < 6.0]
    if rim:
        f = cheek.makeFillet(1.6, rim)
        if f.isValid() and len(f.Solids) == 1:
            cheek = f
            print("cheek: filleted %d rim edges" % len(rim))
except Exception as e:
    print("cheek: fillet skipped (%s)" % str(e)[:60])

p20 = O("P20_KneeShroud")
before = p20.Shape.Volume / 1000.0
if ALREADY:
    print("P20 already carries the cheek (bbox XMax %.1f) -- refusing to double-fuse"
          % p20.Shape.BoundBox.XMax)
fused = need(p20.Shape.fuse(cheek).removeSplitter(), "P20 + cheek")
p20.Shape = fused
print("P20_KneeShroud  %.1f -> %.1f cm3  (cheek adds %.1f)"
      % (before, fused.Volume / 1000.0, fused.Volume / 1000.0 - before))
b = fused.BoundBox
print("  bbox X %+.1f..%+.1f  Y %+.1f..%+.1f  Z %+.1f..%+.1f"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

# ------------------------------------------------------------- the drive cap
N_EXP, N_PTS = 5.5, 40


def sell(y, xc, a, b, zc):
    """superellipse section in the XZ plane at station y, centre (xc, zc)"""
    pts = []
    for i in range(N_PTS + 1):
        th = 2.0 * math.pi * i / N_PTS
        c, s = math.cos(th), math.sin(th)
        x = xc + a * math.copysign(abs(c) ** (2.0 / N_EXP), c)
        z = zc + b * math.copysign(abs(s) ** (2.0 / N_EXP), s)
        pts.append(V(x, y, z))
    pts[-1] = pts[0]
    return Part.Wire(Part.makePolygon(pts))


def loft(st):
    return Part.makeLoft([sell(*s) for s in st], True, True)


# trim P21 so the cap has 24 mm to get from P21's section up to motor size
JOIN = 290.0
p21 = O("P21_ShellAnterior")
if p21.Shape.BoundBox.YMax > JOIN + 0.5:
    trimmed = need(p21.Shape.cut(Part.makeBox(400., 60., 200., V(-200., JOIN, 40.)))
                   .removeSplitter(), "P21 trimmed")
    p21.Shape = trimmed
    print("P21_ShellAnterior trimmed to Y <= %.0f  (%.1f cm3)"
          % (JOIN, trimmed.Volume / 1000.0))
else:
    print("P21_ShellAnterior already trimmed")

# The motor is a 63 mm can at X = -58, Z = 118, so the cap has to reach X = -89.5 and
# Z = 149.5. A symmetric section wide enough for that needs a = 100, i.e. a 200 mm wide
# pod, most of it empty on the posterior side -- so the section centre walks out to
# xc = -20 instead. Two constraints set the timing of that walk:
#   * the posterior reach (xc + a) must stay past X = +74 until the drive box ends at
#     Y = 311, or walking xc negative pulls the wall into A7;
#   * the section must stay full until Y = 389, because the motor runs to 388. Necking
#     down at 384 put 1.22 cm3 of motor through the wall.
#           y      xc     a     b     zc
OUTER = [(JOIN,    0.0, 84.0, 23.0, 115.0),      # matches P21's section exactly
         (300.0,  -2.0, 86.0, 28.0, 116.0),
         (308.0,  -4.0, 88.0, 35.0, 117.5),
         (312.0,  -8.0, 90.0, 39.0, 118.5),      # drive box clear from here
         (317.0, -14.0, 90.0, 41.0, 118.5),      # motor starts at 314
         (324.0, -20.0, 86.0, 41.0, 118.5),
         (348.0, -20.0, 82.0, 40.0, 118.5),
         (375.0, -20.0, 80.0, 39.5, 118.5),
         (389.0, -19.0, 79.0, 39.0, 118.5),      # motor ends at 388 -- stay full
         (394.0, -18.0, 62.0, 30.0, 118.5),
         (399.0, -17.0, 36.0, 17.0, 118.5)]
W = 3.5
# inner OVERRUNS the open distal end and stops SHORT of the closed tip, or the boolean
# leaves an end wall -- the trap that put a phantom 0.441 cm3 in the shank fairing
INNER = [(st[0], st[1], st[2] - W, st[3] - W, st[4]) for st in OUTER[:-1]]
INNER[0] = (JOIN - 2.0, 0.0, 84.0 - W, 23.0 - W, 115.0)

o_ = need(loft(OUTER), "cap outer")
i_ = need(loft(INNER), "cap inner")
cap = o_.cut(i_)
# open the medial face, the side lying against the limb -- same convention as P21
cap = cap.cut(Part.makeBox(400., 130., 40.0, V(-200., JOIN - 4.0, 52.0)))
cap = need(cap.removeSplitter(), "P22_DriveCap")

p22 = O("P22_DriveCap")
if p22 is None:
    p22 = doc.addObject("Part::Feature", "P22_DriveCap")
    p22.Label = "P22_DriveCap"
p22.Shape = cap
b = cap.BoundBox
print("P22_DriveCap    %.1f cm3" % (cap.Volume / 1000.0))
print("  bbox X %+.1f..%+.1f  Y %+.1f..%+.1f  Z %+.1f..%+.1f"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))

# --- the checks that matter -------------------------------------------------
# 1. nothing may pierce the cap WALL
for n in ("A3_Motor_6374", "A7_DriveBox", "A2_BallScrew_SFU1620", "A2c_BallScrew_LH",
          "P3_Carriage", "P3b_CarriageB", "REF_Thigh", "P21_ShellAnterior",
          "A1_Extrusion_20x60_VSlot"):
    o = O(n)
    if o and cap.BoundBox.intersect(o.Shape.BoundBox):
        v = cap.common(o.Shape).Volume / 1000.0
        print("  %-24s pierces the wall by %6.2f cm3 %s"
              % (n, v, "<-- FAIL" if v > 0.01 else "ok"))
# 2. the motor and drive box must sit INSIDE the outer envelope, bar the medial slice
medial = Part.makeBox(500., 200., 60., V(-250., JOIN - 10., 32.))    # Z 32..92
for n in ("A3_Motor_6374", "A7_DriveBox"):
    s = O(n).Shape
    outside = s.cut(o_).cut(medial).Volume / 1000.0
    print("  %-24s outside the envelope above Z=92: %6.2f cm3 %s"
          % (n, outside, "<-- FAIL" if outside > 0.05 else "ok"))
# 3. seam with P21
print("  P21 <-> cap Y seam       %.3f mm gap, %.3f cm3 overlap"
      % (cap.BoundBox.YMin - O("P21_ShellAnterior").Shape.BoundBox.YMax,
         O("P21_ShellAnterior").Shape.common(cap).Volume / 1000.0))

doc.recompute()
doc.save()
print("done")
