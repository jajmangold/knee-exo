# -*- coding: utf-8 -*-
"""The knee pivot: what bearing, where, and what it is worth. A decision, with its numbers.

Raised by asking whether HW_PinB_M12_KneePin is an off-the-shelf part. It is -- ISO 7379 12 x 70,
or an ISO 8734 dowel -- but the question exposed that BOM K3's two M12 flanged bushings have
nowhere to sit: the knee axis carries three 12.3 mm bores, which is clearance for a bare pin, and a
12 mm-bore bushing needs a 14-16 mm seat. As drawn, a steel pin runs directly in printed PETG.

The argument for fixing it is NOT strength. PETG at 2.5 MPa of bearing pressure is fine statically.
It is friction, and specifically friction the patient feels when the motor is off -- the property
this entire drivetrain was sized around (reflected inertia 0.22x the limb's, 300_drivetrain.py).

    freecadcmd.exe scripts/801_knee_bearing.py       (arithmetic only, no document needed)
"""
import math

N_BELT = 764.0          # N, capstan differential at peak torque (BOM K1)
R_PIN = 0.006           # m, 12 mm pin
TAU = 28.2              # N.m at the knee

print("=" * 92)
print("1.  WHY A BEARING AT ALL: what each option costs in friction the patient fights")
print("=" * 92)
print("  %-30s %8s %12s %10s" % ("", "mu", "N.m at joint", "% of 28.2"))
for name, mu in (("printed PETG journal (as drawn)", 0.30),
                 ("igus plain bushing (BOM K3)", 0.15),
                 ("bronze, greased", 0.10),
                 ("sealed deep-groove ball", 0.0015)):
    t = mu * N_BELT * R_PIN
    print("  %-30s %8.4f %10.3f   %9.1f%%" % (name, mu, t, 100 * t / TAU))
print()
print("  The percentages understate it. A 0.69 N.m deadband is not 2.4%% of the assist, it is a")
print("  stiff hinge on a limb that is supposed to swing freely when the device is off -- and")
print("  a post-operative knee is exactly the case where that matters. 100x is the whole")
print("  argument; the strength numbers below are all comfortable either way.")

print()
print("=" * 92)
print("2.  WHERE IT GOES. Not where the BOM says, and not where splitting the hub would put it.")
print("=" * 92)
print("  The hub STRADDLES the yoke:  hub lug Z 70..76 | yoke Z 76..88 | hub lug Z 88..113")
print()
print("  Measured twice, by ray section and by point marching, both agreeing: at Z 82 the yoke is")
print("  solid from r 6.5 out to r 43..55 at every one of 18 bearings. No window, no fork.")
print("  The pulley rim is at r 35.5. So EVERY radius inside the pulley is inside the yoke:")
print("  two hub halves cannot be bolted to each other past it. They would have to sit on the")
print("  same side, turning the straddle into a cantilever and the bearing span from 37 mm to 19.")
print()
print("  Which is moot, because the straddle is the reason to put the bearing in the YOKE:")
print("  the load arrives symmetrically about it, so one centred bearing sees no cocking moment,")
print("  where two in the hub would spend their span fighting one.")
print()
print("  yoke bore today: dia 12.3 x 12 mm, with material out to r 43 around it")
print("  %-6s %-10s %7s %7s %10s %s" % ("", "OD x W", "C0 N", "SF", "shoulder", "verdict"))
for nm, od, w, c0 in (("6801", 21, 5, 1180), ("6901", 24, 6, 1500), ("6001", 28, 8, 2400)):
    sf = c0 / N_BELT
    print("  %-6s %2d x %-5d %7d %7.1f %7d mm  %s"
          % (nm, od, w, c0, sf, (12 - w) // 2,
             "the pick: SF 3.1 and still 29 mm of wall" if nm == "6001" else
             "workable" if sf >= 2.0 else "too little margin for a joint that must not develop play"))
print()
print("  PRESS FITS DO NOT HOLD IN PETG. The plastic creeps under hoop stress and thermal")
print("  cycling and the interference is gone within months. Bond the seat instead -- structural")
print("  methacrylate or epoxy, or bond a thin aluminium sleeve in and press the bearing into")
print("  that. It is the same move as a square tube bonded into a printed gear hub: put metal")
print("  where the plastic is not being asked to hold the load.")

print()
print("=" * 92)
print("3.  SPLITTING THE HUB IS STILL WORTH DOING -- for printing and marking, not for the bearing")
print("=" * 92)
BOLTS, R_CIRCLE = 5, 0.022
f_tan = TAU / R_CIRCLE
print("  P2a is a 29T capstan AND a 165 mm hinge plate in one part: 143 cm3, 185 mm tall, the")
print("  tallest thing in the set, 10.6 h and 10.5%% support. Split at the capstan/plate junction")
print("  and both halves lie flat with the teeth as vertical walls.")
print()
print("  The joint then carries the full %.1f N.m:" % TAU)
print("    %d x M5 on a %.0f mm circle -> %.0f N tangential, %.0f N per bolt in shear"
      % (BOLTS, R_CIRCLE * 1000, f_tan, f_tan / BOLTS))
print("    bearing on the plastic: %.1f MPa over a 5 x 8 mm hole -- fine"
      % (f_tan / BOLTS / (5.0 * 8.0)))
print("    or drive it by FRICTION: %.1f kN of clamp per bolt at mu 0.3 gives %.0f N.m each,"
      % (1.3, 0.3 * 1300 * R_CIRCLE))
print("    which wants heat-set inserts and steel washers so the preload is not crushing PETG.")
print()
print("  NOT across the belt face. The capstan is 30 mm wide and the belt rides on it; a seam at")
print("  mid-width needs the two tooth sets aligned within about 0.1 mm or the belt climbs a step")
print("  every revolution, and a bolt circle will not hold that -- it would need dowels.")
print()
print("  The bonus is that P2a is the ONE part of fifteen with no engraved number: 16 stations x")
print("  36 bearings found nowhere hidden on it (412_engrave.py). A split makes two mating faces,")
print("  which are hidden by definition, and the set becomes 15 of 15.")

print()
print("=" * 92)
print("4.  SO")
print("=" * 92)
print("  a. DONE. 6001 in the yoke, bore 12.3 -> 28H7, bonded not pressed, pin clamped through")
print("     both hub lugs -- the retention already modelled. 418_knee_bearing.py, both legs.")
print("  b. DONE. K3's bushings are out of the BOM; the 6001 replaces them.")
print("  c. DONE. K2 reads ISO 7379 12 x 70 (shoulder 12 h8, thread M10) or an ISO 8734 dowel.")
print("  d. Splitting P2a was overtaken by a better idea, and this is where the thinking went:")
print()
print("     Why not a large-bore bearing and no pin at all? Three layouts, and the number that")
print("     decides it is where the belt pulls relative to where the bearing sits:")
print()
print("       one 6815 (75x95x10) beside the teeth   dia 75 is bigger than the 71.1 tooth tips")
print("                                              and lands inside the belt band (r 35.6..41.1),")
print("                                              so the bearing ends up ~20 mm off the belt")
print("                                              plane: 764 N x 0.020 = %.1f N.m on one raceway"
      % (764 * 0.020))
print("       a fork, two 6815                       symmetric, 382 N each, no moment -- but two")
print("                                              dia 95 seats that must be coaxial in printed")
print("                                              parts, and one race free to float axially")
print("       one 6808 (40x52x7) INSIDE the pulley   the tooth root circle is dia 64.3, so a")
print("                                              bearing under ~62 nests inside the ring and")
print("                                              the belt pulls straight through its plane")
print()
print("     The third is modelled in 419_knee_coaxial.py: no interference, full belt land, 107")
print("     poses clean, 47 g lighter, and a hollow dia 20 through the knee for cabling. It is")
print("     NOT built -- it still needs coverage, printability, engraving and the mirror, and")
print("     KneeExo_v6 is the print-ready design today.")
