# -*- coding: utf-8 -*-
"""The limb, as a solid nothing may enter. One authority, because the cylinder version was wrong.

Every limb cut in this project used to be a CYLINDER about the limb axis -- 399_drivecap.py
carves the cladding with r 87.9 and r 85.0 -- and REF_Thigh is a TAPER, r 62.5 at the knee rising
to 85 at the hip end. A cylinder is right at one station and up to 20 mm too generous everywhere
else, so "3 mm clear of the leg" could not be expressed, and the 3 mm neoprene sleeve of BOM S5
was never in anyone's arithmetic. The controller's cover turned out to be 2.9 mm inside it.

So: the forbidden volume is a stack of cones following the limb's own measured radius, grown by
the sleeve and a little air. Three callers share it -- 434_odrive_mount.py cuts the cover it
draws, 439_limb_trim.py trims the rest of the cladding, 438_limb_clearance.py checks -- and they
share it from here rather than each carrying a copy, because four copies of a mark frame
disagreeing is how twelve part numbers came out mirrored.

THE MODEL'S THIGH STOPS AT Y 300 AND A LEG DOES NOT. Above the truncation the taper is held at
its last measured radius, which is optimistic (a real thigh keeps thickening toward the hip) and
is the least-bad assumption available. Every number that comes out of here is therefore a floor,
not a guarantee, and it is waiting on a tape measure.
"""
import math

import Part
from FreeCAD import Vector as V

SLEEVE = 3.0            # BOM S5, on the limb
MARGIN = 0.5            # and a little air, so "just touching" is not a pass
_cache = {}


def radius(ref, y):
    """the limb's own radius at this station, measured by ray-casting, not assumed"""
    key = (id(ref), round(y, 1))
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


def envelope(ref, sleeve=SLEEVE, margin=MARGIN, above=60.0, step=10.0):
    """the limb plus its sleeve, as one solid: a cone stack following the measured taper"""
    bb = ref.BoundBox
    steps, y = [], bb.YMin
    while y < bb.YMax + above:
        steps.append((y, radius(ref, y) + sleeve + margin))
        y += step
    out = None
    for (y0, r0), (y1, r1) in zip(steps, steps[1:]):
        # makeCone refuses equal radii, and above the truncation every segment has them
        seg = (Part.makeCylinder(r0, y1 - y0, V(0, y0, 0), V(0, 1, 0)) if abs(r1 - r0) < 1e-6
               else Part.makeCone(r0, r1, y1 - y0, V(0, y0, 0), V(0, 1, 0)))
        out = seg if out is None else out.fuse(seg)
    return out


def describe(ref, sleeve=SLEEVE, margin=MARGIN):
    bb = ref.BoundBox
    return ("limb + %.0f mm sleeve + %.1f mm air: r %.1f at Y %.0f to r %.1f at Y %.0f, "
            "held above the model's truncation"
            % (sleeve, margin, radius(ref, bb.YMin) + sleeve + margin, bb.YMin,
               radius(ref, bb.YMax) + sleeve + margin, bb.YMax))
