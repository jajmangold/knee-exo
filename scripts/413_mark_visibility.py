# -*- coding: utf-8 -*-
"""Are the engraved part numbers actually hidden?

412 places each mark on what it calls an inner face and claims they are hidden once
assembled. That was never tested, and the user reports seeing part numbers on outside faces.

Getting this test right took three attempts, each of which looked like a pass:

  1. Occluders included the GROUPS (C_Drive, B_Shank, A_ThighRail), whose Shape is a compound
     of everything inside them. Every mark duly reported as hidden behind its own parent.
  2. Occluders were compared by Label while the marks are keyed by internal Name, and several
     parts differ (P21_ShellAnterior is labelled P21_FairingThigh). A part occluding ITSELF
     read as hidden.
  3. The ray was cast along the face normal as if the mark faced outward. It does not: 412
     cuts the recess INTO the surface going outward, so the material lies outboard of the
     mark and the mark looks back toward the limb.

What the question actually is: standing anywhere outside the device, with the limb in place,
is there a line of sight to the mark? So fire a fan of rays out from just off the marked
surface and ask whether any of them escapes without meeting material. The reference limbs are
occluders here -- a mark facing the thigh is not on show, there is a leg in the way.

Send with:  python tools/fcsend.py scripts/413_mark_visibility.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

# (part, mark point, outward normal) -- taken from 412's own report
MARKS = [
    # (part, a point on the marked surface, the face normal, how 412 cut it)
    #   "r" radial: the tool starts at the surface and extrudes OUTWARD, so material lies
    #       outboard and the mark looks back toward the limb  -> test along -normal
    #   "p" planar: the tool is driven INTO the named face, so the mark looks out of it
    #       -> test along +normal
    # Getting this backwards is how an earlier run of this check cleared five marks it had
    # never actually looked at -- it was firing rays into solid material and finding them
    # blocked, which is not the same as the mark being covered.
    ("P5_ThighCuff",       V(13.2, 135.0, 74.5),    V(0.17, 0.0, 0.98), "r"),
    ("P7_ShankCuff",       V(29.4, -320.0, -35.0),  V(0.64, 0.0, -0.77), "r"),
    ("P21_ShellAnterior",  V(0.0, 70.0, 134.9),     V(0.0, 0.0, 1.0), "r"),
    ("P22_DriveCap",       V(0.0, 250.0, 135.5),    V(0.0, 0.0, 1.0), "r"),
    ("P25_MotorNacelle",   V(-72.0, 250.0, 62.0),   V(1.0, 0.0, 0.0), "r"),
    ("P24_FairingShank",   V(18.2, -175.0, 103.3),  V(0.17, 0.0, 0.98), "r"),
    ("P20_KneeShroud",     V(47.3, 15.0, 130.1),    V(0.34, 0.0, 0.94), "r"),
    ("P1_KneeYoke",        V(0.0, 60.0, 77.6),      V(0.0, 0.0, 1.0), "r"),
    ("P6_ShankSocket",     V(0.0, -260.0, 68.0),    V(0.0, 0.0, 1.0), "r"),
    ("P23a_FairingMount",  V(47.0, 88.0, 109.0),    V(1.0, 0.0, 0.0), "p"),
    ("P23b_FairingMount",  V(47.0, 124.0, 109.0),   V(1.0, 0.0, 0.0), "p"),
    ("P23c_FairingMount",  V(47.0, 160.0, 109.0),   V(1.0, 0.0, 0.0), "p"),
    ("P30_InterfaceProx",  V(20.0, 255.0, 137.0),   V(1.0, 0.0, 0.0), "p"),
    ("P31_InterfaceDist",  V(0.0, -275.0, 123.0),   V(0.0, 0.0, -1.0), "p"),
    # P2a_KneeHingePlate carries NO mark. 414 searched 16 stations x 36 bearings and found
    # nowhere covered: it is the knee hub at an open joint, reachable from every direction.
    # Its recess was filled. It is the 143 cm3 29T pulley; an unmarked part is the better trade.
]

# Part::Feature only. Groups carry a compound of their children and occlude everything.
# The reference limbs ARE occluders: a mark facing the thigh is not on show.
PARTS = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids]
print("  checking against %d parts including the reference limbs" % len(PARTS))


def escapes(pt, d, skip):
    """can a ray leave pt in direction d without meeting anything (skip = the marked part)"""
    far = V(pt.x + d.x * 400.0, pt.y + d.y * 400.0, pt.z + d.z * 400.0)
    seg = Part.makeLine(V(pt.x + d.x * 0.25, pt.y + d.y * 0.25, pt.z + d.z * 0.25), far)
    for o in PARTS:
        if not seg.BoundBox.intersect(o.Shape.BoundBox):
            continue
        k = o.Shape.common(seg)
        if not k.isNull() and k.Edges:
            return False
    return True


def fan(n, k=13):
    """n plus a spread of directions around it, out to 70 degrees"""
    n = V(n.x, n.y, n.z); n.normalize()
    a = V(0.0, 1.0, 0.0) if abs(n.y) < 0.9 else V(1.0, 0.0, 0.0)
    u = n.cross(a); u.normalize()
    w = n.cross(u)
    out = [n]
    for ang in (35.0, 70.0):
        for j in range(6):
            ph = 2.0 * math.pi * j / 6.0
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            out.append(V(n.x * c + (u.x * math.cos(ph) + w.x * math.sin(ph)) * s,
                         n.y * c + (u.y * math.cos(ph) + w.y * math.sin(ph)) * s,
                         n.z * c + (u.z * math.cos(ph) + w.z * math.sin(ph)) * s))
    return out[:k]


print("=" * 84)
print("ARE THE MARKS HIDDEN?  a fan of rays out from each marked surface")
print("=" * 84)
print("  %-20s %-14s %s" % ("part", "escaping rays", "verdict"))
exposed = []
for name, pt, nrm, mode in MARKS:
    look = V(-nrm.x, -nrm.y, -nrm.z) if mode == "r" else V(nrm.x, nrm.y, nrm.z)
    esc = sum(1 for d in fan(look) if escapes(pt, d, name))
    if esc:
        exposed.append(name)
    print("  %-20s %2d of 13       %s" % (name, esc, "ON SHOW" if esc else "hidden"))

print()
if exposed:
    print("  %d of %d marks can be seen from outside:" % (len(exposed), len(MARKS)))
    for e in exposed:
        print("     %s" % e)
else:
    print("  all %d marks are covered" % len(MARKS))
