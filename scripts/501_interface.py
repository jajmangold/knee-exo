# -*- coding: utf-8 -*-
"""The KX-1 module interface: what it has to carry, and therefore how big it is.

500_as_a_module.py named a structural interface at both ends as the one thing expensive to
retrofit. This sizes it. The trap is sizing it for TODAY's load.

Standalone, the interface would only ever relieve the cuff: 148 N at the thigh, 104 N at the
shank. Federated with a load-to-ground structure, the same joint carries body weight plus
device weight plus a dynamic factor, which is an order of magnitude more. An interface sized
for the first number is scrap the day the second module arrives -- which is the exact failure
this whole exercise is meant to avoid.

So: size for the system, use it standalone.

Pure Python, no FreeCAD.
"""
import math

BW = 80.0
M_DEV_FULL = 20.0        # kg of federated exo, from 500's shed table (8 x 2.53)
G = 9.81
DYN = 1.5                # heel strike; 1.3-1.8 in the literature, take the middle-high
SF = 2.0                 # on a wearable, against a printed part, under cyclic load

print("=" * 84)
print("WHAT THE INTERFACE HAS TO CARRY")
print("=" * 84)
CASES = [
    ("standalone: relieve the thigh cuff", 28.2 / 0.190, "the couple the cuff reacts today"),
    ("standalone: relieve the shank cuff", 28.2 / 0.270, "ditto, distal end"),
    ("federated: carry the device", M_DEV_FULL * G, "exo weight through the leg structure"),
    ("federated: load to ground, stance", (BW + M_DEV_FULL) * G * DYN,
     "body + device, single-leg stance, x%.1f dynamic" % DYN),
]
worst = 0.0
for lbl, f, why in CASES:
    worst = max(worst, f)
    print("  %-36s %7.0f N   %s" % (lbl, f, why))
print()
print("  Design load = worst case x SF %.1f = %.0f N" % (SF, worst * SF))
DES = worst * SF

print()
print("=" * 84)
print("SIZING, PRINTED PETG")
print("=" * 84)
SY_PETG = 45.0           # MPa tensile at break; design well under it
ALLOW = 12.0             # MPa, allowing for layer adhesion, creep and cyclic load
print("  PETG breaks around %.0f MPa. Design allowable %.0f MPa -- a third of it -- because"
      % (SY_PETG, ALLOW))
print("  this is a layered part under cyclic load on a person, and PETG creeps under")
print("  sustained stress in a way the tensile number does not show.")
print()
a_need = DES / ALLOW
print("  section needed in tension: %.0f N / %.0f MPa = %.0f mm2" % (DES, ALLOW, a_need))
for w, t in ((40.0, 6.0), (50.0, 8.0), (50.0, 10.0), (60.0, 8.0)):
    a = w * t
    print("     %2.0f x %-4.0f plate = %4.0f mm2   %s  (%.1fx)"
          % (w, t, a, "OK " if a > a_need else "NO ", a / a_need))
print()
M5_AREA = 14.2           # mm2 stress area
print()
print("  BEARING is what sizes this, not tension and not the bolts. 4 x M5 fails at every")
print("  sensible thickness:")
for nb in (4, 6):
    print("     %d bolts: %.0f N each" % (nb, DES / nb))
    for t in (8.0, 10.0, 12.0):
        brg = DES / nb / (5.0 * t)
        print("        %4.0f mm thick -> %5.1f MPa  %s"
              % (t, brg, "OK" if brg < ALLOW else "over the %.0f MPa allowable" % ALLOW))
print()
print("  So the pattern is SIX bolts, not four. Worth getting right now: bolt count is the")
print("  one thing in a mating pattern that cannot be changed later without changing both")
print("  halves. In aluminium (6061, ~%.0f MPa allowable) the same pattern needs only %.1f mm"
      % (80.0, DES / 6 / (5.0 * 80.0)))
print("  of bearing thickness, so the SAME holes work in a 6 mm plate.")
print()
print("  Which is the resolution: the PATTERN is the standard, the PART is sized per use.")
STANDALONE = CASES[0][1] * SF
print("     standalone, this module      %.0f N design -> %.1f MPa bearing in 8 mm PETG, fine"
      % (STANDALONE, STANDALONE / 6 / (5.0 * 8.0)))
print("     federated, load to ground    %.0f N design -> wants 6 mm aluminium, same holes"
      % DES)
print("  This module gets the printed version today and nothing has to be redesigned when a")
print("  leg that carries weight needs the metal one.")
print()
print("=" * 84)
print("THE PATTERN  --  KX-1")
print("=" * 84)
print("  A pattern is a contract, so it needs to be boring and fully constrained:")
print()
print("     face          56 x 40 mm flat; 10 mm boss printed, 6 mm if aluminium")
print("     bolts         6 x M5 clearance 5.5, at X -18/0/+18 by Z +/-9 -- six because")
print("                   BEARING in a printed boss sizes this, not tension")
print("     location      2 x dia 5 H7 dowels at (+/-24, 0) -- two pins fully constrain the")
print("                   joint in plane, which matters because this interface sets where the")
print("                   joint axis ends up relative to the patient's")
print("     frame         face origin on the module axis, +X of the face along +Y of the")
print("                   module (proximal), face normal pointing OUT of the module")
print("     identity      part number engraved beside it (412), so a cold module is")
print("                   identifiable without a BOM")
print()
print("  Two dowels and six bolts is deliberately more than %.0f N needs. It is sized for the"
      % (CASES[0][1]))
print("  %.0f N stance case so that the standalone knee and a future load-bearing leg use the"
      % CASES[3][1])
print("  SAME interface, which is the entire point of fixing it now.")
print()
print("  What it cost this module, as built by 502: P30 %.0f g and P31 %.0f g, and nothing out"
      % (35.0, 26.0))
print("  of the interconnect budget -- both lie inside the existing envelope, the proximal one")
print("  by piercing the drive shell through a port it then fills. That mattered because 500")
print("  showed only %d mm above the drive end before the hip joint centre." % 95)
