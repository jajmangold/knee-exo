# -*- coding: utf-8 -*-
"""Give the ball screw the machined ends every part on it is bored for.

A2 is drawn as one ⌀15.80 cylinder from Y 70 to 314 -- the thread's major diameter carried the
whole length. BOM D1 says "machined ends", and everything that mounts on those ends is bored 8 mm:

    D8   KP08 pillow block      8 mm bore      the lower end
    D8a  608-2RS                8 mm bore      the upper end, in the bracket's screw boss
    D7   20T HTD-5M pulley      8 mm bore      Y 302..314, driven by the link belt

So the uniform rod is a mockup that disagrees with three bought parts at once, and 601 found it the
moment the boss existed to disagree with: 0.622 cm3 of screw inside A7_DriveBox at Y 286..290.8,
where 422 cut a ⌀9.2 clearance for a shaft the model draws at ⌀15.8. Enlarging the bore to clear
the rod would have been the wrong fix -- it would have put a ⌀16 hole through the seat of an 8 mm
bearing.

    Y  70.0 ..  78.0    ⌀8.0     lower journal, into the KP08
    Y  78.0 .. 284.0    ⌀15.8    thread and body; the nut sweeps Y 140..182
    Y 284.0 .. 314.0    ⌀8.0     upper journal: the 608 at Y 290.8..298, then the 20T pulley

WHAT IS STILL A MOCKUP HERE, said plainly: the shoulders are square steps, not the relieved and
ground seats a real screw end has, and there is no provision drawn for the locknut or spacer that
sets the 608's axial position -- the bearing is simply seated in the boss. Neither the KP08 nor the
20T pulley is modelled as a solid at all; they are BOM lines, so nothing in CAD checks that they
fit. What this file does fix is the one thing that was actively wrong: a 16 mm rod passing through
8 mm holes.

    freecadcmd.exe scripts/426_screw_ends.py
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

R_BODY, R_END = 7.90, 4.00
# The lower journal cannot start at the modelled screw's end. The nut body is Y 140..182 and the
# stroke is 68.3 mm, so at full extension the nut reaches Y 71.7 and needs thread to there -- BOM
# D1 says the same thing from the other direction ("the nut sweeps Y 73..183"). The screw therefore
# has to reach BELOW Y 70, where it was drawn stopping, to carry a journal clear of the thread.
Y_LO, Y_LO_END, Y_HI_END, Y_HI = 57.0, 71.0, 284.0, 314.0
SCR_X, SCR_Z = -62.0, 106.0

o = doc.getObject("A2_BallScrew_SFU1620")
assert o is not None, "no ball screw in this document"
b = o.Shape.BoundBox
mirrored = b.ZMax < 0
z = -SCR_Z if mirrored else SCR_Z

print("=" * 96)
print("BALL SCREW ENDS  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 96)
was = o.Shape.Volume / 1000.0

shaft = Part.makeCylinder(R_END, Y_LO_END - Y_LO, V(SCR_X, Y_LO, z), V(0, 1, 0)) \
    .fuse(Part.makeCylinder(R_BODY, Y_HI_END - Y_LO_END, V(SCR_X, Y_LO_END, z), V(0, 1, 0))) \
    .fuse(Part.makeCylinder(R_END, Y_HI - Y_HI_END, V(SCR_X, Y_HI_END, z), V(0, 1, 0)))
tidy = shaft.removeSplitter()
try:
    tidy.check(True)
    shaft = tidy
except Exception:
    pass
assert len(shaft.Solids) == 1, "the screw came out as %d solids" % len(shaft.Solids)
shaft.check(True)
o.Shape = shaft
# the label said SFU1620 for a part the BOM has ordered as an SFU1610 since 240_nut1610.py
o.Label = "A2_BallScrew_SFU1610"
nut = doc.getObject("A2b_BallNut_SFU1620")
if nut is not None:
    nut.Label = "A2b_BallNut_SFU1610"

print("  dia %.1f journals over Y %.0f..%.0f and %.0f..%.0f, dia %.1f body between: %.1f -> %.1f cm3"
      % (2 * R_END, Y_LO, Y_LO_END, Y_HI_END, Y_HI, 2 * R_BODY, was, shaft.Volume / 1000.0))
print("  total length Y %.0f..%.0f = %.0f mm. BOM D1 orders 330 mm, which would overhang the"
      % (Y_LO, Y_HI, Y_HI - Y_LO))
print("  bracket's top by %.0f mm: the screw wants to be about %.0f mm, cut to length."
      % (330.0 - (Y_HI - Y_LO), Y_HI - Y_LO + 3.0))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- does it pass through its bores?
print()
print("  the screw against everything it touches:")
fail = []
for nm in ("A7_DriveBox", "P3_Carriage", "A2b_BallNut_SFU1620", "P25_MotorNacelle",
           "P22_DriveCap", "P21_ShellAnterior"):
    t = doc.getObject(nm)
    if t is None:
        continue
    c = shaft.common(t.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    note = ""
    if nm == "A2b_BallNut_SFU1620":
        note = "the nut rides the thread, so this one is meant to be solid"
    elif v > 0.02:
        note = "<-- the screw is inside this part"
        fail.append("%s: %.3f cm3" % (nm, v))
    print("   %-26s %8.3f cm3  %s" % (t.Label, v, note))

# and the nut must still have thread to ride on over its whole stroke
ny = (doc.getObject("A2b_BallNut_SFU1620").Shape.BoundBox
      if doc.getObject("A2b_BallNut_SFU1620") else None)
if ny is not None:
    stroke = 68.3
    print()
    print("   nut body Y %.0f..%.0f, stroke %.1f mm -> it needs thread from Y %.0f to %.0f"
          % (ny.YMin, ny.YMax, stroke, ny.YMin - stroke, ny.YMax))
    if ny.YMin - stroke < Y_LO_END or ny.YMax > Y_HI_END:
        fail.append("the nut runs off the dia %.1f body at one end of its stroke" % (2 * R_BODY))
    else:
        print("   the dia %.1f body runs Y %.0f..%.0f, so the nut stays on it throughout"
              % (2 * R_BODY, Y_LO_END, Y_HI_END))
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  the screw passes through its dia 9.2 clearance and its 8 mm bores, and touches nothing")
sys.stdout.flush()
sys.exit(1 if fail else 0)
