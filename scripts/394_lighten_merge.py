# -*- coding: utf-8 -*-
"""STAGE 4: lighten the drive bracket, and merge the belt into two static strands.

Two corrections to stages 1-3.

1. A7 came out 230 cm3, which in aluminium is 622 g and swallows most of the saving. The
   bracket does carry the largest single load in the machine -- the idler reaction is
   2*T_b, up to 1828 N -- but it does not need to be solid to do it. Windows out. (The sections themselves
   were then thinned in 393 once 400_bracket_stress.py showed the whole load path
   running at 18 MPa against 240 MPa yield -- about 50x overbuilt.)

2. The belt is a CLOSED LOOP, so both straight strands are geometrically STATIC: the
   clamp slides along the -X strand, the strand itself never moves. 391 split it into a
   lower and an upper piece either side of the clamp, which is wrong -- the belt runs
   continuously through the gantry's slot. One static strand per side.

   Which also means nothing about the belt has to be rebuilt per pose in the sweep. The
   two-screw build had to rebuild two runs every pose because the runs ENDED at the
   carriages. This one does not.

Send with:  python tools/fcsend.py scripts/394_lighten_merge.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
BIN, BOUT = R - 1.372, R + 4.2
BZ = (96.0, 126.0)
IDL_Y = 255.0
T_HI, T_LO = 914.0, 150.0


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


# ------------------------------------------------- merge the -X strand, drop A5e
o = doc.getObject("A5b_Belt_DriveRun")
o.Shape = bx(-BOUT, -BIN, 0.0, IDL_Y, BZ[0], BZ[1])
o.Label = "A5b_Belt_Strand_NegX"
doc.getObject("A5c_Belt_TakeRun").Label = "A5c_Belt_Strand_PosX"
if doc.getObject("A5e_Belt_Return") is not None:
    doc.removeObject("A5e_Belt_Return")
    print("A5e merged into A5b -- the strand is static, the CLAMP moves along it")

# ------------------------------------------------------------------ lighten A7
a = doc.getObject("A7_DriveBox").Shape
v0 = a.Volume / 1000.0
# top and bottom plates: keep a band around the idler axle, window out the rest
for z0, z1 in ((87.0, 93.0), (125.3, 131.3)):        # bands follow 393's 4 mm plates
    for y0, y1 in ((219.0, 236.0), (274.0, 296.0)):
        a = a.cut(bx(-30.0, 30.0, y0, y1, z0, z1))
# cheeks: two windows each
for sgn in (-1.0, 1.0):
    lo, hi = sorted((sgn * 40.5, sgn * 47.5))
    for y0, y1 in ((226.0, 244.0), (266.0, 292.0)):
        a = a.cut(bx(lo, hi, y0, y1, 100.0, 122.0))
# motor plate: corner windows, clear of the motor bore and the screw
for x0, x1 in ((-80.0, -54.0), (36.0, 46.0)):
    for z0, z1 in ((80.0, 94.0), (128.0, 142.0)):
        a = a.cut(bx(x0, x1, 297.0, 307.0, z0, z1))
a = a.removeSplitter()
assert len(a.Solids) == 1, "A7 solids=%d" % len(a.Solids)
assert a.isValid(), "A7 invalid"
o = doc.getObject("A7_DriveBox")
o.Shape = a
print("A7 %.1f -> %.1f cm3  (%.0f -> %.0f g in 6061)"
      % (v0, a.Volume / 1000., v0 * 2.70, a.Volume / 1000. * 2.70))
print()
print("Sizing note for that bracket -- the idler reaction is 2*T_b, and T_b is the")
print("tension in the strand on the FAR side of the capstan from the clamp:")
print("  assist pulling on the lower strand : T_b = %.0f N -> idler sees %.0f N" % (T_LO, 2 * T_LO))
print("  assist pulling on the upper strand : T_b = %.0f N -> idler sees %.0f N" % (T_HI, 2 * T_HI))
print("So the winding sense is a free design choice worth making deliberately: wind it so")
print("EXTENSION assist -- the stair case, section 7 of ELECTRONICS.md -- loads the lower")
print("strand, and the bracket only sees %.0f N in the direction that matters, with %.0f N"
      % (2 * T_LO, 2 * T_HI))
print("reserved for flexion assist, which that section runs at near-zero torque anyway.")

doc.recompute()
doc.save()
print("STAGE 4 DONE, saved. objects now %d" % len(doc.Objects))
