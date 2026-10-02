# -*- coding: utf-8 -*-
"""Put a sealed 6001 in the knee yoke, so the pin stops running in printed plastic.

WHY HERE AND NOT IN THE HUB. The hub straddles the yoke -- lug Z 70..76, yoke 76..88, lug 88..113 --
so the load arrives symmetrically about the yoke. One bearing there is centred and sees no cocking
moment, where two in the hub would spend their 37 mm of span fighting one. It is also the only
option that works: at Z 82 the yoke is solid from r 6.5 out to r 43..55 at every one of 18 bearings
(measured by ray section and again by point marching), and the pulley rim is at r 35.5 -- so every
radius inside the pulley is inside the yoke, and two hub halves could not be bolted to each other
past it anyway.

WHY AT ALL, since 2.5 MPa of bearing pressure is nothing for PETG: friction, not strength.

    printed PETG journal   mu 0.30    1.375 N.m at the joint
    igus bushing (BOM K3)  mu 0.15    0.688
    sealed 6001            mu 0.0015  0.007

A 0.69 N.m deadband is a stiff hinge on a limb that is meant to swing freely when the device is
off, which is the property the whole 14.5:1 drivetrain was sized around (reflected inertia 0.22x
the limb's). 100x is the argument. See 801_knee_bearing.py for the full working.

THE SEAT. 6001 is 28 x 12 x 8. The yoke is 12 mm thick, so: dia 28 for 8 mm from the hub side, then
the remaining 4 mm opened to dia 26, which is the standard abutment diameter for a 6001 outer race
-- the bearing drops in until it stops, and the pin passes through the lip with 7 mm of clearance.

BONDED, NOT PRESSED. A press fit into PETG does not hold: the plastic creeps under hoop stress and
thermal cycling and the interference is gone within months. Print it, bore to 28.2 for a 0.1 mm
bond line, and use structural methacrylate or epoxy. Same reasoning as a square tube bonded into a
printed gear hub -- put metal where the plastic is not being asked to hold the load.

Works on either leg: the right document is the left mirrored through Z = 0, so the yoke sits at
negative Z and the seat is cut from the other side. Detected, not assumed.

    freecadcmd.exe scripts/418_knee_bearing.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/418_knee_bearing.py
"""
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

OD, ID, W = 28.0, 12.0, 8.0        # 6001
ABUT = 26.0                        # outer-race abutment, and clearance round the pin
PIN_D = 12.3                       # the bore as drawn

yoke = doc.getObject("P1_KneeYoke")
assert yoke is not None, "no P1_KneeYoke in this document"
b = yoke.Shape.BoundBox
mirrored = b.ZMax < 0             # the right leg lives at negative Z
sgn = -1.0 if mirrored else 1.0
z_in, z_out = (76.0 * sgn, 88.0 * sgn) if not mirrored else (-76.0, -88.0)
zlo, zhi = min(z_in, z_out), max(z_in, z_out)

print("=" * 88)
print("KNEE BEARING  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 88)
print("  yoke spans Z %.1f..%.1f (%.0f mm thick)" % (zlo, zhi, zhi - zlo))

# Already done? The seat is the only thing on the knee axis bigger than the pin bore.
have = [round(2 * f.Surface.Radius, 2) for f in yoke.Shape.Faces
        if f.Surface.TypeId == "Part::GeomCylinder" and abs(f.Surface.Axis.z) > 0.9
        and (f.Surface.Center.x ** 2 + f.Surface.Center.y ** 2) ** 0.5 < 2.0]
if any(abs(d - OD) < 0.5 for d in have):
    print("  seat already cut (bores %s) -- nothing to do" % sorted(set(have)))
else:
    # The bearing goes in from the HUB side: the long lug is at Z 88..113 on the left, so the
    # seat is cut from the Z = 88 face downward, and the 4 mm lip is left at the Z = 76 end.
    if mirrored:
        seat_z0, seat_z1 = zlo, zlo + W            # from the -88 face
        lip_z0, lip_z1 = zlo + W, zhi
    else:
        seat_z0, seat_z1 = zhi - W, zhi            # from the +88 face
        lip_z0, lip_z1 = zlo, zhi - W
    v0 = yoke.Shape.Volume
    cut = yoke.Shape.cut(Part.makeCylinder(OD / 2.0, seat_z1 - seat_z0, V(0, 0, seat_z0),
                                           V(0, 0, 1)))
    cut = cut.cut(Part.makeCylinder(ABUT / 2.0, lip_z1 - lip_z0, V(0, 0, lip_z0), V(0, 0, 1)))
    cut = cut.removeSplitter()
    if cut.Volume < 0:
        cut.reverse()
    cut.check(True)
    assert len(cut.Solids) == 1, "the seat split the yoke into %d solids" % len(cut.Solids)
    yoke.Shape = cut
    print("  seat cut: dia %.0f x %.0f mm from Z %.1f, then dia %.0f for the remaining %.0f mm"
          % (OD, W, seat_z1 if not mirrored else seat_z0, ABUT, lip_z1 - lip_z0))
    print("  removed %.2f cm3; the yoke is now %.2f cm3"
          % ((v0 - cut.Volume) / 1000.0, cut.Volume / 1000.0))

# The bearing itself, so the sweep and the coverage test can see it.
if mirrored:
    bz0 = zlo
else:
    bz0 = zhi - W
ring = Part.makeCylinder(OD / 2.0, W, V(0, 0, bz0), V(0, 0, 1)) \
    .cut(Part.makeCylinder(ID / 2.0, W + 2.0, V(0, 0, bz0 - 1.0), V(0, 0, 1)))
o = doc.getObject("HW_Bearing_6001")
if o is None:
    o = doc.addObject("Part::Feature", "HW_Bearing_6001")
    g = doc.getObject("HW") or doc.getObject("G_HW")
    if g is not None:
        g.addObject(o)
o.Shape = ring
o.Label = "HW_Bearing_6001_KneePivot"
print("  bearing modelled: %.2f cm3 ring at Z %.1f..%.1f" % (ring.Volume / 1000.0, bz0, bz0 + W))

# Does it actually fit where it has to?
pin = doc.getObject("HW_PinB_10")
hub = doc.getObject("P2a_KneeHingePlate")
for nm, other in (("P1_KneeYoke", yoke), ("P2a hub", hub)):
    k = ring.common(other.Shape)
    v = 0.0 if k.isNull() else k.Volume / 1000.0
    print("  bearing vs %-14s %.3f cm3 %s" % (nm, v, "" if v < 0.02 else "<-- INTERFERENCE"))
    assert v < 0.02, "the bearing fouls %s by %.3f cm3" % (nm, v)
if pin is not None:
    k = ring.common(pin.Shape)
    print("  bearing vs pin           %.3f cm3 -- the pin runs through the bore, as it should"
          % (0.0 if k.isNull() else k.Volume / 1000.0))

doc.recompute()
doc.save()
print()
print("  Saved. The pin no longer touches printed plastic anywhere it rotates.")
print("  BOM: K3's two bushings come out, K2 stays (ISO 7379 12 x 70, or an ISO 8734 dowel).")
print("  Assembly: bore the seat to 28.2 and BOND the bearing -- do not press it into PETG.")
