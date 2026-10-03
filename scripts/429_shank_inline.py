# -*- coding: utf-8 -*-
"""Should the shank rail run in line with the thigh rail, with the hub forked around it?

Asked at the bench, in these words: "A4_Shank2020_VSlot could be directly below the knee and in
line with the 2040 vslot above, which would save a lot of plastic and be stronger... Could
entirely remove the fairing for it too and have P2a on both sides of it, bolted through. Or hell
even on all 4 sides."

This file answers it with the model's own numbers before anything is moved. It changes nothing.

WHAT IS THERE NOW

    thigh rail A1   X +-20   Y  51..207   Z  88..108     centre Z  98
    shank rail A4   X +-10   Y -300..-70  Z  94..114     centre Z 104     6 mm lateral of A1
    P2a's plate     a 6 mm sheet at Z 88..94, reaching from the hub out to Y -149, lying UNDER
                    the rail and bolted up into its bottom slot on 3 x M5 at Y -90, -110, -125

THE LOAD PATH, WHICH IS THE REAL FINDING. The shank carries the full 28.2 N.m of knee torque, and
the only thing joining the hub to the shank rail is that line of three bolts. Three collinear
bolts react a moment in their own plane as a couple about their centroid, so the force on the
outermost one is M * r / sum(r^2):

    bolts at Y -90, -110, -125   centroid Y -108.3   r = 18.3, 1.7, 16.7   sum r^2 = 617 mm^2
    F_outer = 28200 * 18.3 / 617 = 836 N
    bearing on a 5 mm bolt through a 6 mm plate = 836 / 30 = 27.9 MPa

against PETG's ~15 MPa sustained bearing allowable. The joint that carries every newton-metre the
machine makes is at 1.9x its allowable, in single shear, on a part nothing else checks -- 417 sees
three M5 holes of the right size, 420 sees "a bolt pattern to the shank rail >= 3", and the sweep
sees no overlap. It is the same class of miss as the pulley with no teeth: present, correct-looking
and not doing the job.

So the answer to "would it be stronger" is that it has to be.

    freecadcmd.exe scripts/429_shank_inline.py
"""
import math
import os

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

TORQUE = 28200.0        # N.mm at the knee
PETG_BEAR = 15.0        # MPa, sustained
M5 = 5.0
TIP, BACK = 36.237, 38.457      # capstan tip, belt back (421/423)


def couple(ys, plates, thick, bolt=M5):
    """force on the outermost bolt of a line, and the bearing it puts on each plate"""
    c = sum(ys) / len(ys)
    s2 = sum((y - c) ** 2 for y in ys)
    f = TORQUE * max(abs(y - c) for y in ys) / s2
    return f, f / plates / (bolt * thick)


print("=" * 98)
print("SHANK RAIL IN LINE WITH THE THIGH RAIL?  --  %s" % _BASE)
print("=" * 98)

a1, a4 = doc.getObject("A1_Extrusion_20x60_VSlot"), doc.getObject("A4_Shank2020_VSlot")
b1, b4 = a1.Shape.BoundBox, a4.Shape.BoundBox
print("  thigh rail   Z %6.1f..%6.1f  centre %6.2f" % (b1.ZMin, b1.ZMax, 0.5 * (b1.ZMin + b1.ZMax)))
print("  shank rail   Z %6.1f..%6.1f  centre %6.2f   %.1f mm lateral of the thigh rail"
      % (b4.ZMin, b4.ZMax, 0.5 * (b4.ZMin + b4.ZMax),
         0.5 * (b4.ZMin + b4.ZMax) - 0.5 * (b1.ZMin + b1.ZMax)))

print()
print("  THE JOINT AS DRAWN")
f, s = couple([-90.0, -110.0, -125.0], 1, 6.0)
print("     3 x M5 in a line over 35 mm, single shear, 6 mm plate")
print("     %6.0f N on the end bolt -> %5.1f MPa bearing   (%s %.1f MPa sustained)"
      % (f, s, "OVER" if s > PETG_BEAR else "under", PETG_BEAR))

print()
print("  THE JOINT FORKED, bolts through both cheeks in double shear")
for span, n, th in ((46.0, 2, 6.0), (46.0, 2, 8.0), (60.0, 2, 8.0), (60.0, 3, 8.0)):
    ys = [-44.0 - (span / (n - 1)) * i for i in range(n)]
    f, s = couple(ys, 2, th)
    print("     %d bolts over %.0f mm, %.0f mm cheeks : %5.0f N -> %5.1f MPa   %s"
          % (n, span, th, f, s, "ok" if s <= PETG_BEAR else "OVER"))

print()
print("  HOW FAR UP THE RAIL CAN COME. The belt wraps the capstan over Y <= 0 at radius")
print("  %.2f..%.2f, so the rail's end must stay outside that circle:" % (TIP, BACK))
for y in (-34.0, -38.0, -42.0, -46.0, -50.0, -70.0):
    r = math.hypot(10.0, abs(y))          # the rail's near corner, X 10
    print("     rail end at Y %6.1f : nearest corner is %5.1f mm from the knee axis  %s"
          % (y, r, "CLEAR" if r > BACK + 2.0 else "FOULS THE BELT"))

print()
print("  WHAT IT WOULD COST AND SAVE")
p2a = doc.getObject("P2a_KneeHingePlate").Shape
reach = p2a.common(Part.makeBox(90.0, 109.0, 30.0, V(-45.0, -149.0, 86.0)))
print("     P2a's reach-down plate, Y -149..-40 at Z 86..116      %6.1f cm3" % (reach.Volume / 1000.0))
fair = doc.getObject("P24_FairingShank")
print("     P24_FairingShank, if the shank needs no cladding      %6.1f cm3"
      % (fair.Shape.Volume / 1000.0 if fair else 0.0))
per_mm = a4.Shape.Volume / 1000.0 / (b4.YMax - b4.YMin)
print("     extra extrusion to bring the rail up to Y -44         %6.1f cm3 (%.0f g of 6063)"
      % (per_mm * 26.0, per_mm * 26.0 * 2.70))
print()
print("  Printed mass changes by roughly %+.0f g, and the joint that carries the torque goes from"
      % ((-(reach.Volume / 1000.0) * 0.5 - (fair.Shape.Volume / 1000.0 if fair else 0)) * 1.27))
print("  1.9x its allowable to inside it. The mass is incidental; the bearing stress is the point.")
print()
print("  WHAT MOVING THE RAIL IN Z DRAGS WITH IT -- everything that touches the shank rail:")
for nm in ("P6_ShankSocket", "P31_InterfaceDist", "P7_ShankCuff", "P24_FairingShank",
           "P2a_KneeHingePlate"):
    o = doc.getObject(nm)
    if o is None:
        continue
    bb = o.Shape.BoundBox
    print("     %-22s Z %6.1f..%6.1f   %6.1f cm3" % (nm, bb.ZMin, bb.ZMax, o.Shape.Volume / 1000.0))
print()
print("  A 6 mm move in Z is not a 6 mm job: the socket wraps the rail, the KX-1 distal interface")
print("  sits on it, the cuff hangs off it and the fairing covers it. Four parts re-cut, re-swept,")
print("  re-engraved and re-mirrored for a 6 mm alignment -- worth doing with the fork, which is")
print("  the part that matters, and not worth doing on its own.")
