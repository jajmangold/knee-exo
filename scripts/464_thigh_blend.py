# -*- coding: utf-8 -*-
"""The motor pod is not a bulge, it is a cliff. Blend it into the thigh.

Asked at the bench: make the whole thigh one cohesive unit, the motor box hanging off separately
is the thing I do not like, and watch for snags.

461 and 463 went looking for a bulge and did not find one -- measured as material, everything
above the knee sits between r 145 and r 161 and the cladding is only 3-7 mm proud of its
contents. 463 also found that fusing the three cladding parts recovers EXACTLY ZERO: they do not
overlap, so there are no doubled walls and no mass in merging them. And the mass itself was 230 g,
not the 531 g I had quoted by applying solid PETG density to a part printed at two walls and low
infill.

SO THE FIRST THREE ANSWERS WERE ALL "THERE IS NOTHING TO FIX", AND ALL THREE WERE LOOKING IN THE
WRONG PLACE. Slicing the cladding by sector found it:

    bearing 135..170 deg, along Y:      Y 200  r 136.7
                                        Y 205  r 158.0     21.3 mm in 5 mm -- a 77 degree face

The pod does not stick OUT further than the rest of the thigh. It starts ABRUPTLY. There is a
21 mm wall facing down the leg at the posterior-lateral quarter, and a wall facing down the leg
is what catches on a chair, a duvet, a trouser leg -- which is exactly the complaint.

THIS RAMPS IT. From the thigh's own radius at Y 160 up to the pod's at Y 205, over enough length
that nothing can catch on it.

    freecadcmd.exe scripts/464_thigh_blend.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v8.FCStd").replace("\\", "/")

# Measured, not guessed. At Y 170 the cladding simply STOPS at bearing 135; at Y 212 it runs
# to 170 at r 158. So the pod is not a step at a bearing, it is a LOBE that appears from
# nothing -- which is why a cone-sector ramp floated free when it was tried: there was no
# surface under it to fuse to. The blend has to narrow in BEARING as well as in radius, and
# die out where the thigh's own shell still exists, at bearing 132.
SECT_ROOT = 132.0                       # where P21's shell still has material to land on
SECT_TIP = 172.0                        # the lobe's far edge at full size
WALL = 2.5                              # the cladding's own skin
MAX_RAMP_DEG = 30.0                     # above this a ledge still catches
# four stations: a teardrop growing in radius AND angular width out of P21's surface
# The first attempt reached the lobe's far edge (bearing 172) only at the very top, so the
# pod's original face still showed between bearings 163 and 172 and the steepest step was 39
# degrees rather than the 25 the radii alone suggested. The angular growth has to finish
# BEFORE the radial growth does.
# and the LAST leg has to arrive at the pod's own radius, not just near it: ending at 156 where
# the pod is 158 left a 2 mm step in 1 mm of length, which measured as 37 degrees all by itself.
# Three passes of this got 77 -> 39 -> 34 degrees and stuck, because the slope was uneven: the
# loft's last leg was still climbing when it met the pod and the pod's own face poked through.
# The constraint is simple once written down -- rise 32 mm at 30 degrees needs 55 mm of run --
# so the stations are evenly spaced and the radius steps are equal. A straight ramp, not a curve.
# and it has to ARRIVE at the pod's radius by Y 205, not Y 206. Ending one station late left
# the blend at 156.6 where the pod is already 158, so the pod's own face poked 1.4 mm through
# and the measured step was 33 degrees however shallow the blend itself was.
PROFILE = [(146.0, 126.0, 140.0),
           (158.0, 132.5, 148.0),
           (170.0, 139.0, 156.0),
           (182.0, 145.5, 163.0),
           (193.0, 152.0, 169.0),
           (205.0, 158.0, SECT_TIP),
           (220.0, 158.0, SECT_TIP)]


class _Tee(object):
    def __init__(self, a, b):
        self.a, self.b = a, b

    def write(self, t):
        self.a.write(t)
        self.b.write(t)
        self.b.flush()

    def flush(self):
        self.a.flush()
        self.b.flush()


sys.stdout = _Tee(sys.__stdout__, sys.__stderr__)


def kx_doc():
    base = DOCFILE.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(DOCFILE)


doc = kx_doc()
g = {o.Name: o for o in doc.Objects}
CLAD = ("P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle")


def sector_r(sh, y, lo, hi):
    try:
        wires = sh.slice(V(0, 1, 0), y)
    except Exception:
        return 0.0
    best = 0.0
    for w in wires:
        for p in w.discretize(Distance=1.0):
            a = math.degrees(math.atan2(p.z, p.x)) % 360.0
            if lo <= a <= hi:
                best = max(best, math.hypot(p.x, p.z))
    return best


print("=" * 96)
print("THIGH BLEND  --  %s" % os.path.basename(doc.FileName))
print("=" * 96)
# Idempotence by MEASUREMENT, not by a marker object. The first draft guarded on a marker
# that a later rewrite stopped creating, so the guard silently stopped guarding and a
# second run blended on top of the blend. The blend extends P25 from Y 178 down to Y 146,
# so if the pod already reaches past Y 170 it has run.
if g["P25_MotorNacelle"].Shape.BoundBox.YMin < 170.0:
    print("  P25_MotorNacelle already reaches Y %.0f -- this has run. Nothing done."
          % g["P25_MotorNacelle"].Shape.BoundBox.YMin)
    sys.exit(0)

clad = g[CLAD[0]].Shape.fuse(g[CLAD[1]].Shape).fuse(g[CLAD[2]].Shape)


def sector_face(y, r, tip):
    """a pie slice from the axis out to r, between SECT_ROOT and tip, at station y"""
    lo, hi = math.radians(SECT_ROOT), math.radians(tip)
    pts = [V(0, y, 0)]
    for k in range(25):
        a = lo + (hi - lo) * k / 24.0
        pts.append(V(r * math.cos(a), y, r * math.sin(a)))
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts))


rise = PROFILE[-1][1] - PROFILE[0][1]
run = PROFILE[-1][0] - PROFILE[0][0]
print()
print("  the lobe appears between Y 200 and 205: r 136.7 -> 158.0, a 77 degree face")
print("  blending it over Y %.0f..%.0f gives %.0f degrees of ramp"
      % (PROFILE[0][0], PROFILE[-1][0], math.degrees(math.atan2(rise, run))))
assert math.degrees(math.atan2(rise, run)) <= MAX_RAMP_DEG, "the run is too short"
print("  and it narrows from bearing %.0f..%.0f at the top to %.0f..%.0f at the root, so it"
      % (SECT_ROOT, SECT_TIP, SECT_ROOT, PROFILE[0][2]))
print("  dies into P21's own shell rather than ending in mid-air")

outer = Part.makeLoft([sector_face(y, r, t) for y, r, t in PROFILE], True, True)
inner = Part.makeLoft([sector_face(y, r - WALL, t) for y, r, t in PROFILE], True, True)
ring = Part.makeCylinder(260.0, run + 40.0, V(0, PROFILE[0][0] - 20.0, 0), V(0, 1, 0)).cut(
    Part.makeCylinder(100.0, run + 44.0, V(0, PROFILE[0][0] - 22.0, 0), V(0, 1, 0)))
ramp = outer.cut(inner).common(ring)
assert ramp.Volume > 500.0, "the blend came out empty (%.1f mm3)" % ramp.Volume
print("  blend shell %.2f cm3" % (ramp.Volume / 1000.0))

bad = 0
for o in doc.Objects:
    if not o.isDerivedFrom("Part::Feature") or o.Name in CLAD or o.Name.startswith("REF_"):
        continue
    try:
        c = o.Shape.common(ramp)
    except Exception:
        continue
    if c.Volume > 20.0:
        print("     blend ^ %-26s %7.3f cm3   relieved" % (o.Name, c.Volume / 1000.0))
        ramp = ramp.cut(o.Shape)
        bad += 1
if not bad:
    print("  the blend hits nothing inside -- it is pure skin")

p25 = g["P25_MotorNacelle"].Shape
new = p25.fuse(ramp)
sols = sorted(new.Solids, key=lambda s: -s.Volume)
print()
print("  fused into P25_MotorNacelle: %.2f -> %.2f cm3, %d solid(s)"
      % (p25.Volume / 1000.0, sols[0].Volume / 1000.0, len(sols)))
assert len(sols) == 1, "the blend left %d solids -- it is not touching the pod" % len(sols)
g["P25_MotorNacelle"].Shape = sols[0]

# P21 runs to Y 206 and the ramp overlaps it; cladding yields to the part that owns the lobe
p21 = g["P21_ShellAnterior"].Shape
k = p21.common(g["P25_MotorNacelle"].Shape)
if k.Volume > 20.0:
    cut = p21.cut(g["P25_MotorNacelle"].Shape)
    s2 = sorted(cut.Solids, key=lambda s: -s.Volume)
    assert sum(s.Volume for s in s2[1:]) / 1000.0 < 0.05, "trimming P21 orphaned material"
    g["P21_ShellAnterior"].Shape = s2[0]
    print("  P21_ShellAnterior gives up %.3f cm3 where the ramp passes through it"
          % (k.Volume / 1000.0))

doc.recompute()
print()
print("  AFTER: the lobe's profile along Y, bearings %.0f..%.0f" % (SECT_ROOT + 6.0, SECT_TIP))
clad2 = g[CLAD[0]].Shape.fuse(g[CLAD[1]].Shape).fuse(g[CLAD[2]].Shape)
prev, worst = 0.0, 0.0
for y in range(155, 216, 5):
    r = sector_r(clad2, float(y), SECT_ROOT + 6.0, SECT_TIP)
    d = (r - prev) if prev else 0.0
    if prev and r:
        worst = max(worst, math.degrees(math.atan2(d, 5.0)))
    print("     Y %3d   r %5.1f%s" % (y, r, "   %+.1f mm" % d if prev else ""))
    prev = r
print()
print("  steepest face now %.0f degrees, was 77" % worst)
doc.save()
print("  saved %s" % doc.FileName)
