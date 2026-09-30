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
Y0 = 204.0
MOT_R, MOT_Z0 = 31.5, 118.0


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
OUT = [(204.0, -19.5, 76.5, 28.0, 110.0),
       (230.0, -19.0, 74.0, 31.0, 112.0),
       (270.0, -18.5, 71.0, 34.0, 115.0),
       (310.0, -18.0, 69.0, 37.0, 118.0),
       # The full section has to run to Y 398, not 380: the 1:1 link belt sits at
       # Y 384..396 and reaches X -80, which the taper was cutting into by 0.088 cm3.
       (398.0, -18.0, 69.0, 37.0, 118.0),
       (404.0, -18.0, 62.0, 33.0, 118.0),
       (412.0, -18.0, 44.0, 24.0, 118.0)]
INN = [(y if 204.0 < y < 412.0 else (202.0 if y == 204.0 else 406.0),
        xc, a - WALL, b - WALL, zc) for y, xc, a, b, zc in OUT]

print("=" * 76)
print("SECTION CHECK -- what the cap's INNER surface has to contain")
xc, a, b, zc = INN[3][1], INN[3][2], INN[3][3], INN[3][4]
print("  widest inner section (Y 310): centre X %.1f, a %.1f, b %.1f, zc %.0f"
      % (xc, a, b, zc))
print("     -> spans X %.1f..%.1f, Z %.0f..%.0f" % (xc - a, xc + a, zc - b, zc + b))
WORST = [("motor, widest point", MOT_R, MOT_Z0),
         ("motor, top of can", 0.0, MOT_Z0 + MOT_R),
         ("motor, far side", -MOT_R, MOT_Z0),
         ("link belt corner", -80.0, 136.0),
         ("ball screw top", -69.9, 113.9),
         ("A7 top plate corner", 48.0, 134.0)]
for nm, x, z in WORST:
    f = inside(x, z, xc, a, b, zc)
    print("     %-22s X %7.1f Z %6.1f   %.3f %s"
          % (nm, x, z, f, "" if f <= 1.0 else "OUTSIDE -- gets trimmed"))
print("  (A7's motor-plate corners at X -84 / Z 151.5 are deliberately outside: a section")
print("   that contained them would be 158 mm wide. They are dead material and get cut.)")

lo, li = loft(OUT), loft(INN)
c = lo.cut(li)
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
keep = a7.Shape.common(li)
# everything distal of the cap stays as it is -- the cap only starts at Y 204
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
print("     The corners the cap cut off were plate that never carried anything --")
print("     the motor bore is 65 mm across and the plate was 132.")

# --------------------------------------------------------------------- checks
print("=" * 76)
for nm in ("REF_Thigh", "A3_Motor_6374", "A6_Idler29T", "A2_BallScrew_SFU1620",
           "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler", "A7b_LinkBelt", "P21_ShellAnterior"):
    ob = doc.getObject(nm)
    if ob is None:
        continue
    k = c.common(ob.Shape)
    v = 0.0 if k.isNull() else k.Volume / 1000.
    print("  P22 vs %-24s %.3f cm3 %s" % (ob.Label, v, "" if v < 0.02 else "<-- CLASH"))
    assert v < 0.02, "P22 clashes with %s by %.3f cm3" % (nm, v)
k = t.common(doc.getObject("A3_Motor_6374").Shape)
print("  A7  vs A3_Motor                 %.3f cm3" % (0.0 if k.isNull() else k.Volume / 1000.))

doc.recompute()
doc.save()
print("STAGE 8 DONE, saved.")
