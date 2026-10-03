# -*- coding: utf-8 -*-
"""P6_ShankSocket would not export. A valid, closed, BOP-clean solid that cannot be meshed.

Found by 219_stl.py refusing to write it:

    P6_ShankSocket will not mesh into a closed solid at any deflection tried
    -- 35250 facets, 15753 points

and nothing else in the repository could see it. isValid() said True, isClosed() said True,
Shape.check(True) was clean, the volume was right and there was exactly one solid. 411's
watertight test never ran, because 411 reads the STLs and the STL was never written.

WHAT IT ACTUALLY WAS. 33 faces under 0.01 mm2, in a band 1.2 NANOMETRES thick at the socket's
own bottom:

    GeomCylinder        Z 67.999999..68.000000   x14
    GeomBSplineSurface  Z 68.000000..68.000000   x10
    GeomPlane           Z 68.000000..68.000000   x6

432_shank_2040_build.py plugs the twelve old clamp holes with cylinders that run from the
socket's bbox ZMin to the pocket, and it makes them EXACTLY flush on purpose -- its own comment
says why: "Overshooting by 1 mm at each end put 0.056 cm3 of P6 inside P31 and 0.028 inside the
cuff -- both found by the sweep, both invisible here." Flush is what the sweep wanted and it is
also a tangent fuse, so OCC closed each plug against the bottom face a nanometre adrift and left
a film of degenerate faces. The engraved "P6L" sits in that same plane, which is where the ten
BSpline slivers come from.

THE FIX IS THE ONE THIS FILE'S WHOLE LESSON LIST ALREADY KNOWS: do not graze a face that is
already there. Overshoot the plug and then trim the part back to its envelope with a single
planar cut, which is a clean half-space operation rather than twelve tangencies. 432 is corrected
to do that for the next full rebuild; this file performs the same trim on the document as it
stands, because rebuilding the socket from 430's output would discard everything run after it.

    removeSplitter, Shape.fix(1e-4) and Shape.fix(1e-3) were all tried first. None of them
    produced a meshable solid; removeSplitter dropped it to 228 faces and broke BOP check.

    freecadcmd.exe scripts/436_socket_mesh.py
"""
import os
import sys

import FreeCAD
import MeshPart
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

SHAVE = 0.002           # mm. The band is 1.2e-6 thick; 2 microns clears it with 3 orders to
                        # spare and is three thousandths of a layer line.
TARGET = "P6_ShankSocket"


def meshes(sh):
    """219_stl.py's own deflection ladder, so this asserts what the exporter will ask"""
    for ld, ad in ((0.08, 0.35), (0.04, 0.2), (0.02, 0.12), (0.01, 0.08)):
        m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=ld, AngularDeflection=ad,
                                   Relative=False)
        m.harmonizeNormals()
        m.removeDuplicatedPoints()
        m.removeDuplicatedFacets()
        if m.isSolid():
            return ld, m.CountFacets
    return None, None


print("=" * 98)
print("THE SOCKET'S MESH  --  %s" % _BASE)
print("=" * 98)

o = doc.getObject(TARGET)
assert o is not None, "no %s in the document" % TARGET
sh = o.Shape
b = sh.BoundBox
tiny0 = len([f for f in sh.Faces if f.Area < 0.01])
ld0, _ = meshes(sh)
print("  before: %.3f cm3, %d faces, %d of them under 0.01 mm2, %s"
      % (sh.Volume / 1000.0, len(sh.Faces), tiny0,
         "meshes" if ld0 else "NO CLOSED MESH at any deflection"))
assert tiny0 > 0, "nothing degenerate to trim -- has 432 already been corrected and re-run?"

trimmed = sh.cut(Part.makeBox(b.XLength + 8.0, b.YLength + 8.0, 10.0,
                              V(b.XMin - 4.0, b.YMin - 4.0, b.ZMin - 10.0 + SHAVE)))
trimmed.check(True)
assert len(trimmed.Solids) == 1, "the trim gave %d solids" % len(trimmed.Solids)
lost = (sh.Volume - trimmed.Volume) / 1000.0
assert lost < 0.05, "the trim removed %.3f cm3, which is not a 2 micron shave" % lost
ld, facets = meshes(trimmed)
tiny = len([f for f in trimmed.Faces if f.Area < 0.01])
print("  after:  %.3f cm3, %d faces, %d under 0.01 mm2, %s"
      % (trimmed.Volume / 1000.0, len(trimmed.Faces), tiny,
         "meshes closed at deflection %.2f, %d facets" % (ld, facets) if ld
         else "STILL NO CLOSED MESH"))
assert ld is not None, "the trim did not make it meshable"
print("  %.4f cm3 removed -- %.1f%% of a 0.2 mm layer over the %.0f cm2 bottom face"
      % (lost, 100.0 * SHAVE / 0.2, b.XLength * b.YLength / 100.0))

# THE ENGRAVING LIVES IN THE FACE BEING TRIMMED, so it has to be shown to have survived: the
# glyphs are a 0.8 mm recess from Z 68 upward and the trim takes 2 microns off their mouth.
glyph = [f for f in trimmed.Faces
         if f.Surface.TypeId == "Part::GeomBSplineSurface" and f.BoundBox.ZMax > b.ZMin + 0.5]
print("  the mark is still cut: %d B-spline glyph faces reaching Z %.3f"
      % (len(glyph), max(f.BoundBox.ZMax for f in glyph) if glyph else 0.0))
assert len(glyph) >= 8, "only %d glyph faces left -- the trim has eaten the engraving" % len(glyph)

o.Shape = trimmed

# and it must not have moved against its neighbours. Only material was removed, so this can
# only improve, but P6 is the part 432 put inside P31 once already.
print()
print("  VERIFICATION")
fail = []
for nm in ("P31_InterfaceDist", "P7_ShankCuff", "A4_Shank2020_VSlot", "P2a_KneeHingePlate",
           "HW_ShankBolts_6xM5", "HW_JointBolts"):
    t = doc.getObject(nm)
    if t is None:
        continue
    c = trimmed.common(t.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    ok = v <= 0.02
    print("     %-24s %7.3f cm3 %s" % (nm, v, "" if ok else "<-- CLASH"))
    if not ok:
        fail.append("%s overlaps %s by %.3f cm3" % (TARGET, nm, v))

doc.recompute()
doc.save()
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  The socket exports. The defect was three orders of magnitude below any tolerance")
    print("  this repository checks, and the only test that saw it was asking for a mesh.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
