# -*- coding: utf-8 -*-
"""Which printed parts are shaped like the part, and which ARE the part?

Asked after noticing the 29T capstan has no teeth. It does not: sampled at the belt plane over 360
bearings, its outer radius is 35.55 mm with a spread of 0.000 mm. It is a plain cylinder. Every
check this repository runs passed it -- the interference sweep, the coverage rays, the printability
pass, the mesh integrity test, the engraving and its visibility fan -- because all of them ask about
the shape a part occupies and none of them asks whether the shape does the job.

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
     lambda sh: (profile_spread(sh, 111.0) or 0) > 1.0,
     "the belt drives the shank through this. A plain rim transmits nothing but friction."),
    ("P2a_KneeHingePlate", "a bolt pattern to the shank rail",
     lambda sh: cyls(sh, 4.5, 5.6) >= 3, "the capstan has to take its torque into the shank"),
    ("P3_Carriage", "V-wheel mounting holes",
     lambda sh: cyls(sh, 4.5, 5.6) >= 4, "four wheels carry the gantry on the rail"),
    ("P3_Carriage", "a belt clamp",
     lambda sh: cyls(sh, 3.0, 7.0) >= 2,
     "the closed belt loop is clamped here; this is how the drive force leaves the screw"),
    ("P3_Carriage", "a ball-nut mounting pattern",
     lambda sh: cyls(sh, 5.5, 7.0) >= 4, "the nut is trapped between plates and bolted"),
    ("A7_DriveBox", "idler bearing seats",
     lambda sh: cyls(sh, 25.8, 26.3) >= 2, "printed, so the axle load must land on a race"),
    ("A7_DriveBox", "a motor bolt pattern",
     lambda sh: cyls(sh, 3.0, 5.6) >= 4, "the C6374 bolts to this face"),
    ("A7_DriveBox", "a KP08 bolt pattern for the screw's top bearing",
     lambda sh: cyls(sh, 4.5, 7.0) >= 2, "the screw's upper block mounts here"),
    ("P1_KneeYoke", "a bolt pattern into the thigh rail",
     lambda sh: cyls(sh, 4.5, 5.6) >= 2, "the yoke is how the thigh side reaches the knee"),
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
print("MOCKUP AUDIT  --  %s" % _BASE)
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
