# -*- coding: utf-8 -*-
"""A pocket on each cuff for an MPU-6050, because tape makes every IMU number a guess.

441_posture.py showed what two leg IMUs can tell apart, and every one of those numbers is an
angle in the SENSOR's frame. "Tilt 135, roll +180" only means something if the sensor's axes are
known with respect to the limb, and a module stuck on with double-sided tape is at whatever
angle the tape allowed. The pocket is the measurement, not the retention.

ADDITIVE, NOT SUBTRACTIVE. These are the two parts that bear on the patient, and 409_cuffs.py
sized their walls against a 15 kPa comfort ceiling. So the platform is fused ON to the outside
and the pocket is cut into the platform -- the cuff's own wall is never touched, and the floor
under the module is new material rather than a thinned shell.

WHERE IT GOES IS SEARCHED, NOT CHOSEN. Both cuffs are posterior shells: material from about
-120 to +90 degrees of bearing and open at the front, where the device is. That leaves three
constraints and they conflict -- posterior is where the patient sits on it, medial is where the
legs touch each other, and lateral at +90 is where the rail runs. So the file sweeps stations
and bearings and takes the first patch that is smooth over the module's whole footprint, clear
of the part's engraved mark, and clear of every other part in the model.

    freecadcmd.exe scripts/442_imu_mounts.py
"""
import json
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from markframe import matrix as mark_matrix                         # noqa: E402

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

# GY-521 breakout, UNVERIFIED -- measure yours. Everything below follows from these three.
MOD = (21.5, 16.0, 3.2)
MARGIN, FLOOR, LID = 3.5, 1.5, 2.0      # platform margin, floor under the module, lid thickness
FIT = 0.4
PLAT = (MOD[0] + 2 * MARGIN, MOD[1] + 2 * MARGIN, MOD[2] + FIT + FLOOR)
SCREW, BOSS = 2.1, 5.0                  # M2.5 into plastic, and the boss it bites
CABLE = (7.0, 3.5)

JOBS = [("P5_ThighCuff", [160.0, 175.0, 190.0, 145.0]),
        ("P7_ShankCuff", [-260.0, -275.0, -245.0, -290.0])]
BEARINGS = [55.0, 40.0, 70.0, 25.0, -30.0, -45.0, 0.0]


def surface(sh, y, bearing, lo=30.0, hi=120.0):
    """where a ray from the limb axis leaves this part, and the outward normal there"""
    a = math.radians(bearing)
    d = (math.cos(a), math.sin(a))
    hit = None
    r = lo
    while r <= hi:
        if sh.isInside(V(r * d[0], y, r * d[1]), 1e-7, True):
            hit = r
        r += 0.25
    if hit is None:
        return None
    return V(hit * d[0], y, hit * d[1]), V(d[0], 0.0, d[1]), hit


def smooth(sh, y, bearing, r0, half_len, half_hoop):
    """is the patch continuous over the whole footprint, or does it run off a slot or an edge"""
    worst = 0.0
    for du in (-half_len, -half_len / 2, 0.0, half_len / 2, half_len):
        for dv in (-half_hoop, 0.0, half_hoop):
            b = bearing + math.degrees(dv / max(r0, 1.0))
            s = surface(sh, y + du, b)
            if s is None:
                return None
            worst = max(worst, abs(s[2] - r0))
    return worst


marks = {}
reg = DOCFILE[:-6] + ".marks.json"
if os.path.exists(reg):
    marks = json.load(open(reg))

others = [o for o in doc.Objects
          if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
          and not o.Shape.isNull() and o.Shape.Solids and not o.Name.startswith("TEST_")]

print("=" * 98)
print("IMU POCKETS  --  %s" % _BASE)
print("=" * 98)
print("  module %.1f x %.1f x %.1f (UNVERIFIED), platform %.1f x %.1f x %.1f, %.1f mm floor"
      % (MOD + PLAT + (FLOOR,)))

# THIS FILE IS NOT IDEMPOTENT and cannot cheaply be made so: it fuses a platform onto a curved
# shell and then searches for a flat patch, so a second run finds the platform it just built,
# treats that as the surface and stacks another on top. The first time I re-ran it the cuffs
# gained 2.0 cm3 and then LOST 0.18, which is what that looks like from the outside. So it
# refuses instead, and the cure is to rebuild the chain rather than to re-run this.
for _probe in ("P28a_IMUCover", "P28b_IMUCover"):
    assert doc.getObject(_probe) is None, (
        "%s already exists: this document has had 442 run on it. Rebuild from the pre-433 "
        "backup through 433, 436, 434, 439 and then this, rather than running it twice."
        % _probe)

fail = []
for name, stations in JOBS:
    o = doc.getObject(name)
    if o is None:
        print("  %-16s MISSING" % name)
        continue
    base = o.Shape
    half_len, half_hoop = PLAT[0] / 2.0, PLAT[1] / 2.0
    chosen = None
    for y in stations:
        for bearing in BEARINGS:
            s = surface(base, y, bearing)
            if s is None:
                continue
            pt, nrm, r0 = s
            # keep clear of this part's own engraved number
            m = marks.get(name)
            if m is not None:
                mp = V(*m["point"])
                if abs(mp.y - y) < 22.0 and \
                        abs(math.degrees(math.atan2(mp.z, mp.x)) - bearing) < 35.0:
                    continue
            dev = smooth(base, y, bearing, r0, half_len, half_hoop)
            if dev is None or dev > 2.0:
                continue
            chosen = (y, bearing, pt, nrm, r0, dev)
            break
        if chosen:
            break
    if chosen is None:
        fail.append("%s: no patch found" % name)
        print("  %-16s NO PATCH -- widen the station or bearing list" % name)
        continue
    y, bearing, pt, nrm, r0, dev = chosen

    mm, into = mark_matrix("r", pt, nrm, standoff=0.0)

    # EVERYTHING IS BUILT IN THE FRAME'S OWN COORDINATES and then placed rigidly. The first
    # version used Shape.transformGeometry, which re-expresses the geometry rather than moving
    # it: the box's planes came back as B-splines and the fuse reported six BOPAlgo GeomAbs_C0
    # errors on a cuff that had been clean. A Placement is a rigid motion and leaves a plane a
    # plane. Local +Z is `into`, so the surface is z = 0 and outward is negative.
    place = FreeCAD.Placement(mm)

    def box(w, d, h, z0):
        b = Part.makeBox(w, d, h, V(-w / 2.0, -d / 2.0, z0))
        b.Placement = place
        return b

    def peg(dia, h, x, z0):
        c = Part.makeCylinder(dia / 2.0, h, V(x, 0.0, z0), V(0, 0, 1))
        c.Placement = place
        return c

    # the platform stands PLAT[2] out of the surface and sinks 1.5 mm in, so it keys rather
    # than perches on a curved shell
    sh = base.fuse(box(PLAT[0], PLAT[1], PLAT[2] + 1.5, -PLAT[2]))
    # the module's pocket in the platform's outer face, and a way out for the cable
    sh = sh.cut(box(MOD[0] + FIT, MOD[1] + FIT, MOD[2] + FIT, -PLAT[2]))
    sh = sh.cut(box(CABLE[0], CABLE[1], MOD[2] + FIT + 2.0, -PLAT[2]))
    for sgn in (-1.0, 1.0):
        shift = sgn * (MOD[0] / 2.0 + FIT + MARGIN / 2.0 + 0.4)
        sh = sh.cut(peg(SCREW, BOSS, shift, -PLAT[2]))
    sh.check(True)
    if len(sh.Solids) != 1:
        fail.append("%s: the platform gave %d solids" % (name, len(sh.Solids)))
        print("  %-16s %d solids" % (name, len(sh.Solids)))
        continue
    added = (sh.Volume - base.Volume) / 1000.0
    o.Shape = sh
    print("  %-16s Y %+7.1f bearing %+5.0f, surface r %5.1f, patch flat to %.2f mm: %+.2f cm3"
          % (name, y, bearing, r0, dev, added))

    # THE LID GOES WHERE IT IS USED, not at the origin. A part modelled at the origin sits
    # inside REF_Knee and reports an overlap at every pose of the 107-pose sweep -- that is
    # exactly what TEST_ToothCoupon does, and it had to be excluded by name to stop it teaching
    # the sweep nothing. Two lids, each on its own platform, are two real parts in real places.
    lid = box(PLAT[0], PLAT[1], LID, -PLAT[2] - LID)
    for sgn in (-1.0, 1.0):
        shift = sgn * (MOD[0] / 2.0 + FIT + MARGIN / 2.0 + 0.4)
        lid = lid.cut(peg(2.9, LID + 2.0, shift, -PLAT[2] - LID - 1.0))
    lid.check(True)
    assert len(lid.Solids) == 1, "the lid came out as %d solids" % len(lid.Solids)
    lname = "P28%s_IMUCover" % ("a" if name.startswith("P5") else "b")
    ol = doc.getObject(lname) or doc.addObject("Part::Feature", lname)
    ol.Shape = lid
    ol.Label = lname
    print("  %-16s %.1f x %.1f x %.1f on %s's platform, 2 x M2.5 clearance"
          % (lname, PLAT[0], PLAT[1], LID, name))

    for t in others:
        if t.Name == name:
            continue
        c = sh.common(t.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > 0.02:
            fail.append("%s's platform overlaps %s by %.3f cm3" % (name, t.Name, v))
            print("     vs %-24s %7.3f cm3 <-- CLASH" % (t.Name, v))

doc.recompute()
doc.save()
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  Both sensors now have a frame. The pocket's long axis runs along the limb, so the")
    print("  module's X is the segment's own axis and 441's table means what it says.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
