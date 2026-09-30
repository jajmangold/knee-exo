# -*- coding: utf-8 -*-
"""What Kv, for what ratio -- and why Kv is not the thing that matters.

Kv is a winding choice. It sets volts-per-rpm and amps-per-newton-metre, and you pick it
to match the bus. It does NOT set how much torque a motor can make: that comes from
airgap radius, stack length and cooling. Rewinding a motor to half the Kv doubles its
torque per amp and halves its speed per volt, and changes its continuous torque hardly at
all, because the copper gets thinner in exactly the proportion that the turns increase.

So the sequence is: pick the ratio, size the MOTOR for the torque, then pick Kv to land
the current and speed inside the bus and the controller.

Run:  python scripts/350_motor_kv.py
"""
import math

TAU_KNEE = 28.2         # N.m peak at the joint
W_KNEE = math.radians(300.0)   # rad/s peak, free swing
ETA = 0.90 * 0.97       # screw x linking belt
V_LOW = 34.0            # V, working bus near the bottom of a 12S LiFePO4 pack
V_NOM = 38.4
I_TARGET = 22.0         # A peak, what this design already sizes for
I_S1_CONT = 40.0        # ODrive S1 continuous
SIGMA = 10e3            # Pa, airgap shear stress, air-cooled outrunner
J_LIMB = 0.30

print("=" * 72)
print("1. THE KV WINDOW, BY RATIO")
print("   motor torque T = %.1f / N ; motor speed = %.0f x N rpm"
      % (TAU_KNEE / ETA, W_KNEE * 60 / (2 * math.pi)))
print()
print("   %-6s %8s %9s %11s %11s %11s" %
      ("ratio", "T_motor", "rpm peak", "Kv for 22 A", "Kv for 40 A", "Kv min for rpm"))
for N in (23.2, 18.0, 14.0, 11.6, 9.0, 6.0):
    T = TAU_KNEE / (N * ETA)
    rpm = W_KNEE * 60 / (2 * math.pi) * N
    kv22 = I_TARGET * 9.549 / T
    kv40 = I_S1_CONT * 9.549 / T
    kvmin = rpm / V_LOW
    print("   %-6.1f %6.2f Nm %7.0f rpm %9.0f Kv %9.0f Kv %9.0f Kv"
          % (N, T, rpm, kv22, kv40, kvmin))
print()
print("   The speed constraint is never binding -- %.0f Kv covers the fastest case." % 34)
print("   So: Kv ~= %.1f x ratio for %d A peak, or %.1f x ratio if you will run %d A."
      % (I_TARGET * 9.549 / (TAU_KNEE / ETA), I_TARGET,
         I_S1_CONT * 9.549 / (TAU_KNEE / ETA), int(I_S1_CONT)))
print("   At the built 23.2:1 that gives %.0f Kv. The motors on hand are 170 Kv -- see"
      % (23.2 * I_TARGET * 9.549 / (TAU_KNEE / ETA)))
print("   360_owned_hw.py; 13% fast, which costs amps and nothing else.")

print("=" * 72)
print("2. BUT THE MOTOR HAS TO BE ABLE TO MAKE THE TORQUE")
print("   T ~ sigma * 2*pi*R^2*L, sigma ~ %.0f kPa air-cooled." % (SIGMA / 1e3))
print()
print("   %-18s %7s %7s %9s %10s" % ("motor", "R mm", "stack", "T_cont", "verdict at"))
# J_rotor is taken to match 300_drivetrain.py's 3.10e-4 for the 6374 and scaled from
# there by bell mass and radius. It is an estimate with maybe +/-25% in it, so the
# ABSOLUTE reflected-inertia numbers carry that; the comparison between options does not.
MOTORS = [("6374 OWNED x4", 31.5, 40.0, 3.10e-4), ("6384", 31.5, 50.0, 3.88e-4),
          ("8085", 40.0, 45.0, 1.13e-3), ("8308 pancake", 41.5, 30.0, 9.5e-4),
          ("110 mm pancake", 55.0, 30.0, 3.55e-3)]
for nm, Rmm, Lmm, J in MOTORS:
    R, L = Rmm / 1000.0, Lmm / 1000.0
    T = SIGMA * 2 * math.pi * R ** 2 * L
    best = None
    for N in (23.2, 18.0, 14.0, 11.6, 9.0, 6.0):
        need = TAU_KNEE / (N * ETA)
        if T >= need and (best is None or N < best):
            best = N
    print("   %-18s %7.1f %5.0f mm %7.2f Nm %8s"
          % (nm, Rmm, Lmm, T, ("%.0f:1" % best) if best else "none"))

print("=" * 72)
print("3. THE CATCH NOBODY MENTIONS: A BIGGER MOTOR HAS MORE ROTOR INERTIA")
print("   reflected J = J_rotor x N^2, and J_rotor ~ m_bell x R^2 grows as you go bigger.")
print()
print("   %-18s %9s %7s %11s %10s" % ("motor", "J_rotor", "ratio", "J_reflected", "vs limb"))
for nm, Rmm, Lmm, J in MOTORS:
    R = Rmm / 1000.0
    T = SIGMA * 2 * math.pi * R ** 2 * (Lmm / 1000.0)
    N = None
    for cand in (6.0, 9.0, 11.6, 14.0, 18.0, 23.2):
        if T >= TAU_KNEE / (cand * ETA):
            N = cand
            break
    if N is None:
        continue
    Jr = J * N ** 2
    print("   %-18s %.2e %5.0f:1 %8.3f kgm2 %8.2fx" % (nm, J, N, Jr, Jr / J_LIMB))
print()
print("   Torque goes as R^2*L and inertia as m*R^2, so buying torque with diameter buys")
print("   inertia back. Dropping the ratio does NOT divide reflected inertia by N^2 -- the")
print("   motor grows to meet the torque and eats most of the gain.")
print("=" * 72)
print("SO, THE ANSWER")
print("   Kv is not a target, it is what falls out once the ratio is fixed:")
print("     Kv ~= 6.5 x ratio at 22 A, ~11.8 x ratio at 40 A")
print("   At the built 23.2:1 that wants ~151 Kv. The motors on hand are 170 Kv, which")
print("   is 13% fast -- 24.8 A instead of 21.7 for the same torque, and no more heat.")
print()
print("   The best point in the table below is NOT the biggest motor: buying torque with")
print("   diameter buys inertia straight back. A 6384 at 11.6:1 beats an 8085 at 9:1 and")
print("   a 110 mm pancake at 6:1. BUT -- and this is the conclusion that matters --")
N, Jr84 = 11.6, 3.88e-4 * 11.6 ** 2
Jr74 = 3.10e-4 * 14.5 ** 2
T84 = TAU_KNEE / (N * ETA)
print("     6384 @ 11.6:1 (SFU1620)   reflected J %.3f kgm2 = %.2fx the limb, %.1f A"
      % (Jr84, Jr84 / J_LIMB, T84 / (9.549 / 170)))
print("     6374 @ 14.5:1 (SFU1616)   reflected J %.3f kgm2 = %.2fx the limb, %.1f A"
      % (Jr74, Jr74 / J_LIMB, TAU_KNEE / (14.5 * ETA) / (9.549 / 170)))
print()
print("   The 6384 does win on inertia -- %.2fx against %.2fx. But read the second"
      % (Jr84 / J_LIMB, Jr74 / J_LIMB))
print("   column: it wants %.1f A where the owned 6374 wants %.1f, and %.1f A is above"
      % (T84 / (9.549 / 170), TAU_KNEE / (14.5 * ETA) / (9.549 / 170),
         T84 / (9.549 / 170)))
print("   any believable continuous rating for the drives on hand. So the comparison is:")
print("     spend $60 and 10 A of headroom you do not have")
print("     to remove %.3f kgm2 -- %.0f%% of the limb's own inertia."
      % (Jr74 - Jr84, 100 * (Jr74 - Jr84) / J_LIMB))
print("   That is a bad trade. The 6384's advantage is real and it is small, and it is")
print("   bought with the one resource that is actually scarce. Do not buy the 6384.")
print("   Buy the screw, and keep the amps.")
print("     SFU1616, 16 mm lead, ratio %.1f:1, nut still OD 36 -- the SAME carriage bore" % 14.5)
print("     the model already has at NUT_R = 18. Verify on the supplier drawing, because")
print("     that is the one thing that decides whether this is a screw swap or a rebuild.")
print()
print("   Caveat that bounds all of the above: J_rotor is an ESTIMATE, +/-25%. Weigh a")
print("   bell and measure its radius before betting the design on 0.22x vs 0.26x.")
print("=" * 72)
