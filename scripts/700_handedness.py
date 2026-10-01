# -*- coding: utf-8 -*-
"""What actually differs between the left leg and the right.

The built device is the LEFT leg: +Z is lateral, the upright hangs off the outside, and the
cuffs open anteromedially. (scripts/02_base.py still carries a line from the first day of the
project saying "Right leg (MIRROR flag for left)" -- that is stale and now wrong.)

The right leg is the mirror image through the sagittal plane, Z -> -Z. Most of what that
implies is boring. Two things are not, and one of them would be an expensive surprise.

Pure Python, no FreeCAD.
"""

print("=" * 82)
print("1.  WHAT MIRRORS, WHAT DOES NOT")
print("=" * 82)
ROWS = [
    ("printed parts, all 15", "MIRROR", "every one is chiral -- the whole device lives at +Z, "
     "nothing\n                                 straddles the sagittal plane"),
    ("P3 gantry plate, alu", "MIRROR", "6 mm plate, cut chiral"),
    ("A7 drive bracket, alu", "MIRROR", "4 mm plates and 5 mm cheeks, cut chiral"),
    ("2040 / 2020 extrusion", "shared", "symmetric section, cut to length"),
    ("HTD-8M and 5M belts", "shared", "symmetric tooth form"),
    ("29T capstan and idler", "shared", "symmetric"),
    ("C6374 motor", "shared", "direction is a firmware sign, see below"),
    ("XDRIVE MINI", "shared", ""),
    ("V-wheels, bearings, fasteners", "shared", ""),
    ("neoprene sleeves", "shared", "a tube is a tube"),
    ("webbing, buckles, D-rings", "shared", ""),
    ("SFU1610 ball screw, RH", "SHARED -- see 2", "the interesting one"),
]
print("  %-32s %-16s %s" % ("item", "", ""))
for a, b, c in ROWS:
    print("  %-32s %-16s %s" % (a, b, c))

print()
print("=" * 82)
print("2.  THE BALL SCREW DOES NOT GET MIRRORED, AND MUST NOT BE")
print("=" * 82)
print("  Mirroring an assembly mirrors its threads: a right-hand screw reflected through a")
print("  plane is a LEFT-HAND screw. Taken literally, the right leg would need an LH SFU1610.")
print()
print("  370_no_lh_screw.py already priced that and rejected it for the left leg -- an LH")
print("  ball screw is a special order at a premium, with worse lead time and no stock. Doing")
print("  it now would double the problem AND make the two legs use different screws.")
print()
print("  It is not necessary. The screw is not a structural mirror of anything -- it is a")
print("  rotary-to-linear converter between two parts that ARE mirrored. Keep the RH screw,")
print("  and the only consequence is that for a given motor direction the nut now travels")
print("  toward the other end. That reverses the sign between motor rotation and knee angle.")
print()
print("     left leg    +motor -> nut travels distal -> knee extends")
print("     right leg   +motor -> nut travels distal -> knee FLEXES")
print()
print("  So the fix is one sign, in one place: the joint direction constant in firmware")
print("  (ODrive axis.controller.config, or the gait controller's joint map). It costs")
print("  nothing and it keeps ONE screw part number across both legs.")
print()
print("  The trap is doing nothing and assuming symmetry. A right leg built with an RH screw")
print("  and the left leg's firmware sign drives the knee the wrong way under load, which on")
print("  a %.1f N.m assist is not a subtle failure." % 28.2)

print()
print("=" * 82)
print("3.  WHAT THIS DOES TO THE BOM")
print("=" * 82)
PRINTED_G = 1263.0
ALU_G = 478.0
RAIL_G = 164.0
print("  Per leg, unchanged:          %.0f g printed + %.0f g aluminium + %.0f g rail"
      % (PRINTED_G, ALU_G, RAIL_G))
print()
print("  For a pair, the printed and fabricated parts DOUBLE but do not repeat -- they are")
print("  17 new part numbers, not 17 more of the same:")
print("     printed    15 L + 15 R = 30 distinct parts, %.1f kg of filament" % (2 * PRINTED_G / 1000))
print("     aluminium   2 L +  2 R =  4 distinct parts, %.0f g" % (2 * ALU_G))
print("  The bought items simply double in quantity, same part numbers.")
print()
print("  Which is the argument for the suffix: a left and right cuff are the same shape")
print("  reflected, they will not fit each other, and at a glance across a print bed they are")
print("  indistinguishable. 412 engraves every part already; the mirrored set has to carry an")
print("  L or R or the marking stops being worth anything.")
print()
print("  And the marks must be RE-CUT, not mirrored: reflected text reads backwards.")

print()
print("=" * 82)
print("4.  WHAT STAYS VERIFIED AND WHAT HAS TO BE RE-RUN")
print("=" * 82)
print("  Interference, coverage, pressure, printability and bed fit are all invariant under")
print("  reflection -- a mirrored assembly collides exactly where its original did. So the")
print("  107-pose sweep does NOT need repeating on the right leg to be trusted.")
print()
print("  Two things are NOT invariant and do need checking:")
print("     * the ENGRAVING, because the marks are re-cut rather than reflected, so their")
print("       placement is new geometry and 413 has to pass on it independently")
print("     * anything that was verified against the REFERENCE LIMB rather than against the")
print("       device, if the limb phantom is not itself symmetric. REF_Thigh and REF_Shank")
print("       are cones on the Y axis, so they are -- but that is worth stating rather than")
print("       assuming, because it is the assumption that makes the rest of this paragraph")
print("       true.")
