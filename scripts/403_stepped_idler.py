# -*- coding: utf-8 -*-
"""Could the idler be GEARED, and would that buy anything downstream?

Two different questions hide in that, with opposite answers.

As a plain idler it carries no torque at all. The ratio is 2*pi*R/lead -- the capstan
radius and the screw lead, nothing else -- and the idler is a free return pulley. Changing
its tooth count changes only where the return strand lands, and equal pulleys are exactly
what keeps the belt envelope unchanged (390_onescrew_section.py). So no.

A STEPPED idler is different: two pulleys on one shaft, two loops. Loop 1 runs capstan to
pulley A; loop 2 runs pulley B to a distal return pulley and carries the carriage clamp.
That DOES gear, and it is the only way to change the total ratio without changing the
screw -- which matters, because the 14.5:1 this design wants needs an SFU1616 and the
search for one mostly turns up SFE1616, a high-lead series with a different nut.

Run:  python scripts/403_stepped_idler.py
"""
import math

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
LEAD = 10.0
TAU_KNEE = 28.2
ETA_S, ETA_B = 0.90, 0.97
J_ROTOR, J_LIMB = 3.10e-4, 0.30
KT = 9.549 / 170.0
T_PRE = 150.0
BELT_W = 30.0
RAIL_X, BIN = 20.0, R - 1.372
WHEEL_OUT = 30.97

print("=" * 76)
print("1. WHY A PLAIN IDLER CANNOT GEAR ANYTHING")
print("   carriage moves d -> belt circulates d -> capstan turns d/R -> knee turns d/R.")
print("   The idler turns d/r_idler, and that appears nowhere in the answer. Ratio is")
print("   2*pi*R/lead = %.1f:1 whatever size it is." % (2 * math.pi * R / LEAD))

print("=" * 76)
print("2. A STEPPED IDLER, AND WHAT IT COSTS TO GET THE RATIO FROM THE BELT")
print("   With pulley A (r1) on loop 1 and pulley B (r2) on loop 2:")
print("     N = (2*pi/lead) * R * r2/r1")
print()
print("   %-22s %7s %9s %9s %10s %9s %9s"
      % ("route to 14.5:1", "r2/r1", "N", "T_motor", "belt diff", "nut force", "refl J"))
F_BELT = TAU_KNEE * 1000.0 / R
for lbl, ratio_step, lead in (("as built, SFU1610", 1.0, 10.0),
                              ("stepped idler 20/32T", 0.625, 10.0),
                              ("SFU1616, plain idler", 1.0, 16.0)):
    N = 2 * math.pi * R * ratio_step / lead
    tau_m = TAU_KNEE / (N * ETA_S * ETA_B)
    belt2 = F_BELT / ratio_step          # loop 2 carries the geared-up tension
    nut = belt2
    jr = J_ROTOR * N ** 2
    print("   %-22s %6.3f %7.1f:1 %6.2f Nm %8.0f N %8.0f N %7.3f  %.2fx"
          % (lbl, ratio_step, N, tau_m, belt2, nut, jr, jr / J_LIMB))
print()
print("   Both routes land on the same %.1f:1 and the same motor torque. They are NOT the"
      % (2 * math.pi * R * 0.625 / 10.0))
print("   same downstream, and this is the whole answer:")
print()
print("     * The LONGER LEAD gets the ratio by making the SCREW less advantaged. The belt")
print("       and the nut never notice -- %.0f N before, %.0f N after." % (F_BELT, F_BELT))
print("     * The STEPPED IDLER gets the ratio out of the BELT, so loop 2 and everything")
print("       downstream of it carries %.1fx more: %.0f N -> %.0f N."
      % (1 / 0.625, F_BELT, F_BELT / 0.625))

print("=" * 76)
print("3. WHAT THAT EXTRA TENSION ACTUALLY BREAKS")
for lbl, f in (("as built", F_BELT + T_PRE), ("stepped idler", F_BELT / 0.625 + T_PRE)):
    print("   %-16s %6.0f N over %.0f mm of HTD-8M = %.1f N/mm"
          % (lbl, f, BELT_W, f / BELT_W))
print("   A 30 mm HTD-8M is good for roughly 30-60 N/mm depending on cord, so the stepped")
print("   version is at or past the top of that band and would want a wider belt -- which")
print("   the 2040's 40 mm face does not have room for.")
print()
print("   The screw's column load rises the same %.1fx, %.0f -> %.0f N, and 400's idler"
      % (1 / 0.625, F_BELT, F_BELT / 0.625))
print("   reaction 2*T_b goes with it: %.0f -> %.0f N on the bracket that was just sized"
      % (2 * (F_BELT + T_PRE), 2 * (F_BELT / 0.625 + T_PRE)))
print("   for 1828.")

print("=" * 76)
print("4. AND WHERE THE SECOND LOOP WOULD RUN")
r2 = 20 * 8.0 / (2 * math.pi)
print("   Loop 2 leaves pulley B on the centreline, so its strands sit at |X| = r2 = %.1f"
      % r2)
print("   for a 20T HTD-8M. That has to thread between the rail at |X| %.0f and loop 1 at"
      % RAIL_X)
print("   |X| %.2f:" % BIN)
print("     rail face %.0f -> loop 2 inner %.1f     %.1f mm" % (RAIL_X, r2 - 2.85, r2 - 2.85 - RAIL_X))
print("     loop 2 outer %.1f -> loop 1 inner %.2f  %.1f mm" % (r2 + 2.85, BIN, BIN - r2 - 2.85))
print("     but the V-wheels reach |X| %.2f, which leaves %.1f mm" % (WHEEL_OUT, r2 - 2.85 - WHEEL_OUT))
print("   It clears neither guide: the mini V-wheel by %.1f mm and an MGN7H block (|X| 28.0)"
      % (r2 - 2.85 - WHEEL_OUT))
print("   by %.1f. Both negative. The only way through is a SMALLER loop-2 pulley, and that"
      % (r2 - 2.85 - 28.0))
print("   raises r1/r2 further -- which raises the tension that was already the problem.")
print("   The geometry and the loading fail in the same direction, which is usually the")
print("   sign that an idea is wrong rather than merely awkward.")

print("=" * 76)
print("VERDICT")
print("   Gearing the idler does buy the one thing worth having -- %.1f:1 and %.2fx the"
      % (14.5, J_ROTOR * 14.5 ** 2 / J_LIMB))
print("   limb's inertia instead of %.2fx -- without needing a screw that may not exist as"
      % (J_ROTOR * 23.2 ** 2 / J_LIMB))
print("   a catalogue part. That is a real argument and it is worth keeping.")
print()
print("   But it buys it in the wrong currency. A longer lead takes the ratio out of the")
print("   SCREW, where there is margin; a stepped idler takes it out of the BELT, where")
print("   there is not. It adds a second loop, a third pulley, a second pretension to set")
print("   and a second place to skip teeth, and it pushes the belt past its load rating,")
print("   the nut 60% harder and the idler bracket past what it was just sized for.")
print()
print("   KEEP IT AS THE FALLBACK, conditional on one purchasing fact: if an SFU1616 with")
print("   an OD 36 nut can be bought, buy it. If only SFE1616 exists and its nut does not")
print("   fit the carriage bore, revisit this -- and widen the belt first.")
print("=" * 76)
