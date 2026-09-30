# -*- coding: utf-8 -*-
"""Can the thigh rail drop from 20x60 to 20x40?

V-wheels ride the extrusion's outer corner V -- the land between two 20-series slots is
about 10 mm of flat and a wheel groove bottoms out on it before its 45 deg flanks engage.
So the wheel centre sits at the corner, |X| = half the profile width, and the wheel
reaches half its OD beyond that. On a 2060 the corners are at |X| 30 and the belt runs
start at |X| 35.55, so even a mini wheel fouls. Narrowing the profile is the only way to
make wheels fit without moving the belt, and the belt cannot move: it is tangent to the
29T pulley and that radius IS the 36.92 mm moment arm.

The question is therefore whether the rail can afford to lose the section.

Run:  python scripts/320_rail_section.py
"""
import math

BIN = 35.55                 # belt run inner face
E = 69e9                    # aluminium
M_HUB = 18.5                # N.m, the knee reaction the rail carries
L = 0.2267                  # m, rail Y 58..284.7
VSLOT_FILL = 0.60           # a V-slot profile keeps roughly 60% of the solid second moment

print("=" * 68)
print("DOES A WHEEL FIT?  (wheel centre at the corner, reaches OD/2 beyond)")
print("  %-10s %8s   %-18s %-18s" % ("profile", "corner", "mini 15.23", "solid 23.89"))
for w in (60.0, 50.0, 40.0, 30.0):
    c = w / 2.0
    row = ""
    for od in (15.23, 23.89):
        hi = c + od / 2.0
        row += "  %-18s" % ("clear %.1f mm" % (BIN - hi) if hi <= BIN
                            else "FOULS %.1f mm" % (hi - BIN))
    print("  20x%-7.0f %6.1f   %s" % (w, c, row))

print("=" * 68)
print("WHAT DOES THE SECTION COST?")
print("  the belt pull yaws the carriage about Z, so the depth that matters is the")
print("  60 mm dimension. Deflection of the rail under the %.1f N.m hub reaction," % M_HUB)
print("  as a cantilever of %.0f mm:  d = M L^2 / (2 E I)" % (L * 1000))
print()
print("  %-10s %12s %12s %12s" % ("profile", "I (cm^4)", "rel. I", "tip defl."))
base = None
for w in (60.0, 50.0, 40.0):
    I = 0.020 * (w / 1000.0) ** 3 / 12.0 * VSLOT_FILL      # m^4
    if base is None:
        base = I
    d = M_HUB * L ** 2 / (2 * E * I)
    print("  20x%-7.0f %12.2f %12.2f %9.3f mm"
          % (w, I * 1e8, I / base, d * 1000))
print()
print("  Both are negligible against the 2.45 deg of lost motion the sprung anchor")
print("  already contributes -- 0.1 mm at the cuff is about 0.06 deg at the knee.")
print("  The rail is enormously overstiff for this load either way, so the section is")
print("  NOT what should decide the profile.")
print("=" * 68)
print("WHAT NARROWING ACTUALLY COSTS")
print("  * every carriage, slider pocket and fairing spine references |X| = 30")
print("  * the fairing spine uses the middle outboard slot at X = 0; a 20x40 keeps it")
print("  * the belt-to-rail gap grows from %.1f to %.1f mm, which is what buys the wheels"
      % (BIN - 30.0, BIN - 20.0))
print("  * fore-aft, the rail itself narrows by 20 mm, though the carriages and nuts")
print("    still set the envelope at |X| 80")
print("=" * 68)
