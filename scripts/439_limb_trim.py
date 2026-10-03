# -*- coding: utf-8 -*-
"""Trim the cladding to the limb's tapered envelope -- but only where a wall survives it.

438_limb_clearance.py found two parts inside the limb plus its 3 mm sleeve, and this trims them
to it. Both came out trimmable, which was not what the arithmetic predicted:

    P25_MotorNacelle    2.3 mm deep, 0.57 cm3  -> trimmed, 2.90 mm of wall left
    P22_DriveCap        0.1 mm deep, 0.07 cm3  -> trimmed, a sliver

I EXPECTED THE POD TO REFUSE, and wrote this file to say so. On the line from the limb axis
through the motor, Y 296 has the limb at r 84.5, the sleeve taking it to 87.5, and the can at
89.6 -- 2.1 mm for a wall, so trimming to the envelope should have left 0.7 mm against
411_printability.py's 1.2 mm floor. It left 2.90 mm, because the deepest intrusion is not on that
line: it is an EDGE at bearing +149 deg and Y 290, where the shell is thick. The analysis was
right about the geometry and wrong about where the geometry mattered, which is the whole reason
this measures the wall it leaves instead of trusting the calculation.

So the refusal path below has never fired. It stays because the arithmetic that predicted it is
still true of that one line: if the limb measurements come back fatter than REF_Thigh's nominal
taper, the pod WILL run out of wall there, and the fix then is not a trim. It is moving the motor
-- a swing about the screw's axis, the only motion that leaves the belt's 60.8 mm centre distance
alone (433_drive_flip.py records the arithmetic and what re-working the pod around a moved can
costs). A trim that leaves no wall is not a fit.

TWO MEASUREMENT TRAPS, both hit here:

  * one ray is not a measurement. The first version fired a single ray through the centre of the
    intersection's bounding box and reported P22's wall as 0.00 mm -- the ray missed the material
    entirely, because the bbox centre of a thin curved sliver need not be inside the part. It now
    scans bearings and stations around the deepest point and takes the thickest wall it finds.
  * and a trim leaves material lying ON the envelope, so 438's gap then reads 0.0 or -0.2 for a
    part that is exactly right. The volume inside is the test; the gap says how far.

    freecadcmd.exe scripts/439_limb_trim.py
"""
import math
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

SLEEVE, MARGIN = 3.0, 0.5
MIN_WALL = 1.2          # 411_printability.py's two-perimeter floor at a 0.4 mm nozzle
CLAD = ("P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle")

_cache = {}


def limb_radius(ref, y):
    key = round(y, 1)
    if key in _cache:
        return _cache[key]
    bb = ref.BoundBox
    yy = min(max(y, bb.YMin + 0.5), bb.YMax - 0.5)
    best = 0.0
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        r = 40.0
        while r <= 120.0:
            if ref.isInside(V(r * math.cos(a), yy, r * math.sin(a)), 1e-7, True):
                best = max(best, r)
            r += 0.5
    _cache[key] = best
    return best


def wall_along(sh, y, bearing_deg):
    """the solid span a ray outward from the limb axis crosses -- the wall, measured"""
    a = math.radians(bearing_deg)
    # 0.25 mm steps over 78..118: isInside on a 400-face shell is milliseconds, and the first
    # version's 0.1 mm over 70..160 was 900 of them per ray against a 35-ray scan
    spans, run = [], None
    r = 78.0
    while r <= 118.0:
        inside = sh.isInside(V(r * math.cos(a), y, r * math.sin(a)), 1e-7, True)
        if inside and run is None:
            run = r
        elif not inside and run is not None:
            spans.append((run, r - 0.25))
            run = None
        r += 0.25
    if run is not None:
        spans.append((run, 118.0))
    return spans


print("=" * 98)
print("TRIMMING THE CLADDING TO THE LIMB  --  %s" % _BASE)
print("=" * 98)

ref = doc.getObject("REF_Thigh")
assert ref is not None, "no REF_Thigh"
rs = ref.Shape
rb = rs.BoundBox

steps = []
y = rb.YMin
while y < rb.YMax + 60.0:
    steps.append((y, limb_radius(rs, y) + SLEEVE + MARGIN))
    y += 10.0
envelope = None
for (y0, r0), (y1, r1) in zip(steps, steps[1:]):
    seg = (Part.makeCylinder(r0, y1 - y0, V(0, y0, 0), V(0, 1, 0)) if abs(r1 - r0) < 1e-6
           else Part.makeCone(r0, r1, y1 - y0, V(0, y0, 0), V(0, 1, 0)))
    envelope = seg if envelope is None else envelope.fuse(seg)

done, refused = [], []
for nm in CLAD:
    o = doc.getObject(nm)
    if o is None:
        continue
    c = o.Shape.common(envelope)
    if c.isNull() or c.Volume < 20.0:
        print("  %-22s already clear" % nm)
        continue
    inside = c.Volume / 1000.0
    cb = c.BoundBox
    # the station and bearing where it is deepest, so the wall is measured where it matters
    ym = 0.5 * (cb.YMin + cb.YMax)
    bearing = math.degrees(math.atan2(0.5 * (cb.ZMin + cb.ZMax), 0.5 * (cb.XMin + cb.XMax)))
    trimmed = o.Shape.cut(envelope)
    if not trimmed.Solids:
        refused.append((nm, inside, 0.0, "the trim would remove the part"))
        continue
    keep = max(trimmed.Solids, key=lambda q: q.Volume)
    lost = len(trimmed.Solids) - 1
    # SCAN, do not sample once. The first version fired a single ray through the centre of the
    # intersection's bounding box and called P22's 0.07 cm3 sliver a 0.00 mm wall -- the ray
    # simply missed the material, because the centre of a thin curved sliver's bbox need not be
    # in the part at all. Take the thickest wall found over the sliver's own angular and axial
    # extent, which is what "is there still a wall here" means.
    wall = 0.0
    for dy in (-6.0, 0.0, 6.0):
        for db in (-15.0, -7.0, 0.0, 7.0, 15.0):
            for lo, hi in wall_along(keep, ym + dy, bearing + db):
                wall = max(wall, hi - lo)
    # and a sliver is a sliver: below this a trim cannot meaningfully thin anything, and the
    # wall measurement is noise next to the cut itself
    SLIVER = 0.15
    print("  %-22s %.2f cm3 inside, deepest at Y %.0f bearing %+.0f deg; wall left %.2f mm%s"
          % (nm, inside, ym, bearing, wall, "  (a sliver)" if inside < SLIVER else ""))
    if (wall < MIN_WALL and inside >= SLIVER) or lost:
        refused.append((nm, inside, wall,
                        "would leave %.2f mm of wall" % wall if wall < MIN_WALL
                        else "would shed %d fragment(s)" % lost))
        continue
    trimmed.check(True)
    assert len(trimmed.Solids) == 1, "%s: trim gave %d solids" % (nm, len(trimmed.Solids))
    v0 = o.Shape.Volume
    o.Shape = trimmed
    done.append((nm, (v0 - trimmed.Volume) / 1000.0, wall))

doc.recompute()
doc.save()
print()
for nm, removed, wall in done:
    print("  TRIMMED  %-22s -%.3f cm3, %.2f mm of wall left" % (nm, removed, wall))
for nm, inside, wall, why in refused:
    print("  REFUSED  %-22s %.2f cm3 stays inside the sleeve: %s" % (nm, inside, why))
print()
if refused:
    print("  What is refused is not a cladding defect. Read the file's docstring: the pod has")
    print("  2.1 mm between the sleeve and a spinning can to put a wall in, and the fix is to")
    print("  move the motor, which moves the belt, the pod and the seam with it.")
sys.stdout.flush()
