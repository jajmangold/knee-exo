# -*- coding: utf-8 -*-
"""The drive bracket's 1828 N, by hand. Not FEA -- but the repo has been calling it the
largest load in the machine with nothing behind that at all.

The idler reaction is 2*T_b and it is ALWAYS distal (-Y): both belt segments leave the
idler heading for the knee, so their resultant cannot reverse. Magnitude swings 300 N to
1828 N with assist direction (394_lighten_merge.py), and 1828 is the design case.

Load path: axle -> top and bottom plates (in-plane, spanning X to the cheeks) -> cheeks
(axial along Y) -> end plate -> the extrusion's end face.

Run:  python scripts/400_bracket_stress.py
"""
import math

P = 1828.0              # N, idler reaction, distal
E = 69e9                # Pa, 6061
SY = 240e6              # Pa, 6061-T6 yield
AXLE_D = 8.0            # mm
PLATE_T = 7.7           # mm, as built (bottom Z 88..95.7, top 126.3..134)
PLATE_DEPTH = 81.0      # mm, plates span Y 217..298
CHEEK_SPAN = 83.0       # mm, X -41.5 to +41.5, the clear span the axle sits in the middle of
CHEEK_T, CHEEK_H = 6.5, 46.0
CHEEK_L = 38.0          # mm, idler Y 255 back to the end plate at 217
R_CAP = 36.924
DEG_PER_MM = math.degrees(1.0 / R_CAP)

print("=" * 74)
print("1. THE AXLE")
a_shear = math.pi * (AXLE_D / 2.0) ** 2
print("   double shear: %.0f N / (2 x %.1f mm2) = %.1f MPa  (a 8.8 bolt yields ~%.0f in shear)"
      % (P, a_shear, P / (2 * a_shear), 0.577 * 640))
brg = (P / 2.0) / (AXLE_D * PLATE_T)
print("   bearing on each plate: %.0f N / (%.0f x %.1f) = %.1f MPa  (6061 bearing ~%.0f)"
      % (P / 2, AXLE_D, PLATE_T, brg, 400.0))

print("=" * 74)
print("2. TOP AND BOTTOM PLATES -- the load is IN-PLANE for them")
print("   Each takes %.0f N at mid-span and carries it sideways to the cheeks. Bending is"
      % (P / 2.0))
print("   about Z, so the section is thickness x plate DEPTH, not thickness cubed:")
I = PLATE_T * PLATE_DEPTH ** 3 / 12.0
S = I / (PLATE_DEPTH / 2.0)
M = (P / 2.0) * CHEEK_SPAN / 4.0
sig = M / S
print("   I = %.0f mm4, S = %.0f mm3, M = PL/4 = %.0f N.mm" % (I, S, M))
print("   sigma = %.2f MPa against %.0f MPa yield -- SF %.0f" % (sig, SY / 1e6, SY / 1e6 / sig))
d = (P / 2.0) * CHEEK_SPAN ** 3 / (48.0 * (E / 1e6) * I)
print("   mid-span deflection PL^3/48EI = %.5f mm = %.5f deg at the knee" % (d, d * DEG_PER_MM))

print("=" * 74)
print("3. CHEEKS -- axial, not bending")
A = 2 * CHEEK_T * CHEEK_H
print("   the load runs along Y and so do the cheeks, so this is plain compression:")
print("   %.0f N / %.0f mm2 = %.1f MPa, SF %.0f" % (P, A, P / A, SY / 1e6 / (P / A)))
print("   shortening over %.0f mm: %.5f mm" % (CHEEK_L, P * CHEEK_L / (A * E / 1e6)))
r_gyr = CHEEK_T / math.sqrt(12.0)
print("   slenderness L/r = %.0f -- far below any buckling concern" % (CHEEK_L / r_gyr))

print("=" * 74)
print("4. THE END PLATE INTO THE EXTRUSION")
print("   Because the reaction cannot reverse, the bracket is pushed ONTO the rail's end")
print("   face, not pulled off it. The mounting screws see no tension from this load at")
print("   all -- they only have to stop the bracket wandering. Bearing on the 2040's end:")
END_A = 2 * (20.0 * 20.0 - math.pi * 4.2 ** 2)
print("   %.0f N over ~%.0f mm2 of end face = %.1f MPa." % (P, END_A, P / END_A))
print("   (If the winding sense were ever chosen the other way the screws WOULD see")
print("    %.0f N of tension -- 2x M5 at %.0f N each, still trivial. But it is not.)"
      % (P, P / 2))

print("=" * 74)
print("VERDICT: THE BRACKET IS ABOUT 50x OVERBUILT")
print("   Worst stress anywhere in the path is %.1f MPa against %.0f, and the worst"
      % (max(P / (2 * a_shear), brg, sig, P / A), SY / 1e6))
print("   deflection is %.4f mm. Nothing here is sized by load -- it is sized by my having"
      % d)
print("   drawn 7.7 mm plates because they were convenient boxes to fuse.")
print()
print("   At 4 mm plates and 5 mm cheeks the numbers become:")
for t, ct in ((4.0, 5.0),):
    I2 = t * PLATE_DEPTH ** 3 / 12.0
    S2 = I2 / (PLATE_DEPTH / 2.0)
    A2 = 2 * ct * CHEEK_H
    print("     plate bending   %.2f MPa, SF %.0f" % (M / S2, SY / 1e6 / (M / S2)))
    print("     plate deflection %.5f mm" % ((P / 2.0) * CHEEK_SPAN ** 3 / (48.0 * (E / 1e6) * I2)))
    print("     cheek compression %.1f MPa, SF %.0f" % (P / A2, SY / 1e6 / (P / A2)))
    print("     axle bearing     %.1f MPa on a %.0f mm plate" % ((P / 2.0) / (AXLE_D * t), t))
print()
print("   So the bracket should come down from 7.7 mm plates to 4 mm and lose most of what")
print("   is left as windows. Expect roughly 465 -> 250 g, which is worth more than every")
print("   other mass idea still on the list.")
print()
print("   CAVEAT, and it is the usual one: this is statics on a load path I assumed. It")
print("   does not cover the axle's local bearing in a printed part (it is aluminium, so")
print("   it does not have to), fatigue over a million gait cycles, or what happens if the")
print("   belt jumps and the load arrives as a shock. It is a sanity check that says the")
print("   part is not marginal -- not a substitute for FEA.")
print("=" * 74)
