# -*- coding: utf-8 -*-
"""A bench rig: 6374 + MKS ODrive Mini, printable tonight, so the motor can run on the side.

Asked at the bench: "lets build a simple quickly printable 6374 + odrive test mount so I can get
the motor working on the side". Four parts, all flat, no supports, about 70 cm3 in total.

IT MOUNTS THE MOTOR BY ITS FLANGE, NOT ITS REAR, and that is the one real design decision here.
434_odrive_mount.py hangs the controller off the motor's REAR bolt circle, which is flagged
UNVERIFIED for a reason: on most 6374-class outrunners the rear is the ROTATING can and there is
no stationary face to bolt to at all. This rig does not need to know. The motor bolts flange-down
to a plate, its shaft comes THROUGH that plate, the magnet goes on the shaft end on the far side
and the board faces it from a second plate on four pillars. Everything stationary hangs off the
one face every outrunner certainly has, and the can spins in free air on the other side.

If the bench proves the 6374 does have a usable rear face, that is worth knowing for the exo; if
it does not, the exo's controller mount has to become a cage off the front flange, and this rig
will have been the thing that found out.

WHAT IS MEASURED AND WHAT IS NOT

    board 63.00 x 58.00, 6 x dia 3.3            MEASURED -- the "Size" drawing in
      columns 56.60 apart                       Smurf/xdrive-mini-docs, corroborated by a
      rows 51.50 corner to corner, middle       photograph of the board's encoder face
      row 24.00 from the top (1.75 above
      the board's centre line)
    AS5047P at the board's centre               PHOTOGRAPHED, in a round window in the encoder
                                                face's backplate, central to about +-1 mm
    magnet 6 x 2.5 diametric, gap 0.5..3.0      AMS datasheet, via BOM D5
    motor bolt pattern                          NOT KNOWN. 25 mm square is the exo's assumption
                                                and nothing has ever checked it.
    shaft protrusion past the flange            NOT KNOWN
    recess from the board's mounting face       NOT KNOWN, and it is the number that sets the
      down to the AS5047P's own face            air gap -- see the note this prints

THE TWO UNKNOWNS ARE ABSORBED, NOT GUESSED. The motor's pattern becomes eight radial SLOTS, which
take any four-bolt square from 17 to 31 mm on either diagonal, so one print fits whatever the
motor turns out to have. The air gap becomes the PILLAR length, printed in three lengths with
0.5 mm shims, so it is set with a caliper at assembly instead of being right by luck.

    freecadcmd.exe scripts/440_bench_rig.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_RIG", r"C:/Users/Josh/KneeExo_BenchRig.FCStd").replace("\\", "/")
OUT = os.environ.get("KX_RIG_STL", r"C:/Users/Josh/KneeExo_BenchRig_STL")

# --- the board, measured -------------------------------------------------------------------
BOARD = (63.0, 58.0)
HOLE_X = 56.60 / 2.0            # +-28.30
HOLE_TOP = 51.50 / 2.0          # +-25.75, the corner rows
HOLE_MID = 51.50 / 2.0 - 24.0   # +1.75, the middle row above centre
M3, M5 = 3.4, 5.4               # clearance
# --- the motor, not measured ---------------------------------------------------------------
MOT_D = 63.0
SLOT_R = (12.0, 22.0)           # eight radial slots: any square from 17 to 31 mm across
SHAFT_D = 8.0
BOSS_D = 24.0                   # clearance for whatever boss is around the shaft
# --- the rig -------------------------------------------------------------------------------
A_SIZE, A_T = 92.0, 5.0         # motor plate
B_SIZE, B_T = (84.0, 76.0), 4.0  # encoder plate
PILLAR = (36.0, 30.0)           # where the four pillars stand
PILLAR_OD, PILLAR_LEN = 10.0, (26.0, 30.0, 34.0)
SHIMS = (0.5, 1.0, 2.0)
MAG_D, MAG_T = 6.0, 2.5
HOLDER = (14.0, 11.0, 7.0)      # OD, length, bore depth onto the shaft

doc = FreeCAD.newDocument("BenchRig") if not os.path.exists(DOCFILE) \
    else FreeCAD.openDocument(DOCFILE)
for o in list(doc.Objects):
    doc.removeObject(o.Name)


def put(name, shape):
    shape.check(True)
    assert len(shape.Solids) == 1, "%s came out as %d solids" % (name, len(shape.Solids))
    o = doc.addObject("Part::Feature", name)
    o.Shape = shape
    o.Label = name
    return o


def plate(w, d, t):
    return Part.makeBox(w, d, t, V(-w / 2.0, -d / 2.0, 0.0))


def hole(sh, dia, x, y, z0, h):
    return sh.cut(Part.makeCylinder(dia / 2.0, h, V(x, y, z0), V(0, 0, 1)))


print("=" * 98)
print("BENCH RIG  --  6374 + MKS ODrive Mini, four printed parts")
print("=" * 98)

# ---------------------------------------------------------------- 1. the motor plate
a = plate(A_SIZE, A_SIZE, A_T)
a = hole(a, BOSS_D, 0.0, 0.0, -1.0, A_T + 2.0)
# eight radial slots, so the motor's unknown square fits either way round
for k in range(8):
    th = math.radians(45.0 * k)
    ux, uy = math.cos(th), math.sin(th)
    for r in [SLOT_R[0] + i * 0.5 for i in range(int((SLOT_R[1] - SLOT_R[0]) / 0.5) + 1)]:
        a = hole(a, M5, ux * r, uy * r, -1.0, A_T + 2.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        a = hole(a, M5, sx * 40.0, sy * 40.0, -1.0, A_T + 2.0)          # bolt it to the bench
        a = hole(a, M3, sx * PILLAR[0], sy * PILLAR[1], -1.0, A_T + 2.0)  # the pillars
pa = put("RIG1_MotorPlate", a)
print("  RIG1_MotorPlate     %5.1f cm3   %.0f x %.0f x %.0f, 8 slots r %.0f..%.0f for the motor,"
      % (a.Volume / 1000.0, A_SIZE, A_SIZE, A_T, SLOT_R[0], SLOT_R[1]))
print("                      4 x M5 at +-40 to bolt it down, dia %.0f clear for the shaft boss"
      % BOSS_D)

# ---------------------------------------------------------------- 2. the encoder plate
b = plate(B_SIZE[0], B_SIZE[1], B_T)
b = hole(b, 26.0, 0.0, 0.0, -1.0, B_T + 2.0)            # window: wiring, and sight of the IC
for sx in (-1, 1):
    for sy in (-1, 1):
        b = hole(b, M3, sx * PILLAR[0], sy * PILLAR[1], -1.0, B_T + 2.0)
for sx in (-1, 1):
    for dz in (HOLE_TOP, HOLE_MID, -HOLE_TOP):
        b = hole(b, 3.3, sx * HOLE_X, dz, -1.0, B_T + 2.0)
pb = put("RIG2_EncoderPlate", b)
print("  RIG2_EncoderPlate   %5.1f cm3   %.0f x %.0f x %.0f, the board's SIX holes on"
      % (b.Volume / 1000.0, B_SIZE[0], B_SIZE[1], B_T))
print("                      %.2f x %.2f with the middle row %.2f above centre"
      % (2 * HOLE_X, 2 * HOLE_TOP, HOLE_MID))

# ---------------------------------------------------------------- 3. pillars and shims
for i, L in enumerate(PILLAR_LEN):
    p = Part.makeCylinder(PILLAR_OD / 2.0, L, V(0, 0, 0), V(0, 0, 1))
    p = p.cut(Part.makeCylinder(M3 / 2.0, L + 2.0, V(0, 0, -1.0), V(0, 0, 1)))
    put("RIG3_Pillar_%02dmm" % int(L), p)
print("  RIG3_Pillar         three lengths %s mm, dia %.0f, print 4 of ONE of them"
      % ("/".join("%.0f" % L for L in PILLAR_LEN), PILLAR_OD))
for t in SHIMS:
    sh = Part.makeCylinder(PILLAR_OD / 2.0, t, V(0, 0, 0), V(0, 0, 1))
    sh = sh.cut(Part.makeCylinder(M3 / 2.0, t + 2.0, V(0, 0, -1.0), V(0, 0, 1)))
    put("RIG3_Shim_%02dmm" % int(t * 10), sh)
print("  RIG3_Shim           %s mm, four of each: this is how the air gap is set"
      % "/".join("%.1f" % t for t in SHIMS))

# ---------------------------------------------------------------- 4. the magnet holder
h = Part.makeCylinder(HOLDER[0] / 2.0, HOLDER[1], V(0, 0, 0), V(0, 0, 1))
h = h.cut(Part.makeCylinder((SHAFT_D + 0.15) / 2.0, HOLDER[2], V(0, 0, -0.001), V(0, 0, 1)))
h = h.cut(Part.makeCylinder((MAG_D + 0.2) / 2.0, MAG_T + 0.1,
                            V(0, 0, HOLDER[1] - MAG_T - 0.1), V(0, 0, 1)))
h = h.cut(Part.makeCylinder(M3 / 2.0, HOLDER[0], V(-HOLDER[0], 0, HOLDER[2] / 2.0), V(1, 0, 0)))
floor = HOLDER[1] - HOLDER[2] - MAG_T - 0.1
assert floor > 0.8, "no floor left between the shaft bore and the magnet pocket: %.2f" % floor
put("RIG4_MagnetHolder", h)
print("  RIG4_MagnetHolder   dia %.0f x %.0f: bore %.2f onto the shaft, dia %.1f x %.1f pocket"
      % (HOLDER[0], HOLDER[1], SHAFT_D + 0.15, MAG_D + 0.2, MAG_T + 0.1))
print("                      for the magnet, %.1f mm floor between them, M3 grub screw"
      % floor)

# ---------------------------------------------------------------- checks
print()
print("  CHECKS")
fail = []
# the pillars must miss the motor and the board
for nm, (px, py) in (("motor", (0.0, 0.0)),):
    r = math.hypot(PILLAR[0], PILLAR[1])
    ok = r > MOT_D / 2.0 + 3.0
    print("     pillars at r %.1f vs the motor's %.1f  %s" % (r, MOT_D / 2.0, "" if ok else "<--"))
    if not ok:
        fail.append("the pillars foul the motor")
ok = PILLAR[0] > BOARD[0] / 2.0 + 2.0 or PILLAR[1] > BOARD[1] / 2.0 + 2.0
print("     pillars at (%.0f, %.0f) vs the board's %.0f x %.0f  %s"
      % (PILLAR[0], PILLAR[1], BOARD[0], BOARD[1], "" if ok else "<-- they overlap the board"))
if not ok:
    fail.append("the pillars overlap the board")
# every hole has to stay on its plate
for lbl, size, pts in (("RIG1", (A_SIZE, A_SIZE),
                        [(40.0, 40.0, M5), (PILLAR[0], PILLAR[1], M3)]),
                       ("RIG2", B_SIZE,
                        [(PILLAR[0], PILLAR[1], M3), (HOLE_X, HOLE_TOP, 3.3)])):
    for x, y, d in pts:
        ex = size[0] / 2.0 - (x + d / 2.0)
        ey = size[1] / 2.0 - (y + d / 2.0)
        ok = min(ex, ey) >= 1.5
        print("     %s hole at (%.1f, %.1f): %.1f mm of material to the nearest edge  %s"
              % (lbl, x, y, min(ex, ey), "" if ok else "<-- too close"))
        if not ok:
            fail.append("%s hole at (%.1f, %.1f) is %.1f from the edge" % (lbl, x, y, min(ex, ey)))

if not os.path.isdir(OUT):
    os.makedirs(OUT)
for f in os.listdir(OUT):
    if f.endswith(".stl"):
        os.remove(os.path.join(OUT, f))
import MeshPart                                                     # noqa: E402
tot = 0.0
for o in doc.Objects:
    m = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.04, AngularDeflection=0.2,
                               Relative=False)
    m.harmonizeNormals()
    assert m.isSolid(), "%s will not mesh closed" % o.Name
    m.write(os.path.join(OUT, o.Name + ".stl"))
    tot += o.Shape.Volume / 1000.0
doc.saveAs(DOCFILE)

print()
print("  %d parts, %.1f cm3 (~%.0f g of PETG) -> %s" % (len(doc.Objects), tot, tot * 1.27, OUT))
print()
print("  HOW IT GOES TOGETHER, and the one number to measure")
print("     1. bolt the motor flange-down to RIG1 through the slots -- the shaft comes through")
print("        the middle and the can spins clear on the other side")
print("     2. RIG1 bolts to anything: a scrap of ply, a vice, a length of 2040")
print("     3. slip RIG4 onto the shaft end, grub screw it, bond the magnet in its pocket")
print("        DIAMETRIC, not axial, and centred on the shaft within 0.5 mm")
print("     4. bolt the board UNDER RIG2, encoder face toward the motor, on its six M3")
print("     5. stand RIG2 off RIG1 on four pillars and set the gap with shims:")
print()
print("            air gap = pillar + shims - (shaft past RIG1 + %.1f) - recess" % (
      HOLDER[1] - HOLDER[2]))
print()
print("        where RECESS is the depth from the board's mounting face down to the AS5047P's")
print("        own face. The encoder side has a BACKPLATE with the chip set in a round window,")
print("        so it is NOT the board's thickness and it is the only number that cannot be")
print("        guessed. Measure it with a depth gauge, pick the pillar, trim with shims.")
print("        The datasheet wants 0.5..3.0 mm and is happiest near 1.5.")
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  Nothing here depends on the motor having a rear bolt circle, which is the exo's")
    print("  biggest unverified assumption. If this rig shows it has one, 434 is right; if not,")
    print("  the exo's controller has to hang off a cage from the front flange instead.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
