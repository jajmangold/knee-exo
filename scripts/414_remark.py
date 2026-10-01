# -*- coding: utf-8 -*-
"""Move the three part numbers that ended up on show.

412 placed every mark on the first surface a ray from the limb axis meets, and called that an
inner face. 413 tested the claim properly for the first time and found three of fifteen marks
with a clear line of sight from outside: P24_FairingShank, P1_KneeYoke and P2a_KneeHingePlate,
all of them around the knee, which is the one part of this device that is deliberately open.

"Inner surface" and "hidden" are not the same property, and nothing was checking the second
one. This script does two things:

  1. FILLS the old recess. The engraving tool is reproducible from its placement, so fusing
     the same solid back restores the surface. These three parts are not in the 393..409
     rebuild chain, so there is no other way to undo a cut on them.
  2. RE-CUTS at a spot that is both smooth AND covered, by running 413's visibility fan
     inside the search instead of after it.

Send with:  python tools/fcsend.py scripts/414_remark.py
"""
import math
import os
import FreeCAD
import Part
from FreeCAD import Vector as V

def _kx_doc():
    """The model, whether we are in the GUI instance or under freecadcmd.

    KX_DOC overrides the file, which is how the mirrored right leg is checked with the same
    scripts. Headless matters: 397 and 409 both exceed the RPC server's 90 s dispatch limit,
    and overrunning it does not fail cleanly -- it keeps working and leaves a half-built
    document the next script reads as finished.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
FONT = r"C:/Windows/Fonts/arialbd.ttf"
DEPTH = 0.8

# (part, mark, the placement 412 used, the stations to try instead)
REDO = [
    ("P1_KneeYoke", "P1", (100.0, 90.0, 8.0),
     tuple(float(v) for v in range(40, 125, 5))),
]

# P31's mark is PLANAR and its X = +20 face is open to the world -- 13 of 13 rays escape.
# Its only covered face is the underside at Z 123, which beds on P6_ShankSocket. A 0.8 mm
# recess in a bolted joint face is harmless; a visible part number is not what was asked for.
PLANAR_REDO = []


def text_faces(s, h):
    out = []
    for ch in Part.makeWireString(s, FONT, h):
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


def tool_at(mark, stn, deg, h, r0):
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
    return tb.transformGeometry(m).extrude(V(rad.x, rad.y, rad.z).multiply(DEPTH + 0.3)), fs


def first_hit(sh, y, deg, want_wall=0.0):
    t = math.radians(deg)
    e = Part.makeLine(V(2 * math.cos(t), y, 2 * math.sin(t)),
                      V(260 * math.cos(t), y, 260 * math.sin(t)))
    k = sh.common(e)
    if k.isNull() or not k.Vertexes:
        return None
    rs = sorted(math.hypot(v.Point.x, v.Point.z) for v in k.Vertexes)
    if want_wall > 0.0 and (len(rs) < 2 or rs[1] - rs[0] < want_wall):
        return None
    return rs[0]


def fan(n, k=13):
    n = V(n.x, n.y, n.z); n.normalize()
    a = V(0., 1., 0.) if abs(n.y) < 0.9 else V(1., 0., 0.)
    u = n.cross(a); u.normalize()
    w = n.cross(u)
    out = [n]
    # 13 rays, matching 413. The 9-ray version cleared P24 at Y -200 and 413 then found
    # two escaping directions it had simply not sampled -- a coarser fan is not a
    # weaker test, it is a test that reports the wrong answer.
    for ang in (35.0, 70.0):
        for j in range(6):
            ph = 2.0 * math.pi * j / 6.0
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            out.append(V(n.x * c + (u.x * math.cos(ph) + w.x * math.sin(ph)) * s,
                         n.y * c + (u.y * math.cos(ph) + w.y * math.sin(ph)) * s,
                         n.z * c + (u.z * math.cos(ph) + w.z * math.sin(ph)) * s))
    return out[:k]


def hidden(pt, look):
    for d in fan(look):
        far = V(pt.x + d.x * 400., pt.y + d.y * 400., pt.z + d.z * 400.)
        seg = Part.makeLine(V(pt.x + d.x * 0.25, pt.y + d.y * 0.25, pt.z + d.z * 0.25), far)
        clear = True
        for o in PARTS:
            if not seg.BoundBox.intersect(o.Shape.BoundBox):
                continue
            k = o.Shape.common(seg)
            if not k.isNull() and k.Edges:
                clear = False
                break
        if clear:
            return False
    return True


print("=" * 84)
print("RE-MARKING -- fill the exposed recess, re-cut somewhere covered")
print("=" * 84)
for name, mark, (ostn, odeg, oh), stations in REDO:
    o = doc.getObject(name)
    sh = o.Shape
    r0 = first_hit(sh, ostn, odeg)
    tool, fs = tool_at(mark, ostn, odeg, oh, r0)
    v0 = sh.Volume
    filled = sh.fuse(tool).removeSplitter()
    if filled.Volume < v0:
        filled = sh.fuse(tool)
    print("  %-20s filled the old mark at Y %+.0f %+.0f: %.3f -> %.3f cm3"
          % (name, ostn, odeg, v0 / 1000., filled.Volume / 1000.))

    placed = False
    for stn in stations:
        for deg in range(0, 360, 10):
            r = first_hit(filled, float(stn), float(deg), want_wall=DEPTH + 0.6)
            if r is None or r < 12.0:
                continue
            t = math.radians(deg)
            pt = V(r * math.cos(t), float(stn), r * math.sin(t))
            if not hidden(pt, V(-math.cos(t), 0.0, -math.sin(t))):
                continue
            for h in (8.0, 5.0):
                tl, fs2 = tool_at(mark, float(stn), float(deg), h, r)
                cut = filled.cut(tl)
                removed = (filled.Volume - cut.Volume) / 1000.
                want = sum(f.Area for f in fs2) * DEPTH / 1000.
                if not (0.5 * want < removed < 1.6 * want):
                    continue
                try:
                    cut.check(True)
                except Exception:
                    continue
                if len(cut.Solids) != 1:
                    continue
                o.Shape = cut
                print("     re-cut at Y %+.0f bearing %+d, r %.1f, %.0f mm text: %.3f cm3, HIDDEN"
                      % (stn, deg, r, h, removed))
                placed = True
                break
            if placed:
                break
        if placed:
            break
    if not placed:
        o.Shape = filled
        print("     no covered spot found -- left FILLED and unmarked")

for name, mark, opt, odir, npt, ndir in PLANAR_REDO:
    o = doc.getObject(name)
    sh = o.Shape

    def planar_tool(pt, d, along, up, h):
        fs = text_faces(mark, h)
        tb = fs[0]
        for f in fs[1:]:
            tb = tb.fuse(f)
        b = tb.BoundBox
        tb.translate(V(-0.5 * (b.XMin + b.XMax), -0.5 * (b.YMin + b.YMax), 0.0))
        m = FreeCAD.Matrix(along.x, up.x, d.x, pt.x,
                           along.y, up.y, d.y, pt.y,
                           along.z, up.z, d.z, pt.z,
                           0., 0., 0., 1.)
        return tb.transformGeometry(m).extrude(V(d.x, d.y, d.z).multiply(DEPTH + 0.6)), fs

    old_tool, _ = planar_tool(opt, odir, V(0., 1., 0.), V(0., 0., 1.), 5.0)
    v0 = sh.Volume
    filled = sh.fuse(old_tool).removeSplitter()
    print("  %-20s filled the exposed X=20 mark: %.3f -> %.3f cm3"
          % (name, v0 / 1000., filled.Volume / 1000.))
    tl, fs = planar_tool(npt, ndir, V(0., 1., 0.), V(1., 0., 0.), 8.0)
    cut = filled.cut(tl)
    removed = (filled.Volume - cut.Volume) / 1000.
    want = sum(f.Area for f in fs) * DEPTH / 1000.
    ok = 0.5 * want < removed < 1.6 * want and len(cut.Solids) == 1
    try:
        cut.check(True)
    except Exception:
        ok = False
    if ok and hidden(npt, V(-ndir.x, -ndir.y, -ndir.z)):
        o.Shape = cut
        print("     re-cut on the underside at Z %.1f: %.3f cm3, HIDDEN" % (npt.z, removed))
    else:
        o.Shape = filled
        print("     underside re-cut rejected (removed %.3f of %.3f) -- left filled"
              % (removed, want))

doc.recompute()
doc.save()
print("DONE.")
