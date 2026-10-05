# -*- coding: utf-8 -*-
"""SFU1610 at 200 mm is not stocked anywhere. What does a 1605 or a 1204 actually cost?

Asked at the bench: "its really hard to find that ball screw -- isn't there a much more common
one we could use? Nobody sells sfu1610 even at 200mm ... Meanwhile sfu1605 and sfu1204 are
everywhere."

THE LEAD IS THE WHOLE RATIO. The knee drives the screw through the capstan, so one screw turn is
lead/(2*pi*R_cap) of knee rotation and nothing else enters it. Halve the lead and the total ratio
DOUBLES, which halves the current and QUADRUPLES reflected inertia -- and reflected inertia is the
number this design is organised around, because it is what the leg feels when the power is off.
404_link_ratio.py rejected a 4:1 reduction for exactly this reason: 9x the limb's own inertia.

WHAT CAN ABSORB A LEAD CHANGE. Only the link belt, and it is bounded at both ends:

  * the motor pulley has to fit inside the motor's own can, or the pod grows and the drive end
    has only 1.6 mm of clearance to the sleeve (438_limb_clearance.py). dia 63 is the ceiling.
  * the screw pulley has to have a 12 mm bore, because that is what the screw's fixed end is
    (the vendor drawing: dia 10 x 15, M12x1 x 14, dia 12 x 25). Below about 18T in HTD-5M the
    wall between the bore and the tooth root is thinner than the teeth.

So the achievable overdrive is roughly 1.0 to 1.9, not the 3.2 a 5 mm lead would need to get
back to where the 10 mm lead already is.

    python scripts/443_screw_sourcing.py
"""
import math

R_CAP = 29 * 8.0 / (2 * math.pi)        # 36.923 mm, fixed by the capstan being a bought 29T
TAU_KNEE = 28.2                         # N.m
ETA_S, ETA_B = 0.90, 0.97
J_ROTOR, J_LIMB = 3.10e-4, 0.30         # kg.m2
KT = 9.549 / 170.0                      # C6374 at 170 Kv
I_CONT = 40.0                           # A, the motor's continuous ceiling
RPM_SCREW_10 = 1160.0                   # screw rpm at a 10 mm lead, set by gait speed
F_NUT = TAU_KNEE * 1000.0 / R_CAP       # 764 N, set by the capstan radius -- fixed
STEEL = 7.85e-3                         # g/mm3
SPAN = 200.0                            # mm of screw the device needs end to end

CAN_D = 63.0                            # the motor pulley must stay inside this
MIN_SCREW_T = 18                        # HTD-5M teeth, below which a 12 mm bore has no wall


def pd(teeth, pitch=5.0):
    return teeth * pitch / math.pi


print("=" * 98)
print("WHAT A DIFFERENT BALL SCREW COSTS")
print("=" * 98)
print("  the capstan is a bought 29T, so R = %.3f mm and the nut force is %.0f N whatever the"
      % (R_CAP, F_NUT))
print("  screw is. Only the LEAD and the link belt can change.")
print()
print("  %-22s %7s %8s %7s %8s %9s %8s %7s"
      % ("screw + link", "N tot", "T motor", "amps", "mot rpm", "refl J", "vs limb", "screw g"))

rows = []
for lead, dia, label in ((10.0, 16.0, "SFU1610"), (5.0, 16.0, "SFU1605"), (4.0, 12.0, "SFU1204")):
    n_screw = 2 * math.pi * R_CAP / lead
    for mt, st in ((32, 20), (38, 20), (20, 20)):
        od = mt / float(st)
        if pd(mt) > CAN_D or st < MIN_SCREW_T:
            continue
        n_tot = n_screw / od
        tau_m = TAU_KNEE / (n_tot * ETA_S * ETA_B)
        amps = tau_m / KT
        rpm_screw = RPM_SCREW_10 * (10.0 / lead)
        rpm_mot = rpm_screw / od
        j = J_ROTOR * n_tot ** 2
        mass = math.pi * (dia / 2.0) ** 2 * SPAN * STEEL
        tag = ""
        if amps > I_CONT:
            tag = "  <-- over %.0f A" % I_CONT
        elif j / J_LIMB > 0.75:
            tag = "  <-- the leg feels %.0f%% heavier unpowered" % (100 * j / J_LIMB)
        rows.append((label, mt, st, n_tot, tau_m, amps, rpm_mot, j, mass))
        print("  %-22s %6.1f:1 %7.2f Nm %6.1f A %8.0f %9.3f %7.2fx %6.0f%s"
              % ("%s + %dT:%dT" % (label, mt, st), n_tot, tau_m, amps, rpm_mot,
                 j, j / J_LIMB, mass, tag))

print()
print("  (%dT on the motor is the largest HTD-5M pulley that still fits inside a dia %.0f can:"
      % (38, CAN_D))
print("   PD %.1f mm. %dT would be PD %.1f and the pod would have to grow, which it cannot --"
      % (pd(38), 50, pd(50)))
print("   the drive end has 1.6 mm to the sleeve at Y 296.)")

base = [r for r in rows if r[0] == "SFU1610" and r[1] == 32][0]
print()
print("=" * 98)
print("  AGAINST THE DESIGN AS IT STANDS (%s %dT:%dT)" % (base[0], base[1], base[2]))
print()
for r in rows:
    if r is base:
        continue
    print("  %-18s ratio %+5.1f:1   current %+6.1f A   reflected inertia %+5.2fx the limb"
          % ("%s %dT:%dT" % (r[0], r[1], r[2]), r[3] - base[3], r[5] - base[5],
             (r[7] - base[7]) / J_LIMB))

print()
print("=" * 98)
print("  THE OTHER WAY OUT: a longer SFU1610, which IS stocked")
print()
for L in (250.0, 300.0, 400.0):
    extra = L - SPAN
    mass = math.pi * 8.0 ** 2 * extra * STEEL
    print("     %3.0f mm -> %3.0f mm of overhang above the drive cap, %+.0f g of dead steel"
          % (L, extra, mass))
print()
print("     The 107-pose clash test in this repository already says the space above the screw's")
print("     top is free: a 200 mm screw reaches Y 257 and touches nothing. 300 mm reaches 358,")
print("     which is 24 mm proud of P22_DriveCap at Y 334 -- cladding to extend, not a collision.")
print("     Against that, %.0f g is most of the %.0f g that turning the motor over saved."
      % (math.pi * 8.0 ** 2 * 100.0 * STEEL, 123.0))
print()
print("     Cutting a long one down is the better version of this and needs a lathe for the")
print("     ends: the journals are what the bearings sit on and they cannot be improvised.")
