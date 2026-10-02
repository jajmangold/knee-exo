# -*- coding: utf-8 -*-
"""Make the two parts that bolt to the thigh rail actually bolt to it.

Found by asking 420's question of the parts 420's table did not cover. Two answers:

THE KNEE YOKE'S BOLTS ARE AT THE OLD RAIL'S SLOT SPACING. P1_KneeYoke has six M5 clearance holes
through its 12 mm plate, at X -20, 0 and +20. A 20x60 V-slot has three 20 mm cells and its slots
are at X -20, 0, +20 -- which is what this pattern was drawn for, and the object is still called
A1_Extrusion_20x60_VSlot. The rail it bolts to is a 20x40: two cells, slots at X +-10. BOM S1 says
so in as many words -- "Its 40 mm face has slots at X = +-10, not X = 0" -- and notes that the
fairing spine has to move because of it. The yoke was not checked, so all six bolts land on solid
aluminium or off the edge, on the part that carries the whole knee reaction.

    sampled through the rail at Z 98:   X 0   -> SOLID CORE
                                        X +-20 -> the outer wall
                                        X +-10 -> SLOT, a bolt can enter

THE DRIVE BRACKET HAS NO FIXING AT ALL. A7_DriveBracket_Idler holds the idler at up to 1828 N --
the largest single load in the machine -- and ASSEMBLY step 5 says to bolt it to the top of the
extrusion. Its hole inventory was 4 x M4 (the motor), one 9.2 (screw clearance), one 22 (the 608
seat), two 26 (idler bearings) and the boss: no M5 anywhere, and 0.000 cm3 of contact with the
rail. It does have a 10 mm plate butted against the rail's end face at Y 207..217, square across
both cells at X +-10, so the fixing was designed and never drilled.

WHAT THIS DOES

  P1  fills the six misaligned holes and cuts four at X +-10, Y 70 and 112. The fill is exact
      rather than approximate: each hole is a plain cylinder through a flat plate whose faces are
      planar and perpendicular to Z over Z 76..88, so a cylinder of exactly that extent restores
      the plate with no bulge. Each fill is checked against the volume it should add.
  A7  cuts two M5 along Y at X +-10, Z 98, through the end plate and into the rail's cell voids,
      for a self-tapping screw or a tapped insert in the extrusion's end.

Both legs: KX_DOC selects the document and the Z sign is taken from the part, as 421 and 426 do.

    freecadcmd.exe scripts/427_rail_bolts.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/427_rail_bolts.py
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

M5 = 5.2
# The old pattern was all three of the 20x60's slots. Only the CENTRE one gets filled: filling
# X +-20 as well blocked P21_ShellAnterior's lip, which passes through the outer part of those two
# holes at Z 85.1..88 -- 0.053 cm3 of canopy inside the yoke, which the sweep reported immediately.
# A hole that looks unused can still be the clearance something else is relying on.
FILL_X = (0.0,)
KEEP_X = (-20.0, 20.0)           # clearance for the canopy's lip; must stay open
OLD_X = (-20.0, 0.0, 20.0)       # the 20x60 rail's slots, for the report
NEW_X = (-10.0, 10.0)            # the 20x40 rail's slots
YOKE_Y = (70.0, 112.0)
PLATE_Z = (76.0, 88.0)           # the yoke plate, flat and perpendicular to Z
RAIL_Z = 98.0                    # the rail's cell centres
A7_Y = (205.0, 230.0)            # through the bracket's end plate, into the rail's end

ext = None
for o in doc.Objects:
    if "Extrusion" in o.Name and getattr(o, "Shape", None) is not None:
        b = o.Shape.BoundBox
        if b.YMax > 180.0 and b.XMax > 15.0:
            ext = o
p1 = doc.getObject("P1_KneeYoke")
a7 = doc.getObject("A7_DriveBox")
assert p1 is not None and ext is not None, "no yoke or no thigh rail in this document"
mirrored = p1.Shape.BoundBox.ZMax < 0
sgn = -1.0 if mirrored else 1.0
pz = (sgn * PLATE_Z[0], sgn * PLATE_Z[1])
pz = (min(pz), max(pz))

print("=" * 98)
print("RAIL BOLTS  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)


def in_slot(x, y):
    """is a bolt at this (x, y) entering a slot, or hitting the rail's solid core?

    Not-inside-the-solid is necessary but not sufficient: at X +-20 the point sits exactly on the
    rail's outer boundary, where isInside is also false, and a bolt there grips nothing. So require
    the point to be INSIDE the rail's envelope by a margin as well as outside its material.
    """
    b = ext.Shape.BoundBox
    if not (b.XMin + 2.0 < x < b.XMax - 2.0):
        return False
    return not ext.Shape.isInside(V(x, y, sgn * RAIL_Z), 1e-7, True)


print("  the rail is %s: at Z %+.0f its slots are the X where a bolt can enter"
      % (ext.Name, sgn * RAIL_Z))
for x in sorted(set(OLD_X) | set(NEW_X)):
    print("     X %+6.1f  %s" % (x, "SLOT" if in_slot(x, YOKE_Y[0]) else "solid"))

# ---------------------------------------------------------------- P1: fill six, cut four
rows = []
sh = p1.Shape
want_fill = math.pi * (M5 / 2.0) ** 2 * (PLATE_Z[1] - PLATE_Z[0]) / 1000.0
for x in FILL_X:
    for y in YOKE_Y:
        cyl = Part.makeCylinder(M5 / 2.0, pz[1] - pz[0], V(x, y, pz[0]), V(0, 0, 1))
        pre = sh.common(cyl)
        if not pre.isNull() and pre.Volume > 0.5 * want_fill * 1000.0:
            rows.append(("P1 fill  X %+6.1f Y %+6.1f" % (x, y), 0.0, True, "already solid"))
            continue
        v0 = sh.Volume
        new = sh.fuse(cyl)
        tidy = new.removeSplitter()
        try:
            tidy.check(True)
            new = tidy
        except Exception:
            pass
        added = (new.Volume - v0) / 1000.0
        ok = (0.85 * want_fill < added < 1.15 * want_fill and len(new.Solids) == 1)
        if ok:
            sh = new
        rows.append(("P1 fill  X %+6.1f Y %+6.1f" % (x, y), added, ok,
                     "" if ok else "expected %.4f cm3" % want_fill))
# re-open anything an earlier run of this script filled that should not have been
for x in KEEP_X:
    for y in YOKE_Y:
        cyl = Part.makeCylinder(M5 / 2.0, (pz[1] - pz[0]) + 8.0, V(x, y, pz[0] - 4.0), V(0, 0, 1))
        pre = sh.common(cyl)
        if pre.isNull() or pre.Volume < 0.1 * want_fill * 1000.0:
            rows.append(("P1 keep  X %+6.1f Y %+6.1f open" % (x, y), 0.0, True, "already open"))
            continue
        v0 = sh.Volume
        new = sh.cut(cyl)
        removed = (v0 - new.Volume) / 1000.0
        ok = removed > 0.5 * want_fill and len(new.Solids) == 1
        if ok:
            sh = new
        rows.append(("P1 reopen X %+5.1f Y %+6.1f (canopy lip)" % (x, y), removed, ok, ""))
for x in NEW_X:
    for y in YOKE_Y:
        assert in_slot(x, y), "X %+.1f is not over a slot -- do not drill it" % x
        cyl = Part.makeCylinder(M5 / 2.0, (pz[1] - pz[0]) + 8.0, V(x, y, pz[0] - 4.0), V(0, 0, 1))
        pre = sh.common(cyl)
        if pre.isNull() or pre.Volume < 0.1 * want_fill * 1000.0:
            rows.append(("P1 drill X %+6.1f Y %+6.1f -> slot" % (x, y), 0.0, True,
                         "already drilled"))
            continue
        v0 = sh.Volume
        new = sh.cut(cyl)
        removed = (v0 - new.Volume) / 1000.0
        ok = removed > 0.5 * want_fill and len(new.Solids) == 1
        if ok:
            tidy = new.removeSplitter()
            try:
                tidy.check(True)
                new = tidy
            except Exception:
                pass
            sh = new
        rows.append(("P1 drill X %+6.1f Y %+6.1f -> slot" % (x, y), removed, ok, ""))
sh.check(True)
assert len(sh.Solids) == 1, "the yoke came out as %d solids" % len(sh.Solids)
p1.Shape = sh

# ---------------------------------------------------------------- A7: two into the rail's end
if a7 is not None:
    ash = a7.Shape
    for x in NEW_X:
        cyl = Part.makeCylinder(M5 / 2.0, A7_Y[1] - A7_Y[0], V(x, A7_Y[0], sgn * RAIL_Z),
                                V(0, 1, 0))
        pre = ash.common(cyl)
        if pre.isNull() or pre.Volume < 20.0:
            rows.append(("A7 drill X %+6.1f along Y into the rail end" % x, 0.0, True,
                         "already drilled"))
            continue
        v0 = ash.Volume
        new = ash.cut(cyl)
        removed = (v0 - new.Volume) / 1000.0
        ok = removed > 0.05 and len(new.Solids) == 1
        if ok:
            tidy = new.removeSplitter()
            try:
                tidy.check(True)
                new = tidy
            except Exception:
                pass
            ash = new
        rows.append(("A7 drill X %+6.1f along Y into the rail end" % x, removed, ok, ""))
    ash.check(True)
    a7.Shape = ash

doc.recompute()
doc.save()

print()
print("  %-44s %10s" % ("feature", "cm3"))
bad = 0
for what, vol, ok, note in rows:
    print("  %-44s %10.4f  %s" % (what, vol, note if note else ("" if ok else "<-- FAILED")))
    if not ok:
        bad += 1

# ---------------------------------------------------------------- do they land in slots now?
print()
fail = []
shell = doc.getObject("P21_ShellAnterior")
if shell is not None:
    _c = p1.Shape.common(shell.Shape)
    _v = 0.0 if _c.isNull() else _c.Volume / 1000.0
    print("  the canopy's lip passes through the yoke's outer holes: overlap %.4f cm3 (must be 0)"
          % _v)
    if _v > 0.002:
        fail.append("P1 overlaps P21 by %.4f cm3 -- a filled hole is blocking the canopy" % _v)
print("  VERIFICATION -- every M5 through the yoke plate, against the rail:")
for f in p1.Shape.Faces:
    s = f.Surface
    if s.TypeId != "Part::GeomCylinder" or not (4.8 <= 2 * s.Radius <= 5.6):
        continue
    if abs(s.Axis.z) < 0.9:
        continue
    x, y = s.Center.x, s.Center.y
    if round(x, 1) in [round(v, 1) for v in KEEP_X]:
        # not a rail bolt: clearance for the canopy's lip, and deliberately over the rail's wall
        print("     X %+6.1f Y %+6.1f  canopy lip clearance, not a rail bolt" % (x, y))
        continue
    good = in_slot(x, y)
    print("     X %+6.1f Y %+6.1f  %s" % (x, y,
                                          "enters a slot" if good else "<-- LANDS ON SOLID RAIL"))
    if not good:
        fail.append("yoke bolt at X %+.1f is not over a slot" % x)
if a7 is not None:
    n = 0
    for f in a7.Shape.Faces:
        s = f.Surface
        if (s.TypeId == "Part::GeomCylinder" and 4.8 <= 2 * s.Radius <= 5.6
                and abs(s.Axis.y) > 0.9):
            n += 1
    print("     bracket has %d M5 along Y into the rail's end" % n)
    if n < 2:
        fail.append("the bracket still has no fixing to the rail")
print()
if fail or bad:
    for f in fail:
        print("  FAIL %s" % f)
    if bad:
        print("  FAIL %d operation(s) did not do what they claimed" % bad)
else:
    print("  the yoke's four bolts and the bracket's two all enter the rail's slots")
sys.stdout.flush()
sys.exit(1 if (fail or bad) else 0)
