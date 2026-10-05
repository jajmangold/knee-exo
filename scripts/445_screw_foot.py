# -*- coding: utf-8 -*-
"""KP10 or KFL10 for the screw's lower end? Neither, and the reason is that there is nothing there.

Asked at the bench: "KFL10 and KP10 are very different designs -- which one do we need".

They are, and BOM line D8 reads "KP08 / KFL08 bearing block", listing them as if they were
interchangeable. They are not. KP is a foot-mounted pillow block: it bolts to a face PARALLEL to
the shaft and the bolts go in across the shaft. KFL is a two-bolt diamond flange: it bolts to a
face PERPENDICULAR to the shaft and the bolts go in along it. Choosing between them is choosing
which face you have.

SO I WENT LOOKING FOR THE FACE, AND THERE ISN'T ONE. Within r 40 of the screw's lower journal
there is the knee yoke's corner 32 mm away in X and 18 mm below in Z, the belt's drive run, and
cladding. No boss, no bolt pattern, no block. This is the same defect 420_mockup_audit.py found
at the other end of the same screw -- "air at every Y from 210 to 296 along the screw axis" --
and 433_drive_flip.py fixed that one by seating a bearing in the motor plate. Nobody ever went
back for the bottom.

AND THE BLOCK ITSELF IS WRONG. KP and KFL are shaft blocks for plain round rail: a pressed
self-aligning insert in a cheap housing, no thrust rating worth quoting. The screw being bought
is sold "FK/FF end machined" -- the vendor drawing in this thread shows dia 10 x 15, then
M12 x 1 x 14 for a locknut, then dia 12 x 25 for the pulley. Those ends are cut to suit FK/FF
(or BK/BF) screw supports, which is a different family of part entirely: a flange with a pair of
angular-contact bearings and a locknut seat at the fixed end, a plain flange with one deep-groove
bearing at the floating end. D8 predates the screw having machined ends at all.

WHICH END IS WHICH. The fixed end takes the thrust and it is the top one, at the motor plate.
The bottom is the FLOATING end: radial load only, and it has to be free to slide as the screw
grows. That is what makes the bottom cheap -- and it is also why a self-aligning insert would
actually have been forgiving here, on a printed bracket that will not be perfectly square.

    python scripts/445_screw_foot.py
"""
import os
import sys

import FreeCAD
import Part

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"
AX_X, AX_Z = -62.0, 106.0           # the screw axis
JOURNAL_Y = (57.0, 71.0)            # where the screw drops to its end diameter

# THE CANDIDATE. A plate across the shaft at its end, reaching inboard under the belt to an end
# plate on the rail's LOWER end face -- which is the fixing BOM line S3a already uses at the
# rail's other end: "M5 x 16 into the extrusion's end ... into the two cell cores at X +-10".
# Anchoring to the aluminium rather than to P1_KneeYoke matters: the yoke is already in the
# print-now queue and bolting to it would take it back out.
PLATE = (AX_X - 18.0, AX_X + 18.0, 50.0, 57.0, AX_Z - 18.0, AX_Z + 18.0)
ARM = (AX_X, -20.0, 50.0, 57.0, 88.0, 93.0)        # ducks under the belt, which starts at Z 96
TONGUE = (-20.0, 20.0, 44.0, 51.0, 88.0, 108.0)    # against the rail's end face, resting on the
BORE_R = 15.0                                      # yoke's top at Z 88 so the M5s are not in shear

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}


def box(t):
    x0, x1, y0, y1, z0, z1 = t
    return Part.makeBox(abs(x1 - x0), y1 - y0, z1 - z0,
                        FreeCAD.Vector(min(x0, x1), y0, z0))


print("=" * 98)
print("THE SCREW'S LOWER END")
print("=" * 98)
sh = g["A2_BallScrew_SFU1620"].Shape
b = sh.BoundBox
print("  screw axis X %.1f Z %.1f, Y %.1f .. %.1f.  The lower journal is Y %.0f .. %.0f;"
      % (AX_X, AX_Z, b.YMin, b.YMax, JOURNAL_Y[0], JOURNAL_Y[1]))
print("  the screw does not exist below Y %.0f, so anything perpendicular to it lives at Y < %.0f."
      % (b.YMin, b.YMin))
print()
print("  modelled journal radius %.2f mm -- the real SFU1605/1610 floating end is dia 10,"
      % 4.0)
print("  so the 608 that 433 seated at the top and this bracket both want dia 10 bearings.")
print()

print("  what is within r 40 of the journal:")
probe = Part.makeCylinder(40.0, 60.0, FreeCAD.Vector(AX_X, 40.0, AX_Z), FreeCAD.Vector(0, 1, 0))
found = []
for o in doc.Objects:
    if not o.isDerivedFrom("Part::Feature") or o.Name.startswith("A2_"):
        continue
    try:
        c = o.Shape.common(probe)
    except Exception:
        continue
    if c.Volume > 50.0:
        found.append((o.Name, c.Volume / 1000.0, c.BoundBox))
for n, v, bb in sorted(found, key=lambda r: -r[1]):
    print("     %-26s %6.2f cm3   X %6.1f..%6.1f Z %6.1f..%6.1f"
          % (n, v, bb.XMin, bb.XMax, bb.ZMin, bb.ZMax))
print("     %s" % ("nothing" if not found else
                   "-- a yoke corner, a belt and cladding. No mount."))
print()

print("=" * 98)
print("WHY THE FACE HAS TO BE PERPENDICULAR  (which settles KFL over KP)")
print("=" * 98)
for n in ("A5b_Belt_DriveRun", "A2b_BallNut_SFU1620", "P3_Carriage"):
    bb = g[n].Shape.BoundBox
    print("  %-24s X %6.1f..%6.1f  Y %6.1f..%6.1f  Z %6.1f..%6.1f"
          % (n, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax))
print()
print("  A KP foot wants a pad running ALONGSIDE the shaft, under it, for the whole length of the")
print("  housing. Alongside the shaft is the belt's drive run (X -38.5, the full Y of the rail)")
print("  and the ball nut's travel. A flange wants one slab ACROSS the shaft at its very end,")
print("  below Y 57, and that is the one place down here that is empty.")
print()

print("=" * 98)
print("CANDIDATE:  P32_ScrewFoot  -- plate across the shaft, arm under the belt, onto the rail's end")
print("=" * 98)
cand = box(PLATE).fuse(box(ARM)).fuse(box(TONGUE))
cand = cand.cut(Part.makeCylinder(BORE_R, 40.0, FreeCAD.Vector(AX_X, 40.0, AX_Z),
                                  FreeCAD.Vector(0, 1, 0)))
cand = cand.removeSplitter() if cand.isValid() else cand
cb = cand.BoundBox
print("  plate  X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f   (%.0f mm square, %.0f thick,"
      % (PLATE[0], PLATE[1], PLATE[2], PLATE[3], PLATE[4], PLATE[5],
         PLATE[1] - PLATE[0], PLATE[3] - PLATE[2]))
print("                                                     centred on the screw axis)")
print("  arm    X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f   (under the belt)"
      % (ARM[0], ARM[1], ARM[2], ARM[3], ARM[4], ARM[5]))
print("  tongue X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f   (2 x M5 at X +-10, Z 98, into the"
      % (TONGUE[0], TONGUE[1], TONGUE[2], TONGUE[3], TONGUE[4], TONGUE[5]))
print("                                                     rail's two cell cores)")
print("  volume %.1f cm3, bbox X %.1f..%.1f Y %.1f..%.1f Z %.1f..%.1f"
      % (cand.Volume / 1000.0, cb.XMin, cb.XMax, cb.YMin, cb.YMax, cb.ZMin, cb.ZMax))
print()

belt = g["A5b_Belt_DriveRun"].Shape.BoundBox
print("  belt clearance: the arm tops out at Z %.0f, the belt starts at Z %.0f -- %.1f mm"
      % (ARM[5], belt.ZMin, belt.ZMin - ARM[5]))
print()

print("  clashes against every solid in the document:")
clash = 0
for o in doc.Objects:
    if not o.isDerivedFrom("Part::Feature"):
        continue
    try:
        c = o.Shape.common(cand)
    except Exception:
        print("     %-26s boolean failed" % o.Name)
        continue
    if c.Volume < 1.0:
        continue
    bb = c.BoundBox
    tag = ""
    if o.Name == "P1_KneeYoke":
        tag = "   <-- the tongue resting on the yoke's top face, in compression"
    elif o.Name.startswith("A1_"):
        tag = "   <-- the rail's end face, which is the fixing"
    elif o.Name.startswith("P21"):
        tag = "   <-- cladding, relieve it"
    else:
        clash += 1
        tag = "   <-- CLASH"
    print("     %-26s %6.3f cm3   X %6.1f..%6.1f Y %6.1f..%6.1f Z %6.1f..%6.1f%s"
          % (o.Name, c.Volume / 1000.0, bb.XMin, bb.XMax, bb.YMin, bb.YMax,
             bb.ZMin, bb.ZMax, tag))
print()
print("  %d real clashes" % clash)
print()
print("=" * 98)
print("  TO BUY:  the floating-end support that matches the screw's own machined end -- FF10 or")
print("  BF10 for a dia 10 journal -- not KP10 and not KFL10. If the screw arrives with plain")
print("  unmachined ends instead, then KFL10, because the face is perpendicular.")
print()
print("  TO BUILD: P32_ScrewFoot, above. It does not exist yet, on either leg.")
