# -*- coding: utf-8 -*-
"""Build the RIGHT leg as a mirror of the left, into its own document.

The built device is the left leg. The right is its reflection through the sagittal plane,
Z -> -Z. 700_handedness.py says what that does and does not change; the one thing it must not
change is the ball screw, which stays right-hand on both legs with the sign absorbed in
firmware.

Two reasons this is a separate DOCUMENT rather than more objects in the existing one:

  * the verification scripts all work on "every Part::Feature in the document", so doubling
    the objects would double every sweep and halve the meaning of the results;
  * interference, coverage and pressure are invariant under reflection, so the right leg does
    NOT need the 107-pose sweep repeated to be trusted. Keeping it separate makes that
    argument cleanly rather than burying it.

MIRRORING REVERSES FACE ORIENTATION. A reflected solid can come back inside out -- the same
defect 410_orientation_audit.py exists to catch, which cost several hours when removeSplitter
did it silently. Every mirrored shape here is checked for positive volume and for
Shape.check(), and the script refuses to save if any part fails.

THE ENGRAVING COMES ACROSS BACKWARDS and is deliberately left that way by this script: 412 is
run afterwards against the right document to fill nothing and cut fresh, correct text. A
mirrored part number is worse than none.

    freecadcmd.exe scripts/701_mirror_build.py
"""
import os
import FreeCAD
from FreeCAD import Vector as V

# The mirror source must be UNMARKED, because mirroring an engraved part reflects its glyphs
# along with it and 702 then cuts fresh text into a face that already has backwards text in it.
# Blanking the real left leg to achieve that is the dangerous way round -- a self-intersecting
# fill has destroyed a good document here before -- so KX_SRC lets the mirror be taken from a
# throwaway copy that 416_unmark.py has blanked, leaving the left leg untouched:
#
#   copy KneeExo_v6.FCStd + .marks.json to KneeExo_v6.blank.FCStd + .blank.marks.json
#   KX_DOC=...blank.FCStd freecadcmd scripts/416_unmark.py
#   KX_SRC=...blank.FCStd freecadcmd scripts/701_mirror_build.py
#   freecadcmd scripts/702_mirror_marks.py
SRC = os.environ.get("KX_SRC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
DST = os.environ.get("KX_DST", r"C:/Users/Josh/KneeExo_v6_R.FCStd").replace("\\", "/")

src = FreeCAD.openDocument(SRC)
# Build to a TEMPORARY file and move it into place only once every part has passed. Deleting
# the destination up front, as this used to, meant a single bad solid destroyed the previous
# good right leg and left nothing: one self-intersecting fill on P24 took out a complete,
# verified 37-part document, and the first sign of it was the user asking where the second leg
# had gone.
# ".partial.FCStd", not ".partial": saveAs appends .FCStd to any other name, so the
# file lands somewhere the rename cannot find it.
TMP = DST[:-6] + ".partial.FCStd"
if os.path.exists(TMP):
    os.remove(TMP)
dst = FreeCAD.newDocument("KneeExoR")

print("=" * 80)
print("MIRRORING THE LEFT LEG INTO THE RIGHT,  Z -> -Z")
print("=" * 80)
bad = []
n = 0
for o in src.Objects:
    sh = getattr(o, "Shape", None)
    if o.TypeId != "Part::Feature" or sh is None or sh.isNull() or not sh.Solids:
        continue
    m = sh.mirror(V(0, 0, 0), V(0, 0, 1))
    # a reflection flips handedness; OCCT may hand back a reversed solid
    if m.Volume < 0:
        m.reverse()
    ok = m.Volume > 0
    chk = "clean"
    try:
        m.check(True)
    except Exception:
        chk = "SELF-INTERSECT"
        ok = False
    if abs(abs(m.Volume) - sh.Volume) > max(1.0, 1e-4 * sh.Volume):
        chk = "VOLUME CHANGED"
        ok = False
    t = dst.addObject("Part::Feature", o.Name)
    t.Shape = m
    t.Label = o.Label
    n += 1
    if not ok:
        bad.append((o.Label, m.Volume / 1000.0, chk))
    print("  %-28s %9.2f -> %9.2f cm3  %s"
          % (o.Label, sh.Volume / 1000.0, m.Volume / 1000.0, chk))

print()
if bad:
    print("  %d parts failed to mirror cleanly:" % len(bad))
    for lbl, v, why in bad:
        print("     %-28s %.2f cm3  %s" % (lbl, v, why))
    raise AssertionError("refusing to save a mirrored set with %d bad solids" % len(bad))

dst.recompute()
dst.saveAs(TMP)
if os.path.exists(DST):
    os.remove(DST)
os.rename(TMP, DST)
print("  %d parts mirrored, all solid and clean -> %s" % (n, DST))
print()
print("  The part numbers are now MIRROR IMAGES and read backwards. Run 412 against this")
print("  document next: it fills nothing and cuts fresh text, which is the only way to get")
print("  a readable mark on a reflected part.")
