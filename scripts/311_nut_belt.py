# -*- coding: utf-8 -*-
"""Does an SFU1610 nut (OD 36) at X = +/-58 foul the belt?

This repository said yes, by 1.1 mm, and made "move the screws out to +/-62, widening the
pack by 8 mm" the stated price of choosing the right screw lead. It came from projecting
the nut and the belt onto the X axis and comparing edges: 58 - 18 = 40 against the belt
outer face at 41.1. That comparison never asks whether the two share any length.

They do not. The nut sits at carrA + 36 and its belt run ends at carrA - 24, so they are
60 mm apart along the limb at every pose, by construction. Swept over all 107 poses the
overlap is 0.000 cm3 for OD 28, OD 36 and OD 40 alike.

What does run alongside the belt is the screw shaft, which is clear until |X| < 49.

Run over the XML-RPC client:  python scripts/fc.py run scripts/311_nut_belt.py
"""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
O = lambda n: doc.getObject(n)
K = json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]; C0=K["C0"]; C1=K["C1"]; BZ=tuple(K["belt_z"])
BIN,BOUT = K["belt_x"][0]+0.05, K["belt_x"][1]
NUT_OFF=(36.,78.)
print("nut A spans Y carrA+36..carrA+78 ; belt run A spans Y 0..carrA-24")
print("  -> separation is a constant %.0f mm in Y, at every pose\n" % (36.+24.))
worst = {}
for r, lbl in ((14.0,"SFU1605 OD28"), (18.0,"SFU1610 OD36"), (20.0,"SFU1620 OD40")):
    mx = 0.0; mxth = None
    for s in S:
        cA, cB, th = s["carrA"], s["carrB"], s["theta"]
        beltA = Part.makeBox(BOUT-BIN, cA-24., BZ[1]-BZ[0], V(-BOUT, 0., BZ[0]))
        beltB = Part.makeBox(BOUT-BIN, cB-24., BZ[1]-BZ[0], V(BIN, 0., BZ[0]))
        nutA = Part.makeCylinder(r, NUT_OFF[1]-NUT_OFF[0], V(-58., cA+NUT_OFF[0], 106.), V(0,1,0))
        nutB = Part.makeCylinder(r, NUT_OFF[1]-NUT_OFF[0], V( 58., cB+NUT_OFF[0], 106.), V(0,1,0))
        v = 0.0
        for n_ in (nutA, nutB):
            for b_ in (beltA, beltB):
                if n_.BoundBox.intersect(b_.BoundBox):
                    v += n_.common(b_).Volume/1000.
        if v > mx: mx, mxth = v, th
    print("  %-14s r=%.0f : worst nut/belt overlap over all %d poses = %.3f cm3 %s"
          % (lbl, r, len(S), mx, "" if mx < 0.01 else "@%.0f deg" % mxth))
    worst[lbl] = mx
# and the screw, which DOES run the full length alongside the belt
print("\nthe screw shaft runs Y 110..290 and does share Y with the belt:")
for r, lbl in ((7.9,"SFU16 shaft r=7.9"),):
    for SX in (58.0, 54.0, 50.0, 49.0, 48.0):
        sc = Part.makeCylinder(r, 180., V(-SX, 110., 106.), V(0,1,0))
        bmax = Part.makeBox(BOUT-BIN, 300., BZ[1]-BZ[0], V(-BOUT, 0., BZ[0]))
        v = sc.common(bmax).Volume/1000.
        print("   %s at X=-%.0f : %.3f cm3 %s" % (lbl, SX, v, "clear" if v<0.01 else "CLASH"))
