# -*- coding: utf-8 -*-
"""Return every part to the 0 deg design pose, and say what moved.

The animation and render scripts pose the model by writing Placements -- the shank side
rotates about the knee axis, the carriage and ball nut translate along the stroke -- and a
pose left behind is invisible in every obvious check: the shapes are valid, the volumes are
right, the document saves clean. What breaks is any boolean against a posed reference, because
obj.Shape bakes the Placement in. That is how 409's fit check came to report "P7_ShankCuff:
only 17 samples landed on the shell": REF_Shank was sitting at a flexed pose, its cross
section at each station a long way from where the cuff is, so rays fired at the cuff missed
the limb entirely. Nothing was wrong with the cuff.

So: zero the Placements before any geometry stage, every time, and print them, because a pose
that silently disappears is as bad as one that silently stays.

    freecadcmd.exe tools/unpose.py              # fix the file
    KX_CHECK=1 freecadcmd.exe tools/unpose.py   # report only, exit 1 if posed

(freecadcmd parses its own argv and rejects unknown flags, hence the environment variable.)
"""
import os
import sys

import FreeCAD

CHECK = bool(os.environ.get("KX_CHECK"))
WANT = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")


def unpose(doc, check=False, quiet=False):
    """Set every Part::Feature's Placement to identity. Returns the names that were posed."""
    moved = []
    for o in doc.Objects:
        if not o.isDerivedFrom("Part::Feature"):
            continue                      # groups have no Placement at all
        if o.Placement.isIdentity():
            continue
        p = o.Placement
        ax, ang = p.Rotation.Axis, p.Rotation.Angle
        moved.append(o.Name)
        if not quiet:
            import math
            print("  %-26s dxyz %7.2f %7.2f %7.2f   %6.2f deg about (%.2f %.2f %.2f)"
                  % (o.Name, p.Base.x, p.Base.y, p.Base.z, math.degrees(ang), ax.x, ax.y, ax.z))
        if not check:
            o.Placement = FreeCAD.Placement()
    return moved


def main():
    doc = FreeCAD.openDocument(WANT)
    print("pose audit: %s" % doc.FileName)
    moved = unpose(doc, check=CHECK)
    if not moved:
        print("  all %d parts at the design pose" % len(doc.Objects))
    elif CHECK:
        print("  %d parts POSED -- geometry stages would read the wrong shapes" % len(moved))
        # freecadcmd aborts on SystemExit without flushing Python's buffer, so the report
        # vanished entirely the first time this exited non-zero. Flush, then exit.
        sys.stdout.flush()
        sys.exit(1)
    else:
        doc.recompute()
        doc.save()
        print("  reset %d parts to the design pose, saved" % len(moved))


# freecadcmd execs this file with its own __name__ (not "__main__"), which is why an
# "if __name__" guard here printed nothing but the banner. Run on execution, and let an
# importer (build_headless.py, which wants only the unpose() function) opt out by setting
# KX_NO_MAIN rather than by guessing at __name__.
if not os.environ.get("KX_NO_MAIN"):
    main()
