# -*- coding: utf-8 -*-
"""Move the motor to the front of the thigh so it stops costing PROXIMAL length.

The drive end currently reaches Y 412 and 390 section 7 shows that is 8 mm PAST the hip
on a 1.65 m patient. The motor is 74 mm of that, and it is 74 mm spent in the one
direction with no budget left.

The reason it sits proximally is that it is on the centreline, where the idler pulley and
its belt wrap already occupy Y 213..296 across |X| <= 41.12. Put the motor ANTERIOR
instead and it can share that Y -- the two never meet in X -- and the whole drive end
shortens by the length of the motor.

Anterior is the cheap direction and posterior is cheaper still: 330_frontmount.py measured
the device as sitting roughly inside the limb's own fore-aft silhouette, and the thigh is
+/-84.9. Lateral is the expensive one (86 mm proud already) and proximal is the one that
has actually run out.

Run:  python scripts/402_motor_anterior.py
"""
import math

R = 29 * 8.0 / (2 * math.pi)
BOUT = R + 4.2                 # 41.124, belt band outer
IDL_Y = 255.0
MOT_R, MOT_L = 31.5, 74.0
SCR_X, SCR_R = -62.0, 7.9
BRACKET_X = 46.5
THIGH_R = 84.9                 # REF_Thigh half-width
GANTRY_Y_MAX = 204.29
CAP_NOW = 412.0

print("=" * 76)
print("1. WHERE CAN A 63 mm MOTOR GO AT Y 213..296?")
print("   Occupied at that Y: the idler and its wrap out to |X| %.2f, and the drive"
      % BOUT)
print("   bracket's cheeks out to |X| %.1f. Everything beyond that is air." % BRACKET_X)
need = BRACKET_X + 2.0 + MOT_R
print("   So the motor axis has to be at |X| >= %.1f + 2 + %.1f = %.1f"
      % (BRACKET_X, MOT_R, need))
print()
print("   But it also has to clear the BALL SCREW, which runs the full length at X %.0f:"
      % SCR_X)
need2 = MOT_R + SCR_R + 2.5
print("   |X_motor - %.0f| >= %.1f + %.1f + 2.5 = %.1f -> X <= %.1f or X >= %.1f"
      % (SCR_X, MOT_R, SCR_R, need2, SCR_X - need2, SCR_X + need2))
print("   X >= %.1f is back inside the belt band, so it is X <= %.1f. That is the binding"
      % (SCR_X + need2, SCR_X - need2))
print("   constraint, not the bracket: a 63 mm can cannot sit 18 mm from a ball screw.")
MOT_X = -104.0
print()
print("   -> motor axis X = %.0f, can spans X %.1f..%.1f" % (MOT_X, MOT_X - MOT_R, MOT_X + MOT_R))
print("      clear of the screw's outer face (%.1f) by %.1f mm"
      % (SCR_X - SCR_R, (SCR_X - SCR_R) - (MOT_X + MOT_R)))

print("=" * 76)
print("2. THE 1:1 LINK BELT STILL HAS TO REACH THE SCREW")
cd = abs(MOT_X - SCR_X)
print("   centre distance %.0f mm. A 20T HTD-5M is PD %.1f, so the pulleys need > %.1f --"
      % (cd, 20 * 5.0 / math.pi, 20 * 5.0 / math.pi))
print("   %.0f mm is comfortable. (At the naive X -76 it would have been 14 mm, which is"
      % cd)
print("   why 'just move it forward a bit' does not work: it has to clear the screw.)")
LINK_Y = (298.0, 310.0)   # 298, not 290: the idler wrap ends at 296.1
print("   Link belt at Y %.0f..%.0f -- past the idler wrap's %.1f, spindle facing PROXIMAL"
      % (LINK_Y[0], LINK_Y[1], IDL_Y + BOUT))
print("   as suggested, with the screw extended to Y %.0f to meet it." % LINK_Y[1])

print("=" * 76)
print("3. WHAT IT SAVES, AND WHAT IT COSTS")
MOT_Y = (213.0, 213.0 + MOT_L)
CAP_NEW = 328.0
print("   motor Y %.0f..%.0f -- it now OVERLAPS the idler (Y %.0f..%.1f) instead of"
      % (MOT_Y[0], MOT_Y[1], IDL_Y - R - 4.2, IDL_Y + BOUT))
print("   queueing behind it. Gantry tops out at Y %.1f, so no conflict there either."
      % GANTRY_Y_MAX)
print()
print("   proximal   cap Y %.0f -> %.0f     %+.0f mm" % (CAP_NOW, CAP_NEW, CAP_NEW - CAP_NOW))
print("   fore-aft   cap X -96 -> %.0f      %+.0f mm, ALL of it anterior"
      % (MOT_X - MOT_R - 3.5, (MOT_X - MOT_R - 3.5) + 96))
print()
print("   %-12s %8s %12s %14s" % ("stature", "thigh", "cap ends", "margin to hip"))
for h in (1.60, 1.65, 1.72, 1.78, 1.85):
    t = 0.245 * h * 1000.0
    print("   %8.2f m %6.0f mm %9.0f mm %11.0f mm   (was %+.0f)"
          % (h, t, CAP_NEW, t - CAP_NEW, t - CAP_NOW))
print()
print("   That turns a design that does not fit a 1.65 m patient into one with 84 mm of")
print("   margin at 1.65 and 65 mm at 1.60.")
print()
print("   The anterior cost, against the limb's own silhouette:")
for lbl, x in (("now", -96.0), ("motor anterior", MOT_X - MOT_R - 3.5)):
    print("     %-16s cap front X %.0f, thigh front X %.1f -> %.0f mm proud"
          % (lbl, x, -THIGH_R, -x - THIGH_R))
print("   Posteriorly it stays at X +57, which is INSIDE the thigh's %.1f -- so the device"
      % THIGH_R)
print("   is still within the limb's silhouette on that side and every millimetre of the")
print("   growth is on the front, where there is nothing to hit while walking or sitting.")

print("=" * 76)
print("4. WHAT THIS DOES NOT FIX, AND WHAT IT BREAKS")
print("   * %.0f mm proud of the front of the thigh is not free. At deep hip flexion --"
      % (-(MOT_X - MOT_R - 3.5) - THIGH_R))
print("     a deep squat, not sitting -- the front of the mid-thigh approaches the")
print("     abdomen. Sitting at 90 deg is fine; the bulge faces the ceiling.")
print("   * The drive bracket has to grow anterior to carry the motor at X %.0f, and it"
      % MOT_X)
print("     becomes a cantilever holding 800 g out at the end of a 42 mm arm rather than")
print("     a plate the motor bolts through. That is a new load path and it is NOT the")
print("     %.0f N idler case 400_bracket_stress.py covered." % 1828.0)
print("   * The cap has to swell anterior over the motor, and its section at Y 204 is")
print("     P21's, so the two no longer blend as simply as they do now.")
print("   * Lateral is untouched at 86 mm proud. This trade spends fore-aft to buy")
print("     proximal and does not touch the expensive direction at all.")
print("=" * 76)
