# -*- coding: utf-8 -*-
"""Laying out the one-screw drive, and the two things that fall out of doing it properly.

380_one_screw.py proved the kinematics and then got two things wrong by reasoning about
the belt as a STRIP with two clamped ends instead of what it actually wants to be:

  1. If the idler is the SAME 29T pulley as the capstan and sits on the centreline, the
     two straight runs land at exactly X = +/-36.92 -- the band the belt already occupies.
     The idler stops being a new part and becomes a second copy of the knee pulley, and
     the belt envelope does not change at all. 380's 86 mm idler was solving a problem
     created by putting the idler in the wrong place.

  2. The added belt is NOT in series with the load. Both strands connect the carriage to
     the capstan, so they are in PARALLEL, and the short direct strand dominates the
     stiffness. 380 charged this architecture 0.8-2.2 deg of lost motion. The real figure
     is about a tenth of that. That was the main objection to the idea and it was an
     error, not a finding.

Then the section question: with only one carriage and the screw off the centreline, can
the 20x60 drop to a 20x40 and the MGN7 rails go back to V-wheels?

Run:  python scripts/390_onescrew_section.py
"""
import math

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)     # 36.924 mm, capstan AND idler
BIN, BOUT = R - 1.372, R + 4.2        # 35.55 .. 41.12, belt band, from 194_layout.py
BELT_T = BOUT - BIN
T_HI, T_LO = 914.0, 150.0
F_DIFF = T_HI - T_LO
STROKE = R * math.radians(106.0)
DEG_PER_MM = math.degrees(1.0 / R)
NUT_R = 18.0
WHEEL_MINI, WHEEL_SOLID = 15.23, 23.89
MGN7_RAIL, MGN7_BLK = 4.8, 8.0        # proud of the mounting face

print("=" * 78)
print("1. THE IDLER IS THE KNEE PULLEY AGAIN, AND THE BELT BECOMES A CLOSED LOOP")
print()
print("   Put a second 29T pulley on the centreline at X = 0. The belt leaves the")
print("   capstan tangentially at X = +%.2f, wraps the idler 180 deg, and comes back" % R)
print("   down at X = -%.2f. Two straight strands at exactly +/-%.2f -- the band the" % (R, R))
print("   belt already lives in. Nothing moves in X.")
print()
print("   The carriage clamps ONE strand. Below the clamp that strand runs to the")
print("   capstan; above it, to the idler. They share an X band and never share Y, so")
print("   there is no collision -- they meet only at the clamp.")
print()
print("   Which makes the belt a plain CLOSED LOOP over two equal pulleys with the")
print("   carriage clamped to one strand. Loop length = 2*pi*R + 2*Y_i, independent of")
print("   where the carriage is, so the loop imposes no constraint at all: move the")
print("   clamp by d and the belt circulates by d, turning both pulleys by d/R.")
print()
print("   ratio       2*pi*R/lead = %.1f:1 at SFU1610 -- unchanged" % (2 * math.pi * R / 10.0))
print("   engagement  180 deg on each pulley = %.1f teeth -- unchanged" % (TEETH / 2.0))
print("   parts       the idler is the SAME 29T HTD-8M pulley as the knee. One fewer")
print("               unique part in the build, not one more.")
print("   tensioning  a closed loop is tensioned by moving the IDLER centre, which is a")
print("               slotted mount. That retires P11_SprungAnchor and P13_HallTension")
print("               as belt-end hardware and moves both jobs to the idler carrier.")

print("=" * 78)
print("2. THE LOST-MOTION ERROR IN 380, CORRECTED")
print()
print("   Both strands join the carriage to the capstan, so as springs they are in")
print("   PARALLEL:  k = EA/L_direct + EA/L_long.")
print()
Y_I = 275.0
YA_MID = 117.0
L_DIR = YA_MID
L_LONG = Y_I + (Y_I - YA_MID) + math.pi * R
TODAY_A, TODAY_B = 128.0, 114.0       # A5b, A5c run lengths from the live model
print("   today   two direct runs, %.0f and %.0f mm" % (TODAY_A, TODAY_B))
print("   one-screw   direct strand %.0f mm, long strand %.0f mm" % (L_DIR, L_LONG))
print("               (clamp at Y %.0f, idler at Y %.0f, %.0f mm of wrap)"
      % (YA_MID, Y_I, math.pi * R))
print()
print("   %-10s %13s %13s %11s %11s" % ("belt EA", "today", "one-screw", "stretch", "knee"))
for EA in (150e3, 300e3, 400e3):
    k0 = EA / TODAY_A + EA / TODAY_B
    k1 = EA / L_DIR + EA / L_LONG
    d0, d1 = F_DIFF / k0, F_DIFF / k1
    print("   %7.0f kN %9.0f N/mm %9.0f N/mm %8.3f mm %8.3f deg   (+%.3f deg)"
          % (EA / 1e3, k0, k1, d1, d1 * DEG_PER_MM, (d1 - d0) * DEG_PER_MM))
print()
print("   The long strand is ~%.1fx the direct one, so it carries almost none of the"
      % (L_LONG / L_DIR))
print("   differential and the compliance barely moves. Against the %.2f deg the sprung"
      % 2.45)
print("   anchor spends deliberately, this is noise. 380's objection is withdrawn.")
print()
print("   It also helps that a longer, softer loop is LESS sensitive to thermal and")
print("   creep changes in pretension than two short anchored runs.")

print("=" * 78)
print("3. WHERE THE ONE SCREW GOES  --  and why it is not the centreline")
print()
print("   The obvious move is a standard V-slot actuator: screw down the middle of the")
print("   lateral face at X = 0. It cannot be done here, and the idler is the reason --")
print("   the idler is already at X = 0, spanning Z %.0f..%.0f with the belt." % (96, 126))
print("   A nut at X = 0 would have to sit above it at Z %.0f..%.0f, putting the fairing"
      % (126 + 0, 126 + 2 * NUT_R))
print("   at Z %.0f and standing %.0f mm proud of the knee against %.0f today."
      % (126 + 2 * NUT_R + 12, 126 + 2 * NUT_R + 12 - 52, 86))
print("   That is +%.0f mm in the one direction 330_frontmount.py measured as fully"
      % (126 + 2 * NUT_R + 12 - 52 - 86))
print("   exposed. So the screw stays beside the rail, and the lateral stack is")
print("   untouched at %.0f mm proud." % 86)
print()
print("   But it has to move OUTBOARD a little. Today the nut at X = -58 overlaps the")
print("   belt band by %.2f mm in X and gets away with it only because the nut never"
      % (BOUT - (58 - NUT_R)))
print("   shares Y with the belt run -- 311_nut_belt.py's whole point. The return strand")
print("   runs PAST the nut to the idler, so that escape is gone:")
print()
print("   %-12s %16s %12s" % ("screw X", "nut spans X", "vs belt %.2f" % BOUT))
for sx in (58.0, 60.0, 62.0, 64.0):
    gap = (sx - NUT_R) - BOUT
    print("   %8.0f %12.1f..%.1f %10s" % (-sx, -(sx + NUT_R), -(sx - NUT_R),
          "FOULS %.2f" % -gap if gap < 0 else "clear %.2f" % gap))
SCR_X = 62.0
print("   -> X = -%.0f. %.2f mm of clearance, and %.0f mm further out than today." % (
      SCR_X, (SCR_X - NUT_R) - BOUT, SCR_X - 58.0))

print("=" * 78)
print("4. 20x60 -> 20x40, AND WHICH GUIDE ACTUALLY FITS")
print()
print("   A V groove seats the extrusion's corner APEX at the bottom of the groove, so the")
print("   wheel centre stands off along the 45 deg bisector by groove_minor/2 -- it does")
print("   NOT sit on the corner, which is what 320_rail_section.py assumed. That matters:")
print()
print("   %-11s %6s %9s %9s %11s   %s" % ("wheel", "OD", "groove", "centre", "outer |X|",
                                          "vs belt %.2f" % BIN))
for nm, od, gr in (("mini V", WHEEL_MINI, 9.5), ("solid V", WHEEL_SOLID, 15.9)):
    for w in (60.0, 40.0):
        cx = w / 2.0 + (gr / 2.0) / math.sqrt(2.0)
        hi = cx + od / 2.0
        print("   %-11s %6.2f %8.1f %8.2f %10.2f   %s on a 20x%.0f"
              % (nm, od, gr, cx, hi,
                 "clears %.2f" % (BIN - hi) if hi <= BIN else "FOULS %.2f" % (hi - BIN), w))
print()
print("   So the honest answer is narrower than hoped: the 2040 makes a wheeled gantry")
print("   POSSIBLE, but only with MINI wheels. The solid wheel fouls the belt even on a")
print("   2040, and 320's table saying both fit is wrong.")
print()
print("   And section 5 puts %.0f N on each wheel at peak torque. That is a lot for a"
      % 362.0)
print("   Delrin mini wheel, and its rating is the one number here I do not have -- it")
print("   needs the supplier's figure, not an estimate.")
print()
print("   Meanwhile MGN7 on the 2040's SIDE faces is now comfortable where it was")
print("   marginal on the 2060:")
print("     on a 2060   rail reaches |X| %.1f, block %.1f -> %.2f mm to the belt"
      % (30 + MGN7_RAIL, 30 + MGN7_BLK, BIN - (30 + MGN7_BLK)))
print("     on a 2040   rail reaches |X| %.1f, block %.1f -> %.2f mm to the belt"
      % (20 + MGN7_RAIL, 20 + MGN7_BLK, BIN - (20 + MGN7_BLK)))
print("   at ~1.0 kN dynamic against a %.0f N reaction, which is %.1fx margin."
      % (362.0, 1000.0 / 362.0))
print()
print("   BUILT WITH MINI V-WHEELS, because they are owned and they do fit. But the")
print("   fallback is real and it is not a rebuild: MGN7 goes on the same 2040, on the")
print("   side faces, and the gantry's web A moves from X -34.5 to clear a block at 28")
print("   instead of a wheel at 31. Decide it on the wheel's load rating.")

print("=" * 78)
print("5. LOADS ON THE ONE CARRIAGE, AGAINST THE TWO IT REPLACES")
print()
X_CLAMP = (BIN + BOUT) / 2.0
print("   The clamp takes the DIFFERENCE of the two strand tensions, not either one,")
print("   because the strands pull it opposite ways: %.0f N, at X = -%.2f."
      % (F_DIFF, X_CLAMP))
print()
# Spacings are AS BUILT (391/392), not aspirational: the two-screw carriage B has its
# blocks 34 mm apart, and the one-screw gantry has its wheels at clamp +/- 25, so 50.
for nm, F, xb, xn, plate, sp in (("today, carriage A", T_HI, X_CLAMP, 58.0, 102.0, 34.0),
                                 ("one screw, 2040", F_DIFF, X_CLAMP, SCR_X, 70.0, 50.0)):
    mz = F * abs(xn - xb) / 1000.0
    print("   %-20s F %3.0f N, dx %4.1f mm -> Mz %4.1f N.m" % (nm, F, abs(xn - xb), mz))
    print("   %-20s reacted over %.0f mm of plate = %3.0f N; guides %.0f mm apart = %3.0f N"
          % ("", plate, mz * 1000 / plate, sp, mz * 1000 / sp))
print()
MZ1 = F_DIFF * abs(SCR_X - X_CLAMP) / 1000.0
print("   The clamp force drops %.0f -> %.0f N because the strands oppose, and the yaw is"
      % (T_HI, F_DIFF))
print("   about the same, %.1f vs %.1f N.m -- the nut moved 4 mm further out, cancelling"
      % (MZ1, T_HI * abs(58.0 - X_CLAMP) / 1000.0))
print("   the lower force. Per guide it is %.0f N against the %.0f N carriage B accepts,"
      % (MZ1 * 1000 / 50.0, T_HI * abs(58.0 - X_CLAMP) / 34.0))
print("   which is better but not the 3x the 100 mm spacing I first assumed: the gantry is")
print("   70 mm long with wheels 50 mm apart, because the wheel footprint has to stay on a")
print("   151 mm rail AND leave the idler room at Y %.0f." % 255.0)
print()
print("   Pushing the wheels to clamp +/- 35 (70 mm apart) drops it to %.0f N, and costs"
      % (MZ1 * 1000 / 70.0))
print("   5 mm off the distal end of the rail -- Y 51 instead of 56. Worth doing if the")
print("   mini wheel's rating turns out tight. Section 4.")
print()
print("   The screw is also less loaded: %.0f N of column load instead of %.0f."
      % (F_DIFF, T_HI))

print("=" * 78)
print("6. MASS, measured off the built model (391-396), not estimated")
# volumes read back out of KneeExo_v4 after the rebuild; densities 2.70 alu, 7.85 steel,
# 1.27 PETG, 1.30 HTD belt per cm3
OLD = [("2x SFU1610 screw, 300 mm", 900.0), ("2x ball nut", 360.0),
       ("P3 + P3b printed carriages", 383.0), ("2x MGN7 rail", 82.0),
       ("4x MGN7H block", 91.0), ("P11 + A8 + P13 tensioner", 14.0),
       ("A1 2060 x 227 mm", 352.0), ("A7 drive box", 201.0),
       ("HTD-8M strip, ~360 mm", 47.0)]
NEW = [("1x SFU1610 screw, 330 mm", 450.0), ("1x ball nut", 180.0),
       ("P3 gantry, 65.0 cm3 alu", 175.0), ("4x mini V-wheel + eccentrics", 60.0),
       ("A6 29T idler + bearings", 120.0), ("A1 2040 x 151 mm", 159.0),
       ("A7 bracket, 172.2 cm3 alu", 465.0), ("HTD-8M loop, 742 mm", 96.0)]
o = sum(m for _, m in OLD); n = sum(m for _, m in NEW)
print("   %-34s %7s   %-34s %7s" % ("two-screw", "g", "one-screw", "g"))
for k in range(max(len(OLD), len(NEW))):
    lo = "%-34s %6.0f" % OLD[k] if k < len(OLD) else " " * 41
    ln = "%-34s %6.0f" % NEW[k] if k < len(NEW) else ""
    print("   %s   %s" % (lo, ln))
print("   %-34s %6.0f   %-34s %6.0f" % ("", o, "", n))
print()
print("   %.0f g off the limb: %.2f kg -> %.2f kg, %.0f%%."
      % (o - n, 4.66, 4.66 - (o - n) / 1000.0, 100 * (o - n) / 4660.0))
print()
print("   But note WHERE it went. Two line items got much heavier:")
print("     A7  %4.0f -> %4.0f g   the idler has to be held against up to %.0f N and the"
      % (201.0, 465.0, 1828.0))
print("                        bracket is now the heaviest fabricated part in the build")
print("     A6     0 -> %4.0f g   a second 29T pulley did not exist before" % 120.0)
print("   Against that, the printed structural carriages are gone entirely -- one bought")
print("   aluminium plate at %.0f g replaces %.0f g of printed PETG doing a structural job"
      % (175.0, 383.0))
print("   it was never well suited to.")
print()
print("   The drive bracket is where the remaining work is. %.0f g of aluminium to react"
      % 465.0)
print("   %.0f N is not obviously wrong, but nothing here is FEA and the 2*T_b winding" % 1828.0)
print("   trick in 394 is the cheapest way to make the number smaller.")
print("=" * 78)
print("7. THE LAYOUT TO BUILD")
print("   extrusion    20x40 V-slot, X +/-20, Z 88..108, Y 58..258  (200 mm, was 227)")
print("   gantry       aluminium V-wheel plate on the Z=108 face, wheels on the |X| 20")
print("                corners, ~100 mm wheel spacing, reaching out to X -84")
print("   screw        ONE SFU1610 RH, X = -%.0f, Z = 106, nut OD %.0f" % (SCR_X, 2 * NUT_R))
print("   idler        29T HTD-8M, X = 0, Y = %.0f, Z 96..126, on a slotted carrier" % Y_I)
print("   belt         closed HTD-8M loop, strands at X = +/-%.2f, clamped to the" % R)
print("                gantry on the -X strand")
print("   motor        belted 1:1 to the screw and sat at X = 0 proximal of the idler,")
print("                which pulls the drive cap in from X -106..84 to about +/-47")
print()
print("   Deletes: A2c, A2d, P3b, A9, A9b, P10a-d, P11, P13, A7. Rebuilds: A1, A2, A2b,")
print("   A5/A5b/A5c, P3, A3, A7, P22. Then 231_verify.py over all 107 poses.")
print("=" * 78)
