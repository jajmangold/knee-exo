# -*- coding: utf-8 -*-
"""Bolt the motor to the bracket. It never was.

The third part found by asking 420's question of something 420's table already "passed". The table
asks A7_DriveBox for "a motor bolt pattern" and tests `cyls(sh, 3.0, 5.6) >= 4`. A7 has exactly
four M4 holes -- at X +-34, Z 118.3, on the TOP plate -- and they are the KX-1 interface's
fixings, 56 mm above the motor and on a different face. The C6374 sits on the axis X -104, Z 62
with its end face at Y 291, and there is nothing holding it there at all.

    A3_Motor_6374 is a plain cylinder: 3 faces, dia 63 x 74, no shaft, no bolt circle.
    A7 has an 8 mm plate at Y 291..299 across the motor's end face.
    The plate already carries the dia 12 shaft clearance on the motor's axis (417 classifies it).
    So the mount was drawn except for its bolts.

WHAT IS ASSUMED HERE, AND WHO SHOULD CHECK IT. A 63 mm outrunner of this class mounts on four
bolts in a 25 mm square about the shaft, and that is what this cuts. The spacing is the assumption:
19 mm and 30 mm patterns both exist on motors sold under similar names, and the model's motor is a
featureless cylinder, so nothing in CAD can confirm it. The holes are cut at dia 5.2, which clears
M4 and M5 alike.

**The motors are on the bench -- there are four of them (BOM D4, owned). Measure the pattern
before printing the bracket**, and set SQUARE here to what the tape says. This is the one feature
in the build whose dimension comes from a catalogue habit rather than from a part or a calculation,
and it is 90 minutes of printing away from being discovered at assembly.

    freecadcmd.exe scripts/428_motor_mount.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/428_motor_mount.py
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

HOLE = 5.2            # clears M4 and M5
SQUARE = 25.0         # ASSUMED bolt spacing -- measure the motor
PLATE_Y = (289.0, 301.0)

a7 = doc.getObject("A7_DriveBox")
mot = doc.getObject("A3_Motor_6374")
assert a7 is not None and mot is not None, "no bracket or no motor in this document"
mb = mot.Shape.BoundBox
cx, cz = 0.5 * (mb.XMin + mb.XMax), 0.5 * (mb.ZMin + mb.ZMax)

print("=" * 98)
print("MOTOR MOUNT  --  %s" % _BASE)
print("=" * 98)
print("  motor axis X %.1f Z %.1f, end face Y %.0f; bracket plate at Y %.0f..%.0f"
      % (cx, cz, mb.YMax, PLATE_Y[0] + 2, PLATE_Y[1] - 2))
print("  4 x dia %.1f on a %.0f mm square -- SPACING ASSUMED, measure the motor" % (HOLE, SQUARE))

sh = a7.Shape
rows = []
h = SQUARE / 2.0
for dx in (-h, h):
    for dz in (-h, h):
        tool = Part.makeCylinder(HOLE / 2.0, PLATE_Y[1] - PLATE_Y[0],
                                 V(cx + dx, PLATE_Y[0], cz + dz), V(0, 1, 0))
        pre = sh.common(tool)
        if pre.isNull() or pre.Volume < 20.0:
            rows.append(("M%s at (%+.1f, %+.1f)" % ("", cx + dx, cz + dz), 0.0, True,
                         "already drilled"))
            continue
        v0 = sh.Volume
        new = sh.cut(tool)
        removed = (v0 - new.Volume) / 1000.0
        ok = removed > 0.05 and len(new.Solids) == 1
        if ok:
            tidy = new.removeSplitter()
            try:
                tidy.check(True)
                new = tidy
            except Exception:
                pass
            sh = new
        rows.append(("bolt at (%+.1f, %+.1f)" % (cx + dx, cz + dz), removed, ok, ""))
sh.check(True)
assert len(sh.Solids) == 1, "the bracket came out as %d solids" % len(sh.Solids)
a7.Shape = sh
doc.recompute()
doc.save()

print()
bad = 0
for what, vol, ok, note in rows:
    print("  %-34s %8.4f cm3  %s" % (what, vol, note if note else ("" if ok else "<-- HIT AIR")))
    if not ok:
        bad += 1

# ---------------------------------------------------------------- is the motor held now?
print()
near = []
for f in a7.Shape.Faces:
    s = f.Surface
    if s.TypeId != "Part::GeomCylinder" or not (4.8 <= 2 * s.Radius <= 5.6):
        continue
    if abs(s.Axis.y) < 0.9:
        continue
    d = ((s.Center.x - cx) ** 2 + (s.Center.z - cz) ** 2) ** 0.5
    if d < 25.0:
        near.append((s.Center.x, s.Center.z, d))
print("  M5-size holes along Y within 25 mm of the motor's axis: %d" % len(near))
for x, z, d in sorted(near):
    print("     (%+7.1f, %+6.1f)  %.1f mm from the axis" % (x, z, d))
fail = bad > 0 or len(near) < 4
if fail:
    print()
    print("  FAIL the motor still has nothing holding it")
else:
    print()
    print("  the motor has four bolts into the bracket's end plate -- SPACING UNVERIFIED")
sys.stdout.flush()
sys.exit(1 if fail else 0)
