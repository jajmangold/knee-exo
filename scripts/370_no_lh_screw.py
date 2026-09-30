# -*- coding: utf-8 -*-
"""Can we avoid the left-hand ball screw?

The LH screw is the only special-order part in the build. Everything else is a catalogue
line item. So: what does it cost to buy two identical RH screws instead and reverse one
of them some other way?

Three architectures do it. All three work. The question is what each one adds.

  A  LH screw            one screw of opposite hand, nothing else changes    (built)
  B  reversing gear      both screws RH, one gear mesh flips screw B
  C  reversing idler     both screws RH, both turning the SAME way, and an
                         idler at the proximal end of belt run 2 inverts the
                         sign of that run's kinematics instead

C is the interesting one and it is not obvious, so section 3 derives it.

Run:  python scripts/370_no_lh_screw.py
"""
import math

R = 29 * 8.0 / (2 * math.pi)   # capstan pitch radius, 36.924 mm
SCR_X = 58.0                   # screw axis |X|
T_RUN = 914.0                  # N, worst-case run tension
TAU_M = 1.39                   # N.m at the screw shaft, SFU1610
ETA_SCREW, ETA_BELT = 0.90, 0.97
ETA_GEAR = 0.98
N_PEAK = 1160.0                # rpm at the screw
LOST_SPRING = 2.45             # deg, lost motion the sprung anchor already costs
DEG_PER_MM = math.degrees(1.0 / R)

# geometry read off 194_layout.py / 240_nut1610.py
C0, C1 = 152.0, 138.0
NUT_Y = (36.0, 78.0)
BODY = (-24.0, 78.0)           # carriage body relative to carr
TH = [float(i) for i in range(-2, 105)]
carrA = [C0 - R * math.radians(t) for t in TH]
carrB = [C1 + R * math.radians(t) for t in TH]
RUN_A = [c + BODY[0] for c in carrA]          # belt run 1 ends here
RUN_B = [c + BODY[0] for c in carrB]
STROKE = max(carrA) - min(carrA)

print("=" * 76)
print("1. WHY A SCREW OF OPPOSITE HAND IS NEEDED AT ALL")
print("   The belt wraps the capstan 180 deg with both ends leaving tangentially and")
print("   proximally. Rotating the capstan by phi winds one run on and pays the other")
print("   out, so L1 = L1_0 - R.phi and L2 = L2_0 + R.phi. Sum is constant:")
print("     runA + runB = %.2f mm at every one of the %d poses."
      % (RUN_A[0] + RUN_B[0], len(TH)))
print("   Each run's length IS its nut's Y, so the two nuts must counter-move. Two")
print("   nuts on one shaft counter-move only if the threads are opposite hands.")
print("   Stroke %.1f mm, %.1f mm of belt per degree of knee." % (STROKE, R * math.pi / 180))

print("=" * 76)
print("2. OPTION B -- REVERSE SCREW B WITH A GEAR")
print("   Meshing gears turn opposite ways, so an ODD number of meshes between the two")
print("   screws makes them counter-rotate. Both screws can then be RH.")
print()
print("   One mesh, gear to gear, is out on size: centre distance must be %.0f mm, so"
      % (2 * SCR_X))
print("   each gear needs pitch radius %.0f mm -- a %.0f mm disc on each screw."
      % (SCR_X, 2 * SCR_X))
print("   Three meshes (4 gears in a row) works: 2r + 4r_i = %.0f." % (2 * SCR_X))
for r in (20.0, 24.0, 30.0):
    ri = (2 * SCR_X - 2 * r) / 4.0
    print("     screw gears PD %.0f -> idler gears PD %.0f" % (2 * r, 2 * ri))
print()
print("   But the cheap version is ONE mesh plus the belt we already have:")
print("     motor -> screw A (coupler) ; A -gear-> idler (reverses) ; idler -belt-> B")
print("   Direction: B is opposite A after 1 mesh + 1 belt. Both screws RH.")
print()
PD = 39.0
F_TOOTH = TAU_M / (PD / 2000.0)
print("   tooth load        %.0f N at PD %.0f -- trivial, an acetal gear carries this"
      % (F_TOOTH, PD))
print("   backlash cost     0.10 mm at the pitch circle")
bl = 0.10 / (PD / 2.0) / (2 * math.pi) * 10.0
print("                     = %.4f mm of nut travel = %.3f deg of knee. Negligible."
      % (bl, bl * DEG_PER_MM))
e_b = ETA_SCREW * ETA_GEAR * ETA_BELT
print("   efficiency        %.3f -> %.3f, so %.1f A becomes %.1f A"
      % (ETA_SCREW * ETA_BELT, e_b, 24.8, 24.8 * ETA_SCREW * ETA_BELT / e_b))
print("   tooth passage     %.0f Hz at %.0f rpm on 26T (belt is ~390 Hz today)"
      % (26 * N_PEAK / 60.0, N_PEAK))

print("=" * 76)
print("3. OPTION C -- REVERSE THE BELT RUN INSTEAD OF THE SCREW")
print("   Route run 2 from the capstan PAST nut B to a fixed idler at Y_i, then back")
print("   down to nut B. The capstan-to-idler segment is then FIXED length, and the")
print("   idler-to-nut segment shortens as the nut moves proximally:")
print()
print("     L2 = (Y_i - Y_P2) + (Y_i - Y_B) = const - Y_B")
print("     but the belt still demands L2 = L2_0 + R.phi")
print("     so  Y_B = const - R.phi   ...and run 1 still gives  Y_A = const - R.phi")
print()
print("   Both nuts now move the SAME way, by the same amount. Two identical RH screws")
print("   on one shaft do exactly that. The idler has inverted the sign of run 2's")
print("   kinematics, which is the job the opposite thread hand was doing.")
print()
print("   It also flips run 2's reaction: the belt now pulls nut B PROXIMALLY while it")
print("   pulls nut A distally, so the two screws' thrusts oppose at the bearing blocks")
print("   instead of adding. That is a small structural improvement.")
print()
D_IDLER = 80.0
Y_I = max(RUN_B) + 8.0 + D_IDLER / 2.0
print("   Idler must clear the most proximal nut: Y_i >= %.0f + %.0f = %.0f"
      % (max(RUN_B), 8.0 + D_IDLER / 2.0, Y_I))
print("   HTD-8M minimum pulley is 22T = %.0f mm PD, and a BACK-side idler wants"
      % (22 * 8 / math.pi))
print("   ~1.4x that, so ~%.0f mm dia, flat and crowned. Rail ends at Y 284.7." % D_IDLER)
print()
old2 = [b for b in RUN_B]
new2 = [(Y_I - 0.0) + (Y_I - b) + math.pi * D_IDLER / 2.0 for b in RUN_B]
print("   run 2 path length %.0f..%.0f mm  ->  %.0f..%.0f mm  (+%.0f mm of belt)"
      % (min(old2), max(old2), min(new2), max(new2),
         sum(new2) / len(new2) - sum(old2) / len(old2)))
dL = sum(new2) / len(new2) - sum(old2) / len(old2)
print()
print("   THE COST IS LOST MOTION, and it is the only serious one:")
print("   %-14s %10s %10s %12s" % ("belt EA", "stretch", "knee", "vs the 2.45 deg"))
for EA in (150e3, 300e3, 400e3):
    d = T_RUN * dL / EA
    print("   %8.0f kN   %7.2f mm %8.2f deg %10s"
          % (EA / 1e3, d, d * DEG_PER_MM,
             "%+.0f%%" % (100 * d * DEG_PER_MM / LOST_SPRING)))
print("   (EA for a 30 mm HTD-8M is not a number I have -- it wants a datasheet or a")
print("    pull test. The range brackets glass and steel cord.)")
print()
print("   And it is ASYMMETRIC: run 1 is direct, run 2 is %.1fx longer. The knee is"
      % (sum(new2) / sum(old2)))
print("   then more compliant assisting one way than the other.")
print()
print("   Two more things it adds:")
print("     idler shaft load  %.0f N (180 deg wrap, both segments at %.0f N) into a"
      % (2 * T_RUN, T_RUN))
print("       bracket on the rail's slots -- a new ~2 kN load path that does not exist")
print("       today. The only comparable load is the sprung anchor at %.0f N." % T_RUN)
print("     reverse bending   the belt bends backwards over the idler once per stroke.")
print("       HTD belts lose fatigue life to this. It is why the idler has to be big.")
print()
print("   One thing it GIVES BACK, unexpectedly: co-moving carriages sweep the same")
print("   band of rail instead of counter-moving through each other's span.")
print("     counter-moving, today   rail span %.0f mm" % (max(RUN_B) + 78 - min(RUN_A)))
print("     co-moving               rail span %.0f mm" % (102 + STROKE))
print("   -- about %.0f mm shorter, which comes straight off the length up the thigh."
      % ((max(RUN_B) + 78 - min(RUN_A)) - (102 + STROKE)))

print("=" * 76)
print("4. WHAT EACH ONE ACTUALLY COSTS")
OPTS = [
    ("A  LH screw (built)", 25.0, 0, 0.0, 0.0, "special order, MOQ 5 at some factories"),
    ("B  reversing gear", 40.0, 6, 0.013, 0.5, "gear centre distance +/-0.05 mm"),
    ("C  reversing idler", 20.0, 4, 2.00, 0.0, "2 kN bracket, reverse belt bending"),
]
print("   %-22s %7s %7s %9s %8s" % ("option", "$ extra", "parts", "lost deg", "extra A"))
for nm, cost, parts, deg, amps, note in OPTS:
    print("   %-22s %6.0f %7d %8.2f %7.1f   %s" % (nm, cost, parts, deg, amps, note))
print()
print("   Every alternative costs MORE MONEY than the $25 the LH screw costs. The")
print("   premium was never the problem -- procurement was.")
print()
print("   B's real objection is not noise (use one acetal gear against one steel and the")
print("   %.0f N tooth load is nothing). It is that a gear mesh needs its centre distance"
      % F_TOOTH)
print("   held to ~0.05 mm between a screw in a KP08 block and an idler on a printed")
print("   bracket. A belt does not care about +/-1 mm. That tolerance is most of why the")
print("   1:1 link is a belt in the first place. A mesh also has to be fully enclosed:")
print("   an open gear pair at %.0f rpm beside a leg is a pinch hazard, and the knee fin"
      % N_PEAK)
print("   was already rejected for being a snag.")
print()
print("   C's real objection is the %.1f deg, which roughly doubles the lost motion the"
      % 2.0)
print("   design already carries, asymmetrically, plus a new 2 kN printed load path.")
print()
print("   SO: buy the LH screw. It is the only option that adds NOTHING -- no mesh, no")
print("   idler, no bracket, no lost motion, no new load path, no enclosure. And the")
print("   bilateral build wants 4 screws, 2 of each hand, so an MOQ of 5 is nearly the")
print("   right quantity anyway.")
print()
print("   KEEP C AS THE FALLBACK. If the LH quote comes back with a 10-week lead time or")
print("   a silly price, C buys two identical catalogue RH screws for one idler, and it")
print("   is the option that makes every screw in a bilateral build the same part.")
print("=" * 76)
