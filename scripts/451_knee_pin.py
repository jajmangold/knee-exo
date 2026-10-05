# -*- coding: utf-8 -*-
"""A 316 stainless rod for the knee pin: softer than the BOM asks for, and better in one way.

Asked at the bench: "PATIKIL 316 Stainless Steel Dowel Pins 12mm x 70mm Round Metal Rods 2 Pcs?"

BOM K2 says "ISO 7379 12 x 70 shoulder screw, or ISO 8734 dia 12 x 70 hardened dowel". Neither of
those is what this is. An ISO 8734 dowel is through-hardened to 58-62 HRC; an ISO 7379 shoulder
screw is alloy steel at 45-50 HRC with a head and a thread. A 316 rod is austenitic stainless --
it cannot be heat treated at all, and annealed it yields at about a fifth of what a dowel does.

SO THE FIRST QUESTION IS WHETHER IT IS STRONG ENOUGH, and the geometry is unusually kind here:
418_knee_bearing.py set the joint up as "lug Z 70..76, yoke 76..88, lug 88..113", so the pin is in
DOUBLE SHEAR across a 12 mm gap, not a cantilever. Short spans make small moments.

AND THE SECOND QUESTION IS ONE NOBODY HAS ASKED. BOM E5 puts the knee encoder's diametric magnet
"into the flush counterbore in the knee pin head", and 210_flush.py recesses that head flush at
Z = 126 so the AS5048A can sit over it. THE PIN IS THE MAGNET'S CARRIER. AMS's own guidance for
the AS5048/AS5047 family is to mount the magnet on a NON-FERROMAGNETIC shaft, because a magnetic
one becomes a flux return path and distorts the field the sensor is trying to measure.

    ISO 8734 hardened dowel     martensitic       ferromagnetic
    ISO 7379 shoulder screw     alloy steel       ferromagnetic
    316 austenitic stainless    non-magnetic      mu_r about 1.005

So the part the BOM asks for is the wrong material for the job the BOM gives it, and the part
being proposed is the right one. That is worth more than the hardness is.

    python scripts/451_knee_pin.py
"""
import math

D = 12.0
LUG1 = (70.0, 76.0)             # 418_knee_bearing.py
YOKE = (76.0, 88.0)
LUG2 = (88.0, 113.0)
BRG = (80.0, 88.0)              # the 6001 is where the load actually enters the pin

R_CAP = 29 * 8.0 / (2 * math.pi)
TAU_KNEE = 28.2
F_DIFF = TAU_KNEE * 1000.0 / R_CAP
T_TIGHT = 1828.0 / 2.0
T_SLACK = T_TIGHT - F_DIFF
F_BELT = T_TIGHT + T_SLACK      # 180 deg wrap: both strands pull the same way on the axis
F_GROUND = 1472.0               # 501_interface.py's load-to-ground case

# material properties: minimums, not typicals
MATS = [("316 annealed (ASTM A276 min)", 205.0, 515.0, 1.005),
        ("316 cold finished (typical)", 310.0, 620.0, 1.05),
        ("ISO 8734 dowel, 58-62 HRC", 1600.0, 2000.0, 300.0),
        ("ISO 7379 shoulder screw", 900.0, 1100.0, 300.0)]

Z_SEC = math.pi * D ** 3 / 32.0
A_SEC = math.pi * D ** 2 / 4.0


def moment(p):
    """simply supported on the two lug centroids, load at the bearing centroid"""
    s1 = (LUG1[0] + LUG1[1]) / 2.0
    s2 = (LUG2[0] + LUG2[1]) / 2.0
    load = (BRG[0] + BRG[1]) / 2.0
    span = s2 - s1
    r1 = p * (s2 - load) / span
    return r1 * (load - s1), span


print("=" * 98)
print("1.  WHAT THE PIN CARRIES")
print("=" * 98)
print("  belt resultant on the capstan  %.0f N   (tight %.0f + slack %.0f, a 180 deg wrap, both"
      % (F_BELT, T_TIGHT, T_SLACK))
print("                                          strands pulling the same way on the axis)")
print("  load-to-ground case            %.0f N   (501_interface.py)" % F_GROUND)
print("  worst case, taken as the sum   %.0f N   -- they are not collinear, so this is"
      % (F_BELT + F_GROUND))
print("                                          pessimistic on purpose")
print()
_, span = moment(1.0)
print("  double shear: lugs at Z %.0f..%.0f and %.0f..%.0f, load at the 6001 at Z %.0f..%.0f,"
      % (LUG1[0], LUG1[1], LUG2[0], LUG2[1], BRG[0], BRG[1]))
print("  so the span between supports is %.1f mm. Section modulus of a dia %.0f pin is %.1f mm3."
      % (span, D, Z_SEC))

print()
print("=" * 98)
print("2.  STRESS, AND THE MARGIN EACH MATERIAL LEAVES")
print("=" * 98)
print("  %-30s %9s %9s %10s %10s" % ("", "load N", "bending", "shear", ""))
cases = [("belt only", F_BELT), ("ground only", F_GROUND), ("both, summed", F_BELT + F_GROUND)]
worst = 0.0
for label, p in cases:
    m, _ = moment(p)
    sb = m / Z_SEC
    ss = p / (2 * A_SEC)
    worst = max(worst, sb)
    print("  %-30s %8.0f %7.1f MPa %7.1f MPa" % (label, p, sb, ss))
print()
print("  %-32s %10s %10s %12s" % ("", "yield MPa", "factor", "magnetic?"))
for name, yld, uts, mu in MATS:
    tag = "non-magnetic" if mu < 1.2 else "FERROMAGNETIC"
    flag = ""
    if yld / worst < 2.5:
        flag = "   <-- thin"
    print("  %-32s %9.0f %9.1fx %13s%s" % (name, yld, yld / worst, tag, flag))
print()
print("  The worst case is %.0f MPa of bending. 316 at its ANNEALED minimum leaves a factor of"
      % worst)
print("  %.1f; cold-finished bar, which is what a ground rod actually is, leaves %.1f. A hardened"
      % (205.0 / worst, 310.0 / worst))
print("  dowel leaves %.0f. So this is not a part that is about to break -- but the margin on the"
      % (1600.0 / worst))
print("  correct part is an order of magnitude better, on the one component in the machine whose")
print("  failure drops the leg rather than stopping it.")
print()
print("  Fatigue is the honest worry, not static yield: this pin sees a load cycle every step.")
print("  316's endurance limit is roughly 0.4 x UTS for a polished specimen, about %.0f MPa, and"
      % (0.4 * 515.0))
print("  %.0f MPa is under it -- but that figure assumes no notch, and a counterbore drilled in"
      % worst)
print("  the end for the magnet is a notch. Put a generous radius at its bottom, do not leave a")
print("  flat-bottomed hole with a sharp corner, and polish the bore.")

print()
print("=" * 98)
print("3.  THE MAGNET, WHICH IS THE REAL ARGUMENT")
print("=" * 98)
print("  BOM E5: the diametric magnet goes 'into the flush counterbore in the knee pin head', and")
print("  210_flush.py recessed that head to Z 126 so the AS5048A could sit over it. The pin IS")
print("  the magnet's carrier, and the sensor's own application guidance is to mount a diametric")
print("  magnet on a NON-FERROMAGNETIC shaft: a steel one becomes a flux return path, pulls the")
print("  field asymmetric, and the error shows up as angle error that looks like mechanical play.")
print()
print("  316 is austenitic -- mu_r about 1.005, and still well under 2 even after the cold work")
print("  of centreless grinding. Both parts BOM K2 actually asks for are ferromagnetic.")
print()
print("  This machine already cares about exactly this class of error. BOM S1a rejected a 2020")
print("  rail for the 2040 because the softer one cost 'most of a degree of knee angle the")
print("  encoder cannot see, because it happens past the sensor'. Field distortion is the same")
print("  error arriving from the other direction -- angle the encoder sees that is not there.")

print()
print("=" * 98)
print("4.  THREE THINGS TO CHECK WITH CALIPERS BEFORE YOU TRUST IT")
print("=" * 98)
print("  a. THE DIAMETER, to a hundredth. A 6001's bore is 12 mm to about -0/+0.008, and the")
print("     inner race has to be a snug fit or it frets and the joint develops play the encoder")
print("     reads as knee angle. 'Round metal rods' are often +-0.05, which is six times the")
print("     tolerance band. Measure at both ends and the middle. Undersize cannot be fixed.")
print("  b. WHETHER IT IS MAGNETIC. Put a magnet on it. 316 should be almost indifferent; if it")
print("     grabs, the bar is not 316 whatever the listing says, and the whole argument above")
print("     evaporates. This is a 5-second test that settles the material question outright.")
print("  c. RETENTION, WHICH IT HAS NONE OF. An ISO 7379 shoulder screw holds itself in with a")
print("     head and a nut. A plain rod walks. It needs either a circlip groove at each end, or")
print("     a head turned on one end and a cross-pin at the other. Decide which BEFORE drilling")
print("     the magnet counterbore, because the counterbore end is the end that has to be the")
print("     head -- the sensor only reads one face of this pin.")
print()
print("  The model's pin spans Z 62..126 = %.0f mm, where BOM K2 says 70. %.0f mm of a 70 mm rod"
      % (126.0 - 62.0, 70.0 - (126.0 - 62.0)))
print("  is left over, which is exactly enough to lose to a circlip groove and a chamfer at each")
print("  end. Buy the pair: the first one is practice for the counterbore.")

print()
print("=" * 98)
print("  VERDICT: yes, buy it -- and for a better reason than price. Then update BOM K2, because")
print("  'hardened dowel' and 'carries the encoder magnet' were never compatible requirements")
print("  and nothing in this repository had noticed.")
