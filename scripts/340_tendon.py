# -*- coding: utf-8 -*-
"""Remote actuation: motor, screws and pack in the backpack, driving the knee capstan
through two low-stretch tendons in PTFE-lined sheaths.

The capstan at the knee is unchanged -- 29T, R = 36.92 mm, 180 deg wrap, two runs. What
changes is where the two runs terminate. Today they end at two carriages 100 mm up the
thigh. Here they leave the knee, run up the thigh, cross the hip and end at two carriages
in the backpack. The mechanism is identical; only the length of the runs changes.

Two tendons, not one, because a tendon only pulls -- and that falls out for free, because
the differential already gives two opposed runs.

This is a real architecture (Harvard's soft exosuit and most tethered exos work this way)
and it fails on exactly two numbers: sheath friction and tendon stretch.

Run:  python scripts/340_tendon.py
"""
import math

F = 914.0                # N, worst-case run tension (764 differential + 150 pretension)
R = 36.924               # mm, capstan radius -- 1 mm of stretch = 1/R rad of knee
L_FREE = 800.0           # mm, knee to backpack
LOST_SPRING = 2.45       # deg, lost motion the sprung anchor already costs

print("=" * 70)
print("1. SHEATH FRICTION  --  the one that usually kills these")
print("   capstan equation: T_out = T_in * exp(-mu * theta), theta = TOTAL wrap along")
print("   the route. It is not a fixed loss: theta changes as the hip and knee move.")
print()
print("   %-28s %8s %8s %8s" % ("route", "90 deg", "180 deg", "270 deg"))
for mat, mu in (("steel on PTFE", 0.12), ("Vectran on PTFE", 0.08), ("UHMWPE on PTFE", 0.06)):
    row = ""
    for th in (90.0, 180.0, 270.0):
        eff = math.exp(-mu * math.radians(th))
        row += "%7.0f%% " % (eff * 100)
    print("   %-28s %s" % (mat + "  mu=%.2f" % mu, row))
print()
print("   A thigh route crosses the hip and follows the femur: 180-270 deg is realistic,")
print("   and it CHANGES with posture. At mu=0.08 and theta swinging 180->270 deg the")
print("   delivered tension moves %.0f%% -> %.0f%% for the same motor torque."
      % (math.exp(-0.08*math.pi)*100, math.exp(-0.08*math.radians(270))*100))
print("   That is not a calibration offset, it is posture-dependent hysteresis, and it")
print("   makes open-loop torque control impossible. Every serious tendon exo puts a")
print("   LOAD CELL in series at the joint end and closes the loop on measured tension.")
print("   That is the real cost of this architecture: a force sensor per tendon.")

print("=" * 70)
print("2. STRETCH  --  lost motion at the knee")
print("   %d N over %.0f mm. 1 mm of stretch = %.2f deg of knee." % (F, L_FREE, math.degrees(1.0/R)))
print()
print("   %-16s %7s %9s %9s %9s" % ("fibre", "E GPa", "for 1 mm", "for 2 mm", "for 3 mm"))
for name, E in (("steel 7x19", 70.0), ("Vectran", 75.0), ("UHMWPE SK99", 110.0),
                ("Kevlar braid", 35.0)):
    row = ""
    for d in (1.0, 2.0, 3.0):
        A = F * L_FREE / (d * E * 1000.0)        # mm^2
        dia = 2.0 * math.sqrt(A / math.pi)
        row += "%7.1f mm" % dia
    print("   %-16s %7.0f %s" % (name, E, row))
print("   (diameter of solid equivalent cross-section needed to hold stretch to that)")
print()
print("   2 mm of stretch is %.1f deg, against %.2f deg the sprung anchor already costs."
      % (2.0 * math.degrees(1.0/R), LOST_SPRING))
print("   So ~3 mm cord in Vectran or UHMWPE is the working point. Both are reachable.")

print("=" * 70)
print("3. FIBRE CHOICE  --  Kevlar is the wrong one")
print("   Kevlar/aramid: high strength, but poor flex fatigue and poor abrasion. A tendon")
print("     that reciprocates every step inside a sheath is the worst case for it.")
print("   UHMWPE (Dyneema SK99): excellent flex life and abrasion, very low friction --")
print("     but it CREEPS under sustained load, and this tendon holds 150 N of pretension")
print("     all day. Creep shows up as lost motion that grows over weeks.")
print("   Vectran (LCP): low creep, good flex life, ~75 GPa. The usual answer for tendon")
print("     drives, and the one to start with.")
print("   Steel 7x19: no creep, cheap, predictable -- but fatigues at small bend radii and")
print("     abrades the liner. Fine for a bench prototype.")

print("=" * 70)
print("4. WHAT COMES OFF THE LEG")
off = [("6374 motor", 800.0), ("2x SFU1610 screws", 900.0), ("2x ball nuts", 360.0),
       ("20x60 rail", 351.0), ("2 carriages", 383.0), ("MGN7 rails + blocks", 95.0),
       ("ODrive S1 + brake R", 120.0), ("drive cap + thigh fairing", 276.0),
       ("bearings, pulleys, fasteners", 200.0)]
stay = [("knee yoke", 167.0), ("hub + 29T pulley", 181.0), ("knee cap", 39.0),
        ("shank socket + cuff", 391.0), ("shank fairing", 53.0), ("thigh cuff", 188.0),
        ("belt, pin, bushings", 60.0), ("2 load cells + tendon terminations", 120.0),
        ("sheath anchors", 80.0)]
o = sum(m for _, m in off); st = sum(m for _, m in stay)
print("   moves to the backpack : %6.0f g" % o)
print("   stays on the leg      : %6.0f g" % st)
print("   one knee now 4.66 kg -> %.2f kg on the limb" % (st/1000.0))
print()
print("   bilateral: %.1f kg on the legs + one backpack, against %.1f kg today."
      % (2*st/1000.0, 2*4.66))

print("=" * 70)
print("5. THE PART THAT IS ACTUALLY BETTER, NOT JUST LIGHTER")
print("   A screw cannot go slack. A tendon can. During free swing both runs unload and")
print("   the limb is decoupled from the motor entirely -- the 0.167 kg.m2 of reflected")
print("   rotor inertia simply is not there. That is the single biggest objection to the")
print("   current design and a tendon removes it, rather than trading it.")
print("   It also puts every heavy, hot, noisy thing in a backpack, which fixes the")
print("   acoustics problem and the thermal one at the same time.")
print("=" * 70)
