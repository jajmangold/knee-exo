# -*- coding: utf-8 -*-
"""Move the knee bearing INTO the capstan: two 6001s under the belt, a plain rod cantilevered.

The bench worked this out over three revisions of a concept file and 453/455/456 checked each one.
The conclusion, now built:

    the 6001 moves from the YOKE at Z 80..88 to a PAIR inside the capstan at Z 96..104 and
    Z 118..126 -- centred in the belt land instead of 27 mm inboard of it.

WHY. 454_knee_ideal.py measured what that 27 mm offset costs: P2a_KneeHingePlate spans Z 68..126
and weighs 188 g because its whole job is to REACH from the belt, where the load is, to the
bearing, where the support is -- only 30 of its 58 mm does transmission work. And the reach turns
the belt's 1064 N into a 28.7 N.m tilting moment carried by two printed bores on a dia 12 pin.
Bearings centred in the belt make both numbers zero.

WHY TWO, AND WHY NOT A HOUSED UNIT. A single bearing cannot react tilt; a pair reacts it as a
couple over their span, which is ordinary radial load. 455_concept_rev2.py found the trap in the
obvious cheap answer: KFL/KP flange units are SELF-ALIGNING -- a spherical insert that swivels on
purpose -- so a pair of them resists tilt not at all, and 145_hinge.py made the pin double shear
precisely to fix "the varus/valgus weakness". A KFL001 body also needs a bore of r 37.6 where a
29T HTD-8M rim roots at r 32.79, so it only ever fitted the oversized pulley the concept drew.
A bare 6001's dia 28 leaves 18.8 mm of wall inside a real 29T rim.

AND IT COSTS NO NEW PART NUMBER: BOM K3 is a 6001-2RS and so is D8a.

WHAT THIS SCRIPT DOES NOT DO. The rod CANTILEVERS from the yoke, because the thigh has nothing
outboard of the belt to support it -- P20_KneeShroud is the only static thing out there and it
only reaches the axis at Z 131.5. That leaves 94 MPa in a dia 12 rod against the 38 MPa a straddle
would give. Fine for a ground rod, and the upgrade path is recorded at the end.

    freecadcmd.exe scripts/457_knee_bearings.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/457_knee_bearings.py
"""
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

# ---------------------------------------------------------------- the new stack, along Z
YOKE_Z = (76.0, 88.0)           # P1 as it stands
BOSS_Z = (88.0, 94.5)           # the yoke's new clamp boss, 1.5 mm clear of the first bearing
BOSS_R = 15.5                   # 1.5 mm clear of P2a's remaining spine at r 17
BORE_D = 12.2                   # the rod's bonded fit
BELT_Z = (96.0, 126.0)          # the capstan's belt land
BRG = (28.0, 8.0)               # 6001-2RS outer, width
BRG_Z = ((96.0, 104.0), (118.0, 126.0))
ABUT_D = 26.0                   # standard housing abutment for a 6001 outer race
SLEEVE_R = 20.0                 # outside of the new hub sleeve -> 6 mm of wall at the dia 28 seats
ROD_Z = (70.0, 130.0)           # dia 12 x 60
ROD_D = 12.0
CLEAR_R = 17.0                  # P2a is emptied inside this radius below the belt.
                                # NOT 20: the capstan's only path down to the shank arm
                                # runs through the r 17..20 band at Z 95.5, and clearing
                                # r < 20 drops the whole 63.7 cm3 capstan off the part.
CLEAR_Z = (60.0, 95.5)
GRUB = 4.2                      # cross-drilled for an M4 grub into a heat-set insert


def kx_doc():
    want = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


def cz(r, z0, z1):
    return Part.makeCylinder(r, z1 - z0, V(0, 0, z0), V(0, 0, 1))


doc = kx_doc()
g = {o.Name: o for o in doc.Objects}
mirrored = g["P1_KneeYoke"].Shape.BoundBox.ZMax < 0
s = -1.0 if mirrored else 1.0
print("=" * 94)
print("KNEE BEARINGS -> INSIDE THE CAPSTAN   (%s leg)" % ("RIGHT, mirrored" if mirrored else "LEFT"))
print("=" * 94)


def z(a, b=None):
    """mirror a Z station or pair through Z = 0 on the right leg"""
    if b is None:
        return s * a
    return (min(s * a, s * b), max(s * a, s * b))


# ---------------------------------------------------------------- refuse a second run
p2 = g["P2a_KneeHingePlate"].Shape
probe = cz(CLEAR_R, *z(*CLEAR_Z)) if not mirrored else \
    Part.makeCylinder(CLEAR_R, CLEAR_Z[1] - CLEAR_Z[0], V(0, 0, -CLEAR_Z[1]), V(0, 0, 1))
if p2.common(probe).Volume < 500.0:
    print("  P2a is already cleared inside r %.0f below the belt -- this has run. Nothing done."
          % CLEAR_R)
    sys.exit(0)

v2_before, v1_before = p2.Volume, g["P1_KneeYoke"].Shape.Volume

# ---------------------------------------------------------------- 1. P2a: clear the old lugs
print()
print("1. P2a_KneeHingePlate")
cut = p2.cut(probe)
assert len(cut.Solids) == 1, "clearing the lugs split P2a into %d solids" % len(cut.Solids)
print("   cleared r < %.0f over Z %.0f..%.0f   -%.2f cm3"
      % (CLEAR_R, CLEAR_Z[0], CLEAR_Z[1], (p2.Volume - cut.Volume) / 1000.0))

# 2. the hub sleeve, fused into whatever the capstan already has there
bz = z(*BELT_Z)
sleeve = Part.makeCylinder(SLEEVE_R, bz[1] - bz[0], V(0, 0, bz[0]), V(0, 0, 1))
cut = cut.fuse(sleeve)
assert len(cut.Solids) == 1, "the sleeve did not fuse"
print("   fused a solid hub sleeve r %.0f over Z %.0f..%.0f   +%.2f cm3"
      % (SLEEVE_R, BELT_Z[0], BELT_Z[1], (cut.Volume - p2.cut(probe).Volume) / 1000.0))

# 3. the bore: dia 28 at the two seats, dia 26 between, overshooting both outer faces
mid = (min(BRG_Z[0][1], BRG_Z[1][0]), max(BRG_Z[0][1], BRG_Z[1][0]))
az = z(*mid)
bore = Part.makeCylinder(ABUT_D / 2.0, az[1] - az[0], V(0, 0, az[0]), V(0, 0, 1))
for z0, z1 in BRG_Z:
    sz = z(z0, z1)
    over = 0.5 if (z0 == BELT_Z[0] or z1 == BELT_Z[1]) else 0.0
    bore = bore.fuse(Part.makeCylinder(BRG[0] / 2.0, (sz[1] - sz[0]) + over,
                                       V(0, 0, sz[0] - (over if sz[0] < az[0] else 0.0)),
                                       V(0, 0, 1)))
cut = cut.cut(bore)
assert len(cut.Solids) == 1, "the bore split P2a into %d solids" % len(cut.Solids)
assert cut.isValid(), "P2a invalid after boring"
cut.check(True)
g["P2a_KneeHingePlate"].Shape = cut
print("   bored dia %.0f at Z %.0f..%.0f and Z %.0f..%.0f, dia %.0f between"
      % (BRG[0], BRG_Z[0][0], BRG_Z[0][1], BRG_Z[1][0], BRG_Z[1][1], ABUT_D))
print("   P2a %.2f -> %.2f cm3  (%+.0f g of PETG)"
      % (v2_before / 1000.0, cut.Volume / 1000.0, (cut.Volume - v2_before) / 1000.0 * 1.27))

# ---------------------------------------------------------------- 4. P1: fill the old seat, clamp
print()
print("2. P1_KneeYoke")
p1 = g["P1_KneeYoke"].Shape
yz = z(*YOKE_Z)
# r 15, not r 14: a plug the exact radius of the seat it fills leaves coincident CYLINDRICAL faces
# and 417_fastener_audit.py then reports a phantom "28 x 0" bearing seat in P1. Overlap 1 mm into
# solid material instead. Its END faces, though, must be exactly flush with the yoke's own: let the
# plug stand 0.5 mm proud and the phantom simply moves to dia 30, as a real 0.5 mm nub this time.
plug = Part.makeCylinder(BRG[0] / 2.0 + 1.0, yz[1] - yz[0], V(0, 0, yz[0]), V(0, 0, 1))
new1 = p1.fuse(plug)
assert len(new1.Solids) == 1, "filling the old 6001 seat split P1"
print("   filled the old dia %.0f x %.0f 6001 seat   +%.2f cm3"
      % (BRG[0], 8.0, (new1.Volume - p1.Volume) / 1000.0))

boz = z(*BOSS_Z)
# overlap 1 mm into the yoke body so the fuse is not a graze
boss = Part.makeCylinder(BOSS_R, (boz[1] - boz[0]) + 1.0, V(0, 0, boz[0] - 1.0), V(0, 0, 1))     if not mirrored else     Part.makeCylinder(BOSS_R, (boz[1] - boz[0]) + 1.0, V(0, 0, boz[0]), V(0, 0, 1))
new1 = new1.fuse(boss)
assert len(new1.Solids) == 1, "the clamp boss did not fuse"
print("   added a clamp boss r %.0f over Z %.0f..%.0f" % (BOSS_R, BOSS_Z[0], BOSS_Z[1]))

cz0 = z(YOKE_Z[0] - 1.0, BOSS_Z[1] + 1.0)
new1 = new1.cut(Part.makeCylinder(BORE_D / 2.0, cz0[1] - cz0[0], V(0, 0, cz0[0]), V(0, 0, 1)))
gz = z(BOSS_Z[0] + 3.0)
new1 = new1.cut(Part.makeCylinder(GRUB / 2.0, BOSS_R + 2.0, V(0, 0, gz), V(0, 1, 0)))
assert len(new1.Solids) == 1, "boring P1 split it into %d solids" % len(new1.Solids)
assert new1.isValid(), "P1 invalid"
new1.check(True)
g["P1_KneeYoke"].Shape = new1
print("   bored dia %.1f through Z %.0f..%.0f, plus an M4 grub cross-hole at Z %.0f"
      % (BORE_D, YOKE_Z[0], BOSS_Z[1], BOSS_Z[0] + 3.0))
print("   P1 %.2f -> %.2f cm3" % (v1_before / 1000.0, new1.Volume / 1000.0))

# ---------------------------------------------------------------- 5. the rod and the two bearings
print()
print("3. hardware")
rz = z(*ROD_Z)
g["HW_PinB_10"].Shape = Part.makeCylinder(ROD_D / 2.0, rz[1] - rz[0], V(0, 0, rz[0]), V(0, 0, 1))
g["HW_PinB_10"].Label = "HW_KneeRod_12x60"
print("   HW_PinB_10 -> a plain dia %.0f x %.0f rod, Z %.0f..%.0f"
      % (ROD_D, ROD_Z[1] - ROD_Z[0], ROD_Z[0], ROD_Z[1]))

rings = None
for i, (z0, z1) in enumerate(BRG_Z):
    sz = z(z0, z1)
    r = Part.makeCylinder(BRG[0] / 2.0, sz[1] - sz[0], V(0, 0, sz[0]), V(0, 0, 1)) \
        .cut(Part.makeCylinder(ROD_D / 2.0, sz[1] - sz[0] + 2.0, V(0, 0, sz[0] - 1.0), V(0, 0, 1)))
    rings = r if rings is None else rings.fuse(r)
g["HW_Bearing_6001"].Shape = rings
g["HW_Bearing_6001"].Label = "HW_Bearing_6001_x2_KneePivot"
print("   HW_Bearing_6001 -> TWO rings at Z %.0f..%.0f and Z %.0f..%.0f, %.0f mm apart"
      % (BRG_Z[0][0], BRG_Z[0][1], BRG_Z[1][0], BRG_Z[1][1],
         (BRG_Z[1][0] + BRG_Z[1][1]) / 2 - (BRG_Z[0][0] + BRG_Z[0][1]) / 2))

# ---------------------------------------------------------------- 6. does it all still fit?
print()
print("4. clearance")
doc.recompute()
pairs = [("P1_KneeYoke", "P2a_KneeHingePlate"), ("P1_KneeYoke", "HW_Bearing_6001"),
         ("P2a_KneeHingePlate", "HW_PinB_10"), ("P1_KneeYoke", "A1_Extrusion_20x60_VSlot"),
         ("HW_PinB_10", "P20_KneeShroud"), ("P2a_KneeHingePlate", "P20_KneeShroud"),
         ("HW_PinB_10", "REF_Knee"), ("P1_KneeYoke", "REF_Knee")]
bad = 0
for a, b in pairs:
    if a not in g or b not in g:
        continue
    c = g[a].Shape.common(g[b].Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    tag = ""
    if v > 0.01:
        bad += 1
        tag = "   <-- CLASH"
    print("   %-26s ^ %-26s %7.3f cm3%s" % (a, b, v, tag))
# the bearings must sit in their seats without fouling the bore walls
seat = g["P2a_KneeHingePlate"].Shape.common(g["HW_Bearing_6001"].Shape)
print("   %-26s ^ %-26s %7.3f cm3   (bonded, so 0 is correct)"
      % ("P2a_KneeHingePlate", "HW_Bearing_6001", 0.0 if seat.isNull() else seat.Volume / 1000.0))
assert bad == 0, "%d clashes" % bad

doc.recompute()
doc.save()
print()
print("   saved %s" % doc.FileName)
print()
print("=" * 94)
print("  THE ROD IS A CANTILEVER AND THAT IS THE ONE COMPROMISE HERE")
print("=" * 94)
print("  Rooted in the yoke's %.0f mm clamp at Z %.0f..%.0f, carrying two %.0f N bearing"
      % (BOSS_Z[1] - YOKE_Z[0], YOKE_Z[0], BOSS_Z[1], 532.0))
print("  reactions at Z %.0f and %.0f: about 94 MPa in a dia %.0f rod, against 38 MPa if the"
      % ((BRG_Z[0][0] + BRG_Z[0][1]) / 2, (BRG_Z[1][0] + BRG_Z[1][1]) / 2, ROD_D))
print("  outboard end were supported too. A ground rod carries it with a factor of ten; 316")
print("  cold-finished carries it with 3.3.")
print()
print("  THE UPGRADE, if it ever reads as slop: P20_KneeShroud is static and its inner face")
print("  reaches the axis at Z 131.5. A boss there clamping the rod's far end turns the")
print("  cantilever into a straddle and halves the stress -- at the price of making a part")
print("  that is currently 3 perimeters and 15 percent infill into a structural one.")
