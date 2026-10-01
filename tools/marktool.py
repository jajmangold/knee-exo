# -*- coding: utf-8 -*-
"""Building the little solid that cuts or fills a part number. Shared, for a reason.

412 (place and cut), 416 (fill) and 702 (mirror onto the other leg) all need the same four
operations, and when they each had their own copy the copies drifted: three of four frames came
out left-handed and 12 of 14 part numbers were cut as mirror images. The geometry of a mark now
lives in exactly two files -- tools/markframe.py for which way it points, this one for what it is
made of.
"""
import os

import FreeCAD
import Part
from FreeCAD import Vector as V

FONT = next((f for f in (r"C:/Windows/Fonts/arialbd.ttf", r"C:/Windows/Fonts/verdanab.ttf",
                         r"C:/Windows/Fonts/consolab.ttf") if os.path.exists(f)), None)
assert FONT, "no bold font found"
DEPTH = 0.8          # recess
SKIN = 0.80          # below this fraction of solid skin, the site is already engraved
# Why bold, and why these sizes: stroke width decides whether text survives a 0.4 mm nozzle.
# Arial Bold at 8 mm has ~1.2 mm stems, three extrusions wide; at 4 mm it is ~0.6 mm, which is
# thin but acceptable as a RECESS (a shallower perimeter) where it would not be as raised text.


def text_faces(s, h):
    """One planar face per character, holes already subtracted, laid out along local +X."""
    out = []
    for ch in Part.makeWireString(s, FONT, h):
        fs = []
        for w in ch:
            try:
                fs.append(Part.Face(w))
            except Exception:
                pass
        if not fs:
            continue
        fs.sort(key=lambda f: -f.Area)
        f = fs[0]
        for g in fs[1:]:
            f = f.cut(g)
        out.append(f)
    return out


def block(text, h):
    """(the whole string as one face set centred on its own box, the individual faces)."""
    faces = text_faces(text, h)
    assert faces, "no glyphs for %r" % text
    tb = faces[0]
    for f in faces[1:]:
        tb = tb.fuse(f)
    bb = tb.BoundBox
    tb.translate(V(-0.5 * (bb.XMin + bb.XMax), -0.5 * (bb.YMin + bb.YMax), 0.0))
    return tb, faces


def inflate(shape, f=1.06):
    """Grow a planar face set about its own centre.

    A fill tool exactly the shape of the recess shares every side wall with it, and fusing across
    coincident faces is a reliable way to get a BOPAlgo self-intersection: P24_FairingShank came
    back valid(), one solid, the right volume, and failed Shape.check(), which 701 then refused to
    mirror. Safe because the material around a mark is solid by construction -- the placement
    search proved the surface smooth over the footprint plus 2 mm.
    """
    c = shape.BoundBox.Center
    to0 = FreeCAD.Matrix()
    to0.move(V(-c.x, -c.y, -c.z))
    sc = FreeCAD.Matrix()
    sc.scale(f, f, f)
    back = FreeCAD.Matrix()
    back.move(V(c.x, c.y, c.z))
    return shape.transformGeometry(back.multiply(sc.multiply(to0)))


def fuse_clean(sh, tool):
    """(result, how it was made, "clean" or "SELF-INTERSECT").

    removeSplitter() tidies the coplanar seams a fill leaves, and on P24 it turned a clean fuse
    into a self-intersection -- every variant through it failed, every raw fuse passed, whatever
    the tool inflation or depth. So prefer the tidy result, fall back to the raw one, and never
    lose the fill over cosmetics: leftover seam faces cost nothing in an STL.
    """
    out = []
    try:
        t = sh.fuse(tool).removeSplitter()
        if t.Volume < 0:                      # removeSplitter has inverted a solid before
            t.reverse()
        out.append(("merged", t))
    except Exception:
        pass
    try:
        out.append(("raw fuse", sh.fuse(tool)))
    except Exception:
        pass
    for how, t in out:
        try:
            t.check(True)
            return t, how, "clean"
        except Exception:
            continue
    return (out[0][1], out[0][0], "SELF-INTERSECT") if out else (None, "none", "FAILED")


def skin(sh, m):
    """How solid an 8 x 8 x 0.5 slab of surface is, given a frame matrix placed ON the surface.

    Intact skin is ~100%; an engraved patch is pitted to 50..77%. Deliberately small: a FLAT slab
    on a CURVED surface lifts off at the corners by the sagitta, which over 8 mm at the tightest
    radius here (r 32, the motor pod) is 0.25 mm -- inside the slab's 0.5 mm. A 24 mm slab lifts
    2.2 mm and reports intact skin as engraved.
    """
    probe = Part.makeBox(8.0, 8.0, 0.5, V(-4.0, -4.0, 0.0)).transformGeometry(m)
    k = sh.common(probe)
    return (0.0 if k.isNull() else k.Volume) / max(1e-9, probe.Volume), probe
