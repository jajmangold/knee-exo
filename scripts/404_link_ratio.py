# -*- coding: utf-8 -*-
"""Gear the motor-to-screw belt instead of the idler. Right idea, wrong direction.

403_stepped_idler.py found that gearing the CAPSTAN loop fails because that loop carries
764 N, and multiplying it breaks the belt, the nut and the bracket at once.

The motor-to-screw link belt is the opposite case. It sits on the motor side of the ball
screw's own mechanical advantage, so it only ever carries the SCREW's torque -- 1.35 N.m,
about 100 N of belt tension. Gearing there is nearly free. It is the right place.

What is not free is the direction. A 4:1 or 5:1 REDUCTION multiplies the total ratio, and
reflected inertia goes as the ratio SQUARED -- which is the single number this design is
worst at. An OVERDRIVE does the opposite, and lands exactly on the 14.5:1 the repo has
been trying to buy an SFU1616 for.

Run:  python scripts/404_link_ratio.py
"""
import math

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
LEAD = 10.0
N_SCREW = 2 * math.pi * R / LEAD       # 23.2, knee -> screw
TAU_KNEE = 28.2
ETA_S, ETA_B = 0.90, 0.97
J_ROTOR, J_LIMB = 3.10e-4, 0.30
KT = 9.549 / 170.0
I_CONT = 40.0
TAU_6374 = 2.49                        # N.m continuous, from 350_motor_kv.py's sigma model
F_NUT = TAU_KNEE * 1000.0 / R          # 764 N, set by the capstan radius -- fixed
TAU_SCREW = F_NUT * (LEAD / 1000.0) / (2 * math.pi * ETA_S)
RPM_SCREW = 1160.0

print("=" * 78)
print("WHY THIS IS THE RIGHT PLACE TO GEAR")
print("   The link belt is on the MOTOR side of the screw, so it never sees the %.0f N the"
      % F_NUT)
print("   capstan loop carries. It carries the screw's torque, %.2f N.m, and that is all."
      % TAU_SCREW)
print("   Whatever ratio you put here, the capstan belt, the ball nut, the screw's column")
print("   load and the idler bracket do not change at all. 403's stepped idler multiplied")
print("   every one of them by 1.6.")

print("=" * 78)
print("BUT THE DIRECTION IS EVERYTHING -- reflected J goes as ratio SQUARED")
print()
print("   %-22s %8s %9s %8s %8s %10s %9s"
      % ("link motor:screw", "N total", "T_motor", "amps", "rpm mot", "refl J", "vs limb"))
for lbl, k in (("5:1 reduction", 5.0), ("4:1 reduction", 4.0), ("1:1, as built", 1.0),
               ("1:1.6 OVERDRIVE", 0.625), ("1:2 overdrive", 0.5)):
    N = N_SCREW * k
    tau_m = TAU_SCREW / (k * ETA_B)
    jr = J_ROTOR * N ** 2
    bad = []
    if tau_m > TAU_6374:
        bad.append("motor can't")
    if tau_m / KT > I_CONT:
        bad.append("over %.0f A" % I_CONT)
    if jr / J_LIMB > 1.0:
        bad.append("inertia")
    print("   %-22s %7.1f:1 %6.2f Nm %6.1f A %7.0f %8.3f %7.2fx  %s"
          % (lbl, N, tau_m, tau_m / KT, RPM_SCREW * k, jr, jr / J_LIMB, ", ".join(bad)))
print()
print("   A 4:1 reduction makes the motor's job trivial -- %.2f N.m and %.1f A -- and makes"
      % (TAU_SCREW / (4 * ETA_B), TAU_SCREW / (4 * ETA_B) / KT))
print("   the device unusable: %.1f kg.m2 reflected is %.0fx the limb's own inertia, so with"
      % (J_ROTOR * (N_SCREW * 4) ** 2, J_ROTOR * (N_SCREW * 4) ** 2 / J_LIMB))
print("   the power off the leg would feel roughly ten times heavier to swing. That is the")
print("   one failure mode this whole design is organised around avoiding.")

print("=" * 78)
print("THE OVERDRIVE IS THE ANSWER THE REPO HAS BEEN LOOKING FOR")
k = 0.625
N = N_SCREW * k
tau_m = TAU_SCREW / (k * ETA_B)
print("   motor:screw = 1:1.6, i.e. a 32T motor pulley driving a 20T screw pulley.")
print()
print("   %-26s %14s %14s" % ("", "SFU1616 route", "overdrive route"))
rows = [("ratio", "14.5:1", "%.1f:1" % N),
        ("motor torque", "2.23 N.m", "%.2f N.m" % tau_m),
        ("peak current at 170 Kv", "39.7 A", "%.1f A" % (tau_m / KT)),
        ("reflected J vs limb", "0.22x", "%.2fx" % (J_ROTOR * N ** 2 / J_LIMB)),
        ("capstan belt / nut force", "764 N", "%.0f N" % F_NUT),
        ("ball screw", "SFU1616 -- may not exist", "SFU1610, already specced"),
        ("carriage bore", "needs OD check", "unchanged"),
        ("new parts", "a screw", "two pulleys")]
for a, b, c in rows:
    print("   %-26s %14s %14s" % (a, b, c))
print()
print("   They are the same machine. The overdrive gets there with two pulleys instead of")
print("   a screw that the supplier search could not confirm exists in the SFU series.")

print("=" * 78)
print("WHAT THE LINK BELT THEN HAS TO CARRY")
for lbl, teeth_s, pitch, width in (("HTD-3M 20T", 20, 3.0, 15.0),
                                   ("HTD-5M 20T", 20, 5.0, 15.0),
                                   ("HTD-5M 24T", 24, 5.0, 15.0)):
    r_s = teeth_s * pitch / (2 * math.pi)
    te = TAU_SCREW / (r_s / 1000.0)
    print("   %-12s screw pulley PD %5.1f mm -> effective tension %5.0f N, tight side ~%3.0f N"
          % (lbl, 2 * r_s, te, 1.8 * te))
    print("   %-12s over %.0f mm of belt that is %.1f N/mm" % ("", width, 1.8 * te / width))
print()
print("   HTD-3M is the small-pitch, quiet choice and it is comfortable here -- this belt")
print("   never sees more than a couple of hundred newtons. Use 15 mm and it is fine; the")
print("   thing to check on the datasheet is the 20T pulley's own rating, not the belt's.")
print()
print("   Centre distance is %.0f mm (motor X -104 Z 62 to screw X -62 Z 106), against a"
      % math.hypot(-104 + 62, 62 - 106))
print("   minimum of about %.0f for a 32T/20T 3M pair. Comfortable."
      % ((32 * 3.0 / math.pi + 20 * 3.0 / math.pi) / 2))

print("=" * 78)
print("ONE THING THE SFU1616 WOULD STILL HAVE DONE BETTER")
print("   A 16 mm lead turns the screw %.2f times over the ROM instead of %.2f, which"
      % (68.31 / 16.0, 68.31 / LEAD))
print("   halves ball-nut recirculation -- ELECTRONICS.md section 9's prime noise suspect")
print("   at ~290 Hz. The overdrive leaves the screw turning exactly as fast as it does")
print("   now and moves the motor slower instead. So if an SFU1616 does turn out to be")
print("   buyable with an OD 36 nut, it is still the better part. The overdrive is what")
print("   makes the design no longer DEPEND on that.")
print("=" * 78)
