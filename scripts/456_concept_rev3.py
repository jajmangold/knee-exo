# -*- coding: utf-8 -*-
"""Concept revision 3: two 6001s inside the pulley. This is the one -- and it costs no new part.

The bench re-saved the concept again. The KFL001 housed units are gone and two bare 6001 deep-
groove bearings are in their place, bonded into the pulley's bore 25 mm apart.

THAT FIXES BOTH OBJECTIONS AT ONCE, which is what 455_concept_rev2.py said it would:

  * RIGID, not self-aligning. A KFL's insert has a spherical outer race and swivels on purpose,
    so two of them resist tilt not at all and varus/valgus falls to the rod alone. A 6001 is a
    plain deep-groove ring: a pair of them reacts tilt as a couple, which is ordinary radial load.
  * IT FITS A REAL PULLEY. A KFL001 body needs a bore of r 37.6 and a 29T HTD-8M rim roots at
    r 32.79 -- the block is wider than the whole pulley, so that layout only ever worked at the
    dia 120 the drivetrain cannot have. A 6001's dia 28 leaves 18.8 mm of wall inside a 29T rim.

AND THE PART IS ALREADY ON THE BUY LIST TWICE. BOM K3 is a 6001-2RS (the knee bearing) and D8a is
a 6001-2RS (the screw's upper bearing under Path B). The knee joint has just been redesigned
around a part number the project was already ordering. That is the opposite of what usually
happens when a joint is reworked.

    freecadcmd.exe scripts/456_concept_rev3.py
"""
import math

import FreeCAD

CONCEPT = r"C:/Users/Josh/Downloads/knee concept test.FCStd"

PITCH, PLD, TOOTH_H = 8.0, 0.686, 3.45
BELT_W_REAL = 30.0
F_BELT = 1064.0
C0_6001 = 2.38          # kN static, catalogue -- CHECK THE VENDOR'S OWN FIGURE
BRG_OD, BRG_W = 28.0, 8.0
ROD_D = 12.0
LEAD, LINK = 5.0, 38 / 20.0
J_ROTOR, J_LIMB = 3.10e-4, 0.30
THREAD, NUT_BODY = 135.0, 35.0
SWING = 68.3 / (29 * PITCH / (2 * math.pi))

doc = FreeCAD.openDocument(CONCEPT)
parts = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature")
         and not o.Label.startswith("Shell")]
g = {}
for o in parts:
    g.setdefault(o.Label, o)

brg = sorted([o for o in parts if o.Label.startswith("6001")],
             key=lambda o: o.Shape.BoundBox.XMin)
cen = [(o.Shape.BoundBox.XMin + o.Shape.BoundBox.XMax) / 2 for o in brg]
span = abs(cen[1] - cen[0])
pb = g["htd8m pulley"].Shape.BoundBox
root29 = 29 * PITCH / (2 * math.pi) - PLD - TOOTH_H

print("=" * 98)
print("1.  THE BEARING, CHECKED")
print("=" * 98)
print("  two 6001 (%.0f x %.0f x %.0f) at X %.0f and %.0f -- %.0f mm apart, inside the pulley"
      % (ROD_D, BRG_OD, BRG_W, cen[0], cen[1], span))
print()
radial = F_BELT / 2.0
print("  %-36s %10s %10s" % ("", "as drawn", "at 29T"))
span29 = BELT_W_REAL - BRG_W
for label, a, b in (("span, mm", span, span29),
                    ("radial load per bearing, N", radial, radial),
                    ("radial safety factor on C0", C0_6001 * 1000 / radial, C0_6001 * 1000 / radial),
                    ("tilt capacity, N.m", C0_6001 * span, C0_6001 * span29),
                    ("PETG wall to the tooth roots, mm",
                     (max(pb.YLength, pb.ZLength) / 2 - TOOTH_H) - BRG_OD / 2,
                     root29 - BRG_OD / 2)):
    print("  %-36s %10.1f %10.1f" % (label, a, b))
print()
print("  The 29T column is the one that matters, because the dia %.0f pulley has to go (section 3)."
      % max(pb.YLength, pb.ZLength))
print("  It still works: %.1f mm of wall, %.1fx on the belt load, %.0f N.m of tilt against a"
      % (root29 - BRG_OD / 2, C0_6001 * 1000 / radial, C0_6001 * span29))
print("  belt contribution that centring the bearings has already driven to zero.")
print()
print("  C0 = %.2f kN is a catalogue figure for the series. Check the one you actually buy --"
      % C0_6001)
print("  455 made exactly this mistake in the other direction by ranking on ratings I had not")
print("  verified, which is how a 6907 nearly got picked on 5.3 mm of wall.")

print()
print("=" * 98)
print("2.  THE ROD STOPS BEING A PROBLEM")
print("=" * 98)
rod = g["12mm steel rod"].Shape.BoundBox
cpl = sorted([o for o in parts if "Coupling" in o.Label], key=lambda o: o.Shape.BoundBox.XMin)
sup = [(o.Shape.BoundBox.XMin + o.Shape.BoundBox.XMax) / 2 for o in cpl]
L = sup[1] - sup[0]
R0 = (radial * (sup[1] - cen[0]) + radial * (sup[1] - cen[1])) / L
M = R0 * (cen[0] - sup[0])
Z = math.pi * ROD_D ** 3 / 32.0
print("  rod %.0f mm, clamped at the coupling centres X %.1f and %.1f -- a %.0f mm simply"
      % (rod.XLength, sup[0], sup[1], L))
print("  supported span with the two %.0f N bearing reactions inside it." % radial)
print("  max moment %.0f N.mm / %.0f mm3  =  %.1f MPa" % (M, Z, M / Z))
print()
print("  451_knee_pin.py put the pin at 99 MPa and spent a page on whether 316 could take it.")
print("  At %.1f MPa even annealed 316 is a factor of %.1f, and cold-finished is %.1f. The rod"
      % (M / Z, 205 / (M / Z), 310 / (M / Z)))
print("  no longer needs to be hardened, and because it does not need to be hardened it can be")
print("  drilled -- so the magnet counterbore, the circlip groove and the whole K2/K2a/K2b")
print("  argument collapse back into one plain rod and two clamps.")

print()
print("=" * 98)
print("3.  WHAT IS STILL WRONG, UNCHANGED FROM 453")
print("=" * 98)
tip = max(pb.YLength, pb.ZLength) / 2.0
stroke = SWING * (tip + PLD)
avail = THREAD - NUT_BODY
n_tot = (2 * math.pi * (tip + PLD) / LEAD) / LINK
print("  THE PULLEY IS STILL dia %.0f. It asks the nut for %.0f mm of travel where the bought"
      % (2 * tip, stroke))
print("  screw has %.0f, and puts %.2fx the limb's own inertia back on the leg unpowered."
      % (avail, J_ROTOR * n_tot ** 2 / J_LIMB))
print("  This is now the ONLY thing in the concept that does not work. Everything else about")
print("  revision 3 survives the change to 29T -- which was not true of revision 2.")

print()
print("=" * 98)
print("4.  SMALL THINGS")
print("=" * 98)
pbb = g["htd8m pulley"].Shape.BoundBox
print("  a. The bearings are not symmetric: one sits X %.0f..%.0f and the other X %.0f..%.0f,"
      % (brg[0].Shape.BoundBox.XMin, brg[0].Shape.BoundBox.XMax,
         brg[1].Shape.BoundBox.XMin, brg[1].Shape.BoundBox.XMax))
print("     so the first protrudes %.0f mm past the pulley face at X %.0f and lands in the"
      % (pbb.XMin - brg[0].Shape.BoundBox.XMin, pbb.XMin))
print("     aluminium plate. Flush to each face is both tidier and the longest span available.")
print("  b. ONE INNER RACE MUST FLOAT. Both outers bond into one housing and both inners sit on")
print("     one rod; if both inners are also clamped, tolerance and temperature preload them")
print("     against each other for the life of the device. Locate one inner against a shoulder")
print("     or collar and leave the other a slip fit on the rod.")
print("  c. BOND the outers, do not press them -- 418_knee_bearing.py's rule, and the numbers are")
print("     easy here: %.0f N over pi x %.0f x %.0f mm2 is %.2f MPa."
      % (radial, BRG_OD, BRG_W, radial / (math.pi * BRG_OD * BRG_W)))
seen = {}
for o in parts:
    b = o.Shape.BoundBox
    k = tuple(round(v, 1) for v in (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
    seen.setdefault(k, []).append(o.Label)
dup = [v for v in seen.values() if len(v) > 1]
print("  d. %d cut-and-base pairs are still in the file, plus %d imported bearing shells:"
      % (len(dup), len([o for o in doc.Objects if o.Label.startswith("Shell")])))
for v in dup:
    print("        %s" % "  /  ".join(v))
print("  e. The THIGH side is still not modelled. The two couplings clamp the rod and have to")
print("     bolt to something -- but that something is now two small flanges rather than two")
print("     KFL blocks, which is a far easier thing for P1_KneeYoke to grow than the clevis")
print("     453_concept_knee.py said the first revision needed.")

print()
print("=" * 98)
print("  VERDICT: revision 3 is the layout. Change the pulley to 29T and nothing else about it")
print("  breaks -- 18.8 mm of wall, 22 mm of span, %.0f N.m of tilt, %.1fx on the belt."
      % (C0_6001 * span29, C0_6001 * 1000 / radial))
print()
print("  And count the parts it deletes: the dia 12 pin's hardness argument, its magnet-carrier")
print("  argument, its retention collars, the bonded dia 28 seat in the yoke, the two printed lug")
print("  bores, and 44 mm of P2a's reach. It adds one 6001 -- the second of a part already")
print("  ordered twice.")
