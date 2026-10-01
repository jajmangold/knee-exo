# -*- coding: utf-8 -*-
"""Is any part in the document inside out?

409_cuffs.py found that Part.removeSplitter() can silently REVERSE a solid. Fusing a box
onto a conical bore leaves a face tangent to the cone, and merging it flipped the
orientation: volume went +153.69 -> -153.69 cm3.

Nothing in FreeCAD complains about this. isValid() stays True. isClosed() stays True.
len(Solids) stays 1. The bounding box is unchanged. What changes is that every subsequent
boolean runs backwards -- a cut ADDS material -- and three separate measurements came back
impossible before the cause was found:

    common(cuff, limb)   4876 cm3, against a 153 cm3 cuff
    distToShape          closest point at r 59.4, inside a limb whose surface is r 71.3
    the solids filter    0 solids, because a negative volume fails "> 0.5 cm3"

removeSplitter is called all over this build chain. If it did that to one part it can have
done it to others, and an inverted part would poison every interference result it appears
in -- including the 107-pose sweep, which is the thing the whole repo trusts.

So: check every solid in the document. Cheap, and it is exactly the class of defect this
project keeps finding -- valid, closed, well-formed, and wrong.

Send with:  python tools/fcsend.py scripts/410_orientation_audit.py
"""
import FreeCAD

def _kx_doc():
    """The model, whether we are in the GUI instance or under freecadcmd.

    KX_DOC overrides the file, which is how the mirrored right leg is checked with the same
    scripts. Headless matters: 397 and 409 both exceed the RPC server's 90 s dispatch limit,
    and overrunning it does not fail cleanly -- it keeps working and leaves a half-built
    document the next script reads as finished.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()

print("=" * 78)
print("ORIENTATION AUDIT -- every solid in the document")
print("=" * 78)
bad, checked, skipped = [], 0, []
for o in doc.Objects:
    sh = getattr(o, "Shape", None)
    if sh is None or sh.isNull():
        skipped.append(o.Label)
        continue
    try:
        v = sh.Volume
    except Exception as e:
        skipped.append("%s (%s)" % (o.Label, e))
        continue
    if not sh.Solids:
        skipped.append("%s (no solids)" % o.Label)
        continue
    checked += 1
    neg = [s for s in sh.Solids if s.Volume < 0.0]
    flag = ""
    if v <= 0.0 or neg:
        bad.append(o.Label)
        flag = "  <-- INSIDE OUT"
    print("  %-30s %10.2f cm3  %d solids  valid=%-5s%s"
          % (o.Label, v / 1000.0, len(sh.Solids), sh.isValid(), flag))

print()
print("  checked %d solids, %d skipped (no shape)" % (checked, len(skipped)))
if skipped:
    print("  skipped: %s" % ", ".join(skipped[:8]))
print()
if bad:
    print("  INSIDE OUT: %s" % ", ".join(bad))
    print("  Every interference result involving these is meaningless -- a cut against an")
    print("  inverted solid adds material instead of removing it.")
else:
    print("  No inverted solids. The removeSplitter inversion found in 409 is so far the")
    print("  only instance, and desplit() in that script now guards against it.")

assert not bad, "inverted solids: %s" % ", ".join(bad)
