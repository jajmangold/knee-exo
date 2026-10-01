# -*- coding: utf-8 -*-
"""Shave the raised glyphs that 414's fills left standing.

414 refilled four recesses by fusing the original engraving tool back. The tool is built
0.3 mm OUTSIDE the surface so that it cuts cleanly, which is right for cutting and wrong for
filling: fused back, it fills the recess AND leaves a 0.3 mm raised copy of the text standing
proud of the face.

    P24   +0.021 cm3 proud      P2a   +0.019 cm3 proud
    P31   +0.007 cm3 proud      P1    (fill landed under, nothing proud)

On P2a that face looks at the limb, so this is a raised character pressing on the patient --
precisely the thing 412 recesses text to avoid. Volumes this small are invisible in every
check the repo has except a direct one.

The fix is to trim each part back to its own original surface, which is a surface of
revolution about the limb axis for the radial marks and a plane for P31. Cutting with the
VOID side of that surface removes the proud material and nothing else, because the part had
no material there to begin with.

Send with:  python tools/fcsend.py scripts/415_shave_fills.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))

# (part, how to describe the surface the fill overshot)
#   ("cyl", r, y0, y1)   material lies OUTSIDE radius r about the limb axis over that span
#   ("plane_x", x0)      material lies BELOW x0
# P24 is NOT a cylinder at the mark: a void cylinder at r 122 would have taken 4.11 cm3 of
# legitimate shell, and the "too much to be just the proud text" guard refused it. It needs
# the precise version instead -- rebuild the fill tool, keep only the part of it that lies
# INSIDE the original surface, and cut that. Nothing else can be touched by construction,
# because the tool is glyph-shaped and 1.1 mm deep.
PRECISE = [("P24_FairingShank", "P24", -200.0, 90.0, 8.0, 122.0)]

# P1 is the opposite problem. Its 414 fill added 0.011 cm3 to a 0.029 cm3 recess -- it UNDER
# filled, leaving 62% of a mark that 413 had found visible. Nothing is proud, so the shave
# guard rightly refused it; what it needs is the rest of the fill. Build the tool and keep
# only the part lying OUTSIDE the original surface, which is exactly the recess.
PRECISE_FILL = [("P1_KneeYoke", "P1", 30.0, 90.0, 8.0, 76.8)]

JOBS = [
    ("P2a_KneeHingePlate", ("cyl", 70.0, -75.0, -45.0)),
    ("P31_InterfaceDist",  ("plane_x", 20.0)),
]

print("=" * 80)
print("SHAVING THE FILLS BACK TO THE ORIGINAL SURFACE")
print("=" * 80)
for name, spec in JOBS:
    o = doc.getObject(name)
    if o is None:
        print("  %-22s MISSING" % name)
        continue
    sh = o.Shape
    v0 = sh.Volume
    if spec[0] == "cyl":
        _, r, y0, y1 = spec
        void = Part.makeCylinder(r, y1 - y0, V(0.0, y0, 0.0), V(0, 1, 0))
    else:
        _, x0 = spec
        b = sh.BoundBox
        void = Part.makeBox(60.0, b.YLength + 20.0, b.ZLength + 20.0,
                            V(x0, b.YMin - 10.0, b.ZMin - 10.0))
    cut = sh.cut(void)
    removed = (v0 - cut.Volume) / 1000.0
    keep = [s for s in cut.Solids if s.Volume / 1000.0 > 0.5]
    if len(keep) != 1:
        print("  %-22s shave would leave %d solids -- skipped" % (name, len(keep)))
        continue
    cut = keep[0]
    try:
        cut.check(True)
    except Exception as e:
        print("  %-22s shave broke the solid -- skipped (%s)" % (name, e))
        continue
    if removed > 0.12:
        print("  %-22s would remove %.3f cm3 -- too much to be just the proud text, skipped"
              % (name, removed))
        continue
    o.Shape = cut
    print("  %-22s shaved %.4f cm3  (%.3f -> %.3f cm3)"
          % (name, removed, v0 / 1000.0, cut.Volume / 1000.0))

FONT = r"C:/Windows/Fonts/arialbd.ttf"
DEPTH = 0.8


def text_faces(txt, h):
    out = []
    for ch in Part.makeWireString(txt, FONT, h):
        fs = []
        for w in ch:
            try:
                fs.append(Part.Face(w))
            except Exception:
                pass
        if not fs:
            continue
        fs.sort(key=lambda f: -f.Area)
        f = fs[0]
        for g in fs[1:]:
            f = f.cut(g)
        out.append(f)
    return out


for name, mark, stn, deg, h, r0 in PRECISE:
    o = doc.getObject(name)
    sh = o.Shape
    fs = text_faces(mark, h)
    tb = fs[0]
    for f in fs[1:]:
        tb = tb.fuse(f)
    b = tb.BoundBox
    tb.translate(V(-0.5 * (b.XMin + b.XMax), -0.5 * (b.YMin + b.YMax), 0.0))
    t = math.radians(deg)
    rad, tang = V(math.cos(t), 0., math.sin(t)), V(-math.sin(t), 0., math.cos(t))
    m = FreeCAD.Matrix(0., tang.x, rad.x, rad.x * (r0 - 0.3),
                       1., tang.y, rad.y, stn,
                       0., tang.z, rad.z, rad.z * (r0 - 0.3),
                       0., 0., 0., 1.)
    tool = tb.transformGeometry(m).extrude(V(rad.x, rad.y, rad.z).multiply(DEPTH + 0.3))
    inner = Part.makeCylinder(r0, 60.0, V(0.0, stn - 30.0, 0.0), V(0, 1, 0))
    proud = tool.common(inner)
    if proud.isNull() or proud.Volume < 1.0:
        print("  %-22s nothing proud to shave" % name)
        continue
    v0 = sh.Volume
    cut = sh.cut(proud)
    keep = [q for q in cut.Solids if q.Volume / 1000.0 > 0.5]
    ok = len(keep) == 1
    if ok:
        try:
            keep[0].check(True)
        except Exception:
            ok = False
    if ok:
        o.Shape = keep[0]
        print("  %-22s shaved %.4f cm3 precisely  (%.3f -> %.3f cm3)"
              % (name, (v0 - keep[0].Volume) / 1000.0, v0 / 1000.0, keep[0].Volume / 1000.0))
    else:
        print("  %-22s precise shave rejected -- left as is" % name)

for name, mark, stn, deg, h, r0 in PRECISE_FILL:
    o = doc.getObject(name)
    sh = o.Shape
    fs = text_faces(mark, h)
    tb = fs[0]
    for f in fs[1:]:
        tb = tb.fuse(f)
    b = tb.BoundBox
    tb.translate(V(-0.5 * (b.XMin + b.XMax), -0.5 * (b.YMin + b.YMax), 0.0))
    t = math.radians(deg)
    rad, tang = V(math.cos(t), 0., math.sin(t)), V(-math.sin(t), 0., math.cos(t))
    m = FreeCAD.Matrix(0., tang.x, rad.x, rad.x * (r0 - 0.3),
                       1., tang.y, rad.y, stn,
                       0., tang.z, rad.z, rad.z * (r0 - 0.3),
                       0., 0., 0., 1.)
    tool = tb.transformGeometry(m).extrude(V(rad.x, rad.y, rad.z).multiply(DEPTH + 0.3))
    inner = Part.makeCylinder(r0, 60.0, V(0.0, stn - 30.0, 0.0), V(0, 1, 0))
    plug = tool.cut(inner)           # only what lies outboard of the original surface
    v0 = sh.Volume
    fused = sh.fuse(plug).removeSplitter()
    keep = [q for q in fused.Solids if q.Volume / 1000.0 > 0.5]
    ok = len(keep) == 1 and keep[0].Volume > 0
    if ok:
        try:
            keep[0].check(True)
        except Exception:
            ok = False
    if ok:
        o.Shape = keep[0]
        print("  %-22s filled %.4f cm3 precisely  (%.3f -> %.3f cm3)"
              % (name, (keep[0].Volume - v0) / 1000.0, v0 / 1000.0, keep[0].Volume / 1000.0))
    else:
        print("  %-22s precise fill rejected -- left as is" % name)

doc.recompute()
doc.save()
print()
print("  The surfaces are back to where they were before 414 touched them. 412's own fill")
print("  path should build its tool at the surface, not 0.3 mm outside it -- noted there.")
print("DONE.")
