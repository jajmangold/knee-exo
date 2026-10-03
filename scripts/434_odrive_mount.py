# -*- coding: utf-8 -*-
"""Put the controller in the machine. It has never been in it.

Forty-two solids in the model and not one of them electronic: the MKS XDRIVE MINI is ordered
(BOM E1, four owned), routed in ELECTRONICS's topology, and has no board, no mount, no standoffs
and no space reserved. It also cannot be put in the backpack with the battery, which is the usual
answer for a controller, because its AS5047P is ON the board and reads the 6 x 2.5 mm diametric
magnet glued to the motor's shaft (BOM D5). From the AMS datasheet:

    air gap, package face to magnet     0.5 to 3 mm
    magnet centred on the package       within 0.5 mm

So the board sits a few millimetres off the end of the motor's free shaft, concentric with it.
433_drive_flip.py turned the motor over, which left exactly that space empty: the link belt used
to occupy Y 302..314 and now runs below the motor instead.

WHAT IS ASSUMED HERE, ALL OF IT FLAGGED, because no mechanical drawing of this board is
published anywhere -- Makerbase's repository carries a schematic and nothing else, the community
notes have a drawing as a PNG with no dimensions, and the 63 x 58 mm that circulates in search
results is not corroborated by the page it is attributed to:

    BOARD           63 x 58 x 1.6, components 10 mm       UNVERIFIED -- measure yours
    BOARD_HOLES     55 x 50 rectangle of M3               GUESSED -- measure yours
    IC_OFFSET       the AS5047P at the board's centre     GUESSED, and it is the one that
                                                          matters: the IC is the datum, not the
                                                          outline, because it must sit on the
                                                          shaft's axis within 0.5 mm
    SHAFT_PROUD     2 mm of shaft past the motor's rear   UNVERIFIED
    REAR_BOLTS      the same 25 mm square as the front    UNVERIFIED -- 428 flags this too

Every one of those is a number that should come off the bench, and the mount is parameterised so
that correcting one and re-running is the whole job. What the file does guarantee is the thing
the datasheet fixes: it refuses to finish if the air gap it has built falls outside 0.5..3 mm.

    freecadcmd.exe scripts/434_odrive_mount.py
"""
import os
import sys

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

M5, M3 = 5.2, 3.2
BOARD = (63.0, 58.0, 1.6)       # UNVERIFIED
BOARD_HOLES = (55.0, 50.0)      # GUESSED
COMPONENTS = 10.0               # GUESSED, the tall side faces away from the motor
SHAFT_PROUD = 2.0               # UNVERIFIED
MAGNET = (6.0, 2.5)             # BOM D5, and what the datasheet asks for
AIR_GAP = 2.0                   # target, inside the datasheet's 0.5..3.0
GAP_LIMITS = (0.5, 3.0)         # AS5047P
REAR_BOLTS = 12.5               # half of the 25 mm square -- UNVERIFIED
CAP_T = 5.0                     # the mount's own plate

mot = doc.getObject("A3_Motor_6374")
a7 = doc.getObject("A7_DriveBox")
assert mot is not None, "no motor in this document"
mb = mot.Shape.BoundBox
MOT_X, MOT_R = 0.5 * (mb.XMin + mb.XMax), 0.5 * mb.XLength
MOT_Z = 0.5 * (mb.ZMin + mb.ZMax)
REAR_Y = mb.YMax                # the free end, after 433 turned the motor over
mirrored = mb.ZMax < 0
sgn = -1.0 if mirrored else 1.0

print("=" * 98)
print("CONTROLLER MOUNT  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)
print("  the motor's free shaft end is at Y %.0f, on the axis X %.0f Z %.0f"
      % (REAR_Y, MOT_X, MOT_Z))

# where everything lands, from the shaft outwards
shaft_end = REAR_Y + SHAFT_PROUD
magnet_face = shaft_end + MAGNET[1]
ic_face = magnet_face + AIR_GAP
board_y = (ic_face, ic_face + BOARD[2])
print("  shaft end Y %.1f -> magnet face %.1f -> board's sensor face %.1f (%.1f mm air gap)"
      % (shaft_end, magnet_face, ic_face, AIR_GAP))

# ---------------------------------------------------------------- the mount
cap = Part.makeCylinder(MOT_R, CAP_T, V(MOT_X, REAR_Y, MOT_Z), V(0, 1, 0))
# clearance for the shaft and its magnet
cap = cap.cut(Part.makeCylinder(MAGNET[0] / 2.0 + 4.0, CAP_T + 4.0,
                                V(MOT_X, REAR_Y - 2.0, MOT_Z), V(0, 1, 0)))
# bolts into the motor's rear face
for dx in (-REAR_BOLTS, REAR_BOLTS):
    for dz in (-REAR_BOLTS, REAR_BOLTS):
        cap = cap.cut(Part.makeCylinder(M5 / 2.0, CAP_T + 4.0,
                                        V(MOT_X + dx, REAR_Y - 2.0, MOT_Z + sgn * dz),
                                        V(0, 1, 0)))
# four bosses carrying the board, their top face at the sensor plane
boss_h = ic_face - (REAR_Y + CAP_T)
assert boss_h > 0.5, "the board would sit inside the mount's own plate"
for dx in (-BOARD_HOLES[0] / 2.0, BOARD_HOLES[0] / 2.0):
    for dz in (-BOARD_HOLES[1] / 2.0, BOARD_HOLES[1] / 2.0):
        p = V(MOT_X + dx, REAR_Y + CAP_T, MOT_Z + sgn * dz)
        cap = cap.fuse(Part.makeCylinder(4.0, boss_h, p, V(0, 1, 0)))
        cap = cap.cut(Part.makeCylinder(M3 / 2.0, boss_h + 6.0,
                                        V(p.x, p.y - 3.0, p.z), V(0, 1, 0)))
# the bosses sit outside the motor's circle, so tie them back with a web
web = Part.makeBox(BOARD_HOLES[0] + 8.0, CAP_T, BOARD_HOLES[1] + 8.0,
                   V(MOT_X - (BOARD_HOLES[0] + 8.0) / 2.0, REAR_Y,
                     MOT_Z - sgn * (BOARD_HOLES[1] + 8.0) / 2.0 if mirrored
                     else MOT_Z - (BOARD_HOLES[1] + 8.0) / 2.0))
cap = cap.fuse(web)
cap = cap.cut(Part.makeCylinder(MAGNET[0] / 2.0 + 4.0, CAP_T + 4.0,
                                V(MOT_X, REAR_Y - 2.0, MOT_Z), V(0, 1, 0)))
for dx in (-REAR_BOLTS, REAR_BOLTS):
    for dz in (-REAR_BOLTS, REAR_BOLTS):
        cap = cap.cut(Part.makeCylinder(M5 / 2.0, CAP_T + 4.0,
                                        V(MOT_X + dx, REAR_Y - 2.0, MOT_Z + sgn * dz),
                                        V(0, 1, 0)))
tidy = cap.removeSplitter()
try:
    tidy.check(True)
    cap = tidy
except Exception:
    pass
cap.check(True)
assert len(cap.Solids) == 1, "the mount came out as %d solids" % len(cap.Solids)
o = doc.getObject("P27_ControllerMount") or doc.addObject("Part::Feature", "P27_ControllerMount")
o.Shape = cap
o.Label = "P27_ControllerMount"
print("  mount %.1f cm3: a cap on the motor's rear bolts, four bosses %.1f mm tall"
      % (cap.Volume / 1000.0, boss_h))

# ---------------------------------------------------------------- the board itself
zc = MOT_Z
board = Part.makeBox(BOARD[0], BOARD[2], BOARD[1],
                     V(MOT_X - BOARD[0] / 2.0, board_y[0], zc - BOARD[1] / 2.0))
board = board.fuse(Part.makeBox(BOARD[0] - 8.0, COMPONENTS, BOARD[1] - 8.0,
                                V(MOT_X - (BOARD[0] - 8.0) / 2.0, board_y[1],
                                  zc - (BOARD[1] - 8.0) / 2.0)))
tidy = board.removeSplitter()
try:
    tidy.check(True)
    board = tidy
except Exception:
    pass
b = doc.getObject("HW_ODrive_XDriveMini") or doc.addObject("Part::Feature", "HW_ODrive_XDriveMini")
b.Shape = board
b.Label = "HW_ODrive_XDriveMini"
print("  board %.0f x %.0f x %.1f at Y %.1f, components to Y %.1f  -- DIMENSIONS UNVERIFIED"
      % (BOARD[0], BOARD[1], BOARD[2], board_y[0], board_y[1] + COMPONENTS))

# ---------------------------------------------------------------- the shell has to grow over it
# The board is 63 x 58 and the motor it sits on is 63 across, so the board's CORNERS stand at
# radius 42.8 where the motor's skin is at 31.5 -- they project straight through the nacelle.
# This is not a clash to relieve, it is a cover that is too small: the shell gets a blister over
# the controller. Sized to the board's unverified dimensions, so it changes when they do.
BLISTER = 3.0
bx = (MOT_X - BOARD[0] / 2.0 - BLISTER, BOARD[0] + 2 * BLISTER)
bz = (zc - BOARD[1] / 2.0 - BLISTER, BOARD[1] + 2 * BLISTER)
# the blister starts at the motor's rear face, not at the board: the mount's web and bosses
# stand proud of the motor's circle from Y 302 upwards, and a blister that begins at the board
# leaves them sticking through the shell
by_ = (REAR_Y - 1.0, (board_y[1] + COMPONENTS + BLISTER) - (REAR_Y - 1.0))
nac = doc.getObject("P25_MotorNacelle")
if nac is not None:
    v = nac.Shape.Volume
    outer = Part.makeBox(bx[1], by_[1], bz[1], V(bx[0], by_[0], bz[0]))
    top = by_[0] + by_[1] - 2.0          # the blister's own 2 mm rear wall
    # No floor at the blister's root: it is a bump on a hollow cover, so its cavity is the
    # nacelle's own.  A 2 mm diaphragm there would sit straight on the mount's web corners --
    # which is exactly what it did, 0.554 cm3 of it in four pieces at Y 302..303.  The cavity
    # therefore starts at by_[0], 1 mm under the motor's rear face, where the tube wall's inner
    # surface is at r 31.8 (measured): the box reaches r 32.5 on the X axes, so it thins ~0.7 mm
    # off a 4 mm wall over a 1 mm band and opens nothing.
    inner = Part.makeBox(bx[1] - 2 * 2.0, top - by_[0], bz[1] - 2 * 2.0,
                         V(bx[0] + 2.0, by_[0], bz[0] + 2.0))
    # The nacelle used to close off at the motor's rear face -- a disc across the whole bore at
    # Y 302..304, measured, not assumed.  The controller now lives in that space and the mount
    # bolts straight through it, so that closure has to move outboard: cut it away over the
    # motor's full circle and let the blister's rear wall be the cover instead.  The drive and
    # controller compartments then share one volume, which is what the motor's own leads want
    # anyway.  The blister's footprint (69 x 64) contains the bore (dia 63), so nothing is
    # left open to the outside.
    inner = inner.fuse(Part.makeCylinder(MOT_R + 0.5, top - by_[0],
                                         V(MOT_X, by_[0], MOT_Z), V(0, 1, 0)))
    assert bx[0] <= MOT_X - MOT_R and bx[0] + bx[1] >= MOT_X + MOT_R,         "the blister is narrower than the bore it now has to close"
    assert bz[0] <= MOT_Z - MOT_R and bz[0] + bz[1] >= MOT_Z + MOT_R,         "the blister is shallower than the bore it now has to close"
    grown = nac.Shape.fuse(outer).cut(inner)
    if len(grown.Solids) == 1:
        grown.check(True)
        nac.Shape = grown
        print("  clad  nacelle blistered over the board, %.0f x %.0f x %.0f: %.1f -> %.1f cm3"
              % (bx[1], bz[1], by_[1], v / 1000.0, grown.Volume / 1000.0))
    else:
        print("  clad  REFUSED to blister the nacelle: %d solids" % len(grown.Solids))
cap22 = doc.getObject("P22_DriveCap")
if cap22 is not None:
    g = cap22.Shape.cut(o.Shape).cut(b.Shape)
    if len(g.Solids) == 1:
        cap22.Shape = g

doc.recompute()
doc.save()

# ---------------------------------------------------------------- verify
print()
print("  VERIFICATION")
fail = []
gap = ic_face - magnet_face
ok = GAP_LIMITS[0] <= gap <= GAP_LIMITS[1]
print("     air gap %.2f mm, datasheet allows %.1f..%.1f  %s"
      % (gap, GAP_LIMITS[0], GAP_LIMITS[1], "" if ok else "<-- OUT OF RANGE"))
if not ok:
    fail.append("air gap %.2f mm is outside the AS5047P's %.1f..%.1f" % (gap,) + GAP_LIMITS)
for nm in ("A3_Motor_6374", "A7_DriveBox", "P25_MotorNacelle", "P22_DriveCap", "A7b_LinkBelt",
           "A2_BallScrew_SFU1620"):
    t = doc.getObject(nm)
    if t is None:
        continue
    for part, lbl in ((o, "mount"), (b, "board")):
        c = part.Shape.common(t.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > 0.02:
            print("     %-6s vs %-22s %7.3f cm3 <-- CLASH" % (lbl, nm, v))
            fail.append("%s overlaps %s by %.3f cm3" % (lbl, nm, v))
        else:
            print("     %-6s vs %-22s %7.3f cm3" % (lbl, nm, v))
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  the controller sits on the motor's free end with its sensor %.1f mm off the magnet," % gap)
    print("  inside the space the link belt vacated. Measure the board before printing the mount:")
    print("  its outline, its hole pattern, and above all where the AS5047P sits on it.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
