# -*- coding: utf-8 -*-
"""STAGE 2: the gantry as a real plate, not a solid block.

391 built P3 as a filled envelope -- 164 cm3, which in aluminium is 443 g and throws away
the whole reason for switching. A V-wheel gantry is a 6 mm plate with a nut mount under it.

Two geometry lessons paid for here, both caught by asserting solids == 1:

  * The belt strand runs at X -41.12..-35.55, BETWEEN the wheels (|X| <= 31.95) and the
    nut (X -80..-44), so the plate is two decks that must be joined over or under the
    belt. Under is free: past |X| 20 the extrusion has ended, so Z 89..95 is open air.

  * A 36.4 mm bore through a 40 mm housing leaves 3.8 mm of wall on one side and NOTHING
    on the other, because inboard is the belt -- so the housing falls into an upper and a
    lower shell (solids=3, then 2). Boring a 6 mm deck for the same nut does the same.
    The fix is to stop trying to clamp the nut radially: the nut's load is AXIAL, along Y,
    so trap it between two end plates and bore those for the SCREW (16.4 mm) instead of
    the nut (36.4 mm). Nothing gets severed and the load goes in the right direction.

  deck A   X -32.5..32     Y A0+/-35  Z 117..123    carries the 4 mini V-wheels
  web A    X -34.5..-32.5  Y A0+/-35  Z 117..130.2  riser, inboard of the belt
  crossing X -43.8..-32.5  Y A0+/-35  Z 126.3..130.2 OVER the belt (top Z 126)
  deck B   X -84..-42      Y A0+/-29  Z 124.2..130.2 over the nut (top Z 124)
  ends     X -84..-44      Y A0+/-21..29             trap the nut axially, bored 16.4
  spine    X -84..-80.2    Y A0+/-29  Z  89..124     outboard face, ties the ends together
  clamp    X -43.8..-32.5  Y A0+/-9   Z  89..130.2   hangs off the crossing, slotted

Send with:  python tools/fcsend.py scripts/392_gantry.py
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
RX = (-20.0, 20.0)
SCR_X, SCR_Z, SCR_R = -62.0, 106.0, 7.9
NUT_R = 18.0
NUT_HALF = 21.0
A0 = 161.0
PLATE_HALF = 35.0
OUT_HALF = 29.0
C = 0.2                                   # clearance everywhere things merely touch

# A mini V-wheel's groove straddles the corner, so its centre stands off by
# groove_minor/2 along the 45 deg bisector: centre |X| 23.36, Z 111.36, outer |X| 30.97,
# top Z 116.46. Deck A has to clear that top, so it sits at 117.
#
# THE CROSSING GOES OVER THE BELT, NOT UNDER IT. First attempt bridged under the belt at
# Z 89..95 and then climbed outboard of it at X -46..-44 -- but X -44 is the ball nut's
# inboard face, so that riser sat inside the nut (0.93 cm3, found by the 107-pose sweep),
# and clearing the nut severed the plate in two. The corridor between the nut at -44 and
# the belt at -41.12 is 2.88 mm wide, which is not a place to put structure. The belt's
# top is Z 126 and the nut's is Z 124, so there is clean air above BOTH at Z 126.3+.
DECK = (117.0, 123.0)
TOPBR_Z = (126.3, 130.2)
DECK_A_X = (-32.5, 32.0)
WEB_A_X = (-34.5, -32.5)
TOPBR_X = (-43.8, -32.5)
CLAMP_X = (-43.8, -32.5)
OUT_X = (-84.0, -42.0)
DECK_B_Z = (SCR_Z + NUT_R + 0.2, TOPBR_Z[1])
SPINE_X = (-84.0, -80.2)
# The end plates and the spine sit OUTSIDE the nut (in Y and in X respectively), so they
# can run the full height and tie deck B down to the bridge. Stopping them at the nut's
# top left a 0.2 mm gap under deck B and the plate came apart into 6 pieces.
END_Z = (89.0, TOPBR_Z[1])
CLAMP_Y = (A0 - 9.0, A0 + 9.0)
CLAMP_Z = (89.0, TOPBR_Z[1])

def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


assert WEB_A_X[0] > -BIN, "web A is inside the belt band"
assert WEB_B_X[1] < -BOUT, "web B is inside the belt band"
assert BRIDGE[1] < BZ[0], "the bridge is inside the belt band"
assert SPINE_X[1] < SCR_X - NUT_R, "the spine is inside the nut"

PY, PYy = A0 - PLATE_HALF, A0 + PLATE_HALF
OY, OYy = A0 - OUT_HALF, A0 + OUT_HALF

print("belt band X %.3f..%.3f, top Z %.0f ; nut inboard face X %.1f, top Z %.1f"
      % (-BOUT, -BIN, BZ[1], SCR_X + NUT_R, SCR_Z + NUT_R))
print("crossing at Z %.1f..%.1f clears the belt by %.1f and the nut by %.1f"
      % (TOPBR_Z[0], TOPBR_Z[1], TOPBR_Z[0] - BZ[1], DECK_B_Z[0] - (SCR_Z + NUT_R)))
assert TOPBR_Z[0] > BZ[1], "the crossing is inside the belt"
assert DECK_B_Z[0] > SCR_Z + NUT_R, "deck B is inside the nut"
assert WEB_A_X[0] > -BIN, "web A is inside the belt band"
assert TOPBR_X[0] > SCR_X + NUT_R, "the crossing starts inside the nut"
assert SPINE_X[1] < SCR_X - NUT_R, "the spine is inside the nut"

g = bx(DECK_A_X[0], DECK_A_X[1], PY, PYy, *DECK)
g = g.fuse(bx(WEB_A_X[0], WEB_A_X[1], PY, PYy, DECK[0], TOPBR_Z[1]))
g = g.fuse(bx(TOPBR_X[0], TOPBR_X[1], PY, PYy, *TOPBR_Z))
g = g.fuse(bx(OUT_X[0], OUT_X[1], OY, OYy, *DECK_B_Z))
g = g.fuse(bx(SPINE_X[0], SPINE_X[1], OY, OYy, *END_Z))
for sgn in (-1.0, 1.0):
    y = A0 + sgn * (NUT_HALF + C)
    e = bx(OUT_X[0], SCR_X + NUT_R - C, min(y, y + sgn * 8.0), max(y, y + sgn * 8.0), *END_Z)
    e = e.cut(cy(SCR_R + 0.3, A0 - 40.0, A0 + 40.0, SCR_X, SCR_Z))
    g = g.fuse(e)
# clamp: hangs off the crossing and reaches down around the belt, slotted so it never
# overlaps it. This is also what carries the 764 N from the belt into the plate.
cl = bx(CLAMP_X[0], CLAMP_X[1], CLAMP_Y[0], CLAMP_Y[1], *CLAMP_Z)
cl = cl.cut(bx(-BOUT - 0.3, -BIN + 0.3, CLAMP_Y[0] - 1, CLAMP_Y[1] + 1,
               BZ[0] - 0.3, BZ[1] + 0.3))
g = g.fuse(cl)
# guard: the nut must pass everything. After the restructure this should remove nothing.
# The nut cut is limited to the nut's OWN Y span -- over the full plate length it would
# eat the end plates, which are exactly the parts that trap the nut. The screw, which does
# run the full length, gets its own smaller bore.
v_before = g.Volume
g = g.cut(cy(NUT_R + 0.2, A0 - NUT_HALF - 0.2, A0 + NUT_HALF + 0.2, SCR_X, SCR_Z))
print("nut-clearance cut removed %.4f cm3 (should be 0 -- nothing is in the nut's way)"
      % ((v_before - g.Volume) / 1000.0))
v_before = g.Volume
g = g.cut(cy(SCR_R + 0.4, PY - 1, PYy + 1, SCR_X, SCR_Z))
print("screw-clearance cut removed %.4f cm3" % ((v_before - g.Volume) / 1000.0))
# lighten deck A
for dy in (-1, 1):
    g = g.cut(bx(-24.0, 24.0, A0 + dy * 22.0 - 8.0, A0 + dy * 22.0 + 8.0,
                 DECK[0] - 1, DECK[1] + 1))
g = g.removeSplitter()

print("solids=%d valid=%s" % (len(g.Solids), g.isValid()))
assert len(g.Solids) == 1, "P3 solids=%d" % len(g.Solids)
assert g.isValid(), "P3 invalid"
o = doc.getObject("P3_Carriage")
o.Shape = g
o.Label = "P3_GantryPlate_Alu"
b = g.BoundBox
print("P3  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"
      % (b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax))
print("    %.1f cm3 -> %.0f g in 6061, against %.0f g of printed twin carriages"
      % (g.Volume / 1000., g.Volume / 1000. * 2.70, 191. * 2))
doc.recompute()
print("STAGE 2 DONE")
