# -*- coding: utf-8 -*-
"""Where a part number's glyphs point. One authority, because four copies disagreed.

A mark needs three directions: the reading direction, the glyph's up, and the surface normal.
Get the HANDEDNESS of the first two wrong and the text is a mirror image -- still 0.8 mm deep,
still on a hidden face, still passing every check in this repository, and unreadable.

That is what happened. 412 built the frame inline in four places, one per mark style, and three
of the four were wrong in a way nothing tested: 9 radial marks and the 3 fairing mounts came out
mirrored, while the two interface bosses came out correct. It surfaced only when the glyphs were
sampled and printed as ASCII from the reader's own viewpoint -- see tools/readmark.py.

THE RULE, and it is worth stating once rather than rediscovering per face:

    a reader stands on the OPEN side of the surface and looks along `into`, the direction the
    material lies. With their head up along `up`, their right hand points along

        right = into x up

    (check it against the familiar case: looking down -Z with up +Y gives right +X). Text reads
    forwards when the glyph layout's reading direction IS that right. Anything else is a mirror.

So this module returns (read, up, normal, into) and everything that places, fills, re-cuts or
renders a mark uses it. The surface geometry decides `into`:

    radial ("r")   the ray from the limb axis meets the surface from the inside, so the material
                   is OUTBOARD: into = +normal. The reader is inside the bore or the shell.
    a face ("P", "P2", "P3", "P4")
                   the normal points out of the face and the material is behind it:
                   into = -normal.
"""
from FreeCAD import Vector as V


def _unit(v):
    u = V(v.x, v.y, v.z)
    u.normalize()
    return u


def frame(mode, normal, hoop=False, legacy=False):
    """(read, up, normal, into) for a mark on this surface.

    legacy=True reproduces the LEFT-HANDED frames this script replaced, for one purpose only:
    filling a mark that was cut with them. A fill tool built on the corrected frame is the
    mirror image of the old recess, so it covers half the old glyphs and leaves the rest -- the
    tool has to match the cut that is actually in the part, not the cut that should have been.

    mode: "r" for a surface of revolution about the limb axis (the normal lies in XZ),
          "P"  a flat X face with the string running along Z (the fairing mounts: 16 mm of limb
               axis against 39 of Z, so the string cannot run along the limb),
          "P2" a flat X face with the string running along the limb (the interface bosses: 56 mm
               along the limb against 7 of height),
          "P3" a bed face whose normal is +/-Z (the distal interface's underside),
          "P4" a face whose normal is +/-Y, string along X and up +Z (the controller mount's
               motor-facing side: a disc normal to the limb axis, so neither of the two X modes
               nor the bed face applies).
    hoop: lay a radial string around the part instead of along the limb.
    """
    n = _unit(normal)
    if mode == "r":
        into = V(n.x, n.y, n.z)
        up = V(-n.z, 0.0, n.x) if not hoop else V(0.0, 1.0, 0.0)
    elif mode == "P":
        into = V(-n.x, -n.y, -n.z)
        up = V(0.0, 1.0, 0.0)
    elif mode == "P2":
        into = V(-n.x, -n.y, -n.z)
        up = V(0.0, 0.0, 1.0)
    elif mode == "P3":
        into = V(-n.x, -n.y, -n.z)
        up = V(1.0, 0.0, 0.0)
    elif mode == "P4":
        into = V(-n.x, -n.y, -n.z)
        up = V(0.0, 0.0, 1.0)
    else:
        raise AssertionError("unknown mark mode %r" % mode)
    read = into.cross(up)
    if read.Length < 1e-9:
        raise AssertionError("mode %s: up is parallel to the view direction" % mode)
    if legacy and mode in ("r", "P"):
        # The two that were wrong, and wrong in the READING direction specifically: the old code
        # took read = +Y on a radial surface and +Z on an X face, where the reader's right hand
        # points the other way. Flipping `up` instead reproduces neither cut -- it turns the text
        # upside down as well, which is how a "fill" of the old recess covered 56% of it and was
        # correctly refused.
        read = V(-read.x, -read.y, -read.z)
    return _unit(read), _unit(up), n, _unit(into)


def matrix(mode, point, normal, standoff=0.0, hoop=False, legacy=False):
    """The placement for a text block centred on `point`, plus the direction to extrude into.

    standoff moves the block off the surface along -into, which is what a cutting tool wants
    (start outside, cut inward) and what a filling tool must NOT have (start on the surface, or
    the fill stands proud and has to be shaved -- 415 exists because of that).
    """
    import FreeCAD
    read, up, n, into = frame(mode, normal, hoop=hoop, legacy=legacy)
    p = V(point.x - into.x * standoff, point.y - into.y * standoff, point.z - into.z * standoff)
    m = FreeCAD.Matrix(read.x, up.x, into.x, p.x,
                       read.y, up.y, into.y, p.y,
                       read.z, up.z, into.z, p.z,
                       0.0, 0.0, 0.0, 1.0)
    return m, into
