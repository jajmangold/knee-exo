# -*- coding: utf-8 -*-
"""STAGE 8: the drive-end cover -- one continuous surface, split into two printed parts.

HISTORY, because this went wrong twice and the reasons are worth keeping.

v1 was a rectangular box. It looked like a shoebox bolted to the end of the canopy.

v2 made the cap a lofted n=5.5 section flush with P21, and gave the motor a separate round
nacelle. Much better, but still read as two objects.

v3 tried to merge them into ONE lofted section. It cannot be done, and the reason is
arithmetic, not taste:

    motor axis sits 121.1 mm from the leg axis, can radius 31.5  -> can face at 89.6
    thigh surface 84.9 + 3.0 comfort clearance                   -> 87.9
    radial room for a cover between them                         -> 1.7 mm

The motor is tucked so hard against the thigh that its cover has to be a tight tube there.
A lofted section big enough to contain BOTH the motor and the lateral hardware has its
floor 60 mm below the hardware, and the limb cut then removes that floor over the whole
central span: at X -55, where the ball screw runs at Z 103, the small cap floor is at Z 78
and survives (the limb cut reaches Z 68.6), while the merged section floor is at Z 22 and
is deleted outright. 406_coverage.py scored the merge at 16 exposed rays against 0 for the
pair -- the ball screw and the motor both became touchable. An n=5.5 section is also wider
on its diagonals than a circle, so no superelliptical pod of any size clears the thigh at
that bearing either.

So the motor keeps its tube. What v4 changes is everything AROUND the tube:

1. ONE SURFACE, NOT TWO SHELLS THAT INTERSECT. v2 built cap = lo-li-NAC_O and
   nacelle = NAC_O-NAC_I-lo. Every point lying in BOTH walls was cut from BOTH -- a thin
   void running the length of the seam, belonging to neither part. v4 builds the wall as
   (lo U POD_O) - (li U POD_I): outer union minus inner union, which is the shell of the
   combined cavity, and then SPLITS it for printing. The two parts tile it exactly, no void
   and no overlap, and the printed seam is a real shared face.

2. A FAIRED FOOT instead of a sawn-off tube. The tube enters the cap between bearings +33
   and +78 deg about the motor axis (measured -- see the table this prints). v4 adds a
   raised-cosine flare over +12..+100 deg, 12 mm at its peak, so the tube grows out of the
   cap flank instead of piercing it. That window is chosen because a ray leaving the motor
   axis above about +15 deg never reaches the thigh at all, so the flare is free there.
   Flare that ends up inside the cap costs nothing: the union already contains it.

3. A DOMED NOSE THAT PRINTS. The proximal end points up the thigh and is the one you see.
   v2 closed it with a flat disc at Y 211. v4 tapers it to a 19 mm blunt nose, running from
   Y 201 to Y 217 -- 16 mm, not the 5.5 it started as. 411_printability.py is why: this part
   prints nose-down, a short nose is 70.7 deg from vertical, and a cone that wide DIVERGES
   upward so every layer overhangs the one below. That was 40.6 cm2 of unsupported surface
   on a part the BOM called support-free. At 16 mm the taper is 44.5 deg, inside what a
   printer bridges unaided. It still has to reach full radius by 217, where the motor starts.

Send with:  python tools/fcsend.py scripts/399_drivecap.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))

N_EXP, N_PTS = 5.5, 32
WALL = 3.0
Y0 = 180.0
MOT_X, MOT_R, MOT_Z0 = -104.0, 31.5, 62.0
SCR_X, SCR_Z = -62.0, 106.0
LINK_R_MOT, LINK_R_SCR = 32 * 5.0 / (2 * math.pi) + 2.0, 20 * 5.0 / (2 * math.pi) + 2.0
LEG_R = 84.9
POD_R = MOT_R + 3.5                   # 35.0 -- the same tube radius as the v2 nacelle
FLARE, FL0, FL1 = 12.0, 12.0, 100.0   # faired foot: amplitude mm, angular window deg


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


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def inside(x, z, xc, a, b, zc):
    return (abs(x - xc) / a) ** N_EXP + (abs(z - zc) / b) ** N_EXP


def win(deg):
    """raised cosine over [FL0, FL1], zero outside -- the flare angular window."""
    d = deg % 360.0
    if not (FL0 < d < FL1):
        return 0.0
    return 0.5 - 0.5 * math.cos(2. * math.pi * (d - FL0) / (FL1 - FL0))


def pod_r(deg, s, inset):
    return (POD_R + FLARE * win(deg)) * s - inset


def pod(y, s, inset=0.0, npts=96):
    pts = []
    for i in range(npts):
        d = 360.0 * i / npts
        t = math.radians(d)
        r = pod_r(d, s, inset)
        pts.append(V(MOT_X + r * math.cos(t), y, MOT_Z0 + r * math.sin(t)))
    pts.append(pts[0])
    return Part.makePolygon(pts)


def pod_loft(st, inset):
    return Part.makeLoft([pod(y, s, inset) for y, s in st], True, True)


# ---------------------------------------------------------------- cap sections
# Y 180 is the P21 section verbatim, so the canopy and this are one continuous form. The
# cap does NOT swell over the motor -- see the docstring.
OUT = [(180.0, -19.5, 76.5, 28.0, 110.0),
       (220.0, -21.0, 77.5, 29.0, 110.0),
       (300.0, -21.5, 78.0, 30.0, 108.0),
       (318.0, -21.5, 78.0, 30.0, 108.0),
       (326.0, -21.0, 70.0, 27.0, 108.0),
       (334.0, -20.0, 52.0, 20.0, 108.0)]
INN = [(y if 180.0 < y < 334.0 else (178.0 if y == 180.0 else 328.0),
        xc, a - WALL, b - WALL, zc) for y, xc, a, b, zc in OUT]

print("=" * 76)
print("WHERE THE TUBE MEETS THE CAP  (radius from the motor axis out to the cap outer")
print("surface, by bearing; the tube itself is at %.0f)" % POD_R)
xc, a, b, zc = OUT[1][1], OUT[1][2], OUT[1][3], OUT[1][4]


def cap_hit(t):
    prev, out = None, []
    for i in range(1, 800):
        r = i * 0.25
        v = inside(MOT_X + r * math.cos(t), MOT_Z0 + r * math.sin(t), xc, a, b, zc)
        if prev is not None and (prev - 1.) * (v - 1.) < 0:
            out.append(r)
        prev = v
    return out


seam = []
for d in range(0, 101, 10):
    h = cap_hit(math.radians(d))
    inn = h[0] if h else None
    print("   %+4d deg   cap outer at r %s   flare +%4.1f   %s"
          % (d, ("%5.1f" % inn) if inn else "   -- ", FLARE * win(d),
             "tube inside cap" if (inn and inn > POD_R) else "tube exposed"))
    if inn and abs(inn - POD_R) < 12.0:
        seam.append(d)
print("   -> the seams sit near %s deg; the flare window %+.0f..%+.0f covers both."
      % (seam, FL0, FL1))

# the flare is only legal because it leans AWAY from the limb
worst = min((math.hypot(MOT_X + pod_r(360. * k / 720., 1.0, 0.) * math.cos(2 * math.pi * k / 720),
                        MOT_Z0 + pod_r(360. * k / 720., 1.0, 0.) * math.sin(2 * math.pi * k / 720)),
             360. * k / 720.) for k in range(720))
plain = math.hypot(MOT_X, MOT_Z0) - POD_R
print("   flared pod closest approach to the leg axis %.1f at %+.0f deg; a plain tube is"
      % (worst[0], worst[1]))
print("   %.1f, so the flare costs %.2f mm of limb clearance." % (plain, plain - worst[0]))
assert worst[0] > plain - 0.05, "the flare has eaten into the limb side of the pod"

# ---------------------------------------------------------------- pod sections
# Full radius by Y 217 because that is where the motor can starts, so the whole taper has to
# fit proximal of it. ONE STRAIGHT TAPER over 16 mm, not 5.5. The short nose was 70.7 deg from vertical, and
# printed nose-down -- which is the orientation 411_printability.py finds best for this part
# -- a cone that wide DIVERGES upward, so every layer overhangs the one below: 40.6 cm2 of
# unsupported surface, on a part the BOM described as "prints nose-down on its domed end, no
# supports". Running the taper from Y 201 instead of 209 puts it at 44.5 deg, inside what a
# printer bridges unaided. It still has to be at full radius by 217, where the motor starts.
POD_O = [(201.0, 0.55), (217.0, 1.00), (320.0, 1.00)]
POD_I = [(204.0, 0.55), (217.5, 1.00), (317.0, 1.00)]


def stadium(r1, r2, y0, y1):
    """A radius at each pulley and a straight span between. NOT a bounding box: the belt
    centreline passes 118 mm from the leg axis, but a box inboard corner would be at 59,
    i.e. buried in the thigh."""
    p1 = Part.makeCylinder(r1, y1 - y0, V(MOT_X, y0, MOT_Z0), V(0, 1, 0))
    p2 = Part.makeCylinder(r2, y1 - y0, V(SCR_X, y0, SCR_Z), V(0, 1, 0))
    dx, dz = SCR_X - MOT_X, SCR_Z - MOT_Z0
    L = math.hypot(dx, dz)
    r = max(r1, r2)
    mid = Part.makeBox(L, y1 - y0, 2 * r, V(0, y0, -r))
    mid.rotate(V(0, y0, 0), V(0, 1, 0), -math.degrees(math.atan2(dz, dx)))
    mid.translate(V(MOT_X, 0, MOT_Z0))
    return p1.fuse(p2).fuse(mid).removeSplitter()


POD_OUT = pod_loft(POD_O, 0.0).fuse(
    stadium(LINK_R_MOT + 4.0, LINK_R_SCR + 4.0, 296.0, 320.0)).removeSplitter()
# The inner stops short of the outer at BOTH ends, so the pod is closed rather than being an
# open tube. The first version ran the inner out to match and left the proximal end open --
# the Cycles render showed daylight straight down the bore past a spinning outrunner, which
# is the one thing this cover exists to stop. Nothing has to pass through either end: the
# motor ends at Y 291 and the screw at 314, both inside.
POD_INN = pod_loft(POD_I, WALL).fuse(
    stadium(LINK_R_MOT + 1.0, LINK_R_SCR + 1.0, 298.0, 317.0)).removeSplitter()
assert POD_OUT.isValid() and POD_INN.isValid(), "pod lofts invalid"
k = POD_INN.cut(POD_OUT)
sp = 0.0 if k.isNull() else k.Volume / 1000.
print("   pod inner outside pod outer: %.4f cm3 (0 required -- the nose taper self-checks)" % sp)
assert sp < 0.01, "the pod inner surface escapes its outer at the nose taper"

lo, li = loft(OUT), loft(INN)

# ------------------------------------------------- ONE wall, then split it for printing
shell = lo.fuse(POD_OUT).cut(li.fuse(POD_INN)).removeSplitter()

# Carve the limb. Two radii on purpose: 3.0 mm of comfort clearance everywhere the cover is
# free to stand off, but the motor pod cannot have it -- the can face is only 1.7 mm clear
# of the 87.9 cylinder, so a 3 mm standoff would leave a 1.2 mm wall there, which does not
# print. Under the pod the cut drops to 0.1 mm clearance, which is where the v2 nacelle
# already sat (closest approach 86.1 against a nominal thigh of 84.9). That the motor cover
# skims the quadriceps is a consequence of tucking the motor this hard; it wants a tape
# measure on the patient, not another boolean.
POD_ZONE = Part.makeCylinder(62.0, 130.0, V(MOT_X, 200.0, MOT_Z0), V(0, 1, 0))
legA = Part.makeCylinder(LEG_R + 3.0, 330.0, V(0., 10., 0.), V(0, 1, 0))
legB = Part.makeCylinder(LEG_R + 0.1, 330.0, V(0., 10., 0.), V(0, 1, 0))
legcut = legA.cut(POD_ZONE).fuse(legB.common(POD_ZONE)).removeSplitter()
shell = shell.cut(legcut)
for nm in ("P5_ThighCuff", "P21_ShellAnterior"):
    ob = doc.getObject(nm)
    if ob is not None:
        shell = shell.cut(ob.Shape)
shell = shell.removeSplitter()
V_SHELL = shell.Volume / 1000.
print("=" * 76)
print("combined wall %.1f cm3 in %d solids before splitting" % (V_SHELL, len(shell.Solids)))

SLIVER = 0.05


def one(sh, nm):
    sh = sh.removeSplitter()
    keep = [t for t in sh.Solids if t.Volume / 1000.0 > SLIVER]
    for t in sh.Solids:
        if t.Volume / 1000.0 <= SLIVER:
            b_ = t.BoundBox
            print("   %s: dropped sliver %.4f cm3 at X %.1f..%.1f Z %.1f..%.1f"
                  % (nm, t.Volume / 1000.0, b_.XMin, b_.XMax, b_.ZMin, b_.ZMax))
    if len(keep) != 1:
        raise AssertionError("%s has %d real solids: %s" % (nm, len(keep),
            "; ".join("%.2f cm3 X%.0f..%.0f Y%.0f..%.0f Z%.0f..%.0f"
                      % (t.Volume / 1000., t.BoundBox.XMin, t.BoundBox.XMax,
                         t.BoundBox.YMin, t.BoundBox.YMax,
                         t.BoundBox.ZMin, t.BoundBox.ZMax) for t in keep)))
    assert keep[0].isValid(), "%s invalid" % nm
    return keep[0]


c = one(shell.cut(POD_OUT), "P22")
nac = one(shell.common(POD_OUT), "P25")
print("the two parts tile the wall: %.1f + %.1f = %.1f against %.1f cm3 (%.1f%% accounted)"
      % (c.Volume / 1000., nac.Volume / 1000., (c.Volume + nac.Volume) / 1000., V_SHELL,
         100.0 * (c.Volume + nac.Volume) / shell.Volume))
k = c.common(nac)
ov = 0.0 if k.isNull() else k.Volume / 1000.
print("   P22 vs P25 overlap %.4f cm3 (the v2 pair left a VOID here instead)" % ov)
assert ov < 0.02, "the split overlaps by %.3f cm3" % ov

o = doc.getObject("P22_DriveCap")
o.Shape = c
o.Label = "P22_DriveCap"
for lbl, sh in (("P22", c), ("P25", nac)):
    bb = sh.BoundBox
    print("%s  X %6.1f..%5.1f  Y %6.1f..%5.1f  Z %5.1f..%5.1f  %5.1f cm3  %4.0f g PETG"
          % (lbl, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax,
             sh.Volume / 1000., sh.Volume / 1000. * 1.27))

# ------------------------------------------------- trim A7 to the combined cavity
a7 = doc.getObject("A7_DriveBox")
v0 = a7.Shape.Volume / 1000.
# GUARD: this trim is destructive. It reaches a fixed point in practice -- a second pass on
# the v4 cavity removes 0.0 cm3, because everything the first pass left is already inside it
# -- but that is a property of this cavity, not of the operation, and it was NOT true of the
# cavity that deleted the motor mount and took A7 from 366 g to 222 without a single sweep
# flag, because a missing part is an absence, not an interference. XMin is the cheap tell:
# the mount disc at X -104 +/- 31.5 is the furthest-anterior thing on the part, and nothing
# else reaches -134.5.
assert a7.Shape.BoundBox.XMin < MOT_X - MOT_R + 1.0, (
    "A7 has already been trimmed (XMin %.1f, expected < %.1f). Re-run 393_driveend.py "
    "first -- this script cannot rebuild what it removed."
    % (a7.Shape.BoundBox.XMin, MOT_X - MOT_R + 1.0))
# Trim to the COMBINED cavity, not the cap alone. The A7 motor mount disc and its arm live
# at (X -104, Z 62), which is inside the pod and far outside the cap section, so trimming to
# the cap alone deleted them outright and took A7 from 366 g to 222. No sweep catches that:
# a missing part is an absence, not an interference. It showed up as a mass that was too
# good to be true.
cav = li.fuse(POD_INN)
keep = a7.Shape.common(cav)
distal = a7.Shape.cut(bx(-200., 200., Y0, 500., 0., 300.))
t = one(keep.fuse(distal), "A7")
a7.Shape = t
bb = t.BoundBox
print("A7   trimmed %.1f -> %.1f cm3 (%.0f -> %.0f g), now X %.1f..%.1f Z %.1f..%.1f"
      % (v0, t.Volume / 1000., v0 * 2.70, t.Volume / 1000. * 2.70,
         bb.XMin, bb.XMax, bb.ZMin, bb.ZMax))
mnt = t.common(Part.makeCylinder(MOT_R + 1.0, 12.0, V(MOT_X, 289.0, MOT_Z0), V(0, 1, 0)))
mv = 0.0 if mnt.isNull() else mnt.Volume / 1000.
print("     motor mount still present: %.2f cm3" % mv)
assert mv > 1.0, "the motor mount got trimmed away"

# ------------------------------------------------- P25
o25 = doc.getObject("P25_MotorNacelle")
if o25 is None:
    o25 = doc.addObject("Part::Feature", "P25_MotorNacelle")
    g = doc.getObject("C_Drive")
    if g is not None:
        g.addObject(o25)
o25.Shape = nac
o25.Label = "P25_MotorNacelle"
# Match P22, or the renders show a bare grey can. A part recreated by addObject gets the
# default grey, and P25 was recreated when the merge experiment deleted it -- which made
# the drive-end shot look like an uncovered motor even though the coverage test said the
# pod was closed. The geometry was right and the picture was wrong, which is the harder
# kind of wrong to notice.
try:
    src = doc.getObject("P22_DriveCap").ViewObject
    o25.ViewObject.ShapeColor = src.ShapeColor
    o25.ViewObject.Transparency = src.Transparency
    print("     P25 colour matched to P22 %s" % (tuple(round(c, 2) for c in src.ShapeColor),))
except Exception as e:
    print("     could not set P25 colour (%s) -- headless?" % e)

# --------------------------------------------------------------------- checks
print("=" * 76)
# How close each part actually gets to the limb. The relaxed cut inside POD_ZONE is meant
# to apply to the pod only; if the cap also dips below 87.9 the zone is reaching too far.
for lbl, sh in (("P22", c), ("P25", nac)):
    rmin = min(math.hypot(v.Point.x, v.Point.z) for v in sh.Vertexes)
    print("  %s closest approach to the leg axis %.1f  -> %+.1f mm off a %.1f thigh"
          % (lbl, rmin, rmin - LEG_R, LEG_R))
for lbl, sh in (("P22", c), ("P25", nac)):
    for nm in ("REF_Thigh", "A3_Motor_6374", "A6_Idler29T", "A2_BallScrew_SFU1620",
               "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler", "A7b_LinkBelt", "A7_DriveBox",
               "P21_ShellAnterior"):
        ob = doc.getObject(nm)
        if ob is None:
            continue
        k = sh.common(ob.Shape)
        v = 0.0 if k.isNull() else k.Volume / 1000.
        print("  %s vs %-24s %.3f cm3 %s" % (lbl, ob.Label, v, "" if v < 0.02 else "<-- CLASH"))
        assert v < 0.02, "%s clashes with %s by %.3f cm3" % (lbl, nm, v)

doc.recompute()
doc.save()
print("STAGE 8 DONE, saved.")
