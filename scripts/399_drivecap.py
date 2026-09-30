# -*- coding: utf-8 -*-
"""STAGE 8: P22 as a lofted cap instead of a box.

393 and 397 built the drive cap as a rectangular box shell because it was quick and it
swept clean. It looks terrible: every other cover on this device is an n=5.5 rounded
rectangle lofted along Y -- the knee cap, the thigh canopy, the shank fairing -- and the
drive end was a shoebox bolted to the end of it.

Fixed by doing two things properly.

1. THE CAP STARTS AS P21'S OWN SECTION. At Y 204 it is exactly the section P21 ends on
   (centre X -19.5, a 76.5, b 28, zc 110), so the two are flush with no step, then it
   swells over the motor and tapers closed at Y 406.

2. THE BRACKET IS TRIMMED TO THE CAP, NOT THE CAP GROWN TO THE BRACKET. A7's bounding box
   is X -84..48 by Z 84.5..151.5, and a section big enough for those RECTANGULAR corners
   needs to be 158 mm wide. But those corners are dead material on a plate that is mostly
   a motor bore, so the cap's inner loft cuts them off instead -- 3.7 cm3 of aluminium,
   and A7 drops 172.2 -> 168.5 cm3. 240_nut1610.py did the same thing to the carriage
   against P21.

The cap ends up 153 mm across, which is not smaller than the 144 mm box -- it is the same
width as P21 (154 mm), because its widest station IS P21's section. That is the point: the
canopy and the cap are now one continuous form instead of a canopy with a shoebox on the
end. The two-screw cap was 190 mm.

Send with:  python tools/fcsend.py scripts/399_drivecap.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

N_EXP, N_PTS = 5.5, 32
WALL = 3.0
Y0 = 180.0
MOT_X, MOT_R, MOT_Z0 = -104.0, 31.5, 62.0
SCR_X, SCR_Z = -62.0, 106.0
LINK_R_MOT, LINK_R_SCR = 32 * 5.0 / (2 * math.pi) + 2.0, 20 * 5.0 / (2 * math.pi) + 2.0


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


# outer stations: (y, xc, a, b, zc). Y 204 is P21's section verbatim.
# The cap no longer has to swell over the motor: with the motor tucked anterior at
# (X -104, Z 62) it is nowhere near this section, and a convex section reaching both it
# and the lateral hardware would swallow the leg. The motor gets P25_MotorNacelle instead
# and this stays close to P21's own profile the whole way.
OUT = [(180.0, -19.5, 76.5, 28.0, 110.0),
       (220.0, -21.0, 77.5, 29.0, 110.0),
       (300.0, -21.5, 78.0, 30.0, 108.0),
       (318.0, -21.5, 78.0, 30.0, 108.0),
       (326.0, -21.0, 70.0, 27.0, 108.0),
       (334.0, -20.0, 52.0, 20.0, 108.0)]
INN = [(y if 180.0 < y < 334.0 else (178.0 if y == 180.0 else 328.0),
        xc, a - WALL, b - WALL, zc) for y, xc, a, b, zc in OUT]

print("=" * 76)
print("SECTION CHECK -- what the cap's INNER surface has to contain")
xc, a, b, zc = INN[3][1], INN[3][2], INN[3][3], INN[3][4]
print("  widest inner section (Y 310): centre X %.1f, a %.1f, b %.1f, zc %.0f"
      % (xc, a, b, zc))
print("     -> spans X %.1f..%.1f, Z %.0f..%.0f" % (xc - a, xc + a, zc - b, zc + b))
WORST = [("gantry, outboard corner", -84.0, 130.2),
         ("gantry, far side", 32.0, 123.0),
         ("A7 yoke corner", 46.5, 130.3),
         ("A7 end plate corner", -46.5, 88.0),
         ("belt strand outer", 41.124, 126.0),
         ("ball screw top", -69.9, 113.9),
         ("link belt, screw-end pulley", -62.0 - LINK_R_SCR, 106.0 + LINK_R_SCR)]
for nm, x, z in WORST:
    f = inside(x, z, xc, a, b, zc)
    print("     %-22s X %7.1f Z %6.1f   %.3f %s"
          % (nm, x, z, f, "" if f <= 1.0 else "OUTSIDE -- gets trimmed"))
print("  (A7's motor mount disc and arm sit outside this on purpose -- they are under the")
print("   nacelle, not the cap.)")

def stadium(r1, r2, y0, y1):
    """A radius at each pulley and a straight span between. NOT a bounding box: the belt
    centreline passes 118 mm from the leg axis, but a box's inboard corner would be at 59,
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


NAC_O = Part.makeCylinder(MOT_R + 3.5, 109.0, V(MOT_X, 211.0, MOT_Z0), V(0, 1, 0))
NAC_O = NAC_O.fuse(stadium(LINK_R_MOT + 4.0, LINK_R_SCR + 4.0, 296.0, 320.0)).removeSplitter()
# The inner stops 3 mm SHORT of the outer at BOTH ends, so the nacelle is capped at each
# end rather than being an open tube. The first version ran the inner out to Y 320 to match
# the outer and left the proximal end open -- the Cycles render showed daylight straight
# down the bore, past a spinning outrunner, which is the one thing this cover exists to
# stop. Nothing has to pass through either end: the motor ends at Y 291 and the screw at
# 314, both inside.
NAC_I = Part.makeCylinder(MOT_R + 0.5, 104.0, V(MOT_X, 213.0, MOT_Z0), V(0, 1, 0))
NAC_I = NAC_I.fuse(stadium(LINK_R_MOT + 1.0, LINK_R_SCR + 1.0, 298.0, 317.0)).removeSplitter()

lo, li = loft(OUT), loft(INN)
# The cap and the nacelle interlock: each is trimmed back to the other's OUTER surface, so
# they meet on a shared face with no overlap and no gap.
c = lo.cut(li).cut(NAC_O)
# open underneath where the leg is -- REF_Thigh's surface is Z 85 out to Y 300
c = c.cut(bx(-110., 70., Y0 - 1., 300., 40., 88.))
c = c.removeSplitter()
assert len(c.Solids) == 1, "P22 solids=%d" % len(c.Solids)
assert c.isValid(), "P22 invalid"
o = doc.getObject("P22_DriveCap")
o.Shape = c
o.Label = "P22_DriveCap"
bb = c.BoundBox
print("=" * 76)
print("P22  X %6.1f..%5.1f  Y %6.1f..%5.1f  Z %5.1f..%5.1f  %5.1f cm3"
      % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax, c.Volume / 1000.))
print("     %.0f mm across -- the same as P21's %.0f, because its widest station IS P21's"
      % (bb.XMax - bb.XMin, 154.0))
print("     section. Flush at Y %.0f, no step. The two-screw cap was 190 mm." % Y0)

# ------------------------------------------------- trim A7 to the cap's inner surface
a7 = doc.getObject("A7_DriveBox")
v0 = a7.Shape.Volume / 1000.
# GUARD: this trim is destructive and not idempotent. Run it twice without rebuilding
# A7 from 393 in between and the second pass eats what the first one left -- which is
# how the motor mount disappeared once already, silently, because a missing part is not
# an interference and no sweep reports it. Fail loudly instead.
assert a7.Shape.BoundBox.XMin < MOT_X - MOT_R + 1.0, (
    "A7 has already been trimmed (XMin %.1f, expected < %.1f). Re-run 393_driveend.py "
    "first -- this script cannot rebuild what it removed."
    % (a7.Shape.BoundBox.XMin, MOT_X - MOT_R + 1.0))
# Trim to the cap's inner surface OR the nacelle's -- not the cap alone. A7's motor
# mount disc and its arm live at (X -104, Z 62), which is under the NACELLE and far
# outside the cap's section, so trimming to the cap alone deleted them outright and took
# A7 from 366 g to 222. No sweep catches that: a missing part is an absence, not an
# interference. It showed up as an implausible mass.
keep = a7.Shape.common(li.fuse(NAC_I))
distal = a7.Shape.cut(bx(-200., 200., Y0, 500., 0., 300.))
t = keep.fuse(distal).removeSplitter()
assert len(t.Solids) == 1, "A7 solids=%d after trimming" % len(t.Solids)
assert t.isValid(), "A7 invalid after trimming"
a7.Shape = t
bb = t.BoundBox
# (v0 reads as already-trimmed if this script is re-run in the same session -- the shape
#  is assigned before the checks below, so a failed run still leaves the trim applied.)
print("A7   trimmed %.1f -> %.1f cm3 (%.0f -> %.0f g), now X %.1f..%.1f Z %.1f..%.1f"
      % (v0, t.Volume / 1000., v0 * 2.70, t.Volume / 1000. * 2.70,
         bb.XMin, bb.XMax, bb.ZMin, bb.ZMax))
print("     What comes off is corner material on the mount plate; what must NOT come off")
print("     is the motor mount itself, which is why the trim is against the cap fused")
print("     with the nacelle rather than the cap alone.")
mnt = t.common(Part.makeCylinder(MOT_R + 1.0, 12.0, V(MOT_X, 289.0, MOT_Z0), V(0, 1, 0)))
print("     motor mount still present: %.2f cm3" % (0.0 if mnt.isNull() else mnt.Volume / 1000.))
assert (0.0 if mnt.isNull() else mnt.Volume / 1000.) > 1.0, "the motor mount got trimmed away"

# --------------------------------------------------------------------- checks
print("=" * 76)
for nm in ("REF_Thigh", "A3_Motor_6374", "A6_Idler29T", "A2_BallScrew_SFU1620",
           "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler", "P21_ShellAnterior"):
    ob = doc.getObject(nm)
    if ob is None:
        continue
    k = c.common(ob.Shape)
    v = 0.0 if k.isNull() else k.Volume / 1000.
    print("  P22 vs %-24s %.3f cm3 %s" % (ob.Label, v, "" if v < 0.02 else "<-- CLASH"))
    assert v < 0.02, "P22 clashes with %s by %.3f cm3" % (nm, v)
k = t.common(doc.getObject("A3_Motor_6374").Shape)
print("  A7  vs A3_Motor                 %.3f cm3" % (0.0 if k.isNull() else k.Volume / 1000.))

# ------------------------------------------------- P25 motor nacelle
nac = NAC_O.cut(NAC_I).cut(lo).removeSplitter()
assert nac.isValid(), "P25 invalid"
o = doc.getObject("P25_MotorNacelle")
if o is None:
    o = doc.addObject("Part::Feature", "P25_MotorNacelle")
    g = doc.getObject("C_Drive")
    if g is not None:
        g.addObject(o)
o.Shape = nac
o.Label = "P25_MotorNacelle"
bb = nac.BoundBox
print("P25  X %6.1f..%5.1f  Y %6.1f..%5.1f  Z %5.1f..%5.1f  %5.1f cm3, %d solids"
      % (bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax,
         nac.Volume / 1000., len(nac.Solids)))
for nm, sh in (("P25", nac), ("P22", c)):
    k = sh.common(REF)
    v = 0.0 if k.isNull() else k.Volume / 1000.
    print("     %s vs REF_Thigh: %.3f cm3" % (nm, v))
    assert v < 0.02, "%s is inside the leg by %.3f cm3" % (nm, v)
for nm in ("A3_Motor_6374", "A7b_LinkBelt", "A7_DriveBox", "P22_DriveCap"):
    ob = doc.getObject(nm)
    k = nac.common(ob.Shape)
    v = 0.0 if k.isNull() else k.Volume / 1000.
    print("     P25 vs %-22s %.3f cm3" % (ob.Label, v))
    assert v < 0.02, "P25 clashes with %s by %.3f" % (nm, v)

doc.recompute()
doc.save()
print("STAGE 8 DONE, saved.")
