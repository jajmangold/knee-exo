# -*- coding: utf-8 -*-
"""Is a Delrin mini V-wheel actually good for 362 N? OpenBuilds does not say.

The BOM has been carrying "check its load rating against 362 N per wheel" as an open item.
There is nothing to check against: OpenBuilds publishes the mini V-wheel's geometry
(OD 15.4, thickness 8.8, bore 9.974) and its material (Delrin, Rockwell M80, compressive
strength 63 MPa) and no load rating at all. So compute it.

The wheel's 90 deg groove sits on the extrusion's 90 deg corner, so the reaction splits
across two flanks at 45 deg. Each flank is a Hertzian LINE contact between the wheel's
conical face and the extrusion's flat.

Run:  python scripts/401_vwheel_load.py
"""
import math

MZ = 18.1                 # N.m, yaw couple on the gantry (390_onescrew_section.py)
OD, THK = 15.4, 8.8       # mm, OpenBuilds Delrin mini V wheel
FLANK_L = 3.0             # mm of contact length per flank -- the groove's flank width
R_EFF = OD / 2.0          # mm, wheel radius at the contact
E_DELRIN, NU_D = 3000.0, 0.35      # MPa
E_ALU, NU_A = 69000.0, 0.33
SY_DELRIN = 63.0          # MPa compressive strength, the only strength number published
# Hertzian contact yields when p_max reaches about 1.6 x the uniaxial yield, because the
# material under the contact is triaxially confined.
P_ONSET = 1.6 * SY_DELRIN

ESTAR = 1.0 / ((1 - NU_D ** 2) / E_DELRIN + (1 - NU_A ** 2) / E_ALU)

print("=" * 74)
print("CONTACT MODEL")
print("  E* = %.0f MPa (Delrin %.0f on aluminium %.0f)" % (ESTAR, E_DELRIN, E_ALU))
print("  90 deg groove on a 90 deg corner -> each flank carries F/(2 cos45) = %.3f F"
      % (1.0 / (2 * math.cos(math.radians(45)))))
print("  line contact, half-width b = sqrt(4 F R / (pi L E*)), p_max = 2F/(pi b L)")
print("  Delrin yields under a confined contact at about 1.6 x %.0f = %.0f MPa"
      % (SY_DELRIN, P_ONSET))
print()
print("  %-12s %9s %10s %9s %9s  %s"
      % ("wheel span", "N/wheel", "N/flank", "b mm", "p_max", "verdict"))


def pmax(f_wheel):
    f = f_wheel / (2.0 * math.cos(math.radians(45)))
    b = math.sqrt(4.0 * f * R_EFF / (math.pi * FLANK_L * ESTAR))
    return f, b, 2.0 * f / (math.pi * b * FLANK_L)


for span in (50.0, 60.0, 70.0, 80.0):
    fw = MZ * 1000.0 / span
    f, b, p = pmax(fw)
    print("  %8.0f mm %8.0f N %9.0f N %8.3f %7.0f MPa  %s"
          % (span, fw, f, b, p,
             "at the yield onset" if p > P_ONSET * 0.95 else
             "%.0f%% margin" % (100 * (P_ONSET / p - 1))))

print()
print("  AS BUILT the wheels are 50 mm apart and that lands at %.0f MPa -- right ON the"
      % pmax(MZ * 1000.0 / 50.0)[2])
print("  onset. Not a failure, but it means the contact flattens and the gantry develops")
print("  play, which on a torque-controlled assist shows up as backlash at every reversal.")
print("  Widening to 70 mm brings it to %.0f MPa -- an 11%% margin, which is thin but is"
      % pmax(MZ * 1000.0 / 70.0)[2])
print("  the most available: 80 mm would give 19%% and push the idler from Y 255 to 257,")
print("  and proximal length is the one budget with nothing left in it (390 section 7).")

print("=" * 74)
print("WHAT 70 mm COSTS")
R = 29 * 8.0 / (2 * math.pi)
A0, W_R = 161.0, 15.23 / 2
YC_MIN, YC_MAX = A0 - R * math.radians(104.0), A0 - R * math.radians(-2.0)
for span, plate_half in ((50.0, 35.0), (70.0, 42.0)):
    wy = span / 2.0
    lo, hi = YC_MIN - wy - W_R, YC_MAX + wy + W_R
    print("  span %2.0f mm: wheels at clamp +/-%2.0f, footprint Y %.1f..%.1f, plate +/-%.0f"
          % (span, wy, lo, hi, plate_half))
    print("             rail must run Y %.0f..%.0f (%.0f mm), idler no closer than Y %.1f"
          % (math.floor(lo), 207, 207 - math.floor(lo), YC_MAX + plate_half + 6 + (R + 4.2)))
print("  So it costs 5 mm off the distal end of the rail and a longer gantry plate --")
print("  about 24 g all told, and the idler stays where it is at Y 255.")

print("=" * 74)
print("THE OTHER OPTION IS STILL THERE")
print("  MGN7H on the same 2040's side faces: ~1.0 kN dynamic against %.0f N, and a steel"
      % (MZ * 1000.0 / 50.0))
print("  recirculating block does not flatten. It costs the V-wheel gantry the user")
print("  already owns, and 310_guides.py measured its rolling friction at 1.4 N against")
print("  the wheels' rather higher polymer hysteresis.")
print()
print("  RECOMMENDATION: widen to 70 mm and keep the wheels, but treat the 11%% as thin")
print("  rather than comfortable. It costs 24 g and uses hardware already on the shelf.")
print("  Bench-test for play at reversal before trusting it; MGN7 is the fallback and it")
print("  drops into the same 2040 side faces.")
print("  And note what this rests on: ONE published number, a 63 MPa compressive strength,")
print("  pushed through a Hertz model with an assumed 3 mm flank length. A measured load")
print("  rating from the supplier would beat all of it.")
print("=" * 74)
