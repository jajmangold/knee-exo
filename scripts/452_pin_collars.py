# -*- coding: utf-8 -*-
"""Flange collars on a hardened rod for the knee pin: the right idea, and one of the two is wrong.

Proposed at the bench: "can't we just put 2 of these on a hardened steel or hss rod with the
flange sides facing away from eachother / rod screw sides facing eachother, then we bolt through
the flange faces to eachother?" -- a dia 12 bore rigid flange collar, flange dia 32 x 3, boss
dia 16 x 13, 4 x M4 on a dia 24 circle, one M4 grub screw.

WHY THIS IS THE RIGHT IDEA. 451_knee_pin.py ended up recommending soft 316 for the knee pin, and
the reason was never strength -- it was that a hardened pin CANNOT BE MACHINED. The pin needs a
retention feature and a counterbore for the encoder magnet, and you cannot cut a circlip groove or
drill a 6 mm pocket in a 60 HRC dowel without carbide and a grinder. A grub-screwed collar needs
NOTHING done to the rod. That single fact puts a proper ground, hardened rod back on the table,
and with it the dimensional tolerance that 451's check (a) was actually worried about.

WHY ONE OF THE TWO IS WRONG, AND THE BOLTS BETWEEN THEM MORE SO. Bolting flange to flange along
the pin puts four M4 at r 12 running the full length of the joint. The yoke lives at Z 76..88 on
that axis and the yoke ROTATES relative to the hub -- that is the knee. Four bolts through it at
r 12 weld the leg straight. The flanges cannot talk to each other; each can only talk to the part
it sits against, and only one end of this joint has a part to sit against.

    freecadcmd.exe scripts/452_pin_collars.py
"""
import FreeCAD
import Part

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"

# the collar, off the vendor drawing
FLANGE_D, FLANGE_T = 32.0, 3.0
BOSS_D, BOSS_H = 16.0, 13.0
PCD, BOLT_D = 24.0, 4.0
BORE = 12.0

# the joint, from 418_knee_bearing.py and the axis scan
LUG1 = (70.0, 76.0)
YOKE = (76.0, 88.0)
LUG2 = (88.0, 113.0)
CBORE = (113.0, 126.0)          # the existing pin-head counterbore, measured at r 11
HUB_FACE = 126.0
SHROUD = 131.87                 # P20_KneeShroud's nearest material on the axis
LIMB = 52.0                     # REF_Knee's top on the axis -- the pin may not go below this
PIN_L = 70.0

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}

print("=" * 98)
print("1.  WHY THE BOLTS BETWEEN THE TWO FLANGES CANNOT EXIST")
print("=" * 98)
print("  bolt circle r %.0f, so four M4 would sweep r %.0f..%.0f for the whole length of the pin."
      % (PCD / 2, PCD / 2 - BOLT_D / 2, PCD / 2 + BOLT_D / 2))
yk = g["P1_KneeYoke"].Shape
tube = Part.makeCylinder(PCD / 2 + BOLT_D / 2, 70.0, FreeCAD.Vector(0, 0, 58.0),
                         FreeCAD.Vector(0, 0, 1)) \
    .cut(Part.makeCylinder(PCD / 2 - BOLT_D / 2, 74.0, FreeCAD.Vector(0, 0, 56.0),
                           FreeCAD.Vector(0, 0, 1)))
hit = yk.common(tube)
print("  that annulus passes through P1_KneeYoke: %.2f cm3, Z %.1f..%.1f"
      % (hit.Volume / 1000.0, hit.BoundBox.ZMin, hit.BoundBox.ZMax))
print("  and the yoke is the THIGH side while the pin is held by the hub, which is the SHANK")
print("  side. Those two rotate past each other -- that is the knee joint. Bolting them")
print("  together through that annulus locks the leg straight.")
print()
print("  So each collar can only fasten to the part at its own end. Which parts are those?")

print()
print("=" * 98)
print("2.  WHAT IS ACTUALLY AT EACH END OF THE PIN")
print("=" * 98)
print("  measured on the knee axis:")
print("     Z < %.0f          the patient. REF_Knee reaches Z %.0f -- nothing may go below it"
      % (LIMB + 4, LIMB))
print("     Z %.0f .. %.0f      open, clear to r 25+. NOTHING TO BOLT TO." % (LIMB + 4, LUG1[0]))
print("     Z %.0f .. %.0f      hub lug 1, bored r 6.5" % LUG1)
print("     Z %.0f .. %.0f      the yoke and the 6001 -- the rotating interface" % YOKE)
print("     Z %.0f .. %.0f     hub lug 2, bored r 6.5" % (LUG2[0], CBORE[0]))
print("     Z %.0f .. %.0f    the existing pin-head counterbore, bored r 11" % CBORE)
print("     Z %.0f            the hub's outer face  <-- THE ONE FLAT FACE THIS PIN HAS"
      % HUB_FACE)
print("     Z %.0f .. %.1f   open; P20_KneeShroud's nearest material is Z %.1f"
      % (HUB_FACE, SHROUD, SHROUD))

print()
print("=" * 98)
print("3.  THE ARRANGEMENT THAT WORKS: one collar, not two")
print("=" * 98)
print("  HEAD END -- the flange collar earns its flange here, and it is already half designed.")
print("  210_flush.py cut a dia 20 x 13 counterbore for a pin head at Z %.0f..%.0f, and this"
      % CBORE)
print("  collar's boss is dia %.0f x %.0f. Open that counterbore to dia 17 and the boss drops"
      % (BOSS_D, BOSS_H))
print("  straight in, with the flange landing flat on the hub face at Z %.0f." % HUB_FACE)
print()
print("     counterbore   dia 17 x %.0f deep, Z %.0f..%.0f   (was dia 20 -- NARROWER, not wider)"
      % (BOSS_H, HUB_FACE - BOSS_H, HUB_FACE))
print("     flange        Z %.0f..%.0f, %.1f mm clear of the shroud at Z %.1f"
      % (HUB_FACE, HUB_FACE + FLANGE_T, SHROUD - HUB_FACE - FLANGE_T, SHROUD))
print("     4 x M4 heat-set inserts at r %.0f in the hub face. The dia 17 counterbore ends at"
      % (PCD / 2))
print("     r 8.5 and the bolt holes span r %.0f..%.0f, so every one lands in solid material"
      % (PCD / 2 - BOLT_D / 2, PCD / 2 + BOLT_D / 2))
print("     -- which the dia 20 counterbore would NOT have allowed: r 10 against a hole")
print("     starting at r %.0f." % (PCD / 2 - BOLT_D / 2))
print()
print("  TAIL END -- nothing to bolt to, so the flange is dead weight. Use a PLAIN dia %.0f shaft"
      % BORE)
print("  collar: same grub screw, same job, smaller, cheaper, and it fits the open space below")
print("  Z %.0f without caring what shape it is." % LUG1[0])

print()
print("=" * 98)
print("4.  DOES A 70 mm ROD STILL REACH?")
print("=" * 98)
lo = LUG1[0] - BOSS_H
hi = lo + PIN_L
print("  tail collar sits Z %.0f..%.0f, hard against lug 1's outer face" % (lo, LUG1[0]))
print("  a %.0f mm rod from there reaches Z %.0f, against the hub face at Z %.0f and the"
      % (PIN_L, hi, HUB_FACE))
print("  flange's own top at Z %.0f -- so it lands %.0f mm inside the flange's bore."
      % (HUB_FACE + FLANGE_T, HUB_FACE + FLANGE_T - hi))
print("  and its bottom at Z %.0f clears REF_Knee's Z %.0f by %.0f mm." % (lo, LIMB, lo - LIMB))
print()
print("  %.0f mm is the right length and there is nothing spare at either end, which is a useful"
      % PIN_L)
print("  check on BOM K2 having said 70 all along.")

print()
print("=" * 98)
print("5.  SO WHAT ROD? AND THE MAGNET, WHERE I OVERSTATED IT")
print("=" * 98)
print("  With retention handled by collars, the rod needs no features at all -- so pick it purely")
print("  on size and strength:")
print()
print("     ISO 8734 hardened dowel   m6, +0.012/+0.023   58-62 HRC. STRONGEST, but m6 into a")
print("                               6001's 0/-0.008 bore is %.3f..%.3f mm of INTERFERENCE --"
      % (0.012, 0.031))
print("                               a press fit needing a press, not a hand assembly.")
print("     ground silver steel /     h6, 0/-0.011        slip fit in the bearing, hardenable,")
print("     drill rod dia 12 x 70                         and cuttable while soft. BEST HERE.")
print("     HSS tool blank            ground, 62-65 HRC   hard AND BRITTLE. A joint pin on a leg")
print("                                                   takes shock loads. Do not.")
print()
print("  ON THE MAGNET, I put that more strongly last time than it deserves. A SYMMETRIC steel")
print("  shaft end directly behind a diametric magnet is ordinary practice -- it is how every")
print("  motor with a shaft-end encoder is built -- and it mostly shunts flux, costing field")
print("  strength at the sensor rather than creating angle error. The sharp risk is ASYMMETRIC")
print("  ferrous material near the magnet. So a steel pin is not disqualifying, and the margin")
print("  is cheap to buy back: the flange gives you 4 x M4 on a dia %.0f circle, which is a" % PCD)
print("  mount for a small aluminium or printed magnet carrier standing the magnet off the steel.")
print("  Load path in steel, magnetic path in air. That is the version to build.")

print()
print("=" * 98)
print("  VERDICT")
print("=" * 98)
print("  Buy ONE flange collar (head end) and ONE plain shaft collar (tail), not two flanges, and")
print("  no bolts between them. The idea's real contribution is that it needs nothing machined")
print("  into the rod -- which is exactly what forced 451 to a soft pin, so this reverses that:")
print("  BOM K2 goes back to a ground hardened rod, h6 rather than m6 so it slips into the 6001.")
