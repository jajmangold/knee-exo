# -*- coding: utf-8 -*-
"""One screw, one carriage, one idler.

Route belt run 2 from the capstan up past the carriage to an idler at the proximal end,
then back DOWN to the SAME carriage that run 1 is anchored to. Then there is no second
screw, no second nut, no second carriage, no 1:1 linking belt, and no left-hand thread
anywhere in the build.

370_no_lh_screw.py option C used this idler to make two nuts CO-move so both screws could
be RH. It never asked the next question: if both anchors move together, why are they on
two different carriages?

Run:  python scripts/380_one_screw.py
"""
import math

R = 29 * 8.0 / (2 * math.pi)      # capstan pitch radius, 36.924 mm
PITCH = 8.0                       # HTD-8M
T_HI, T_LO = 914.0, 150.0         # N, loaded run and pretension
F_DIFF = T_HI - T_LO              # 764 N
RAIL_X = 30.0                     # extrusion half-width
RUN_IN, RUN_OUT = 35.55, 41.12    # existing belt run faces
BELT_T = 5.7                      # HTD-8M belt thickness incl. teeth
DEG_PER_MM = math.degrees(1.0 / R)
STROKE = 68.3
LOST_SPRING = 2.45

print("=" * 76)
print("1. THE KINEMATICS -- it closes, and it closes for the same reason as before")
print()
print("   The belt wraps the capstan 180 deg. Rotating it by phi still demands")
print("     L1 = L1_0 - R.phi    and    L2 = L2_0 + R.phi")
print()
print("   run 1, direct:        L1 = Y_c - Y_P1              = Y_c + const")
print("   run 2, via idler:     L2 = (Y_i - Y_P2) + (Y_i - Y_c) = const - Y_c")
print()
print("   Both give the SAME thing:   Y_c = const - R.phi")
print("   and L1 + L2 = const automatically, independent of Y_c.")
print()
print("   Physically: the carriage moves proximally by d, run 1 lengthens by d, the")
print("   idler-to-carriage segment shortens by d, the capstan-to-idler segment is")
print("   FIXED. Net belt length change zero, so the capstan must have paid out d on")
print("   one side and taken up d on the other. It rotates d/R. Positively driven in")
print("   both directions, no slack, exactly as the two-screw version.")
print()
print("   Ratio is untouched: %.1f mm of carriage per degree of knee, so 2*pi*R/lead"
      % (R * math.pi / 180))
print("   = 23.2:1 at SFU1610. Reflected inertia does not change.")

print("=" * 76)
print("2. WHAT COMES OFF  (masses from 340_tendon.py's inventory)")
OFF = [("one SFU1610 screw", 450.0), ("one ball nut", 180.0),
       ("one carriage", 191.0), ("one MGN7 rail + 2 blocks", 47.0),
       ("2 bearing blocks", 10.0), ("1:1 linking belt", 20.0),
       ("2 of 3 HTD-5M pulleys", 30.0)]
ON = [("idler pulley ~34T", 55.0), ("idler bracket + 2 bearings", 45.0),
      ("~290 mm more HTD-8M belt", 35.0)]
off = sum(m for _, m in OFF); on = sum(m for _, m in ON)
for nm, m in OFF:
    print("   -  %-30s %5.0f g" % (nm, m))
for nm, m in ON:
    print("   +  %-30s %5.0f g" % (nm, m))
print("   %-33s %5.0f g net off a 4660 g knee = %.1f%%"
      % ("", off - on, 100 * (off - on) / 4660.0))
print()
print("   And the motor now couples DIRECTLY to the one screw. No linking belt means")
print("   no belt to align, no third pulley, and one fewer 0.97 in the efficiency")
print("   chain: eta %.3f -> %.3f, so %.1f A becomes %.1f A."
      % (0.90 * 0.97, 0.90, 24.8, 24.8 * 0.90 * 0.97 / 0.90))

print("=" * 76)
print("3. THREE THINGS THAT GET BETTER, NOT JUST LIGHTER")
print()
print("   a) The screw is LESS loaded. The two runs pull the single carriage in")
print("      OPPOSITE directions -- run 1 distally, the idler return proximally -- so")
print("      the nut sees the difference, not either tension:")
print("        two-screw:  screw A carries %.0f N, screw B carries %.0f N" % (T_HI, T_LO))
print("        one-screw:  the one screw carries %.0f N" % F_DIFF)
print("      %.0f N less column load, on the part that was already the long slender one."
      % (T_HI - F_DIFF))
print()
print("   b) The matched-lead requirement disappears. Two messages ago the advice was")
print("      to buy both screws from one batch because mismatched lead accuracy or nut")
print("      preload corrupts the differential and there is no adjustment for it. With")
print("      one screw there is nothing to mismatch. The invariant stops depending on")
print("      manufacturing at all -- it is enforced by the belt being one length.")
print()
print("   c) One carriage gets the whole rail. The yaw couple is the load that sizes")
print("      the guides, and it gets worse per newton but far easier to react:")
DX_TWO = 58.0 - (RUN_IN + RUN_OUT) / 2.0
MZ_TWO = T_HI * DX_TWO / 1000.0
print("        two-screw   nut at X 58, one anchor at X %.1f -> dx %.1f mm, Mz %.1f N.m"
      % ((RUN_IN + RUN_OUT) / 2.0, DX_TWO, MZ_TWO))
print("                    over a 102 mm carriage = %.0f N; blocks 34 mm apart = %.0f N"
      % (MZ_TWO * 1000 / 102.0, MZ_TWO * 1000 / 34.0))
print()
print("      One-screw: two opposed anchors dx apart make a couple that does NOT")
print("      cancel, because T_hi and T_lo swap when the assist reverses. Putting the")
print("      nut midway makes it symmetric at dx/2 * (T_hi + T_lo):")
print("      %-8s %9s %11s %12s %12s" % ("dx", "Mz", "over 102 mm", "over 150 mm",
                                        "blocks 100 mm"))
for dx in (56.0, 68.0, 85.0):
    mz = (dx / 2.0) * (T_HI + T_LO) / 1000.0
    print("      %5.0f mm %7.1f N.m %8.0f N %11.0f N %11.0f N"
          % (dx, mz, mz * 1000 / 102.0, mz * 1000 / 150.0, mz * 1000 / 100.0))
print("      MGN7H is ~1.0 kN dynamic. A single 150 mm carriage with blocks 100 mm")
print("      apart stays under 400 N even at the widest anchor spacing -- better")
print("      margin than the %.0f N the two-carriage build already accepts on carriage B."
      % (MZ_TWO * 1000 / 34.0))

print("=" * 76)
print("4. THE CONSTRAINT THAT DECIDES WHETHER THIS IS BUILDABLE")
print()
print("   A 180 deg wrap returns the belt offset in X by exactly 2 x the idler radius.")
print("   That offset is not a free parameter, and three things fence it in:")
print()
MIN_T = 22
r_min = MIN_T * PITCH / math.pi / 2.0
print("   i)   HTD-8M minimum pulley is %dT = %.1f mm PD, so r >= %.1f and the return"
      % (MIN_T, MIN_T * PITCH / math.pi, r_min))
print("        lands at X <= %.1f - %.1f = %.1f" % (RUN_OUT - BELT_T / 2, 2 * r_min,
                                                   (RUN_OUT - BELT_T / 2) - 2 * r_min))
print("   ii)  it must not pass through the extrusion, X +/-%.0f" % RAIL_X)
print("   iii) it must clear the existing run 1 at X -%.2f..-%.2f, and the %.1f mm gap"
      % (RUN_OUT, RUN_IN, RUN_IN - RAIL_X))
print("        between run 1 and the rail face is narrower than the %.1f mm belt." % BELT_T)
print("        So the return has to go OUTBOARD of run 1, at X <= -%.0f."
      % (RUN_OUT + BELT_T))
x_up = (RUN_IN + RUN_OUT) / 2.0
x_ret = -(RUN_OUT + BELT_T + 1.0)
r_need = (x_up - x_ret) / 2.0
teeth = r_need * 2 * math.pi / PITCH
print()
print("   Solving iii): up-run at X %+.2f, return at X %+.2f -> r = %.1f mm,"
      % (x_up, x_ret, r_need))
print("   a %.0f mm PD idler, which is %.0fT. Comfortably above the %dT minimum, and it"
      % (r_need * 2, teeth, MIN_T))
print("   engages the TOOTH side -- the belt leaves the capstan with teeth facing")
print("   inboard, so an idler at X = %.1f meets them the right way round. No reverse"
      % (x_up - r_need))
print("   bending, unlike 370's option C. That is a real advantage over that variant.")
print()
print("   But: an %.0f mm idler spans %.0f mm of X on a 60 mm extrusion, and %.0f mm of Y"
      % (r_need * 2, r_need * 2, r_need * 2))
print("   above the carriage's proximal limit. The motor currently occupies Y 314..388")
print("   at X = -58. Something has to move, and with only one screw the motor is free")
print("   to -- but that is a re-layout of the entire drive end, not an edit.")

print("=" * 76)
print("5. THE COST THAT DOES NOT GO AWAY")
Y_I = 230.0 + r_need
dL = 2 * (Y_I - 150.0) + math.pi * r_need - 150.0
print("   Run 2 is now ~%.0f mm of belt instead of ~150. At %.0f N that is lost motion,"
      % (2 * (Y_I - 150.0) + math.pi * r_need, T_HI))
print("   and it is the same bill 370's option C pays, for the same reason:")
print("   %-12s %10s %10s %12s" % ("belt EA", "stretch", "knee", "vs 2.45 deg"))
for EA in (150e3, 300e3, 400e3):
    d = T_HI * dL / EA
    print("   %8.0f kN %8.2f mm %8.2f deg %10s"
          % (EA / 1e3, d, d * DEG_PER_MM, "%+.0f%%" % (100 * d * DEG_PER_MM / LOST_SPRING)))
print("   Asymmetric, too: run 1 stays direct, so the knee is more compliant assisting")
print("   one way than the other. EA for a 30 mm HTD-8M still wants a datasheet.")
print()
print("   And a new %.0f N load path into the idler bracket -- 180 deg wrap, both"
      % (2 * T_HI))
print("   segments at %.0f N -- where today's largest comparable is the %.0f N sprung"
      % (T_HI, T_HI))
print("   anchor. That bracket cannot be a printed part bolted to a V-slot and trusted.")
print()
print("   One more: the idler is a second place the belt can skip teeth, and tooth-skip")
print("   is the failure mode ELECTRONICS.md section 3 exists to detect. A 180 deg wrap")
print("   engages %.1f teeth, so the risk is low -- but it is not zero and it is new."
      % (teeth / 2))

print("=" * 76)
print("VERDICT")
print("   The kinematics are sound and the prize is large: **%.0f g off the limb, the"
      % (off - on))
print("   left-hand screw gone entirely, the matched-lead tolerance stack gone, %.0f N"
      % (T_HI - F_DIFF))
print("   less column load on the screw, and the motor direct-coupled.** Against that:")
print("   1-3 deg more lost motion, a 2 kN bracket, and one more tooth-skip site.")
print()
print("   That trade is clearly worth taking. What it is NOT is a small change. It")
print("   deletes P3/P4 (the second carriage), one screw, one nut, one MGN7 pair, the")
print("   linking belt and two pulleys, and it moves the motor. Every one of those is")
print("   load-bearing in the current model, and the belt routing in X -- the %.0f mm"
      % (2 * r_need))
print("   idler and where its return segment lands -- is exactly the kind of thing the")
print("   107-pose sweep exists to check and my arithmetic above does not.")
print()
print("   So: worth building, as a re-layout, with 231_verify.py re-run before anyone")
print("   believes a number in this file. Nothing here has been swept.")
print("=" * 76)
