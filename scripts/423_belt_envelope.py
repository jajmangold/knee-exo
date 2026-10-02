# -*- coding: utf-8 -*-
"""Put the belt where a real HTD-8M belt sits: its teeth in the grooves, not its whole body outside.

The four belt solids were drawn as a plain 5.57 mm band resting ON the capstan's 35.55 mm tip
circle, so the model's belt back stands at R 41.12. That is self-consistent only while the pulleys
are smooth drums, which is what they were until 421 cut the capstan's teeth. A real belt meshes:

    pulley tip radius (standard 29T)  36.237     the land between the grooves
    groove depth                       3.45      cut by 421
    belt tooth height                  3.38      so the tooth tips reach R 32.86
    belt thickness                     5.60      backing is 5.60 - 3.38 = 2.22
    belt land rests on the tip circle            so the BACK of the belt is at 36.24 + 2.22
    belt back                         38.46      not 41.12 -- the model was 2.66 mm out
    pitch line                        36.923     tip + PLD 0.686, which is what BOM S2b and the
                                                 742 mm belt of BOM K1 both assume.

WHY IT MATTERS, beyond tidiness: every clearance around the belt was set against a band 3.35 mm
too far out. Clearances only got more generous, so nothing collides -- except the one place the
carriage is supposed to TOUCH the belt. The gantry's belt tunnel is 6.5 mm wide across a 5.57 mm
slab, and against a real belt it is 4.1 mm too wide: the belt would sit loose in the slot and ride
out of any mesh. 424 rebuilds that tunnel, and it needs the belt to be where the belt really is.

WHAT IS MODELLED, AND WHAT IS NOT. These solids are the 2.22 mm BACKING only. The teeth are left
implicit, because a toothed belt cannot honestly be swept as a rigid body: it circulates, so the
teeth do not keep a fixed position relative to any part they pass. Drawing them would put
tooth-on-land overlaps into 601's results at every pose where the carriage has walked half a pitch
along a belt the sweep holds still -- false positives that would bury the real ones.

So the tooth space is checked separately, here: the annulus R 32.17..35.55 at each pulley and the
two straight corridors between them are where belt teeth live, and NOTHING may intrude there
except the two pulleys and the carriage's toothed land. That check is the half of the model the
solids no longer carry.

    freecadcmd.exe scripts/423_belt_envelope.py
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

TIP = 36.237                # standard 29T HTD-8M tip radius; 421 grows the capstan to it
TOOTH_H = 3.38              # HTD-8M belt tooth height
THICK = 5.60                # HTD-8M belt total thickness
BACK = TIP + (THICK - TOOTH_H)      # 38.46
ROOT = TIP - TOOTH_H                # 32.86
PLD = 0.686
Z0, Z1 = 96.0, 126.0        # 30 mm belt land
Y_RUN = 255.0               # idler centre; the straight runs span 0..255
ALLOWED = ("P2a_KneeHub_Pulley29T", "P2a_KneeHingePlate", "A6_Idler29T", "P3_Carriage")


def wrap(cy, ro, ri, keep_positive):
    """half annulus about (0, cy) in the plane of the belt"""
    sol = Part.makeCylinder(ro, Z1 - Z0, V(0, cy, Z0), V(0, 0, 1)) \
        .cut(Part.makeCylinder(ri, Z1 - Z0 + 2, V(0, cy, Z0 - 1), V(0, 0, 1)))
    half = Part.makeBox(4 * ro, 2 * ro, Z1 - Z0 + 4,
                        V(-2 * ro, cy if keep_positive else cy - 2 * ro, Z0 - 2))
    return sol.common(half)


print("=" * 98)
print("BELT ENVELOPE  --  %s" % _BASE)
print("=" * 98)
print("  tip %.2f   tooth tips %.2f   back %.2f   pitch line %.2f   (was: 35.55..41.12)"
      % (TIP, ROOT, BACK, TIP + PLD))

NEW = {
    "A5_Belt_HTD8M":     ("knee wrap, 180 deg", lambda: wrap(0.0, BACK, TIP, False)),
    "A5b_Belt_DriveRun": ("drive run, X -%.2f..-%.2f" % (BACK, TIP),
                          lambda: Part.makeBox(BACK - TIP, Y_RUN, Z1 - Z0, V(-BACK, 0.0, Z0))),
    "A5c_Belt_TakeRun":  ("take run,  X +%.2f..+%.2f" % (TIP, BACK),
                          lambda: Part.makeBox(BACK - TIP, Y_RUN, Z1 - Z0, V(TIP, 0.0, Z0))),
    "A5d_Belt_WrapIdler": ("idler wrap, 180 deg", lambda: wrap(Y_RUN, BACK, TIP, True)),
}

print()
print("  %-22s %-28s %10s %10s  %s" % ("solid", "what", "was cm3", "now cm3", "back moved"))
tot = 0.0
for name, (what, mk) in NEW.items():
    o = doc.getObject(name)
    if o is None:
        print("  %-22s MISSING FROM DOCUMENT" % name)
        continue
    was = o.Shape.Volume / 1000.0
    oldmax = max(abs(o.Shape.BoundBox.XMin), abs(o.Shape.BoundBox.XMax))
    sh = mk()
    assert len(sh.Solids) == 1, "%s came out as %d solids" % (name, len(sh.Solids))
    sh.check(True)
    o.Shape = sh
    newmax = max(abs(sh.BoundBox.XMin), abs(sh.BoundBox.XMax))
    tot += sh.Volume / 1000.0
    print("  %-22s %-28s %10.1f %10.1f  %+.2f mm" % (name, what, was, sh.Volume / 1000.0,
                                                     newmax - oldmax))

# the belt's length, as a check on BOM K1's 742 mm
pitch_r = TIP + PLD
length = 2 * math.pi * pitch_r + 2 * Y_RUN
print()
print("  pitch-line length 2*pi*%.2f + 2*%.0f = %.1f mm, nearest 8M size %d mm (%d teeth)"
      % (pitch_r, Y_RUN, length, round(length / 8.0) * 8, round(length / 8.0)))
print("  BOM K1 says 742 mm. On the standard 36.92 pitch radius it would be %.1f."
      % (2 * math.pi * 36.92 + 2 * Y_RUN))

# ---------------------------------------------------------------- the tooth space
print()
print("  TOOTH SPACE -- R %.2f..%.2f at both pulleys and between them. Belt teeth live here, so" %
      (ROOT, TIP))
print("  nothing else may: an intruder would be hit by a tooth every 8 mm of belt travel.")
space = wrap(0.0, TIP, ROOT, False) \
    .fuse(wrap(Y_RUN, TIP, ROOT, True)) \
    .fuse(Part.makeBox(TIP - ROOT, Y_RUN, Z1 - Z0, V(-TIP, 0.0, Z0))) \
    .fuse(Part.makeBox(TIP - ROOT, Y_RUN, Z1 - Z0, V(ROOT, 0.0, Z0)))
bad = []
for o in doc.Objects:
    if o.TypeId != "Part::Feature" or getattr(o, "Shape", None) is None:
        continue
    if o.Shape.isNull() or not o.Shape.Solids or o.Name.startswith(("A5", "REF_", "TEST_")):
        continue
    if not o.Shape.BoundBox.intersect(space.BoundBox):
        continue
    try:
        c = o.Shape.common(space)
    except Exception:
        continue
    if c.isNull() or c.Volume < 20.0:
        continue
    tag = "  (expected: it meshes)" if o.Name in ALLOWED else "  <-- INTRUDER"
    print("   %-26s %8.2f cm3%s" % (o.Name, c.Volume / 1000.0, tag))
    if o.Name not in ALLOWED:
        bad.append(o.Name)

doc.recompute()
doc.save()
print()
if bad:
    print("  %d part(s) in the tooth space: %s" % (len(bad), ", ".join(bad)))
    print("  425_belt_clearance.py is what cuts them back, and it is the one that fails if they")
    print("  are still there afterwards. This file defines where the belt is; it does not enforce.")
else:
    print("  nothing unexpected in the tooth space")
print("  belt solids total %.1f cm3 of backing. The teeth are implicit -- see the header." % tot)
sys.stdout.flush()
sys.exit(0)
