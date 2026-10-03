# -*- coding: utf-8 -*-
"""Should the shank rail be a 2040 too, with a yoke over its END rather than bolted to a face?

Asked at the bench: "we should make it a 2040 as well, and basically make another knee yoke-type
part, except it can be directly over the top/end of the 2040 and not just bolted to the back" --
and before that, "it needs to be even closer to the leg and aligned actually with the P1_KneeYoke
piece, the knee joint itself should sit directly over the 2020".

This file answers all three with the model's own numbers and changes nothing.

THE SECTIONS ARE MEASURED, NOT LOOKED UP. Both rails are modelled with their real profiles -- 23
faces on the 2020, slots and core void included -- so the second moment of area comes from the
section itself through FreeCAD's MatrixOfInertia, not from a catalogue figure for a profile that
might not be the one drawn.

WHAT BENDS THE SHANK RAIL. The knee applies 28.2 N.m in the sagittal plane, which is bending
about the Z axis, and a section resists that with its X dimension. The thigh rail already puts its
40 mm across X for exactly this reason. The shank rail is a 2020: square, so it has the 20 mm
dimension in the direction that matters.

    freecadcmd.exe scripts/431_shank_2040.py
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

TORQUE = 28200.0        # N.mm
E_AL = 69000.0          # MPa, 6063
RHO_AL = 2.70e-3        # g/mm3
LEN_SHANK = 244.0       # the rail as it now stands, Y -300..-56


def section(shape, y):
    """the rail's real cross-section as a face, holes subtracted"""
    ws = shape.slice(V(0, 1, 0), y)
    fs = [Part.Face(w) for w in ws]
    outer = max(fs, key=lambda f: f.Area)
    prof = outer
    for f in fs:
        if f is not outer:
            prof = prof.cut(f)
    # Face.cut returns a Compound; the face with the hole in it is inside
    return prof if prof.ShapeType == "Face" else prof.Faces[0]


def inertia(face):
    """(area, I for sagittal bending, I for the other plane) in mm^2 and mm^4

    The section lies in the X-Z plane at a fixed Y, and MatrixOfInertia is taken about the
    section's own centroid, so the Y terms vanish: A33 = integral of (x-x0)^2 dA, which is the
    second moment about the Z axis -- the one the knee's 28.2 N.m bends the rail around, and the
    one the 40 mm dimension serves. A11 is the other plane. Getting these the wrong way round
    makes a 2040 look no better than a 2020, which is the answer the catalogue would also give
    if you read the wrong column.
    """
    m = face.MatrixOfInertia
    return face.Area, m.A33, m.A11


print("=" * 98)
print("A 2040 SHANK RAIL, AND A YOKE OVER ITS END  --  %s" % _BASE)
print("=" * 98)

a4 = doc.getObject("A4_Shank2020_VSlot")
a1 = doc.getObject("A1_Extrusion_20x60_VSlot")
s20 = section(a4.Shape, -200.0)
s40 = section(a1.Shape, 150.0)
a20, i20x, i20z = inertia(s20)
a40, i40x, i40z = inertia(s40)

print("  measured from the model's own profiles:")
print("     %-22s area %6.1f mm2   I(sagittal bending) %8.0f mm4" % ("2020 shank rail", a20, i20x))
print("     %-22s area %6.1f mm2   I(sagittal bending) %8.0f mm4" % ("2040 thigh rail", a40, i40x))
print("     the 2040 is %.1fx the section and %.1fx the stiffness in the plane the knee bends"
      % (a40 / a20, i40x / i20x))

print()
print("  WHAT THAT IS WORTH, over %.0f mm of shank rail at %.1f N.m:" % (LEN_SHANK, TORQUE / 1000))
for nm, area, i in (("2020 as drawn", a20, i20x), ("2040", a40, i40x)):
    half = max(abs(s20.BoundBox.XMin), abs(s20.BoundBox.XMax)) if "2020" in nm else \
        max(abs(s40.BoundBox.XMin), abs(s40.BoundBox.XMax))
    stress = TORQUE * half / i
    tip = math.degrees(TORQUE * LEN_SHANK / (E_AL * i))
    print("     %-14s  %5.1f MPa in the rail,  %5.2f deg of twist-up at the ankle,  %5.0f g"
          % (nm, stress, tip, area * LEN_SHANK * RHO_AL))
print("  The 2020 is strong enough -- 6063 yields at ~170 -- but it is SOFT: most of a degree of")
print("  knee angle that the encoder on the motor cannot see, because it happens past the sensor.")

print()
print("  WHERE THE JOINT IS, AND WHERE THE RAIL WOULD HAVE TO BE TO SIT UNDER IT")
p1 = doc.getObject("P1_KneeYoke").Shape
seat = [f for f in p1.Faces if f.Surface.TypeId == "Part::GeomCylinder"
        and 27.5 <= 2 * f.Surface.Radius <= 28.5]
zc = None
if seat:
    b = seat[0].BoundBox
    zc = 0.5 * (b.ZMin + b.ZMax)
    print("     the 6001 sits at Z %.1f..%.1f, so the joint's plane is Z %.1f" % (b.ZMin, b.ZMax, zc))
b4 = a4.Shape.BoundBox
print("     the rail is centred at Z %.1f -- %.1f mm outboard of the joint"
      % (0.5 * (b4.ZMin + b4.ZMax), 0.5 * (b4.ZMin + b4.ZMax) - (zc or 0)))
print("     putting a 20-deep rail under the joint means Z %.1f..%.1f" % ((zc or 0) - 10, (zc or 0) + 10))

print()
print("  IS THERE ROOM? the limb is the thing that decides")
ref = doc.getObject("REF_Shank").Shape
for y in (-60.0, -100.0, -160.0, -220.0, -300.0):
    hits = [zt for zt in [40.0 + i * 1.0 for i in range(60)] if ref.isInside(V(0.0, y, zt), 1e-7, True)]
    skin = max(hits) if hits else None
    if skin is None:
        print("     Y %6.0f : no limb" % y)
        continue
    print("     Y %6.0f : skin at Z %4.0f, rail's inner face would be Z %4.0f -> %5.1f mm of gap"
          % (y, skin, (zc or 0) - 10, (zc or 0) - 10 - skin))
print("     (3 mm of that is the neoprene sleeve, so the cuff shell needs the rest)")

print()
print("  WHAT IT COSTS. The shank swings about the knee, so mass here is not free the way thigh")
print("  mass is -- it is the reflected inertia the whole 14.5:1 was chosen to keep low.")
extra = (a40 - a20) * LEN_SHANK * RHO_AL
print("     +%.0f g of aluminium on the shank" % extra)
print("     at a mean radius of about 0.18 m that is +%.4f kg.m2 against the limb's own ~0.30"
      % (extra * 1e-3 * 0.18 ** 2))
print("     and the device already reflects 0.065 kg.m2 of rotor, so this is ~%.0f%% of that"
      % (100 * extra * 1e-3 * 0.18 ** 2 / 0.065))

print()
print("  THE YOKE OVER THE END. A 2040's end face has two cells, so two M5 self-tapping screws")
print("  into the core on the rail's own axis at X +-10 -- against one on a 2020. Those two take")
print("  the rail's torsion directly, which is what 'bolted to the back' cannot do: a plate on one")
print("  face reacts torsion as a couple on its bolts, an end cap reacts it in the screws' shear")
print("  and the cap's wrap.")
