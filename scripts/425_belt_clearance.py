# -*- coding: utf-8 -*-
"""Relieve everything the belt and the rebuilt tunnel now pass through.

Two consequences of 421/423/424 that the parts around them have not been told about:

  A7_DriveBox      two ribs at Y 207..217 stand in the annulus the belt's teeth sweep, 0.29 cm3
                   each side. They were clear of the OLD belt, which was drawn 2.7 mm further out
                   as a plain band; against a real meshing belt a tooth strikes them every 8 mm of
                   travel. 423's tooth-space check is what found them.
  P21_ShellAnterior  0.76 cm3 of the canopy stands inside 424's new tunnel wall and floor. The
                   tunnel is sized by the belt and carries 764 N; the canopy is cosmetic. So the
                   canopy yields.

The cut tool is the belt's own swept space -- backing corridor plus tooth annulus, both runs and
both wraps -- plus the tunnel blocks, each with clearance. Nothing here is a judgement about where
a part should be: it is the belt's envelope, and anything that is not a pulley or the toothed land
has to be outside it.

    freecadcmd.exe scripts/425_belt_clearance.py
"""
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

TIP, BACK, ROOT = 36.237, 38.457, 32.857
Z0, Z1 = 96.0, 126.0
YR = 255.0
CLEAR = 0.4
ALLOWED = ("P2a_KneeHub_Pulley29T", "P2a_KneeHingePlate", "A6_Idler29T", "P3_Carriage")
# the tunnel blocks 424 built, inflated, as a cut tool for cladding that stands in them
TUNNEL = (-41.9, -27.6, 143.6, 186.4, 88.6, 126.9)


def wrap(cy, ro, ri, positive):
    sol = Part.makeCylinder(ro, Z1 - Z0 + 2 * CLEAR, V(0, cy, Z0 - CLEAR), V(0, 0, 1)) \
        .cut(Part.makeCylinder(ri, Z1 - Z0 + 4, V(0, cy, Z0 - 2), V(0, 0, 1)))
    half = Part.makeBox(4 * ro, 2 * ro, Z1 - Z0 + 6,
                        V(-2 * ro, cy if positive else cy - 2 * ro, Z0 - 3))
    return sol.common(half)


print("=" * 96)
print("BELT CLEARANCE  --  %s" % _BASE)
print("=" * 96)

# the whole space the belt occupies or sweeps, with clearance
belt_space = wrap(0.0, BACK + CLEAR, ROOT - CLEAR, False) \
    .fuse(wrap(YR, BACK + CLEAR, ROOT - CLEAR, True))
for sx in (-1.0, 1.0):
    x0 = -(BACK + CLEAR) if sx < 0 else ROOT - CLEAR
    belt_space = belt_space.fuse(
        Part.makeBox(BACK - ROOT + 2 * CLEAR, YR, Z1 - Z0 + 2 * CLEAR,
                     V(x0, 0.0, Z0 - CLEAR)))
tunnel = Part.makeBox(TUNNEL[1] - TUNNEL[0], TUNNEL[3] - TUNNEL[2], TUNNEL[5] - TUNNEL[4],
                      V(TUNNEL[0], TUNNEL[2], TUNNEL[4]))

print("  %-24s %-34s %9s  %s" % ("part", "relieved against", "cm3", ""))
rows = []
for name, tool, what in (("A7_DriveBox", belt_space, "the belt's swept space"),
                         ("P21_ShellAnterior", tunnel, "the gantry's belt tunnel")):
    o = doc.getObject(name)
    if o is None:
        print("  %-24s not in this document" % name)
        continue
    v0 = o.Shape.Volume
    new = o.Shape.cut(tool)
    tidy = new.removeSplitter()
    try:
        tidy.check(True)
        new = tidy
    except Exception:
        pass
    removed = (v0 - new.Volume) / 1000.0
    nsol = len(new.Solids)
    if nsol != 1:
        print("  %-24s %-34s %9.3f  REFUSED: would become %d solids" % (name, what, removed, nsol))
        rows.append((name, False))
        continue
    new.check(True)
    o.Shape = new
    print("  %-24s %-34s %9.3f  %.1f -> %.1f cm3"
          % (name, what, removed, v0 / 1000.0, new.Volume / 1000.0))
    rows.append((name, True))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- is the belt's space its own now?
print()
print("  nothing but the two pulleys and the toothed land may be in the belt's space:")
bad = []
for o in doc.Objects:
    if o.TypeId != "Part::Feature" or getattr(o, "Shape", None) is None:
        continue
    if o.Shape.isNull() or not o.Shape.Solids or o.Name.startswith(("A5", "REF_", "TEST_")):
        continue
    if not o.Shape.BoundBox.intersect(belt_space.BoundBox):
        continue
    try:
        c = o.Shape.common(belt_space)
    except Exception:
        continue
    if c.isNull() or c.Volume < 20.0:
        continue
    ok = o.Name in ALLOWED
    print("   %-26s %8.2f cm3   %s" % (o.Name, c.Volume / 1000.0,
                                       "meshes, expected" if ok else "<-- STILL INTRUDING"))
    if not ok:
        bad.append(o.Name)
print()
if bad:
    print("  %d part(s) still in the belt's space: %s" % (len(bad), ", ".join(bad)))
else:
    print("  the belt's space is clear")
sys.stdout.flush()
sys.exit(1 if (bad or any(not ok for _, ok in rows)) else 0)
