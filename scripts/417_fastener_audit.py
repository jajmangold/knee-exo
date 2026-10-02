# -*- coding: utf-8 -*-
"""Every hole in every printed part: what fits it, and what has to happen after printing.

411 answers "will this print" -- bed, overhangs, walls, closed mesh. It says nothing about whether
the holes are the right size for the hardware, and that is the other half of "ready to print",
because a hole is the one feature a printer reliably gets WRONG. A 4.0 mm hole modelled for an M4
comes off the bed at 3.7-3.9 (elephant's foot on the first layers, die swell on the walls, and the
nozzle cutting the corner of every arc), so a clearance hole becomes an interference fit and a
bearing seat becomes a press that cracks the boss.

What this does: find every cylindrical face in every printed part, cluster by diameter, and say for
each cluster what hardware it matches, whether it is a clearance fit or a tapping size, and whether
its axis is along the recommended build direction (a hole on the build axis prints round; a
horizontal hole prints as an egg and needs reaming).

It is also the raw material for the assembly list, which is why it prints a per-part table rather
than just a verdict: a part with eight M4 clearance holes and two 5 mm dowel holes is a part whose
assembly step can be written without opening the CAD.

    freecadcmd.exe scripts/417_fastener_audit.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/417_fastener_audit.py
"""
import math
import os

import FreeCAD

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

# The printed set, from 219_stl.py.
PRINTED = ["P1_KneeYoke", "P2a_KneeHingePlate", "P5_ThighCuff", "P6_ShankSocket", "P7_ShankCuff",
           "P30_InterfaceProx", "P31_InterfaceDist", "P20_KneeShroud", "P21_ShellAnterior",
           "P22_DriveCap", "P25_MotorNacelle", "P24_FairingShank",
           "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount"]

# Diameter -> what it is. Ranges are generous because a lofted shell's bolt bosses are drawn by
# cylinder cuts whose nominal is whatever the script that made them used.
#   clearance  = bolt passes through, head bears on the surface
#   tapping    = a self-tapping screw cuts its own thread in PETG, or the hole is for a heat-set
#               insert, which needs the insert's OD and not the bolt's
CLASS = [
    (2.60, 2.75, "M2.5 tapping / self-tap", "drill 2.6 after printing if a screw must bite"),
    (2.80, 3.10, "M3 tapping / self-tap", "self-tapping screw, or tap M3"),
    (3.20, 3.50, "M3 clearance", "prints undersize -- ream 3.4"),
    (3.90, 4.10, "M4 tapping / self-tap", "self-tapping screw, or tap M4"),
    (4.20, 4.45, "M4 clearance", "prints undersize -- ream 4.3"),
    (4.50, 4.80, "M3 heat-set insert", "insert OD ~4.6; print 4.6-4.8 and melt in"),
    (4.90, 5.15, "5 mm dowel / M5 tapping", "a dowel wants H7; ream 5.0"),
    (5.20, 5.55, "M5 clearance", "prints undersize -- ream 5.3"),
    (5.60, 6.10, "M4 heat-set insert", "insert OD ~6.0; print 5.8-6.0 and melt in"),
    # A heat-set insert's hole is about its OD MINUS 0.5, because the brass melts its way in and
    # displaces material rather than cutting it. An M5 insert is OD 6.9-7.1, so 6.4 is correct and
    # is what 502 drills (INSERT_R 3.2, 7 mm deep). Calling 6.4 "M6 clearance" is what made this
    # audit report a conflict with the BOM that did not exist.
    (6.30, 6.55, "M5 heat-set insert", "insert OD ~7.0; 6.4 is right, melt it in"),
    # P2a's one remaining cylinder: 6.2 mm at (0, -25, 89.8), axis Z, and only 3.5 mm deep, which
    # is a POCKET rather than a hole -- it sits on the belt land side of the knee hub, so it is
    # almost certainly a belt-end or clamp pocket. Inferred from position and depth: no script in
    # the repository was found that builds it, which is its own small warning about the ~290
    # scripts that ran before the current chain.
    (6.15, 6.28, "pocket, 3.5 mm deep (not a fastener)", "nothing to do"),
    (6.56, 6.80, "M6 clearance", "ream 6.4"),
    (7.80, 8.20, "8 mm shaft / rod", "ream 8.0 H7 if it must rotate"),
    # 10.4 appears four times on each cuff, each one directly over a 5.2 clearance: that is a cap
    # head recess, not a hole for hardware of its own.
    (10.30, 10.60, "M5/M6 cap head counterbore", "nothing to do; the head sits in it"),
    (9.80, 10.29, "10 mm pin or 10 mm ID bearing", "ream 10.0"),
    # The knee pin, BOM K2: an M12 x 70 shoulder bolt or hardened dowel through P1 and P2a.
    (12.10, 12.45, "M12 knee pin clearance", "ream 12.3; this is the joint axis, so do it on a mill"),
    (12.80, 13.20, "13 mm OD bearing seat (695)", "press fit: print 12.9 and face it"),
    (18.80, 19.20, "19 mm OD bearing seat (6800)", "press fit: print 18.9 and face it"),
    (21.80, 22.20, "22 mm OD bearing seat (6900)", "press fit: print 21.9 and face it"),
]
# Best build orientation per part, from 411's own search -- a hole parallel to this prints round.
UP = {"P1_KneeYoke": (0, -1, 0), "P2a_KneeHingePlate": (0, 1, 0), "P5_ThighCuff": (0, -1, 0),
      "P6_ShankSocket": (0, -1, 0), "P7_ShankCuff": (0, -1, 0), "P30_InterfaceProx": (0, 1, 0),
      "P31_InterfaceDist": (0, 1, 0), "P20_KneeShroud": (0, 1, 0), "P21_ShellAnterior": (0, 1, 0),
      "P22_DriveCap": (0, -1, 0), "P25_MotorNacelle": (0, 1, 0), "P24_FairingShank": (0, -1, 0),
      "P23a_FairingMount": (0, 0, -1), "P23b_FairingMount": (0, 0, -1),
      "P23c_FairingMount": (0, 0, -1)}


def classify(d):
    for lo, hi, what, note in CLASS:
        if lo <= d <= hi:
            return what, note
    return None, None


print("=" * 100)
print("FASTENER AND HOLE AUDIT  --  %s" % _BASE)
print("=" * 100)
print("  A printed hole comes out 0.1-0.3 mm UNDER its modelled size on most machines, so every")
print("  clearance hole below needs reaming or a drill pass, and every bearing seat needs facing.")
print("  Holes whose axis is NOT along the build direction print as an egg: reaming is mandatory.")
print()
print("  %-22s %7s %5s %-28s %-9s %s"
      % ("part", "dia mm", "count", "what fits", "axis", "after printing"))
unknown = []
tiny = []
total_holes = 0
for name in PRINTED:
    o = doc.getObject(name)
    if o is None:
        print("  %-22s MISSING" % name)
        continue
    up = UP.get(name, (0, 1, 0))
    # Collect cylindrical faces. A cylinder in a cut is a hole; one on the outside is a boss or a
    # fillet, so keep only cylinders whose surface normal points INTO the solid -- the orientation
    # of the face tells us, and this is also why Shape.check() mattering earlier matters here.
    holes = {}
    for f in o.Shape.Faces:
        s = f.Surface
        if s.TypeId != "Part::GeomCylinder":
            continue
        d = 2.0 * s.Radius
        if d > 60.0:                  # the shell itself, not a hole
            continue
        # P2a is a 29T pulley with a lightening pattern, so its 16/20/28/36/48/56 mm cylinders are
        # the pattern and the belt land, not holes anything goes through. Anything over 13 mm that
        # is not the knee pin is geometry, and listing it as "unclassified hardware" is noise.
        if d > 13.5:
            continue
        ax = s.Axis
        ax = (abs(ax.x), abs(ax.y), abs(ax.z))
        along = max(range(3), key=lambda i: ax[i])
        key = (round(d, 1), along)
        holes[key] = holes.get(key, 0) + 1
    if not holes:
        print("  %-22s %s" % (name, "no cylindrical holes at all"))
        continue
    first = True
    for (d, along), n in sorted(holes.items()):
        total_holes += n
        what, note = classify(d)
        axname = "XYZ"[along]
        on_build = abs(up[along]) > 0.5
        if what is None:
            unknown.append((name, d, n))
            what, note = "unclassified", "check against the BOM by hand"
        if d < 2.0:
            tiny.append((name, d, n))
        print("  %-22s %7.1f %5d %-28s %-9s %s"
              % (name if first else "", d, n, what,
                 "%s %s" % (axname, "(build)" if on_build else "(cross)"),
                 note if on_build else note + " -- AND it prints oval"))
        first = False

print()
print("=" * 100)
print("WHAT TO DO BEFORE ASSEMBLY")
print("=" * 100)
print("  %d holes across %d printed parts." % (total_holes, len(PRINTED)))
if tiny:
    print("  HOLES THAT WILL CLOSE UP (under 2 mm, a 0.4 nozzle bridges them):")
    for nm, d, n in tiny:
        print("     %-22s %.1f mm x %d" % (nm, d, n))
else:
    print("  No hole is under 2 mm, so nothing closes up at a 0.4 nozzle.")
if unknown:
    print("  DIAMETERS THAT MATCH NO STANDARD HARDWARE -- each is either a deliberate clearance")
    print("  for something that is not a fastener, or a mistake:")
    for nm, d, n in unknown:
        print("     %-22s %.1f mm x %d" % (nm, d, n))
print()
print("  The pattern to expect: bolt holes on the BUILD axis get a quick twist of the right drill;")
print("  cross-axis holes get drilled and reamed because layer stacking makes them oval; bearing")
print("  seats get faced with the bearing itself as the gauge. None of that is a design change --")
print("  it is the post-processing list, and it belongs in the assembly instructions rather than")
print("  being rediscovered part by part at the bench.")
