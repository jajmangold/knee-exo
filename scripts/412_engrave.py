# -*- coding: utf-8 -*-
"""STAGE 10: engrave the part number into each printed part.

Thirteen printed parts, several of them visually similar once they come off the bed -- three
identical-looking fairing mounts, two conical cuffs, two halves of one drive shell. Sorting
them by eye against a BOM is how the wrong bolt goes in the wrong hole.

So: recess the part number into a face that is HIDDEN once assembled, readable while you are
holding the part.

Choices and why:

  RECESSED, not raised. On the cuffs the engraved face is the bore, which sits against a
  neoprene sleeve. A raised character is a pressure point; a 0.8 mm recess under a 3 mm
  sleeve cannot be felt. It also prints better -- a recess in a vertical wall is just a
  shallower perimeter, where raised text on a vertical wall is a 0.8 mm island per layer.

  0.8 mm deep, 8 mm tall, ARIAL BOLD. Bold because stroke width is what decides whether text
  survives a 0.4 mm nozzle: Arial Bold at 8 mm has ~1.2 mm stems, three extrusions wide.
  Regular weight is ~0.8 mm and comes out as a single wobbly bead.

  PLACED BY RAY-CAST, not by hand. Fire a ray out from the part's own axis at a chosen
  station and bearing, take the first surface it meets, and build the text on the tangent
  plane there. That puts the engraving on the inner surface of whatever shape the part
  actually is -- conical cuff, superelliptical fairing, round pod -- without anyone having to
  work out where that surface is.

  VERIFIED, because an engraving that misses the part removes nothing and says nothing. Each
  cut is checked for a plausible removed volume, and every part is re-checked with
  Shape.check() afterwards: text is dozens of small faces and tight curves, which is exactly
  the kind of geometry that produced a BOPAlgo SelfIntersect on the cuff earlier.

Run ONE PART PER CALL. The bearing search is ~1000 line-solid booleans and chunks of
three went past the 90 s GUI dispatch limit -- which does not fail cleanly, it keeps
working in the background and leaves the document in a state the next run misreads:

  for i in $(seq 0 14); do ... I0=$i I1=$((i+1)) ; done
"""
import math
import os
import FreeCAD
import Part
from FreeCAD import Vector as V

# Runs either in the GUI instance or headless under freecadcmd. Headless matters: the
# bearing search on P24 takes over 90 s, which is the RPC server's dispatch limit, and
# overrunning it does not fail cleanly -- it keeps working and leaves a half-applied document.
DOCFILE = r"C:/Users/Josh/KneeExo_v6.FCStd"
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
except Exception:
    doc = FreeCAD.openDocument(DOCFILE)

FONT = None
for cand in (r"C:/Windows/Fonts/arialbd.ttf", r"C:/Windows/Fonts/verdanab.ttf",
             r"C:/Windows/Fonts/consolab.ttf"):
    if os.path.exists(cand):
        FONT = cand
        break
assert FONT, "no bold font found"
H = 8.0          # cap height
DEPTH = 0.8      # recess
MIN_STEM = 1.1   # mm, what a 0.4 nozzle resolves at 3 perimeters

# part -> (label, axis to cast from, station along it). The BEARING is searched for, not
# chosen: hand-picked bearing 0 (posterior) missed ten of the thirteen parts outright,
# because most of this device is lateral and nothing is at +X. The search wants a patch that
# is smooth over the whole footprint of the text, so the engraving does not run off an edge
# or over a step.
MOT = V(-104.0, 0.0, 62.0)
JOBS = [
    ("P5_ThighCuff",      "P5",  "Y", (150.0, 165.0, 135.0)),
    ("P7_ShankCuff",      "P7",  "Y", (-320.0, -305.0, -335.0)),
    ("P21_ShellAnterior", "P21", "Y", (100.0, 70.0, 140.0)),
    # NOT Y 226..283: 502 ports the shell there for the interface boss, so the old mark
    # site is now a hole and the search correctly refuses it.
    ("P22_DriveCap",      "P22", "Y", (205.0, 310.0, 195.0, 320.0)),
    ("P25_MotorNacelle",  "P25", "M", (250.0, 235.0, 265.0)),
    # Stations vetted by 413: the knee end of these parts is OPEN, and marks placed there
    # are visible from outside however "inner" the surface is.
    ("P24_FairingShank",  "P24", "Y", (-175.0, -180.0, -170.0)),
    ("P20_KneeShroud",    "P20", "Y", (0.0, 15.0, -15.0)),
    ("P1_KneeYoke",       "P1",  "Y", (55.0, 60.0, 90.0)),
    # P2a_KneeHingePlate is deliberately absent. 414 searched 16 stations x 36 bearings
    # and found nowhere covered -- it is the knee hub at an open joint, reachable from
    # every direction. It is the 143 cm3 29T pulley; an unmarked part is the better trade.
    ("P6_ShankSocket",    "P6",  "Y", (-260.0, -240.0, -280.0)),
    # The three mounts are the SAME PART printed three times -- 398 builds one shape at
    # three stations, 6.4 cm3 each, identical bounding box. They are interchangeable, so
    # they get the same mark, and "P23a" never fitted anyway: the bracket is 16 mm along
    # the limb axis and the four-character string is 22 mm at full height.
    # PLANAR, not radial. These are 27 x 16 x 39 brackets sitting off to the side at
    # X 20..47, not shells around the limb axis: a ray from that axis hits one of them at
    # exactly ONE bearing out of 36, so the smoothness search can never find a patch.
    # The face is X = 47, which faces the thigh fairing's inner surface and is hidden once
    # assembled. X = 20 was the first choice -- it beds against the rail -- but a material map
    # showed it solid over only 12 mm of Z, so a third of the glyphs fell into air and the cut
    # removed 0.016 cm3 of an expected 0.050. X = 47 is solid for 36 mm.
    ("P23a_FairingMount", "P23", "P", (47.0, 88.0, 109.0)),
    ("P23b_FairingMount", "P23", "P", (47.0, 124.0, 109.0)),
    ("P23c_FairingMount", "P23", "P", (47.0, 160.0, 109.0)),
    # The KX-1 bosses, on their X = +20 side face -- not on the mating face, which has to stay
    # flat, and not on the underside, which beds on its host. 501 says a cold module should be
    # identifiable without a BOM; that is only true if the interface itself is marked.
    ("P30_InterfaceProx", "P30", "P2", (20.0, 255.0, 137.0)),
    # UNDERSIDE, not the side face. 413 found the X=20 face open to the world, 13 of 13
    # rays escaping; the underside at Z 123 beds on P6_ShankSocket. A 0.8 mm recess in a
    # bolted joint face is harmless, a readable part number on the outside is not.
    ("P31_InterfaceDist", "P31", "P3", (0.0, -275.0, 123.0)),
]


def text_faces(s, h=None):
    """One planar face per character, holes already subtracted, laid out along local +X."""
    out = []
    for ch in Part.makeWireString(s, FONT, h or H):
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
        for h in fs[1:]:
            f = f.cut(h)
        out.append(f)
    return out


def first_hit(sh, origin, y, deg, rmax=260.0, want_wall=0.0):
    """Radius at which a ray leaving `origin` at `deg` first meets the shape.

    want_wall > 0 also demands that much material BEHIND that surface. Without it the
    search happily picks a tangent graze -- three parts reported a surface and then removed
    0.000 cm3, because the text was placed on a shape the ray only touched."""
    t = math.radians(deg)
    d = V(math.cos(t), 0.0, math.sin(t))
    p0 = V(origin.x, y, origin.z)
    e = Part.makeLine(p0.add(d.multiply(2.0)), V(origin.x, y, origin.z).add(
        V(math.cos(t), 0.0, math.sin(t)).multiply(rmax)))
    k = sh.common(e)
    if k.isNull() or not k.Vertexes:
        return None
    rs = sorted(math.hypot(v.Point.x - origin.x, v.Point.z - origin.z) for v in k.Vertexes)
    if want_wall > 0.0:
        if len(rs) < 2 or (rs[1] - rs[0]) < want_wall:
            return None
    return rs[0]


def _fan(n, k=9):
    n = V(n.x, n.y, n.z); n.normalize()
    a = V(0., 1., 0.) if abs(n.y) < 0.9 else V(1., 0., 0.)
    u = n.cross(a); u.normalize()
    w = n.cross(u)
    out = [n]
    for ang in (35.0, 70.0):
        for j in range(4):
            ph = 2.0 * math.pi * j / 4.0
            c, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            out.append(V(n.x * c + (u.x * math.cos(ph) + w.x * math.sin(ph)) * sn,
                         n.y * c + (u.y * math.cos(ph) + w.y * math.sin(ph)) * sn,
                         n.z * c + (u.z * math.cos(ph) + w.z * math.sin(ph)) * sn))
    return out[:k]


def _occluders():
    return [o for o in doc.Objects
            if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
            and not o.Shape.isNull() and o.Shape.Solids]


def is_hidden(pt, look, parts):
    """no line of sight from outside, with the reference limbs counted as occluders"""
    for d in _fan(look):
        far = V(pt.x + d.x * 400., pt.y + d.y * 400., pt.z + d.z * 400.)
        seg = Part.makeLine(V(pt.x + d.x * 0.25, pt.y + d.y * 0.25, pt.z + d.z * 0.25), far)
        clear = True
        for o in parts:
            if not seg.BoundBox.intersect(o.Shape.BoundBox):
                continue
            k = o.Shape.common(seg)
            if not k.isNull() and k.Edges:
                clear = False
                break
        if clear:
            return False
    return True


def find_spot(sh, org, stations, half_len, half_h, hoop=False):
    """a (station, bearing) whose surface is smooth across the whole text footprint"""
    best = None
    for stn in stations:
        for d10 in range(0, 360, 10):
            deg = float(d10)
            r0 = first_hit(sh, org, stn, deg, want_wall=DEPTH + 0.6)
            if r0 is None or r0 < 12.0:
                continue
            # AXIAL lays the string along the limb; HOOP lays it around the part. The
            # fairing mounts are 16 mm of limb axis and 'P23' is 12 mm at 5 mm height, so
            # axially the edge probes land exactly on the part's boundary and the search
            # finds nothing. Around the hoop at r 113 the same string is 6 degrees of arc.
            dang = math.degrees((half_len if hoop else half_h) / r0)
            dlen = half_h if hoop else half_len
            # five probes, not nine: centre plus the four edge midpoints. The corners were
            # costing 44% of the search for no case they alone rejected.
            probes = [first_hit(sh, org, stn + dy, deg + da, want_wall=DEPTH + 0.4)
                      for dy, da in ((0.0, 0.0), (-dlen, 0.0), (dlen, 0.0),
                                     (0.0, -dang), (0.0, dang))]
            if any(q is None for q in probes):
                continue
            spread = max(probes) - min(probes)
            if spread > 1.2:
                continue
            # VISIBILITY GATE. A smooth inner surface is not the same as a hidden one, and
            # placing marks without this check put six of them on show -- the user spotted two
            # by eye. The mark looks back along -rad, so that is the direction to test.
            t = math.radians(deg)
            pt = V(org.x + r0 * math.cos(t), stn, org.z + r0 * math.sin(t))
            if not is_hidden(pt, V(-math.cos(t), 0.0, -math.sin(t)), OCC):
                continue
            if best is None or spread < best[0]:
                best = (spread, stn, deg, r0)
            if spread < 0.25:          # flat enough; stop looking
                break
        if best is not None:
            break
    return best


OCC = _occluders()
print("=" * 86)
print("ENGRAVING -- %s, %.0f mm tall, %.1f mm deep" % (os.path.basename(FONT), H, DEPTH))
print("=" * 86)
print("  %-20s %-6s %-19s %-11s %-11s %s"
      % ("part", "mark", "placed at", "removed", "expected", "check"))
I0, I1 = __I0__, __I1__          # chunked: the bearing search is ~2000 ray casts
done = 0                         # per part and the GUI dispatch dies at 90 s
for name, mark, axis, stations in JOBS[I0:I1]:
    o = doc.getObject(name)
    if o is None:
        print("  %-22s MISSING" % name)
        continue
    sh = o.Shape

    if axis in ("P", "P2", "P3"):
        # explicit face: point on it, outward normal -X, text along +Z, up +Y
        px, py, pz = stations
        faces = None
        for h in ((H, 6.0, 5.0) if axis == "P" else (5.0, 4.0)):
            faces = text_faces(mark, h)
            tb = faces[0]
            for f in faces[1:]:
                tb = tb.fuse(f)
            if tb.BoundBox.XLength < 34.0:
                break
        bb = tb.BoundBox
        tb.translate(V(-0.5 * (bb.XMin + bb.XMax), -0.5 * (bb.YMin + bb.YMax), 0.0))
        if axis == "P":
            # local x -> +Z, local y -> +Y, local z -> -X (into the part from X = 47)
            m = FreeCAD.Matrix(0.0, 0.0, -1.0, px + 0.3,
                               0.0, 1.0, 0.0, py,
                               1.0, 0.0, 0.0, pz,
                               0.0, 0.0, 0.0, 1.0)
        elif axis == "P2":
            # P2: local x -> +Y, local y -> +Z, local z -> -X. Same face normal, but the
            # string runs along the limb because these bosses are 56 long and 7 tall.
            m = FreeCAD.Matrix(0.0, 0.0, -1.0, px + 0.3,
                               1.0, 0.0, 0.0, py,
                               0.0, 1.0, 0.0, pz,
                               0.0, 0.0, 0.0, 1.0)
        else:
            # P3: an UNDERSIDE. local x -> +Y, local y -> +X, local z -> +Z (upward into
            # the part from below).
            m = FreeCAD.Matrix(0.0, 1.0, 0.0, px,
                               1.0, 0.0, 0.0, py,
                               0.0, 0.0, 1.0, pz - 0.3,
                               0.0, 0.0, 0.0, 1.0)
        d = V(-(DEPTH + 0.3), 0.0, 0.0) if axis in ("P", "P2") else V(0.0, 0.0, DEPTH + 0.3)
        tool = tb.transformGeometry(m).extrude(d)
        v0 = sh.Volume
        cut = sh.cut(tool)
        removed = (v0 - cut.Volume) / 1000.0
        want = sum(f.Area for f in faces) * DEPTH / 1000.0
        try:
            cut.check(True)
            chk = "clean"
        except Exception:
            chk = "SELF-INTERSECT"
        ok = 0.35 * want < removed < 1.8 * want and chk == "clean"
        print("  %-20s %-6s %-11s %7.3f cm3 %7.3f cm3  %s%s"
              % (name, mark, ("face X %.0f" % px) if axis != "P3" else ("under Z %.0f" % pz),
                 removed, want, chk, "" if ok else "  <-- MISSED"))
        if ok and len(cut.Solids) == 1:
            o.Shape = cut
            done += 1
        continue

    org = MOT if axis.startswith("M") else V(0.0, 0.0, 0.0)
    hoop = axis.endswith("h")
    # SHRINK TO FIT. "P23a" at 8 mm is 22 mm long and the mount is 16 mm of limb axis, so
    # the search could never find room. Step the cap height down until it fits; 4 mm in a
    # bold face still has ~0.6 mm stems, which is thin but legible as a recess.
    spot = faces = tb = tbb = None
    for h in (H, 5.0):
        faces = text_faces(mark, h)
        if not faces:
            continue
        tb = faces[0]
        for f in faces[1:]:
            tb = tb.fuse(f)
        tbb = tb.BoundBox
        spot = find_spot(sh, org, stations, 0.5 * tbb.XLength + 2.0, 0.5 * h + 1.5,
                         hoop=hoop)
        if spot is not None:
            if h != H:
                print("  %-20s %-6s shrunk to %.0f mm to fit" % (name, mark, h))
            break
    if spot is None:
        print("  %-20s %-6s no patch with %.1f mm of wall on any station -- not engraved"
              % (name, mark, DEPTH + 0.6))
        continue
    _, stn, deg, r0 = spot
    blk = tb
    bb = tbb
    # centre the string on its own box, then map local (x -> +Y of the limb, y -> tangential)
    blk.translate(V(-0.5 * (bb.XMin + bb.XMax), -0.5 * (bb.YMin + bb.YMax), 0.0))
    t = math.radians(deg)
    rad = V(math.cos(t), 0.0, math.sin(t))
    tang = V(-math.sin(t), 0.0, math.cos(t))
    axis_y = V(0.0, 1.0, 0.0)
    u, w = (tang, axis_y) if hoop else (axis_y, tang)
    m = FreeCAD.Matrix(u.x, w.x, rad.x, org.x + rad.x * (r0 - 0.3),
                       u.y, w.y, rad.y, stn,
                       u.z, w.z, rad.z, org.z + rad.z * (r0 - 0.3),
                       0.0, 0.0, 0.0, 1.0)
    blk = blk.transformGeometry(m)

    # ALREADY ENGRAVED? This script is destructive and not idempotent, and it cannot
    # otherwise tell "the cut missed" from "the cut was made last time" -- both remove
    # 0.000 cm3 and both printed MISSED. Parts outside the 393..409 rebuild chain (P1, P20,
    # P2a, P6) keep their engraving across runs, so this matters. Measure how solid the
    # surface slab is before cutting: intact skin is ~100%, an engraved one is pitted.
    # 8 x 8 x 0.5, deliberately small: this is a FLAT slab laid on a CURVED surface, and
    # its corners lift off by the sagitta. Over 8 mm at the tightest radius here (r 32, the
    # motor pod) that is 0.25 mm, comfortably inside 0.5 mm of thickness. A 24 mm slab would
    # lift 2.2 mm and report intact skin as engraved.
    probe = Part.makeBox(8.0, 8.0, 0.5, V(-4.0, -4.0, 0.0))
    probe = probe.transformGeometry(FreeCAD.Matrix(
        u.x, w.x, rad.x, org.x + rad.x * r0,
        u.y, w.y, rad.y, stn,
        u.z, w.z, rad.z, org.z + rad.z * r0,
        0.0, 0.0, 0.0, 1.0))
    pk = sh.common(probe)
    frac = (0.0 if pk.isNull() else pk.Volume) / max(1e-9, probe.Volume)
    if frac < 0.88:
        print("  %-20s %-6s already engraved (%.0f%% solid skin at Y %+.0f %+.0f) -- skipped"
              % (name, mark, 100 * frac, stn, deg))
        continue

    tool = blk.extrude(V(rad.x, rad.y, rad.z).multiply(DEPTH + 0.3))
    v0 = sh.Volume
    cut = sh.cut(tool)
    removed = (v0 - cut.Volume) / 1000.0
    want = sum(f.Area for f in faces) * DEPTH / 1000.0
    ok = 0.35 * want < removed < 1.8 * want
    try:
        cut.check(True)
        chk = "clean"
    except Exception:
        chk = "SELF-INTERSECT"
    print("  %-20s %-6s Y%+7.0f %+4.0f r%5.1f %7.3f cm3 %7.3f cm3  %s%s"
          % (name, mark, stn, deg, r0, removed, want, chk, "" if ok else "  <-- MISSED"))
    if not ok:
        print("       engraving removed the wrong amount -- not applied")
        continue
    if chk != "clean":
        print("       engraving broke the solid -- not applied")
        continue
    assert len(cut.Solids) == 1, "%s split into %d solids" % (name, len(cut.Solids))
    o.Shape = cut
    done += 1

print()
print("  engraved %d of %d parts in this chunk" % (done, len(JOBS[I0:I1])))
print()
print("  NOTE ON VERIFYING THIS. A tempting shortcut is to scan each part's surface for")
print("  voids and call a pitted patch 'engraved'. It does not work: bolt holes, lightening")
print("  windows and shell ports all read the same way. A probe written that way scored the")
print("  interface bosses as engraved at 68%% solid skin when they were still blank -- it was")
print("  reading their bolt holes. The only trustworthy record is this script's own report.")
print("  Stem width at %.0f mm in this font is about %.1f mm; a 0.4 nozzle needs %.1f."
      % (H, 0.15 * H, MIN_STEM))
doc.recompute()
doc.save()
print("STAGE 10 DONE, saved.")
