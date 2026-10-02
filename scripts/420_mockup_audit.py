# -*- coding: utf-8 -*-
"""Which printed parts are shaped like the part, and which ARE the part?

Asked after noticing the 29T capstan had no teeth. It did not: sampled at the belt plane over 360
bearings, its outer radius was 35.55 mm with a spread of 0.000 mm -- a plain cylinder. Every check
this repository runs passed it -- the interference sweep, the coverage rays, the printability pass,
the mesh integrity test, the engraving and its visibility fan -- because all of them ask about the
shape a part occupies and none of them asks whether the shape does the job.

(It has teeth now: 421_pulley_teeth.py. The entries below are what the table has learned since,
including two that this file had WRONG -- it asked the gantry for a ball-nut bolt pattern that the
design deliberately does not have, and the drive bracket for a KP08 pattern that a seated 608
replaced. An audit's expectations go stale exactly like documentation does.)

That is a different question from "is it strong enough" or "does it fit", and it needs stating
explicitly per part, because only a person knows what a part is FOR. So this file carries a table of
required features and checks each one. It will never be complete; it is a place to write down what
has been noticed.

A part that passes here is not verified. A part that fails here cannot work.

    freecadcmd.exe scripts/420_mockup_audit.py
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


# MIRROR AWARE. Every height below was written for the left leg, and run against the right one
# the belt plane at Z 111 is empty space -- so the audit reported the capstan's teeth, the belt
# land and both tip radii MISSING on a document that is a verified isometric mirror of a
# document where they are all present. An audit that can only read one of the two legs is half an
# audit, and the half it cannot read is the one assembled from a mirror script.
MIRRORED = False
_p1 = doc.getObject("P1_KneeYoke")
if _p1 is not None and getattr(_p1, "Shape", None) is not None and not _p1.Shape.isNull():
    MIRRORED = _p1.Shape.BoundBox.ZMax < 0
SGN = -1.0 if MIRRORED else 1.0
BELT_PLANE = SGN * 111.0


def cyls(sh, lo, hi, axis=None):
    """count cylindrical faces with a diameter in [lo, hi], optionally on one axis"""
    n = 0
    for f in sh.Faces:
        s = f.Surface
        if s.TypeId != "Part::GeomCylinder":
            continue
        if not (lo <= 2 * s.Radius <= hi):
            continue
        if axis is not None and abs(getattr(s.Axis, axis)) < 0.9:
            continue
        n += 1
    return n


def land_spread(sh, z, y0, y1, x_out=-36.74, x_in=-28.0, step=0.5):
    """how much a flat land's surface steps in and out along Y -- grooves, or a plain wall

    The ray runs from outside the tip plane inboard, so the land surface is the first boundary it
    meets. A plain wall gives a spread of zero whatever holes are drilled through it.
    """
    xs = []
    y = y0 + 1.0
    while y <= y1 - 1.0:
        ln = Part.makeLine(V(x_out, y, z), V(x_in, y, z))
        k = sh.common(ln)
        if not k.isNull() and k.Vertexes:
            xs.append(-min(v.Point.x for v in k.Vertexes))
        y += step
    return (max(xs) - min(xs)) if xs else None


def rail_bolts_aligned(sh, rail_z=98.0, margin=2.0):
    """how many of a part's vertical M5 holes sit over a clear channel in the thigh rail"""
    rail = None
    for o in doc.Objects:
        if "Extrusion" in o.Name and getattr(o, "Shape", None) is not None:
            b = o.Shape.BoundBox
            if b.YMax > 180.0 and b.XMax > 15.0:
                rail = o.Shape
    if rail is None:
        return 0
    rb = rail.BoundBox
    sgn = -1.0 if sh.BoundBox.ZMax < 0 else 1.0
    n = 0
    for f in sh.Faces:
        s = f.Surface
        if s.TypeId != "Part::GeomCylinder" or not (4.8 <= 2 * s.Radius <= 5.6):
            continue
        if abs(s.Axis.z) < 0.9:
            continue
        x, y = s.Center.x, s.Center.y
        if not (rb.XMin + margin < x < rb.XMax - margin):
            continue
        if not (rb.YMin < y < rb.YMax):
            continue
        if not rail.isInside(V(x, y, sgn * rail_z), 1e-7, True):
            n += 1
    return n


def outer_radius(sh, z, cx=0.0, cy=0.0, r0=20.0, r1=60.0, n=72):
    """the largest outer radius at one height -- the tip circle of a toothed pulley"""
    best = None
    for i in range(n):
        t = 2 * math.pi * i / n
        ln = Part.makeLine(V(cx + r0 * math.cos(t), cy + r0 * math.sin(t), z),
                           V(cx + r1 * math.cos(t), cy + r1 * math.sin(t), z))
        k = sh.common(ln)
        if k.isNull() or not k.Vertexes:
            continue
        r = max(math.hypot(v.Point.x - cx, v.Point.y - cy) for v in k.Vertexes)
        best = r if best is None else max(best, r)
    return best if best is not None else 0.0


def profile_spread(sh, z, cx=0.0, cy=0.0, r0=20.0, r1=60.0, n=240):
    """how much the outer radius varies around a part at one height -- teeth, or not"""
    rs = []
    for i in range(n):
        t = 2 * math.pi * i / n
        ln = Part.makeLine(V(cx + r0 * math.cos(t), cy + r0 * math.sin(t), z),
                           V(cx + r1 * math.cos(t), cy + r1 * math.sin(t), z))
        k = sh.common(ln)
        if k.isNull() or not k.Vertexes:
            continue
        rs.append(max(math.hypot(v.Point.x - cx, v.Point.y - cy) for v in k.Vertexes))
    return (max(rs) - min(rs)) if rs else None


# (part, what it must have, test, why it matters)
CHECKS = [
    ("P2a_KneeHingePlate", "29 HTD-8M teeth on the belt land",
     lambda sh: (profile_spread(sh, BELT_PLANE) or 0) > 1.0,
     "the belt drives the shank through this. A plain rim transmits nothing but friction."),
    # Teeth are not enough on their own: the rim was drawn at 35.552 for months, 0.685 under the
    # standard 29T tip radius, because the pitch line differential had been deducted twice. The
    # belt and the idler are both BOUGHT to the standard, so the radius is theirs to set, not
    # ours -- and a drum of the wrong radius with correct teeth cut into it still mismatches the
    # idler strand for strand and arrives 4.3 mm short of a 742 mm belt.
    ("P2a_KneeHingePlate", "its teeth at the STANDARD tip radius 36.24",
     lambda sh: abs(outer_radius(sh, BELT_PLANE) - 36.237) < 0.05,
     "the bought idler is 72.48 over the tips and the bought belt is 742 mm"),
    ("A6_Idler29T", "the same tip radius as the capstan",
     lambda sh: abs(outer_radius(sh, BELT_PLANE, cy=255.0) - 36.237) < 0.05,
     "both strands have to land at the same distance from the centreline"),
    ("P2a_KneeHingePlate", "a bolt pattern to the shank rail",
     lambda sh: cyls(sh, 4.5, 5.6) >= 3, "the capstan has to take its torque into the shank"),
    ("P3_Carriage", "V-wheel mounting holes",
     lambda sh: cyls(sh, 4.5, 5.6) >= 4, "four wheels carry the gantry on the rail"),
    # EXPECTATION CORRECTED, AND THE CHECK WITH IT. "A belt clamp" tested for two cylindrical
    # faces of 3..7 mm -- two bolt holes -- and 422 satisfied it while cutting its five grooves in
    # the wrong plane entirely (elliptical tunnels bored sideways through the carriage at Z 96).
    # Counting holes cannot tell a clamp from a colander. 424 grips the belt with a toothed land
    # in the tunnel instead of a bolt-on clamp, so measure the land: scan along Y at the belt
    # plane and demand the surface step in and out by the groove depth.
    ("P3_Carriage", "a toothed belt land, 8 mm pitch",
     lambda sh: (land_spread(sh, BELT_PLANE, 144.0, 186.0) or 0) > 2.5,
     "the closed belt loop is gripped here; this is how the drive force leaves the screw"),
    # EXPECTATION CORRECTED, not relaxed. The nut is NOT bolted: BOM D3 traps the flangeless
    # SFU1610 nut axially between two end plates, which is right for thrust. What it lacks is
    # anything to stop it TURNING with the screw -- a flangeless nut in a round pocket has no
    # anti-rotation feature at all. 422 adds two radial M5 set screws, so that is what to check.
    ("P3_Carriage", "nut anti-rotation (it is trapped, not bolted)",
     lambda sh: cyls(sh, 4.5, 5.6, "x") >= 2,
     "a flangeless nut in a round pocket spins with the screw"),
    ("A7_DriveBox", "idler bearing seats",
     lambda sh: cyls(sh, 25.8, 26.3) >= 2, "printed, so the axle load must land on a race"),
    ("A7_DriveBox", "a motor bolt pattern",
     lambda sh: cyls(sh, 3.0, 5.6) >= 4, "the C6374 bolts to this face"),
    # EXPECTATION CORRECTED. Probing the screw axis showed the bracket is AIR at every Y from 210
    # to 296 -- there was no screw boss for a KP08 to bolt to, and no support of any kind for the
    # screw's upper end. 422 builds the boss and seats a 608 (8 x 22 x 7) in it, which is one
    # bought part instead of a pillow block and two bolts, and the same answer that made the idler
    # and the knee printable. Check for the seat, not for bolts that should not exist.
    ("A7_DriveBox", "support for the screw's upper end",
     lambda sh: cyls(sh, 21.8, 22.3) >= 1,
     "without it the ball screw is a cantilever off its bottom block"),
    # COUNTING THE HOLES WAS NOT ENOUGH HERE EITHER. The yoke had six M5 at X -20, 0 and +20 --
    # the slot spacing of a 20x60 rail, which is what the object is still called and what this
    # design used to use. The rail is a 20x40: two cells, channels at X +-10. So all six bolts
    # landed on solid aluminium or off the edge, on the part that carries the whole knee reaction,
    # and "cyls >= 2" was satisfied throughout. 427_rail_bolts.py fills them and drills four that
    # line up. Check ALIGNMENT, by sampling the rail at the height of its channel.
    #
    # Sample laterally, never along the bolt: the bought rail's mockup carries a 2 mm web across
    # the slot centreline at Z 92..94 that a real V-slot does not have, so a ray fired along a
    # correctly placed bolt reports "hits material" and a ray along a wrong one can report clear.
    ("P1_KneeYoke", "rail bolts that land in the rail's channels",
     lambda sh: rail_bolts_aligned(sh) >= 4,
     "six M5 at the 20x60 spacing cannot reach a 20x40's slots"),
    ("A7_DriveBox", "a fixing to the rail at all",
     lambda sh: cyls(sh, 4.8, 5.6, "y") >= 2,
     "it holds the idler at 1828 N and had no M5 anywhere"),
    ("P6_ShankSocket", "a clamp pattern onto the shank rail",
     lambda sh: cyls(sh, 3.8, 4.6) >= 8, "16 x M4 was the spec"),
    ("P5_ThighCuff", "webbing slots", lambda sh: len(sh.Faces) > 60,
     "the strap passes through it; 409 verifies the slots are open"),
    ("P7_ShankCuff", "webbing slots", lambda sh: len(sh.Faces) > 60, "as above"),
    ("P30_InterfaceProx", "6 x M5 inserts and 2 dowels",
     lambda sh: cyls(sh, 6.3, 6.6) >= 6 and cyls(sh, 4.9, 5.2) >= 2, "the KX-1 pattern"),
    ("P31_InterfaceDist", "6 x M5 inserts and 2 dowels",
     lambda sh: cyls(sh, 6.3, 6.6) >= 6 and cyls(sh, 4.9, 5.2) >= 2, "the KX-1 pattern"),
    ("P20_KneeShroud", "some way of attaching",
     lambda sh: cyls(sh, 3.0, 7.0) >= 1, "cladding still has to stay on"),
    ("P22_DriveCap", "some way of attaching", lambda sh: cyls(sh, 3.0, 7.0) >= 1, "as above"),
    ("P25_MotorNacelle", "some way of attaching", lambda sh: cyls(sh, 3.0, 7.0) >= 1, "as above"),
    ("P24_FairingShank", "some way of attaching", lambda sh: cyls(sh, 3.0, 7.0) >= 1, "as above"),
    ("P21_ShellAnterior", "mounts to the three brackets",
     lambda sh: cyls(sh, 4.5, 5.6) >= 3, "the canopy hangs on P23a/b/c"),
    ("P23a_FairingMount", "a bolt into the extrusion slot",
     lambda sh: cyls(sh, 4.5, 5.6) >= 1, "one M5 into the posterior slot"),
]

print("=" * 100)
print("MOCKUP AUDIT  --  %s, %s leg" % (_BASE, "right" if MIRRORED else "left"))
print("=" * 100)
print("  Every other check in this repository asks about the shape a part occupies. None of them")
print("  asks whether the shape does the job. This one does, from a hand-written table, because")
print("  only a person knows what a part is for.")
print()
print("  %-22s %-40s %s" % ("part", "must have", "state"))
missing = []
for name, want, test, why in CHECKS:
    o = doc.getObject(name)
    if o is None:
        print("  %-22s %-40s PART MISSING" % (name, want))
        missing.append((name, want, "the part is not in the document"))
        continue
    try:
        ok = bool(test(o.Shape))
    except Exception as e:
        ok, why = False, "check itself failed: %s" % e
    print("  %-22s %-40s %s" % (name[:22], want[:40], "ok" if ok else "MISSING"))
    if not ok:
        missing.append((name, want, why))

print()
print("=" * 100)
if missing:
    print("  %d FEATURES MISSING -- these parts are printable and not usable" % len(missing))
    print("=" * 100)
    for name, want, why in missing:
        print("  %s: no %s" % (name, want))
        print("      %s" % why)
else:
    print("  every feature in the table is present")
print()
print("  Passing this is not a guarantee. The table only contains what someone has thought to")
print("  write down, and the capstan's teeth were missing for months while every automated check")
print("  in the repository reported the part fine.")
sys.stdout.flush()
sys.exit(1 if missing else 0)
