# -*- coding: utf-8 -*-
"""Concept revision 2: the bearings moved inside the belt. Right move, wrong bearing.

The bench re-saved "knee concept test.FCStd". What changed, measured rather than described:

    bearing centres     72 mm apart  ->  26 mm apart, and now INSIDE the pulley
    rod                 80 mm        ->  70 mm, clamped at its two extremities
    plates              60 x 78 x 3  ->  65 x 205 x 3, carrying the rail socket as well
    overall width       88 mm        ->  70 mm
    pulley              dia 120      ->  dia 120, unchanged

MOVING THE BEARINGS INTO THE BELT PLANE IS THE RIGHT MOVE AND IT IS THE SAME ONE
454_knee_ideal.py arrived at from the other direction. Today's 6001 sits 27 mm inboard of the
belt it carries, which is why P2a_KneeHingePlate spans 58 mm and weighs 188 g to reach between
them, and why the belt's 1064 N arrives at the bearing as a 28.7 N.m tilting moment. Bearings
centred in the belt make that offset, and that moment, zero. The plates growing to carry both the
pulley and the rail socket is the same idea applied again: one structure, no reaching.

BUT KFL001 IS A SELF-ALIGNING BEARING, AND THAT IS THE ONE PROPERTY THIS JOINT MUST NOT HAVE.
445_screw_foot.py already wrote it down for the other end of the machine: "KP/KFL are shaft blocks
for plain round rail -- a pressed self-aligning insert in a cheap housing". The insert's outer race
is spherical and swivels in its seat ON PURPOSE, so it can take misalignment. Two of them on one
shaft do not resist tilt at all: they simply both swivel, and the only thing left opposing
varus/valgus is the dia 12 rod bending between them. 145_hinge.py made the knee pin work in double
shear specifically to fix "the varus/valgus weakness flagged earlier". This gives it back.

    freecadcmd.exe scripts/455_concept_rev2.py
"""
import math

import FreeCAD
import Part

CONCEPT = r"C:/Users/Josh/Downloads/knee concept test.FCStd"
MAIN = r"C:/Users/Josh/KneeExo_v6.FCStd"

PITCH, PLD, TOOTH_H = 8.0, 0.686, 3.45
F_BELT = 1064.0
LEAD, LINK = 5.0, 38 / 20.0
J_ROTOR, J_LIMB = 3.10e-4, 0.30
THREAD, NUT_BODY = 135.0, 35.0
SWING = 68.3 / (29 * PITCH / (2 * math.pi))      # rad, the modelled knee range
ROD_D = 12.0

doc = FreeCAD.openDocument(CONCEPT)
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature")]
g = {}
for o in parts:
    g.setdefault(o.Label, o)

print("=" * 98)
print("1.  HOUSEKEEPING: three parts are still in the file twice")
print("=" * 98)
seen = {}
for o in parts:
    b = o.Shape.BoundBox
    k = tuple(round(v, 1) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    seen.setdefault(k, []).append(o.Label)
dupes = [v for v in seen.values() if len(v) > 1]
for v in dupes:
    print("     %s" % "  /  ".join(v))
print("  Cut-and-base pairs that never got cleaned up. Harmless to look at, but any volume or")
print("  clash number taken off this document counts them twice -- %d of %d solids are copies."
      % (sum(len(v) - 1 for v in dupes), len(parts)))

print()
print("=" * 98)
print("2.  THE SELF-ALIGNING PROBLEM, WHICH IS THE REAL ONE")
print("=" * 98)
kfl = sorted([o for o in parts if o.Label.startswith("KFL")],
             key=lambda o: o.Shape.BoundBox.XMin)
cen = [(o.Shape.BoundBox.XMin + o.Shape.BoundBox.XMax) / 2 for o in kfl]
span = abs(cen[1] - cen[0])
print("  bearing centres X %.0f and %.0f -- %.0f mm apart, down from 72 in revision 1."
      % (cen[0], cen[1], span))
print()
print("  A KFL001's insert has a SPHERICAL outer race in a spherical seat. It is built to swivel")
print("  so the housing can be bolted to something out of true. On a knee that means:")
print()
print("     tilt stiffness from the bearings           none -- both simply swivel")
print("     tilt stiffness from the rod                a dia %.0f rod over %.0f mm of span"
      % (ROD_D, span))
I = math.pi * ROD_D ** 4 / 64.0
print("     dia %.0f second moment                      %.0f mm4 -- all of the stiffness there is"
      % (ROD_D, I))
print()
print("  For comparison, two RIGID deep-groove bearings the same distance apart resist tilt as a")
print("  couple -- the load divides by the span and goes in as plain radial force, which is what")
print("  a deep-groove bearing is for:")
print()
print("  %-28s %10s %12s %12s" % ("tilt moment", "span 26", "span 21", "span 72"))
for m in (10.0, 20.0, 29.0):
    print("  %-28s %8.0f N %10.0f N %10.0f N"
          % ("%.0f N.m reacted as a couple" % m, m * 1000 / 26, m * 1000 / 21, m * 1000 / 72))
print()
print("  so a rigid pair even at this short span turns tens of N.m into a few hundred newtons")
print("  of ordinary radial load. A self-aligning pair turns it into rod bending and slop.")
print()
print("  THE DEMAND IS NOT WRITTEN DOWN ANYWHERE IN THIS REPOSITORY. The belt's contribution is")
print("  now genuinely zero -- that is what centring the bearings in the belt bought. What is")
print("  left is varus/valgus from the limb, which no script here has ever put a number on, and")
print("  which 145_hinge.py nonetheless thought important enough to redraw the hub as a fork for.")
print("  Whatever that number is, self-aligning bearings supply none of the stiffness that")
print("  resists it and rigid ones supply it in proportion to their span. That settles the")
print("  family without needing the number.")

print()
print("=" * 98)
print("3.  AND THE HOUSED BLOCKS ONLY FIT BECAUSE THE PULLEY IS WRONG")
print("=" * 98)
pul = g["htd8m pulley"].Shape
pb = pul.BoundBox
tip120 = max(pb.YLength, pb.ZLength) / 2.0
root120 = tip120 - TOOTH_H
tip29 = 29 * PITCH / (2 * math.pi) - PLD
root29 = tip29 - TOOTH_H
body = (kfl[0].Shape.BoundBox.YLength, kfl[0].Shape.BoundBox.ZLength)
need = math.hypot(body[0], body[1]) / 2.0
print("  a KFL001 body is %.0f x %.0f mm, so it needs a bore of r %.1f to be swallowed."
      % (body[0], body[1], need))
print("     at the drawn dia %.0f pulley: tooth roots at r %.1f  ->  %.1f mm of wall. Fits."
      % (2 * tip120, root120, root120 - need))
print("     at the CORRECT 29T pulley:   tooth roots at r %.1f  ->  %.1f mm of wall."
      % (root29, root29 - need))
print("        The block is wider than the whole rim. It cannot go in.")
print()
stroke = SWING * (tip120 + PLD)
avail = THREAD - NUT_BODY
n_tot = (2 * math.pi * (tip120 + PLD) / LEAD) / LINK
print("  and dia %.0f is not a free choice, which 453_concept_knee.py already found: it asks the"
      % (2 * tip120))
print("  nut for %.0f mm of travel where the bought screw has %.0f, and puts %.2fx the limb's own"
      % (stroke, avail, J_ROTOR * n_tot ** 2 / J_LIMB))
print("  inertia back on the leg.")
print()
print("  SO THE TWO IDEAS ARE MUTUALLY EXCLUSIVE AS DRAWN. Bearings inside the pulley is right.")
print("  Housed bearing units inside the pulley needs a pulley the drivetrain cannot have.")

print()
print("=" * 98)
print("4.  THE SAME LAYOUT WITH BARE BEARINGS -- what it costs to fix")
print("=" * 98)
print("  Bare thin-section deep-groove bearings bonded straight into the pulley's bore. No")
print("  housing, so the OD is the bearing's own:")
print()
PUL_W = 30.0        # the REAL belt width, not the 32 drawn
print("  %-8s %-12s %6s %8s %8s %9s %8s  %s"
      % ("", "size", "wall", "C0 kN", "arm", "radial SF", "tilt N.m", "shaft"))
for name, bore, od, w, c0 in (("6901", 12, 24, 6, 0.95), ("6902", 15, 28, 7, 1.3),
                              ("6905", 25, 42, 9, 2.6), ("6906", 30, 47, 9, 4.0)):
    wall = root29 - od / 2.0
    arm = PUL_W - w
    sf = c0 * 1000.0 / (F_BELT / 2.0)
    flag = "" if sf > 2.5 else "   <-- tight on the belt alone"
    print("  %-8s %-12s %5.1f %8.2f %7.0f %8.1fx %8.0f %6d mm%s"
          % (name, "%dx%dx%d" % (bore, od, w), wall, c0, arm, sf, c0 * 1000.0 * arm / 1000.0,
             bore, flag))
print()
print("  6901 keeps everything else in the concept exactly as drawn -- same dia 12 rod, same")
print("  couplings, same plates -- and simply swaps two housed units for two bare rings bonded")
print("  into the pulley. It is the smallest edit that fixes both problems at once, but it is")
print("  working at only %.1fx on the belt load alone before any tilt is added."
      % (950.0 / (F_BELT / 2.0)))
print("  6902 on a dia 15 shaft costs one shaft size and buys %.1fx -- and dia 15 is still a"
      % (1300.0 / (F_BELT / 2.0)))
print("  stocked linear-shaft size with SHF15 and SK15 holders to match. 6905 on dia 25 is what")
print("  454 recommends and is stiffer again, but it changes the rod, the couplings and the")
print("  clamps with it.")
print()
print("  THE SPAN IS ALREADY AT ITS MAXIMUM and that is worth knowing: flush to each face of a")
print("  %.0f mm pulley, two %.0f mm rings sit %.0f mm apart, which is what the file already has."
      % (pb.XLength, 6.0, pb.XLength - 6.0))
print("  On the real %.0f mm belt it becomes %.0f. There is no more arm to find inside the belt;"
      % (PUL_W, PUL_W - 6.0))
print("  more tilt capacity has to come from a bigger bearing, not a wider stance.")

print()
print("=" * 98)
print("5.  WHAT REVISION 2 GOT RIGHT, AND KEEP")
print("=" * 98)
main = FreeCAD.openDocument(MAIN)
mg = {o.Name: o for o in main.Objects}
hub = mg["P2a_KneeHingePlate"].Shape
allb = None
for o in parts:
    b = o.Shape.BoundBox
    allb = b if allb is None else (allb.add(b) or allb)
print("  * bearings centred in the belt. Today's 6001 is 27 mm inboard of it, which is what makes")
print("    P2a_KneeHingePlate a %.0f mm deep, %.0f g part. Centred, that reach stops existing."
      % (hub.BoundBox.ZLength, hub.Volume / 1000.0 * 1.27))
print("  * the plates carrying BOTH the pulley and the rail socket, so there is one load path")
print("    from the belt to the shank rail and no printed part spanning between two others.")
print("  * the rod clamped at its extremities rather than in the middle: the bearings sit between")
print("    the clamps, so the rod is a simply supported beam and not a cantilever.")
print("  * %.0f mm across the knee, down from %.0f in revision 1." % (allb.XLength, 88))
print()
print("  The architecture is right. It needs a rigid bearing instead of a self-aligning one, and")
print("  a 29T pulley instead of a dia 120 one -- and those two changes are the same change,")
print("  because a bare ring is what fits inside a 29T rim.")
