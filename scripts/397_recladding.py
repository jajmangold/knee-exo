# -*- coding: utf-8 -*-
"""STAGE 6: re-cladding, and the spine has to go entirely.

The five flags left by 395_verify1.py were all cladding, and chasing them turned up
something bigger than the missing slot.

WHY THE SPINE CANNOT SURVIVE. P21 hung off five posts dropping into the extrusion's
MIDDLE outboard slot at X = 0. Two things killed that:

  * a 2040's 40 mm face has slots at X = +/-10, not at X = 0, and
  * far worse, the OUTBOARD face is now OCCUPIED. The gantry deck sweeps X -32.5..32 over
    Y 59..197, and the idler pulley spans X +/-35.55 over Y 213..291. Between them they
    own that whole face. A post at X = +/-10 would be inside the gantry for most of the
    stroke and inside the idler for the rest.

The mount moves to the extrusion's POSTERIOR SIDE face, which 398_sidemounts.py proves
clear at three stations over all 107 poses. (An earlier version of this file said there was
no central mount left at all and went to two end flanges -- that generalised from the
outboard face without checking the other three, and the flanges then fouled the rail, the
belt and the gantry. The anterior side face really is blocked, by the gantry's nut
structure; the posterior one is not.)

That is not a loss. Section 9 of docs/ELECTRONICS.md already named the rigid spine as the
most likely noise path: "a 284 mm canopy of ~3 mm PETG on a rigid spine straight into the
rail's middle slot -- a direct structure-borne path into a large thin panel", and its
top mitigation was "isolate the fairings (rubber grommets instead of the rigid spine;
highest leverage and it costs grams)". The one-screw layout forces the fix that was already
recommended.

WHY THE SECTION GOES ASYMMETRIC. The gantry reaches X -84 (nut at -80, plus wall) while
nothing on the +X side passes X 48. A symmetric shell wide enough for -84 would have to be
+/-93, i.e. 186 mm across -- wider than the 168 it is today. Offsetting the section's
centre to X -19.5 covers X -93..54 with a smaller half-width, and comes out 15 mm NARROWER
than the symmetric shell it replaces.

P21 also stops at Y 204 instead of 290: past that the drive bracket's top plate reaches
Z 134 at X +/-48, which is outside any section that keeps the 86 mm knee standoff. P22
takes over there and now covers the idler as well.

Send with:  python tools/fcsend.py scripts/397_recladding.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

N_EXP, N_PTS = 5.5, 32
ZC = 110.0
B_OUT, B_IN = 28.0, 25.0
XC_MID, A_MID = -19.5, 76.5          # outer; inner is 3 mm in
# P21 hands over at Y 180, not 204: the motor now starts at Y 217 and the cap has to be
# at full anterior width by then. Ending at 204 left 13 mm to flare from this section out
# to X -146, which is a shoulder, not a blend. At 180 it has 37 mm.
Y_KNEE, Y_FLARE, Y_END = 28.0, 58.0, 180.0
WALL = 3.0

CAP_X = (-90.0, 54.0)
CAP_Y = (Y_END, 406.0)
CAP_Z = (88.0, 156.0)


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cz(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def sm(u):
    u = max(0., min(1., u))
    return u * u * (3. - 2. * u)


def sell(y, xc, a, b, zc):
    pts = []
    for i in range(N_PTS):
        t = 2. * math.pi * i / N_PTS
        ct, st = math.cos(t), math.sin(t)
        pts.append(V(xc + a * math.copysign(abs(ct) ** (2. / N_EXP), ct), y,
                     zc + b * math.copysign(abs(st) ** (2. / N_EXP), st)))
    pts.append(pts[0])
    return Part.makePolygon(pts)


def loft(st):
    return Part.makeLoft([sell(*s) for s in st], True, True)


def prof(y):
    """outer (xc, a) at station y -- symmetric a=58 at the knee, morphing to the
    offset section over the same Y 28..58 the old flare used."""
    if y <= Y_KNEE:
        return 0.0, 58.0
    u = sm((y - Y_KNEE) / (Y_FLARE - Y_KNEE))
    return XC_MID * u, 58.0 + (A_MID - 58.0) * u


def inside(x, z, xc, a, b):
    return (abs(x - xc) / a) ** N_EXP + (abs(z - ZC) / b) ** N_EXP


print("=" * 74)
print("SECTION CHECK -- inner surface must contain everything that lives inside it")
xc, a = prof(160.0)
ai, bi = a - WALL, B_IN
print("  inner section: centre X %.1f, a %.1f, b %.1f -> spans X %.1f..%.1f, Z %.0f..%.0f"
      % (xc, ai, bi, xc - ai, xc + ai, ZC - bi, ZC + bi))
WORST = [("gantry deck B / spine corner", -84.0, 130.2),
         ("gantry crossing top", -32.5, 130.2),
         ("gantry deck A far side", 32.0, 123.0),
         ("belt strand +X outer", 41.124, 126.0),
         ("belt strand -X outer", -41.124, 126.0),
         ("ball nut top", -44.0, 124.0),
         ("V-wheel outer", 31.0, 116.5)]
ok = True
for nm, x, z in WORST:
    f = inside(x, z, xc, ai, bi)
    print("     %-28s X %7.1f Z %6.1f   %.3f %s" % (nm, x, z, f, "" if f <= 1 else "OUTSIDE"))
    ok = ok and f <= 1.0
assert ok, "the inner section does not contain the mechanism"
print("  (superellipse containment: (|x-xc|/a)^n + (|z-zc|/b)^n <= 1, n = %.1f)" % N_EXP)

# ------------------------------------------------------------------- P21
YS = [Y_KNEE, 38., 48., Y_FLARE, 120., 170., Y_END]
outer = [(y,) + prof(y) + (B_OUT, ZC) for y in YS]
inner = [(y, prof(y)[0], prof(y)[1] - WALL, B_IN, ZC)
         for y in [26.] + YS[1:-1] + [Y_END + 2.]]
lo = loft(outer)
f = lo.cut(loft(inner))
# THE UNDERSIDE FOLLOWS THE LEG, it is not cut off flat. 217_fairing.py opened the shell
# below Z 92 across its whole width, on the argument that "the thigh cuff tops out at Z 88
# and the carriage bottom is at Z 90, so there is no room for a wall between them". That
# is true directly under the rail and nowhere else: the leg is a CYLINDER and curves away,
# so the gap between it and where the shell's own surface naturally falls is 2.5 mm at
# X -30, 7 mm at X -40, 22 mm at X -60 and 55 mm at X -80. A flat cut throws all of that
# away and leaves the ball nut and the gantry's whole outboard structure facing the limb
# through a 66 mm wide slot running the length of the thigh.
#
# So cut with the LIMB instead of with a plane: a cylinder 3 mm proud of REF_Thigh, plus
# the cuff's own solid. The shell then closes wherever there is room and opens only where
# the leg or the cuff actually is -- and the resulting underside is a concave surface that
# follows the limb, which is what a brace should look like anyway.
# SKIRTS. 406_coverage.py fires rays from the skin and finds the gantry and the V-wheels
# reachable at +/-14 degrees -- the band just either side of the extrusion, at X ~ +/-26.
# Several of those rays report NO blocker at all between skin and gantry. The shell's own
# wall there is only Z 82..85 and the leg cut takes most of it, while the rail does not
# start until |X| 20, so there is a longitudinal slot down each side. These close it.
#
# They have to thread the gantry's own travel: web A occupies X -34.5..-32.5 and the belt
# clamp X -43.8..-32.5, both sweeping the full stroke, and the wheels reach |X| 31 at
# Z 106..117. So the skirts sit inboard of 31.5 and stop below Z 95.
for sgn in (-1.0, 1.0):
    sk0, sk1 = sorted((sgn * 20.4, sgn * 31.0))   # not lo/hi: `lo` is the outer loft
    # They run past P21's own body to Y 206.5 -- P21 stops at 180 but the gantry's deck
    # sweeps to 204, and a ray at +14 deg found P3_Carriage through that 24 mm. They
    # cannot be grown onto P22 instead: the cap's bottom wall sits at Z 78..81 and the
    # limb cut removes all of it, so a skirt there has nothing to attach to. 206.5 stops
    # short of the drive bracket's end plate at 207.
    f = f.fuse(bx(sk0, sk1, Y_KNEE, 206.5, 83.0, 95.0))
f = f.removeSplitter()

LEG_CLEAR = 3.0
legcut = Part.makeCylinder(84.9 + LEG_CLEAR, 400.0, V(0., 10., 0.), V(0, 1, 0))
f = f.cut(legcut)
cuff = doc.getObject("P5_ThighCuff")
if cuff is not None:
    f = f.cut(cuff.Shape)
f = f.cut(bx(-110., 80., 20., 50., 40., 96.))             # fork cheek sweeps to Z 94 here
# ...and the YOKE, which the skirts above drove straight through. The 107-pose sweep flagged
# P1_KneeYoke^P21 at 5.323 cm3 in two symmetric lumps, X +/-20.4..30.0 by Y 50..124 by
# Z 82.6..88 -- i.e. the full skirt cross-section, for 74 mm of its length. The yoke is a
# 12 mm plate at Z 76..88 spanning X -47..43 and reaching Y 124, and the skirts hang to
# Z 83, so they interfere over the whole of their proximal half. Two printed parts that do
# not fit together; the hand-written box above only covered Y 20..50.
# The skirt is shortened rather than moved, because what it is closing is the sightline to
# the gantry at +/-14 deg and the yoke itself blocks that band over exactly this Y range --
# it is in the BLOCK list in 406_coverage.py for the same reason. Verified by re-running it.
# The cut follows the YOKE, not its bounding box. A box spanning the yoke's X -47..43 by
# Z 40..88.6 was the obvious first try and it cost three rays: it also removed the canopy's
# own floor in that band -- the 0.7 mm of skin between the limb cut at r 87.9 and Z 88.6 --
# and that floor was the only thing standing between the skin and the ball screw at -28 deg
# over Y 76..112. 406_coverage.py went 0 -> 3 and named it. So dilate the yoke by translated
# copies (cheap, and makeOffsetShape on a 131 cm3 gyroid part is neither) and cut that.
yoke = doc.getObject("P1_KneeYoke")
if yoke is not None:
    CL = 0.6
    dil = yoke.Shape
    for d in (V(CL, 0, 0), V(-CL, 0, 0), V(0, CL, 0), V(0, -CL, 0),
              V(0, 0, CL), V(0, 0, -CL)):
        t = yoke.Shape.copy()
        t.translate(d)
        dil = dil.fuse(t)
    dil = dil.removeSplitter()
    v0 = f.Volume / 1000.0
    f = f.cut(dil)
    print("   yoke clearance: %.3f cm3 off P21 for a %.1f mm gap around the yoke"
          % (v0 - f.Volume / 1000.0, CL))
# MOUNTING. The first version of this put a full-width rib across the section at each end
# to replace the spine, and the 107-pose sweep returned four flags for it: a rib spanning
# X -100..60 at Z 92..98 cuts straight through the extrusion, BOTH belt strands and the
# gantry. A plate across the section is not a mount, it is an obstruction.
#
# 398_sidemounts.py then measured what is actually free and found the extrusion's
# POSTERIOR side face clear at every pose, at three stations -- the anterior one is not,
# because that is where the gantry's nut structure lives. So P21 gets three internal bosses
# meeting P23a/b/c, and nothing crosses the section at all.
for ystn in (88.0, 124.0, 160.0):
    boss = bx(41.5, 47.0, ystn - 8.0, ystn + 8.0, 127.8, 140.0).common(lo)
    f = f.fuse(boss)
    f = f.cut(cz(2.6, 126.0, 140.0, 44.25, ystn))
f = f.removeSplitter()
# vents, on the outboard face, clear of the new section's offset centre
for y in (80., 130., 176.):
    for sx in (-1., 1.):
        f = f.cut(bx(*sorted((XC_MID + sx * 8., XC_MID + sx * 18.)), y, y + 34., 130., 146.))
f = f.removeSplitter()
if len(f.Solids) != 1:
    raise AssertionError("P21 solids=%d, bboxes %s" % (len(f.Solids),
        ["X %.0f..%.0f Z %.0f..%.0f" % (t.BoundBox.XMin, t.BoundBox.XMax,
         t.BoundBox.ZMin, t.BoundBox.ZMax) for t in f.Solids]))
assert f.isValid(), "P21 invalid"
o = doc.getObject("P21_ShellAnterior")
o.Shape = f
o.Label = "P21_FairingThigh"
b = f.BoundBox
print("=" * 74)
print("P21  X %6.1f..%5.1f  Y %6.1f..%5.1f  Z %5.1f..%5.1f  %5.1f cm3"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, f.Volume / 1000.))
print("     %.0f mm across, against 168 for the symmetric +/-84 shell it replaces"
      % (b.XMax - b.XMin))
print("     knee standoff still Z %.0f = %.0f mm proud of a 52 mm knee" % (b.ZMax, b.ZMax - 52))
print("     Underside CLOSED against the limb: cut by a cylinder %.0f mm proud of the" % LEG_CLEAR)
print("     thigh rather than by a flat plane, so it shuts wherever there is room.")
print("     NO SPINE. Three grommeted M5 into the POSTERIOR side face (P23a/b/c, proved")
print("     clear over all 107 poses by 398_sidemounts.py), and nothing crossing the")
print("     section. Still delivers ELECTRONICS.md section 9's top noise mitigation --")
print("     isolate the canopy instead of bolting it rigidly into the rail's middle slot --")
print("     but with real mid-span support, which two end flanges would not have given.")

# ------------------------------------------------------------------- P22
c = bx(CAP_X[0], CAP_X[1], CAP_Y[0], CAP_Y[1], *CAP_Z)
c = c.cut(bx(CAP_X[0] + WALL, CAP_X[1] - WALL, CAP_Y[0] - 1, CAP_Y[1] - WALL,
             CAP_Z[0] - 1, CAP_Z[1] - WALL))
c = c.removeSplitter()
assert len(c.Solids) == 1, "P22 solids=%d" % len(c.Solids)
o = doc.getObject("P22_DriveCap")
o.Shape = c
o.Label = "P22_DriveCap"
b = c.BoundBox
print("P22  X %6.1f..%5.1f  Y %6.1f..%5.1f  Z %5.1f..%5.1f  %5.1f cm3"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, c.Volume / 1000.))
print("     %.0f mm across, against 190 for the two-screw cap. Open below Z %.0f and at"
      % (b.XMax - b.XMin, CAP_Z[0]))
print("     its distal face, so the rail, the belt and the bracket pass through, and it")
print("     now covers the idler as well as the motor.")

REF = doc.getObject("REF_Thigh").Shape
for nm, sh in (("P21", f), ("P22", c)):
    k = sh.common(REF)
    v = 0.0 if k.isNull() else k.Volume / 1000.0
    print("     %s vs REF_Thigh: %.3f cm3" % (nm, v))
    assert v < 0.02, "%s intrudes into the leg by %.3f cm3" % (nm, v)
# The skirts went through the yoke for 107 poses before the sweep was read carefully enough
# to notice that this pair was not one of the deliberate bonds. Check it here, where it is
# cheap, rather than at the end of a 20-minute sweep.
for nm in ("P1_KneeYoke", "P2a_KneeHingePlate", "P20_KneeShroud"):
    ob = doc.getObject(nm)
    if ob is None:
        continue
    k = f.common(ob.Shape)
    v = 0.0 if k.isNull() else k.Volume / 1000.0
    print("     P21 vs %-20s %.3f cm3" % (nm, v))
    assert v < 0.02, "P21 clashes with %s by %.3f cm3" % (nm, v)

doc.recompute()
doc.save()
print("STAGE 6 DONE, saved.")
