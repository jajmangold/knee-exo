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

Run headless, all parts in one process:

    KX_DOC=.../KneeExo_v6.FCStd KX_SUFFIX=L freecadcmd.exe scripts/412_engrave.py

KX_DRYRUN=1 reports each mark site without cutting. KX_I0/KX_I1 narrow the job list to
re-cut a single part. (The old form was one part per GUI call, because the bearing search is
~1000 line-solid booleans and three parts went past the 90 s dispatch limit -- which does not
fail cleanly, it keeps working in the background and leaves a document the next run misreads.)
"""
import json
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

# Runs either in the GUI instance or headless under freecadcmd. Headless matters: the
# bearing search on P24 takes over 90 s, which is the RPC server's dispatch limit, and
# overrunning it does not fail cleanly -- it keeps working and leaves a half-applied document.
DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

# KX_SUFFIX appends a leg letter, so the pair is "P5L" and "P5R" rather than two parts with
# the same number and no way to tell which leg they came off. It used to live only in the GUI
# session's globals -- the same failure as vs_leg: the script read SUFFIX and nothing in the
# repository ever set it, so a clean run died with NameError.
SUFFIX = os.environ.get("KX_SUFFIX", "")
# DRY RUN reports what each part's mark site looks like -- blank, already engraved, or no
# patch at all -- and cuts nothing. Needed before mirroring: a mark that survives into the
# right document reads backwards, and the only way to know which parts carry one is to probe.
DRY = bool(os.environ.get("KX_DRYRUN"))
# FILL mode puts a mark BACK. It exists because the four parts outside the 393..409 rebuild
# chain (P1, P20, P2a, P6) keep their engraving forever, and a kept mark is a mirrored mark
# once 701 reflects the document -- "P6" reads backwards on the right leg, which is worse than
# no mark. The tool is built by exactly the same placement code as the cut, which is the only
# way to be sure it lands on the same glyphs; a hand-written filler for three parts (414) had
# to be measured by hand and then shaved by 415 when it came out proud. Verified both ways:
# the skin must read PITTED before the fuse and SOLID after it.
FILL = bool(os.environ.get("KX_FILL"))
# KX_LEGACY builds the tool on the pre-fix, left-handed frame. Needed to FILL the 12 marks that
# were cut mirrored before tools/markframe.py existed; never for cutting.
LEGACY = bool(os.environ.get("KX_LEGACY"))
# An EXPLICIT site, "station,bearing,radius", for a fill whose placement this script's own
# search cannot rediscover. P1_KneeYoke is the case: 414 re-cut its mark with a looser wall
# criterion than find_spot demands, so find_spot now reports "no patch" on a part that is
# definitely engraved. The authoritative record of where every mark went is 413's MARKS
# table -- P1 is the point V(0, 55, 78.4), i.e. station 55, bearing +90, radius 78.4.
SITE = os.environ.get("KX_SITE")

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from markframe import matrix as mark_matrix     # noqa: E402

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
# How solid an 8 x 8 x 0.5 slab of skin has to be for the site to count as NOT yet engraved.
# Measured, not guessed. Engraved sites: P20 59%, P6 59%, P24 76%. Blank sites: P5 87%,
# P30 91%, P7 92%, P22 95%, P21 99%, P23 100%, P25 100%. The gap is 76..87, so 80% separates
# them; the 88% this started at called P5's blank bore "already engraved" and skipped it,
# because the slab there clips the edge of a webbing slot.
SKIN = 0.80

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
    # P24_FairingShank is gone, not merely unmarked: 430 moved the shank rail in-line under
    # the knee joint and there was nothing left for it to fair.
    ("P20_KneeShroud",    "P20", "Y", (0.0, 15.0, -15.0)),
    ("P1_KneeYoke",       "P1",  "Y", (55.0, 60.0, 90.0)),
    # P2a_KneeHingePlate is deliberately absent. 414 searched 16 stations x 36 bearings
    # and found nowhere covered -- it is the knee hub at an open joint, reachable from
    # every direction. It is the 135 cm3 29T pulley; an unmarked part is the better trade.
    ("P6_ShankSocket",    "P6",  "Y", (-260.0, -240.0, -280.0)),
    # THESE TWO WERE MISSING, and the hole was opened by 802_no_metal.py rather than by this
    # file: the gantry plate and the drive bracket were fabricated ALUMINIUM when the table was
    # written, so they were never engraved. Printing them made them printed parts like any other,
    # and nobody added them here -- so two of the seventeen carried no part number while the BOM
    # said "each engraved with its leg letter". 902's mark count expects PRINTED - 1 and was
    # reporting 14 against 16 without anyone reading it as this.
    ("P3_Carriage",       "P3",  "Y", (160.0, 130.0, 190.0)),
    ("A7_DriveBox",       "A7",  "Y", (240.0, 200.0, 280.0)),
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
    # The controller mount, on the face that beds against the motor's rear -- the same argument
    # as P31's underside: a 0.8 mm recess in a bolted joint face is harmless, a readable part
    # number on an outside face is not. Y 302 is that face; Z 86 is 24 mm above the motor's
    # axis, which clears the four M5 at Z 49.5/74.5 and still has 40 mm of disc across it.
    # NEEDS A FOURTH PLANAR MODE: this is the only mark in the device on a face normal to the
    # limb axis, so neither X mode nor the bed face frames it. markframe grew "P4" for it.
    ("P27_ControllerMount", "P27", "P4", (MOT.x, 302.0, 86.0)),
]


def fuse_clean(sh, tool):
    """Fuse and return the result that passes Shape.check(), with how it was made.

    removeSplitter() tidies the coplanar seams a fill leaves behind, and on P24_FairingShank it
    also produced a BOPAlgo self-intersection from a fuse that was already clean -- valid(),
    one solid, the right volume, and rejected by 701 on the mirror. Measured on that part:
    every variant through removeSplitter failed, every raw fuse passed, regardless of tool
    inflation, depth or fusing glyph by glyph. So prefer the tidy result and fall back to the
    raw one rather than losing the fill; leftover seam faces cost nothing in an STL.
    """
    out = []
    try:
        t = sh.fuse(tool).removeSplitter()
        if t.Volume < 0:                       # removeSplitter has inverted a solid before
            t.reverse()
        out.append(("merged", t))
    except Exception:
        pass
    try:
        out.append(("raw fuse", sh.fuse(tool)))
    except Exception:
        pass
    for how, t in out:
        try:
            t.check(True)
            return t, how, "clean"
        except Exception:
            continue
    return (out[0][1], out[0][0], "SELF-INTERSECT") if out else (None, "none", "FAILED")


def inflate(shape, f=1.06):
    """Grow a planar face set about its own centre.

    A fill tool that is exactly the shape of the recess shares every side wall with it, and
    fusing two solids across coincident faces is the classic way to get a BOPAlgo
    self-intersection: P24_FairingShank came back valid(), one solid, the right volume, and
    failed Shape.check() -- which 701 then refused to mirror. Growing the glyphs a few percent
    removes the coincidence. It is safe because the material around a mark is solid by
    construction: find_spot proved the surface smooth over the footprint plus 2 mm.
    Isotropic, about the centre, so a planar face set stays planar.
    """
    c = shape.BoundBox.Center
    m = FreeCAD.Matrix()
    m.move(V(-c.x, -c.y, -c.z))
    sc = FreeCAD.Matrix()
    sc.scale(f, f, f)
    back = FreeCAD.Matrix()
    back.move(V(c.x, c.y, c.z))
    return shape.transformGeometry(back.multiply(sc.multiply(m)))


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


# WHERE EVERY MARK WENT, written next to the document. 413 used to carry a hand-maintained
# table of these points, and a hand-maintained table of a thing a script computes goes stale
# the first time anything moves: the leg suffix alone shifted five marks and pushed two onto a
# smaller cap height. The registry is also the only record of a site the search cannot
# rediscover -- P1_KneeYoke's, which needed KX_SITE to find at all.
REG = DOCFILE[:-6] + ".marks.json"
registry = {}
if os.path.exists(REG):
    try:
        registry = json.load(open(REG))
    except Exception:
        registry = {}


def record(name, text, pt, normal, mode, h, axis):
    """mode is what 413 needs (which way to fire its rays); axis is the exact frame style, so
    that a later fill, re-cut or render reconstructs the SAME frame rather than guessing."""
    registry[name] = {"text": text, "point": [round(v, 3) for v in pt],
                      "normal": [round(v, 4) for v in normal], "mode": mode,
                      "axis": axis, "height": h}


OCC = _occluders()
print("=" * 86)
print("ENGRAVING -- %s, %.0f mm tall, %.1f mm deep" % (os.path.basename(FONT), H, DEPTH))
print("=" * 86)
print("  %-20s %-6s %-19s %-11s %-11s %s"
      % ("part", "mark", "placed at", "removed", "expected", "check"))
# The chunking (one part per call, __I0__/__I1__ substituted by fcsend.py) was a GUI
# workaround: the bearing search is ~2000 ray casts per part and the RPC dispatch dies at
# 90 s. freecadcmd has no such limit, so the default is now every job in one process.
# KX_I0/KX_I1 still narrow it when re-cutting a single part.
I0 = int(os.environ.get("KX_I0", 0))
I1 = int(os.environ.get("KX_I1", len(JOBS)))
done = 0
for name, mark, axis, stations in JOBS[I0:I1]:
    o = doc.getObject(name)
    if o is None:
        print("  %-22s MISSING" % name)
        continue
    sh = o.Shape

    if axis in ("P", "P2", "P3", "P4"):
        # explicit face: point on it, outward normal -X, text along +Z, up +Y
        px, py, pz = stations
        faces = None
        for h in ((H, 6.0, 5.0) if axis in ("P", "P4") else (5.0, 4.0)):
            faces = text_faces(mark + SUFFIX, h)
            tb = faces[0]
            for f in faces[1:]:
                tb = tb.fuse(f)
            if tb.BoundBox.XLength < 34.0:
                break
        bb = tb.BoundBox
        tb.translate(V(-0.5 * (bb.XMin + bb.XMax), -0.5 * (bb.YMin + bb.YMax), 0.0))
        # The face's outward normal: +X for the two X faces, -Z for the underside. Every
        # frame in this script now comes from tools/markframe.py, because when they were
        # written out inline here -- four of them, one per style -- three were LEFT-handed and
        # cut 12 of 14 part numbers as mirror images. Nothing caught it: the volume was right,
        # the solid was clean and the mark was hidden. See tools/readmark.py.
        nrm = (V(1.0, 0.0, 0.0) if axis in ("P", "P2")
               else V(0.0, -1.0, 0.0) if axis == "P4" else V(0.0, 0.0, -1.0))
        m, into = mark_matrix(axis, V(px, py, pz), nrm, standoff=0.3, legacy=FILL and LEGACY)
        d = V(into.x, into.y, into.z).multiply(DEPTH + 0.3)
        flat = tb.transformGeometry(m)
        if FILL:
            # Same face, but starting ON it rather than 0.3 mm proud of it, so the fill is
            # flush. The sign matters and is easy to get backwards: the cutting tool is placed
            # 0.3 mm OUTSIDE the face (px + 0.3 for the X faces, pz - 0.3 for the underside)
            # and cuts inward, so the fill moves back toward the material, not further out.
            # Getting it wrong adds a 0.3 mm proud layer to a face that was never engraved --
            # which is exactly what the first run of this did to five blank parts.
            back = V(into.x, into.y, into.z).multiply(0.3)
            # And gate on the skin, as the radial branch does. Without this the fill is
            # applied to any part whose mark site is blank, bulging a flat mating face.
            # The slab goes INTO the material (local +z is `into`), which is the one thing a
            # skin probe must get right: built the other way it sits in air and reports 0% solid
            # on a perfectly blank face.
            pb = Part.makeBox(8.0, 8.0, 0.5, V(-4.0, -4.0, 0.0))
            pm, _ = mark_matrix(axis, V(px, py, pz), nrm, standoff=0.0, legacy=FILL and LEGACY)
            pb = pb.transformGeometry(pm)
            pk = sh.common(pb)
            frac = (0.0 if pk.isNull() else pk.Volume) / max(1e-9, pb.Volume)
            if frac >= SKIN:
                print("  %-20s %-6s skin already %.0f%% solid -- nothing to fill"
                      % (name, mark, 100 * frac))
                continue
            fl = inflate(flat.copy())
            fl.translate(back)
            fd = V(into.x, into.y, into.z).multiply(DEPTH)
            v0 = sh.Volume
            new, how, pchk = fuse_clean(sh, fl.extrude(fd))
            added = (abs(new.Volume) - v0) / 1000.0 if new else 0.0
            want = sum(f.Area for f in faces) * DEPTH / 1000.0
            ok = (new is not None and 0.35 * want < added < 2.2 * want
                  and len(new.Solids) == 1 and pchk == "clean")
            print("  %-20s %-6s FILL %-11s +%6.3f cm3 %7.3f cm3  skin %.0f%%  %s, %s %s"
                  % (name, mark, ("face X %.0f" % px) if axis != "P3" else ("under Z %.0f" % pz),
                     added, want, 100 * frac, how, pchk, "filled" if ok else "NOT APPLIED"))
            if ok and not DRY:
                o.Shape = new
                done += 1
            continue
        tool = flat.extrude(d)
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
        if ok and len(cut.Solids) == 1 and not DRY:
            o.Shape = cut
            record(name, mark + SUFFIX, (px, py, pz), (nrm.x, nrm.y, nrm.z), "p", h, axis)
            done += 1
        continue

    org = MOT if axis.startswith("M") else V(0.0, 0.0, 0.0)
    hoop = axis.endswith("h")
    # SHRINK TO FIT. "P23a" at 8 mm is 22 mm long and the mount is 16 mm of limb axis, so
    # the search could never find room. Step the cap height down until it fits; 4 mm in a
    # bold face still has ~0.6 mm stems, which is thin but legible as a recess.
    spot = faces = tb = tbb = None
    ladder = () if SITE else (H, 5.0, 4.0)
    # 8, then 5, then 4 mm. The ladder gained its bottom rung when the leg suffix went on:
    # "P24L" is one character longer than "P24", which is 5.5 mm more string at 8 mm and
    # 3.4 mm more at 5 mm, and that was enough for the search to find no smooth patch at all
    # on P24_FairingShank and P1_KneeYoke -- both of which had fitted unsuffixed. 4 mm bold is
    # ~0.6 mm stems: thin for a 0.4 nozzle, but this is a recess, not an island, so it prints
    # as a shallower perimeter rather than a bead that may not stick.
    for h in ladder:
        faces = text_faces(mark + SUFFIX, h)
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
    if SITE and spot is None:
        # An EXPLICIT site skips the SEARCH, not the checks: the removed-volume band and
        # Shape.check() below still have to pass, and 413 still has to agree the mark is
        # covered. Worth skipping -- the search is ~2000 ray casts and on a part it cannot
        # satisfy it spends all of them before giving up, which is minutes per run.
        _stn, _deg, _r = (float(v) for v in SITE.split(","))
        for h in (H, 5.0, 4.0):
            faces = text_faces(mark + SUFFIX, h)
            tb = faces[0]
            for f in faces[1:]:
                tb = tb.fuse(f)
            tbb = tb.BoundBox
            break
        spot = (0.0, _stn, _deg, _r)
        print("  %-20s %-6s using the explicit site Y %+.0f %+.0f r %.1f"
              % (name, mark, _stn, _deg, _r))
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
    surf = V(org.x + rad.x * r0, stn, org.z + rad.z * r0)
    m, into = mark_matrix("r", surf, rad, standoff=0.3, hoop=hoop, legacy=FILL and LEGACY)
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
    pm0, _ = mark_matrix("r", surf, rad, standoff=0.0, hoop=hoop, legacy=FILL and LEGACY)
    probe = probe.transformGeometry(pm0)
    pk = sh.common(probe)
    frac = (0.0 if pk.isNull() else pk.Volume) / max(1e-9, probe.Volume)
    if FILL:
        if frac >= SKIN:
            print("  %-20s %-6s skin already %.0f%% solid -- nothing to fill"
                  % (name, mark, 100 * frac))
            continue
        # from the surface INWARD by exactly DEPTH. The cutting tool starts 0.3 mm proud so
        # it cannot miss the surface; reusing that offset here is what left 415 with raised
        # glyphs to shave off.
        base = inflate(blk.copy())
        base.translate(V(into.x, into.y, into.z).multiply(0.3))
        tool = base.extrude(V(into.x, into.y, into.z).multiply(DEPTH))
        v0 = sh.Volume
        new, how, chk = fuse_clean(sh, tool)
        added = (abs(new.Volume) - v0) / 1000.0 if new else 0.0
        pk2 = new.common(probe) if new else None
        f2 = (0.0 if (pk2 is None or pk2.isNull()) else pk2.Volume) / max(1e-9, probe.Volume)
        ok = new is not None and f2 > 0.95 and len(new.Solids) == 1 and chk == "clean"
        print("  %-20s %-6s FILL Y%+7.0f %+4.0f  +%6.3f cm3  skin %.0f%% -> %.0f%%  %s, %s %s"
              % (name, mark, stn, deg, added, 100 * frac, 100 * f2, how, chk,
                 "filled" if ok else "NOT APPLIED"))
        if ok and not DRY:
            o.Shape = new
            registry.pop(name, None)
            done += 1
        continue

    tool = blk.extrude(V(into.x, into.y, into.z).multiply(DEPTH + 0.3))
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
    if DRY:
        continue
    o.Shape = cut
    record(name, mark + SUFFIX, (surf.x, surf.y, surf.z),
           (rad.x, rad.y, rad.z), "r", h, "r")
    done += 1

print()
print("  %s %d of %d parts" % ("filled" if FILL else "engraved", done, len(JOBS[I0:I1])))
print()
print("  NOTE ON VERIFYING THIS. A tempting shortcut is to scan each part's surface for")
print("  voids and call a pitted patch 'engraved'. It does not work: bolt holes, lightening")
print("  windows and shell ports all read the same way. A probe written that way scored the")
print("  interface bosses as engraved at 68%% solid skin when they were still blank -- it was")
print("  reading their bolt holes. The only trustworthy record is this script's own report.")
print("  Stem width at %.0f mm in this font is about %.1f mm; a 0.4 nozzle needs %.1f."
      % (H, 0.15 * H, MIN_STEM))
if DRY:
    print("DRY RUN -- nothing cut, nothing saved.")
else:
    doc.recompute()
    doc.save()
    json.dump(registry, open(REG, "w"), indent=1, sort_keys=True)
    print("  %d marks recorded in %s" % (len(registry), os.path.basename(REG)))
    print("STAGE 10 DONE, saved.")
