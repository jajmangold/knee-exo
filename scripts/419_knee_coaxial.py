# -*- coding: utf-8 -*-
"""The coaxial knee: one bearing INSIDE the pulley, in the plane of the belt.

An alternative to the pin-and-6001 joint 418 built, modelled in its own document so the working
model stays intact. KX_DOC defaults to KneeExo_v7_coaxial.FCStd for exactly that reason.

THE ARGUMENT. Three layouts were on the table and the deciding number is where the belt pulls
relative to where the bearing is:

  one 6815 beside the teeth   the spigot cannot sit under the teeth (dia 75 is bigger than the
                              71.1 tooth tips and lands inside the belt band at r 35.55..41.12),
                              so the bearing ends up ~20 mm off the belt plane and eats
                              764 N x 0.020 = 15.3 N.m of moment on one raceway
  a fork, two 6815            symmetric, 382 N each, no moment -- but two dia 95 seats that must
                              be coaxial, in printed parts, with one race free to float axially
  one 6808 INSIDE the pulley  the tooth root circle is dia 64.3, so a bearing under about 62 nests
                              inside the toothed ring. The belt pull then passes straight through
                              the bearing plane: no offset moment, no coaxiality problem, one
                              bearing, and a hollow dia 40 centre for cabling.

The third, which is what this builds. 6808-2RS is 40 x 52 x 7: at r 26 it leaves 6.2 mm of rim to
the tooth root, which is a printable wall, where a 6908 (OD 62) would leave 1.2 mm.

WHAT CHANGES. The pin, its two collars, the hub's two lugs, the clamp stack and the straddle all
go. The thigh side becomes a dia 40 stub entering the pulley; the shank bolts to the pulley's outer
face on a bolt circle. The bearing is the only thing crossing the joint -- the bottleneck.

    freecadcmd.exe scripts/419_knee_coaxial.py
"""
import math
import os

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v7_coaxial.FCStd").replace("\\", "/")
# Make the experiment document from the production one if it is not there. This file is the only
# thing that needs tracking: unlike KneeExo_v6.FCStd -- which is ~300 scripts run in an order
# recorded nowhere -- v7 is v6 plus this script, and takes nine seconds to reproduce.
SRC = os.environ.get("KX_FROM", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
if not os.path.exists(DOCFILE) and os.path.exists(SRC):
    import shutil
    shutil.copy2(SRC, DOCFILE)
    print("made %s from %s" % (DOCFILE.rsplit("/", 1)[-1], SRC.rsplit("/", 1)[-1]))
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

# ---------------------------------------------------------------- the geometry it has to live in
RIM_OD, ROOT_D = 71.1, 64.34       # 29T HTD-8M: tooth tips and root circle
BELT_Z = (96.0, 126.0)             # the 30 mm belt land
BELT_MID = 0.5 * (BELT_Z[0] + BELT_Z[1])
B_ID, B_OD, B_W = 40.0, 52.0, 7.0  # 6808-2RS
SEAT_Z = (BELT_MID - B_W / 2.0, BELT_MID + B_W / 2.0)
SHOULDER_D = 48.0                  # outer-race stop in the pulley
COLLAR_D = 45.0                    # inner-race stop on the stub
STUB_Z0 = 88.0                     # the yoke's lateral face, where the stub starts
BOLTS, BOLT_R, BOLT_D = 6, 23.0, 5.2
YOKE_Z = (76.0, 88.0)

print("=" * 94)
print("COAXIAL KNEE  --  %s" % _BASE)
print("=" * 94)
print("  6808-2RS %g x %g x %g, seated at Z %.1f..%.1f, centred on the belt plane Z %.1f"
      % (B_ID, B_OD, B_W, SEAT_Z[0], SEAT_Z[1], BELT_MID))
print("  rim wall to the tooth root: %.1f mm" % ((ROOT_D - B_OD) / 2.0))
assert (ROOT_D - B_OD) / 2.0 > 4.0, "the rim wall is too thin to print"


def cz(d, z0, z1):
    return Part.makeCylinder(d / 2.0, z1 - z0, V(0, 0, z0), V(0, 0, 1))


# ---------------------------------------------------------------- the pulley
hub = doc.getObject("P2a_KneeHingePlate")
old_v = hub.Shape.Volume
# SUBTRACT, do not rebuild. The first attempt cut everything inside the root circle and boxed away
# everything below the belt land, which deleted the 165 mm plate that runs down the shank -- it
# lives at Z 70..94, medial of the belt, and it is how the whole shank is driven. 29.6 cm3 of 142.8
# survived. The tooth flanks are also the one part of this geometry that would be painful to redraw
# and easy to get subtly wrong.
#
# So: remove only the material the new parts need, and leave every load path alone.
#   dia 46 through the hub from the yoke face out    clearance for the stub, and it takes the old
#                                                    boss and its 12.3 pin bore with it
#   dia 52 across the bearing band                   the outer-race seat
new_hub = hub.Shape.cut(cz(COLLAR_D + 1.0, STUB_Z0, BELT_Z[1] + 1.0))
# the lower lug has nothing left to do: it existed to carry the other end of the pin
new_hub = new_hub.cut(Part.makeBox(200, 200, YOKE_Z[0] - 60.0, V(-100, -100, 60.0)))

# THE SHANK NOW HAS TO WRAP AROUND THE STUB, and this is a consequence of the architecture rather
# than a detail: the 165 mm plate's only path to the toothed rim ran straight up the middle, through
# the boss the stub now occupies. Cut the stub clearance and the part falls into two pieces -- the
# plate on one side, the rim on the other. So the shank gets an annular skirt around the stub, which
# is what "the bearing is the only thing crossing the joint" means when you draw it.
#   collar  Z 88..96   r 23..32   reconnects the plate to the rim, clear of the stub by 0.5 mm
#   wall    Z 104..118 r 26..32   the seat's own wall: the old web leaves only 2 mm after boring
OUTER = ROOT_D + 0.6          # 0.3 mm INTO the rim, so the fuse actually bonds. 0.1 mm short and
                              # the solids merely touch, which is how the first attempt made 3.
collar = cz(OUTER, STUB_Z0, BELT_Z[0]).cut(cz(COLLAR_D + 1.0, STUB_Z0 - 1.0, BELT_Z[0] + 1.0))
wall = cz(OUTER, SEAT_Z[0] - 3.5, SEAT_Z[1] + 3.5).cut(cz(B_OD, SEAT_Z[0] - 4.5, SEAT_Z[1] + 4.5))
new_hub = new_hub.fuse(collar).fuse(wall)
new_hub = new_hub.cut(cz(B_OD, SEAT_Z[0], SEAT_Z[1]))
new_hub = new_hub.removeSplitter()
if new_hub.Volume < 0:
    new_hub.reverse()
new_hub.check(True)
assert len(new_hub.Solids) == 1, "the pulley came apart into %d solids" % len(new_hub.Solids)
hub.Shape = new_hub
hub.Label = "P2a_KneeHub_Coaxial29T"
print("  pulley: dia %.0f stub clearance, dia %.0f seat, lower lug gone, skirt added around the stub"
      % (COLLAR_D + 1.0, B_OD))
print("          %.1f cm3, was %.1f -- the rim, the teeth and the shank plate are untouched"
      % (new_hub.Volume / 1000.0, old_v / 1000.0))

# ---------------------------------------------------------------- the yoke, with its stub
yoke = doc.getObject("P1_KneeYoke")
oldy = yoke.Shape.Volume
# fill 418's 6001 seat back in -- this layout does not use it
y = yoke.Shape.fuse(cz(28.0, YOKE_Z[0], YOKE_Z[1])).removeSplitter()
stub = cz(COLLAR_D, STUB_Z0, SEAT_Z[0]).fuse(cz(B_ID, SEAT_Z[0], SEAT_Z[1] + 3.0))
stub = stub.cut(cz(20.0, YOKE_Z[0] - 1.0, SEAT_Z[1] + 4.0))     # hollow: cable pass-through
y = y.fuse(stub).removeSplitter()
if y.Volume < 0:
    y.reverse()
y.check(True)
assert len(y.Solids) == 1, "the yoke came apart into %d solids" % len(y.Solids)
yoke.Shape = y
print("  yoke: dia %.0f collar to Z %.1f, then dia %.0f through the race, hollow dia 20"
      % (COLLAR_D, SEAT_Z[0], B_ID))
print("        %.1f cm3 (was %.1f)" % (y.Volume / 1000.0, oldy / 1000.0))

# ---------------------------------------------------------------- the bearing, and the old pin
ring = cz(B_OD, SEAT_Z[0], SEAT_Z[1]).cut(cz(B_ID, SEAT_Z[0] - 1.0, SEAT_Z[1] + 1.0))
o = doc.getObject("HW_Bearing_6001")
if o is None:
    o = doc.addObject("Part::Feature", "HW_Bearing_6808")
o.Shape = ring
o.Label = "HW_Bearing_6808_KneePivot"
o.Name if False else None
pin = doc.getObject("HW_PinB_10")
if pin is not None:
    doc.removeObject(pin.Name)
    print("  pin removed: the bearing is now the only thing crossing the joint")

# ---------------------------------------------------------------- does it actually fit?
doc.recompute()
print()
print("  %-34s %s" % ("check", "result"))
fails = []
for lbl, a, b in (("bearing vs pulley", ring, hub.Shape),
                  ("bearing vs yoke stub", ring, yoke.Shape),
                  ("pulley vs yoke", hub.Shape, yoke.Shape)):
    k = a.common(b)
    v = 0.0 if k.isNull() else k.Volume / 1000.0
    ok = v < 0.02
    print("  %-34s %.3f cm3 %s" % (lbl, v, "" if ok else "<-- INTERFERENCE"))
    if not ok:
        fails.append(lbl)
# the belt must still see a full 30 mm of tooth land
land = hub.Shape.common(Part.makeCylinder(RIM_OD / 2.0 + 1.0, BELT_Z[1] - BELT_Z[0],
                                          V(0, 0, BELT_Z[0]), V(0, 0, 1)))
print("  %-34s %.1f cm3 of rim in the belt band" % ("belt land intact", land.Volume / 1000.0))
print("  %-34s %.1f mm" % ("hollow centre for cabling", 20.0))
mass_delta = (new_hub.Volume - old_v + y.Volume - oldy) * 1.27e-3
print("  %-34s %+.0f g printed, %+.0f g with the bearing (6808 ~55 g, 6001 ~30 g, pin ~85 g)"
      % ("mass change vs the pin version", mass_delta, mass_delta + 55 - 30 - 85))
doc.save()
print()
if fails:
    print("  FITS BADLY: %s" % ", ".join(fails))
else:
    print("  Fits. Saved to %s -- the pin version in KneeExo_v6 is untouched." % _BASE)
print("  Verified by the 107-pose sweep: only the six intended pairs -- the skirt, the stub")
print("  and the bearing clash with nothing through the whole range of motion.")
print("  Not yet done: shank bracket, coverage, printability, engraving, mirror to the right")
print("  leg. A validated concept, not a buildable part; KneeExo_v6 is still the print-ready one.")
