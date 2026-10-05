# -*- coding: utf-8 -*-
"""What the knee joint should be, if cheap CNC hardware is allowed to do the work.

Asked at the bench: "there are a lot of super cheap bearing and coupling options from the cnc
world we could lean on here to get the petg parts where they need to be. Dig into what would be
ideal."

FIRST, A CORRECTION TO MY OWN FRAMING. I told you 88 mm across the concept was worse than today's
81 and that width was the thing to settle. Measured properly, width is NOT what the joint decides:

    the rail's nearest corner is 90.2 mm from the limb axis and the thigh reaches r 84.3
    the belt runs in the same band, Z 96..126
    the knee's surface is Z 52 and the outermost hardware is Z 133

So of the 81 mm of stand-off, 30 mm is belt, 7 mm is shroud, and the belt's position is fixed by
the RAIL having to clear an 84 mm thigh -- not by anything at the joint. No bearing arrangement
moves it. What the joint decides is the other 44 mm: Z 52..96, which exists for one reason only.

THE 6001 IS 27 mm INBOARD OF THE BELT IT CARRIES. That single offset is why P2a_KneeHingePlate
spans Z 68..126 and weighs 148 cm3 -- it is a 58 mm deep part whose whole job is to reach from
the belt, where the load is, to the bearing, where the support is. Put the bearings UNDER THE
BELT and that 44 mm of reaching stops existing.

AND THE CAPSTAN HAS ROOM. A 29T HTD-8M rim roots at r 32.79, so a bore of dia 65 fits inside the
teeth. Every thin-section bearing in the 69xx series fits in there with wall to spare. The
capstan can BE the bearing housing, which is the whole idea.

    freecadcmd.exe scripts/454_knee_ideal.py
"""
import math

import FreeCAD

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"
PITCH, PLD, TOOTH_H = 8.0, 0.686, 3.45
TEETH = 29
TIP_R = TEETH * PITCH / (2 * math.pi) - PLD
ROOT_R = TIP_R - TOOTH_H
BELT_W = 30.0
F_BELT = 1064.0                 # tight + slack on a 180 deg wrap
TAU_KNEE = 28.2
PETG_BOND = 10.0                # MPa, structural methacrylate, conservative
PETG_BEARING = 40.0

# bore, OD, width, rough static rating kN, how easy the matching SHAFT and SHF holder are to get
# (VENDOR FIGURES MUST BE CHECKED -- the ratings are indicative, read off the series not a part)
BEARINGS = [
    ("6805", 25, 37, 7, 1.6, "everywhere"), ("6905", 25, 42, 9, 2.6, "everywhere"),
    ("16005", 25, 47, 8, 3.0, "everywhere"), ("6806", 30, 42, 7, 2.3, "common"),
    ("6906", 30, 47, 9, 4.0, "common"), ("6807", 35, 47, 7, 2.7, "rare"),
    ("6907", 35, 55, 10, 5.2, "rare"), ("6808", 40, 52, 7, 3.4, "rare"),
]
MIN_WALL = 8.0          # mm of PETG between the bearing OD and the tooth roots
MIN_TILT_SF = 1.5       # on the belt-offset tilting moment

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}
hub = g["P2a_KneeHingePlate"].Shape
belt = g["A5b_Belt_DriveRun"].Shape.BoundBox
brg = g["HW_Bearing_6001"].Shape.BoundBox
knee = g["REF_Knee"].Shape.BoundBox
shroud = g["P20_KneeShroud"].Shape.BoundBox

print("=" * 98)
print("1.  WHAT THE 27 mm OFFSET COSTS TODAY")
print("=" * 98)
hb = hub.BoundBox
off = (belt.ZMin + belt.ZMax) / 2 - (brg.ZMin + brg.ZMax) / 2
print("  belt centre Z %.0f, 6001 centre Z %.0f  ->  %.0f mm of offset"
      % ((belt.ZMin + belt.ZMax) / 2, (brg.ZMin + brg.ZMax) / 2, off))
print("  P2a_KneeHingePlate spans Z %.0f..%.0f (%.0f mm) and is %.1f cm3 -- about %.0f g of PETG"
      % (hb.ZMin, hb.ZMax, hb.ZLength, hub.Volume / 1000.0, hub.Volume / 1000.0 * 1.27))
frac = BELT_W / hb.ZLength
print("  Only %.0f mm of that %.0f is doing transmission work. The rest is reach."
      % (BELT_W, hb.ZLength))
print("  A hub that spans the belt alone would be of order %.0f cm3 -- %.0f g saved."
      % (hub.Volume / 1000.0 * frac, hub.Volume / 1000.0 * (1 - frac) * 1.27))
print()
print("  And the tilting moment that offset creates has to go somewhere: %.0f N x %.0f mm is"
      % (F_BELT, off))
print("  %.1f N.m, carried from the belt to the bearing by two PRINTED bores on a dia 12 pin."
      % (F_BELT * off / 1000.0))
print("  It is shared with the shank rail, which sits near the belt plane, so this is not the")
print("  bearing's load alone -- but every newton of it passes through printed plastic.")

print()
print("=" * 98)
print("2.  WHAT FITS INSIDE THE CAPSTAN")
print("=" * 98)
print("  29T HTD-8M roots at r %.2f, so the usable bore is dia %.1f." % (ROOT_R, 2 * ROOT_R))
print("  Two bearings fit across the belt's %.0f mm width. Spacing them to the ends of it gives" % BELT_W)
print("  the longest possible couple arm, which is what reacts tilt.")
print()
demand = F_BELT * off / 1000.0
print("  %-8s %-14s %7s %6s %9s %9s %8s  %s"
      % ("", "size", "wall", "arm", "tilt N.m", "vs %.0f" % demand, "bond", "shaft + SHF"))
ok = []
for name, bore, od, w, c0, avail in BEARINGS:
    wall = ROOT_R - od / 2.0
    arm = BELT_W - w                       # centre to centre with both flush to the ends
    cap_m = c0 * 1000.0 * arm / 1000.0      # N.m before either bearing reaches its static rating
    bond = (F_BELT / 2.0) / (math.pi * od * w)
    sf = cap_m / demand
    flag = ""
    if wall < MIN_WALL:
        flag = "  <-- wall"
    elif sf < MIN_TILT_SF:
        flag = "  <-- capacity"
    elif avail == "rare":
        flag = "  <-- sourcing"
    else:
        ok.append((name, cap_m, bore, od, w, arm, wall, sf))
    print("  %-8s %-14s %6.1f %6.0f %8.0f %8.1fx %7.2f  %-10s%s"
          % (name, "%dx%dx%d" % (bore, od, w), wall, arm, cap_m, sf, bond, avail, flag))
print()
print("  THE CRITERION IS NOT CAPACITY. Sorting on tilt capacity alone picks the 6907, which has")
print("  the thinnest wall (%.1f mm) on the least-stocked shaft size. The demand is %.0f N.m and"
      % (ROOT_R - 55 / 2.0, demand))
print("  it is SHARED with the shank rail, which sits in the belt plane -- so anything past about")
print("  %.1fx is capacity nobody collects. Wall thickness and sourcing decide it." % MIN_TILT_SF)
print()
best = ok[0]
for r in ok:
    if r[6] > best[6]:                      # thickest wall among the survivors
        best = r
print("  %s is the pick: dia %d bore -- THE universally stocked linear-shaft size, so the shaft,"
      % (best[0], best[2]))
print("  the SHF holder, the shaft collars and the bearing are all shelf items -- %.1f mm of PETG"
      % best[6])
print("  wall to the tooth roots, and %.0f N.m of tilt against %.0f demanded, a factor of %.1f."
      % (best[1], demand, best[7]))
print("  Step up to the 6906 on dia 30 if the vendor's real static rating comes in under mine.")
print()
print("  BOND the outer races, do not press them. 418_knee_bearing.py's rule stands -- 'the")
print("  plastic creeps under hoop stress and the interference is gone within months' -- but the")
print("  bond is easy here: %.0f N over pi x %d x %d mm2 is %.2f MPa against a methacrylate's %.0f."
      % (F_BELT / 2, best[3], best[4], (F_BELT / 2) / (math.pi * best[3] * best[4]), PETG_BOND))

print()
print("=" * 98)
print("3.  WHAT CARRIES THE INNER RACES -- and this is where the CNC catalogue pays")
print("=" * 98)
print("  The bearings need a journal belonging to the THIGH, poking into the capstan. That is a")
print("  short cantilever, and there is a stock part for exactly it:")
print()
print("     SHF%d  'shaft holder, flange type'  -- an aluminium flange that bolts flat to a plate"
      % best[2])
print("            and clamps a shaft sticking out PERPENDICULAR to it. ~$8.")
print("     dia %d hardened, ground, chromed linear shaft, h6 -- the size every printer and"
      % best[2])
print("            router uses, so it is the cheapest precision cylinder you can buy. ~$10/100mm.")
print()
cant = BELT_W / 2.0 + 5.0
z_mod = math.pi * best[2] ** 3 / 32.0
print("  cantilever: the stub roots at the thigh plate and the belt's %.0f N lands %.0f mm out."
      % (F_BELT, cant))
print("  dia %d section modulus %.0f mm3 -> %.0f N.mm / %.0f = %.1f MPa in a hardened shaft."
      % (best[2], z_mod, F_BELT * cant, z_mod, F_BELT * cant / z_mod))
print("  Against the dia 12 pin's %.0f MPa in 451_knee_pin.py. The pin stops being a structural"
      % 99.0)
print("  concern entirely, and it stops needing to be non-magnetic, hardened, retained or ground")
print("  to a bearing fit -- it is a bought shaft that already is all four.")

print()
print("=" * 98)
print("4.  WHERE THE THIGH PLATE GOES, WHICH IS THE ONLY WIDTH DECISION LEFT")
print("=" * 98)
print("  OUTBOARD (Z %.0f..%.0f): simple, and the stand-off grows from %.0f mm to %.0f."
      % (belt.ZMax, belt.ZMax + 10, shroud.ZMax - knee.ZMax, belt.ZMax + 10 - knee.ZMax))
print("  INBOARD  (Z %.0f..%.0f): sits in space P2a currently fills anyway, the stub cantilevers"
      % (belt.ZMin - 10, belt.ZMin))
print("     outboard through the capstan, and the stand-off stays %.0f mm while Z %.0f..%.0f"
      % (shroud.ZMax - knee.ZMax, knee.ZMax, belt.ZMin - 10))
print("     -- %.0f mm of it -- empties out completely." % (belt.ZMin - 10 - knee.ZMax))
print()
print("  INBOARD, and the reason is not width: it is that the thigh plate then sits between the")
print("  belt and the leg, where the yoke already is, so P1_KneeYoke keeps its job and its bolt")
print("  pattern instead of being redrawn as the clevis 453 said the two-block concept needs.")

print()
print("=" * 98)
print("5.  THE FOUR LAYOUTS, SIDE BY SIDE")
print("=" * 98)
print("  %-34s %7s %7s %8s %9s %8s"
      % ("", "bought", "printed", "pin", "stand-off", "cost"))
rows = [
    ("A  today: dia 12 pin + one 6001", "1 brg", "hub+yoke", "yes", 81, 13),
    ("B  concept: dia 12 rod + 2 KFL001", "2 blk", "stack", "yes", 88, 25),
    ("C  two %s in the capstan" % best[0], "2brg+SHF", "capstan", "no", 81, 30),
    ("D  C, but one bearing only", "1brg+SHF", "capstan", "no", 81, 20),
]
for name, b, pr, pin, so, cost in rows:
    print("  %-34s %8s %8s %7s %7d mm %6d$" % (name, b, pr, pin, so, cost))
print()
print("  A is what exists. B fixes the bearing but keeps a pin in bending and widens the joint.")
print("  C deletes the pin, the bonded seat, the printed lug bores and 44 mm of reach, for the")
print("  price of one more bearing than B and no new structure -- the yoke stays a yoke.")
print("  D is C with the tilt couple halved; worth it only if the %s turns out unobtainable."
      % best[0])

print()
print("=" * 98)
print("  WHAT I WOULD BUILD")
print("=" * 98)
print("     2 x %s bonded into the capstan's dia %d bore, flush to each face" % (best[0], best[3]))
print("     1 x dia %d hardened ground linear shaft, about %.0f mm long" % (best[2], BELT_W + 25))
print("     1 x SHF%d flange clamp, bolted to P1_KneeYoke's outer face" % best[2])
print("     a shoulder and a shaft collar to locate the inners; bond only the outers")
print()
print("  The capstan grows a dia %d bore and loses 44 mm of reach. The yoke grows a 4-bolt SHF"
      % best[3])
print("  pattern. The pin, its counterbore, its collars, its retention and its magnet carrier all")
print("  disappear -- and so do BOM lines K2, K2a, K2b and the argument about 316 versus hardened.")
print("  The encoder magnet goes in the END of the stub, which is stationary, reading a magnet")
print("  carrier on the rotating capstan instead -- or the reverse. Either way it is a flat face")
print("  on the axis, which is what 210_flush.py was trying to make out of a pin head.")
print()
print("  CHECK FIRST: the real static ratings from the vendor, SHF%d's actual flange size against"
      % best[2])
print("  the yoke, and whether a dia %d shaft and a %s are both stocked where you buy."
      % (best[2], best[0]))
