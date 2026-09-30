# -*- coding: utf-8 -*-
"""Would two smaller screws carry the load? They would -- and so would one, easily.

The premise is worth testing before the answer: nothing about the SFU1610 was ever chosen
for load. It was chosen for its LEAD, because lead sets the ratio (2*pi*R/lead), and the
16 mm diameter simply came attached to the 10 mm lead in the SFU16xx series.

So the real question is not "can two smaller screws share 764 N" -- one small screw is
already an order of magnitude over. It is "what does the diameter actually cost us", and
the answer turns out to be about 240 g and 8 mm of the device's width.

Run:  python scripts/405_screw_size.py
"""
import math

R_CAP = 36.924
F_NUT = 28.2 * 1000.0 / R_CAP      # 764 N, set by the capstan radius
F_PRE = 150.0
F_PEAK = F_NUT + F_PRE
L_SCREW = 244.0                    # mm, Y 70..314
RPM = 1160.0
E = 200000.0                       # MPa, steel
BELT_OUT = 41.124
BOUT_GAP = 2.0
STROKE = 68.31
LINK_OVERDRIVE = 20.0 / 32.0

# d, lead, root d, nut OD, typical C_dyn (N) from supplier tables
SCREWS = [("SFU1005", 10.0, 5.0, 8.5, 24.0, 4200.0),
          ("SFU1204", 12.0, 4.0, 10.2, 28.0, 6300.0),
          ("SFU1210", 12.0, 10.0, 10.2, 28.0, 7800.0),
          ("SFU1610 (built)", 16.0, 10.0, 13.8, 36.0, 12500.0),
          ("SFU1605", 16.0, 5.0, 13.8, 28.0, 10000.0)]

print("=" * 80)
print("1. IS LOAD EVER THE CONSTRAINT?  peak axial %.0f N" % F_PEAK)
print("   %-16s %9s %10s %11s %13s" % ("screw", "C_dyn", "SF on C", "buckling SF", "L10 life"))
for nm, d, lead, dr, od, c in SCREWS:
    I = math.pi * dr ** 4 / 64.0
    pcr = math.pi ** 2 * E * I / L_SCREW ** 2
    revs = (c / F_PEAK) ** 3 * 1e6
    cycles = revs / (STROKE / lead)
    print("   %-16s %7.0f N %8.1fx %10.1fx %9.2e gait cycles"
          % (nm, c, c / F_PEAK, pcr / F_PEAK, cycles))
print()
print("   Even the SMALLEST, an SFU1005, is %.1fx over on rated load and %.0fx on buckling,"
      % (SCREWS[0][5] / F_PEAK, math.pi ** 2 * E * (math.pi * 8.5 ** 4 / 64.0) / L_SCREW ** 2 / F_PEAK))
print("   with a fatigue life of %.0f million gait cycles." % ((4200.0 / F_PEAK) ** 3 * 1e6 / (STROKE / 5.0) / 1e6))
print("   So no, we do not need two screws to carry anything. We never needed the one we")
print("   have to be 16 mm.")

print("=" * 80)
print("2. CRITICAL SPEED -- the other thing that usually sizes a screw")
print("   n_cr ~ 1.27e8 * d_root / L^2 for simple supports; the screw runs at %.0f rpm." % RPM)
for nm, d, lead, dr, od, c in SCREWS:
    ncr = 1.27e8 * dr / L_SCREW ** 2
    print("   %-16s %8.0f rpm  -> %.0fx margin" % (nm, ncr, ncr / RPM))
print("   Also never binding. The screw is short and slow.")

print("=" * 80)
print("3. WHAT THE DIAMETER ACTUALLY COSTS")
print("   The nut's OD sets how close the screw can sit to the belt band at |X| %.2f,"
      % BELT_OUT)
print("   and that sets the device's fore-aft width on that side.")
print()
print("   %-16s %7s %9s %11s %10s %9s" %
      ("screw", "nut OD", "screw X", "gantry to", "screw g", "nut g"))
for nm, d, lead, dr, od, c in SCREWS:
    sx = -(BELT_OUT + BOUT_GAP + od / 2.0)
    gantry = sx - od / 2.0 - 4.0
    m_screw = math.pi * (d / 2.0) ** 2 * L_SCREW / 1000.0 * 7.85
    m_nut = 180.0 * (od / 36.0) ** 2
    print("   %-16s %5.0f mm %8.1f %10.1f %8.0f g %7.0f g"
          % (nm, od, sx, gantry, m_screw, m_nut))
print()
b = [s for s in SCREWS if s[0].startswith("SFU1610")][0]
t = [s for s in SCREWS if s[0] == "SFU1210"][0]
dm = (math.pi * (b[1] / 2) ** 2 - math.pi * (t[1] / 2) ** 2) * L_SCREW / 1000.0 * 7.85
dn = 180.0 - 180.0 * (t[4] / 36.0) ** 2
dx = (b[4] - t[4]) / 2.0
print("   SFU1610 -> SFU1210, keeping the 10 mm lead:")
print("     mass      %.0f g of screw + %.0f g of nut = %.0f g off the limb" % (dm, dn, dm + dn))
print("     width     the screw moves in %.0f mm and the gantry's outboard edge %.0f --"
      % (dx, 2 * dx))
print("               and the MOTOR can follow. It has to clear the screw by %.1f mm"
      % (31.5 + 6.0 + 2.5))
print("               (402_motor_anterior.py), which with a 12 mm screw means X <= %.0f"
      % (-(BELT_OUT + BOUT_GAP + 14.0) - 40.0))
print("               instead of -104, taking about %.0f mm off the front of the cap too."
      % (104.0 - 97.0))
print("     ratio     unchanged -- same lead, so still %.1f:1 before the overdrive and"
      % (2 * math.pi * R_CAP / 10.0))
print("               %.1f:1 after it" % (2 * math.pi * R_CAP / 10.0 * LINK_OVERDRIVE))

print("=" * 80)
print("4. AND THE LEAD ANGLE GETS BETTER, NOT WORSE")
print("   Backdrivability is a core requirement here -- power off must leave a free")
print("   swinging brace. It depends on the LEAD ANGLE, and a narrower screw at the same")
print("   lead has a STEEPER one:")
print()
RHO = 0.6
print("   %-16s %10s %12s %12s" % ("screw", "lead angle", "eta fwd", "eta backdrive"))
for nm, d, lead, dr, od, c in SCREWS:
    beta = math.degrees(math.atan(lead / (math.pi * d)))
    ef = math.tan(math.radians(beta)) / math.tan(math.radians(beta + RHO))
    eb = math.tan(math.radians(beta - RHO)) / math.tan(math.radians(beta))
    print("   %-16s %8.1f deg %10.3f %11.3f" % (nm, beta, ef, eb))
print()
print("   SFU1210 is the steepest of the lot at %.1f deg. The gain in backdrive efficiency"
      % math.degrees(math.atan(10.0 / (math.pi * 12.0))))
print("   is only about a point, and PRIOR_ART.md notes most of the real backdrive torque")
print("   is motor cogging multiplied by the ratio rather than screw friction -- so treat")
print("   this as a small bonus, not the reason.")

print("=" * 80)
print("VERDICT")
print("   TWO screws: no. The load case does not need them, and the one-screw layout was")
print("   bought at some cost -- a second screw brings back the second nut, the")
print("   synchronisation between them, and the matched-lead tolerance stack that")
print("   390_onescrew_section.py was pleased to delete.")
print()
print("   ONE smaller screw: yes, and it is worth doing. SFU1210 keeps the 10 mm lead")
print("   that sets the ratio, is still %.0fx over on load and %.0fx on buckling, saves"
      % (7800.0 / F_PEAK, math.pi ** 2 * E * (math.pi * 10.2 ** 4 / 64.0) / L_SCREW ** 2 / F_PEAK))
print("   about %.0f g, brings the screw and the whole gantry %.0f mm inboard, and has a"
      % (dm + dn, dx))
print("   steeper lead angle into the bargain.")
print()
print("   Check before ordering: SFU1210's nut is OD 28 in most tables but the flangeless")
print("   body varies by supplier, and the gantry is bored for %.0f. That bore is the one"
      % 36.0)
print("   dimension that has to be right -- 392_gantry.py traps the nut between end plates")
print("   rather than clamping it radially, so the END PLATE spacing is what changes, not")
print("   a clamp diameter.")
print("=" * 80)
