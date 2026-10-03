# -*- coding: utf-8 -*-
"""Does anything sit inside the limb plus its sleeve? A check, not a study.

437_leg_size.py measured the closest approach of every part to the limb and found the drive end
is 0.4 to 3.5 mm off the bare thigh at Y 295..300 -- so the 3 mm neoprene sleeve of BOM S5 does
not fit under it. That is a fit defect and it had never been checked, for a reason worth keeping:

    REF_Thigh is a TAPER and every limb cut in the repository is a CYLINDER. 399_drivecap.py
    carves the cladding with cylinders of r 87.9 and r 85.0 about the limb axis, which is correct
    at the top of the taper and 20 mm too generous at the knee. A cylindrical cut cannot express
    "3 mm clear of the leg" on a conical leg, so nothing ever asked the question.

This file asks it, as a pass/fail, against the limb's own radius at each station:

    clearance(part) = min over Y of [ min radius of part at Y - (limb radius at Y + SLEEVE) ]

and it reports the VOLUME inside the sleeve as well as the gap, because those two numbers imply
different answers. A sliver means trim the part; a solid lump means the frame has to stand off
further and that is a cuff decision, not a cladding one.

THE CUFFS ARE MEANT TO TOUCH. P5, P7 and the shank socket bear on the limb through the sleeve --
that is what they are for, and 409_cuffs.py sizes the pressure. They are listed and excused.

    freecadcmd.exe scripts/438_limb_clearance.py        (exits non-zero if anything is inside)
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

SLEEVE = 3.0            # BOM S5, on the limb
MARGIN = 0.5            # and a little air, so "just touching" is not a pass
STEP = 3.0
ARC = 1.0
TOUCHING = ("P5_ThighCuff", "P7_ShankCuff", "P6_ShankSocket")

# The modelled thigh stops at Y 300 and the real one does not -- it goes on getting fatter toward
# the hip. Above the truncation the taper is held at its last measured radius, which is the
# least-bad assumption available and is still optimistic.
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


def min_radius(sh, y):
    try:
        ws = sh.slice(V(0, 1, 0), y)
    except Exception:
        return None
    best = None
    for w in ws:
        try:
            pts = w.discretize(Distance=ARC)
        except Exception:
            pts = [v.Point for v in w.Vertexes]
        for p in pts:
            r = math.hypot(p.x, p.z)
            if best is None or r < best:
                best = r
    return best


print("=" * 98)
print("LIMB CLEARANCE  --  %s, limb + %.0f mm sleeve + %.1f mm air" % (_BASE, SLEEVE, MARGIN))
print("=" * 98)

ref = doc.getObject("REF_Thigh")
assert ref is not None, "no REF_Thigh"
rs = ref.Shape
rb = rs.BoundBox

# the forbidden volume: the limb grown by the sleeve, as a cone stack following the real taper
steps = []
y = rb.YMin
while y < rb.YMax + 60.0:
    steps.append((y, limb_radius(rs, y) + SLEEVE + MARGIN))
    y += 10.0
envelope = None
for (y0, r0), (y1, r1) in zip(steps, steps[1:]):
    # makeCone refuses equal radii, and above the limb's truncation every segment has them
    if abs(r1 - r0) < 1e-6:
        seg = Part.makeCylinder(r0, y1 - y0, V(0, y0, 0), V(0, 1, 0))
    else:
        seg = Part.makeCone(r0, r1, y1 - y0, V(0, y0, 0), V(0, 1, 0))
    envelope = seg if envelope is None else envelope.fuse(seg)
print("  the no-go envelope is a cone stack from r %.1f at Y %.0f to r %.1f at Y %.0f,"
      % (steps[0][1], steps[0][0], steps[-1][1], steps[-1][0]))
print("  which is the limb's measured taper plus the sleeve -- not the cylinder 399 cuts with.")

parts = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids
         and not o.Name.startswith("TEST_") and not o.Name.startswith("REF_")]

print()
print("     %-26s %9s %9s %8s   %s" % ("part", "gap mm", "inside", "at Y", "verdict"))
fail = []
rows = []
for o in parts:
    bb = o.Shape.BoundBox
    y0, y1 = max(bb.YMin, rb.YMin), bb.YMax
    if y1 - y0 < STEP:
        continue
    worst = None
    n = int((y1 - y0) // STEP)
    for i in range(n + 1):
        yy = y0 + 1.0 + i * STEP
        if yy > y1 - 0.5:
            break
        mr = min_radius(o.Shape, yy)
        if mr is None:
            continue
        gap = mr - (limb_radius(rs, yy) + SLEEVE + MARGIN)
        if worst is None or gap < worst[0]:
            worst = (gap, yy)
    if worst is None:
        continue
    c = o.Shape.common(envelope)
    vol = 0.0 if c.isNull() else c.Volume / 1000.0
    rows.append((worst[0], o.Name, vol, worst[1]))
rows.sort()
for gap, nm, vol, yy in rows:
    # THE VOLUME IS THE TEST, NOT THE GAP. A part trimmed exactly to this envelope has material
    # lying ON it, and a gap measured from a discretised section then reads 0.0 or -0.2 -- which
    # is the trim having worked, not a part inside the leg. 439_limb_trim.py leaves both drive
    # shells in exactly that state. The gap stays in the report because it says HOW FAR, which
    # the volume does not.
    if nm in TOUCHING:
        verdict = "bears on the limb by design (409_cuffs.py)"
    elif vol <= 0.01:
        verdict = "clear" if gap > 0.2 else "trimmed to the envelope"
    else:
        verdict = "INSIDE THE SLEEVE"
        fail.append((nm, gap, vol, yy))
    if gap < 8.0 or vol > 0.01 or nm in TOUCHING:
        print("     %-26s %9.1f %7.2f cm3 %8.0f   %s" % (nm, gap, vol, yy, verdict))

print()
if fail:
    print("  %d PART(S) INSIDE THE LIMB'S SLEEVE:" % len(fail))
    for nm, gap, vol, yy in fail:
        print("     %-26s %.1f mm deep, %.2f cm3, worst at Y %.0f" % (nm, -gap, vol, yy))
    print()
    print("  Read the volume, not just the gap. A few hundredths of a cm3 is a sliver and the")
    print("  part can be trimmed; a lump means the frame itself stands too close and no amount of")
    print("  cladding work will fix it -- that is the cuff's standoff, and it moves the knee")
    print("  pivot with it, which is a fitting decision rather than a geometry one.")
else:
    print("  Nothing but the cuffs touches the limb, with %.0f mm of sleeve and %.1f mm of air."
          % (SLEEVE, MARGIN))
sys.stdout.flush()
sys.exit(1 if fail else 0)
