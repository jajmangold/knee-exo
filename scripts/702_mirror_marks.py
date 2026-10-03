# -*- coding: utf-8 -*-
"""Engrave the RIGHT leg by reflecting the LEFT leg's mark registry.

412 places marks by searching: fire rays from the limb axis, find a patch that is smooth over the
text footprint and has no line of sight from outside, cut there. Run against the mirrored document
that search gets 6 of 14, and the eight failures are structural rather than marginal:

  * five marks are PLANAR and 412 names their face by coordinate -- X 47 Z 109 for the fairing
    mounts, Z 123 for the distal interface. Mirroring is Z -> -Z, so those Z values point at empty
    space; the cut removed 0.000 cm3 and reported MISSED, correctly.
  * P25_MotorNacelle casts from the motor pod's centre, V(-104, 0, 62). On the right leg the pod is
    at Z -62, so every ray left from the wrong place and no patch was ever found.
  * P24_FairingShank needs a 4 mm cap height and P1_KneeYoke an explicit site even on the left leg.
    Both sit at the edge of what the search can do, and re-deriving them on a reflected document
    asks the same marginal search the same marginal question.

None of that is worth fixing in the search, because the search's answer is already known: the left
leg's registry records where all fourteen marks went, and the right leg's correct sites are exactly
those reflected. It is the better result too -- the legs end up marked in mirror-image places rather
than wherever two independent searches happened to land -- and it takes seconds rather than twenty
minutes.

WHAT MUST NOT BE MIRRORED IS THE TEXT. Reflecting the mark along with the part gives backwards
glyphs, which is why 701 hands over an un-engraved document. Only the SITE is reflected; the frame
is rebuilt from the reflected normal by tools/markframe.py, which is what guarantees both legs are
marked by the same rule instead of by two hand-written ones. This script kept its own copy of that
arithmetic for exactly one run, and in that run it put the tool on the wrong side of a bore surface
-- material lies OUTBOARD of a radial mark, not behind it -- and reported three parts as already
engraved when it had been probing air.

    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd KX_SUFFIX=R freecadcmd.exe scripts/702_mirror_marks.py

KX_ONLY=P25_MotorNacelle,P24_FairingShank narrows it to named parts; KX_DRYRUN=1 reports only.
"""
import json
import os
import sys

import FreeCAD
from FreeCAD import Vector as V

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from markframe import matrix as mark_matrix                         # noqa: E402
from marktool import DEPTH, SKIN, block, fuse_clean, inflate, skin  # noqa: E402

SRC_REG = os.environ.get("KX_MARKS", r"C:/Users/Josh/KneeExo_v6.marks.json")
DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6_R.FCStd").replace("\\", "/")
SUFFIX = os.environ.get("KX_SUFFIX", "R")
ONLY = [s for s in os.environ.get("KX_ONLY", "").split(",") if s]
DRY = bool(os.environ.get("KX_DRYRUN"))

_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

DST_REG = DOCFILE[:-6] + ".marks.json"
left = json.load(open(SRC_REG))
registry = {}
if os.path.exists(DST_REG):
    try:
        registry = json.load(open(DST_REG))
    except Exception:
        registry = {}

print("=" * 94)
print("MIRRORING THE MARKS  %s -> %s  (%d in the source)"
      % (os.path.basename(SRC_REG), _BASE, len(left)))
print("=" * 94)
print("  %-20s %-6s %-24s %-11s %-11s %s"
      % ("part", "mark", "site, reflected", "removed", "expected", "check"))
done = skipped = missed = 0
for name in sorted(left):
    if ONLY and name not in ONLY:
        continue
    rec = left[name]
    o = doc.getObject(name)
    if o is None:
        print("  %-20s MISSING in this document" % name)
        continue
    sh = o.Shape
    axis = rec.get("axis", "r" if rec["mode"] == "r" else "P")
    h = rec["height"]
    stem = rec["text"][:-1] if rec["text"][-1:] in ("L", "R") else rec["text"]
    text = stem + SUFFIX
    pt = V(rec["point"][0], rec["point"][1], -rec["point"][2])        # the reflection, Z -> -Z
    nrm = V(rec["normal"][0], rec["normal"][1], -rec["normal"][2])

    tb, faces = block(text, h)
    m, into = mark_matrix(axis, pt, nrm, standoff=0.3)
    tool = tb.transformGeometry(m).extrude(V(into.x, into.y, into.z).multiply(DEPTH + 0.3))

    pm, _ = mark_matrix(axis, pt, nrm, standoff=0.0)
    frac, _ = skin(sh, pm)
    # IS THERE ANYTHING TO FILL? The absolute threshold alone says yes far too often. P22's
    # reflected site reads 79% against SKIN's 80%, so this tried to fill a patch whose glyphs the
    # left leg had ALREADY had filled before 701 mirrored it -- the fill added 0.000 cm3, was
    # correctly refused, and the part was then skipped with no mark at all. The same reference the
    # acceptance test below uses settles it: a site as solid as the blank surface either side of
    # it has nothing in it. P22 reads 79% against a local 68%, which is blanker than its own
    # neighbourhood.
    base = 0.0
    nb = []
    for dy in (14.0, -14.0):
        bm, _ = mark_matrix(axis, V(pt.x, pt.y + dy, pt.z), nrm, standoff=0.0)
        try:
            nb.append(skin(sh, bm)[0])
        except Exception:
            pass
    if nb:
        base = sum(nb) / len(nb)
    if frac < SKIN and frac < base - 0.05:
        # The site is already engraved -- and on a freshly mirrored leg it ALWAYS is, with the
        # left leg's text reflected into backwards glyphs. This used to skip, which is why a
        # mirrored document got 6 of 14: the eight it did cut were the ones whose reflected site
        # happened to land somewhere blank.
        #
        # The fill tool needs no reasoning about frames at all. Whatever is in this part is the
        # Z-mirror of what is in the left part, so build the tool the left leg would be filled
        # with -- the LEFT text, the LEFT site, the current frame, exactly as 416_unmark.py does
        # it -- and mirror the solid. Deriving a frame for the reflected glyphs instead means
        # guessing which in-plane axis the reflection flipped, and it depends on the direction of
        # each mark's normal: legacy=True is right for some of the fourteen and wrong for others,
        # which is how a first attempt at this filled 7 and refused 7.
        ltext = rec["text"]
        ltb, lfaces = block(ltext, h)
        lpt = V(rec["point"][0], rec["point"][1], rec["point"][2])
        lnrm = V(rec["normal"][0], rec["normal"][1], rec["normal"][2])
        lm, linto = mark_matrix(axis, lpt, lnrm, standoff=0.0)
        fwant = sum(f.Area for f in lfaces) * DEPTH / 1000.0
        # WHAT COUNTS AS FILLED is 416_unmark.py's test, unchanged: most of the expected glyph
        # volume went back, the skin improved by a wide margin, one clean solid. Absolute skin is
        # not usable as a target -- probing blank surface 14 and 28 mm along these parts reads
        # anywhere from 55% to 100%, because the probe clips bolt holes, slots and part edges, so
        # "within x% of a blank patch" rejects any fill near an edge.
        # What IS new is searching the tool's inflation instead of trusting one value: at 1.06 the
        # fuse self-intersects on P24, whose glyphs are 4 mm tall on a tight radius, and at 1.00 it
        # fills to 100%.
        # On a strongly curved site the volume test is unreachable even for a perfect fill: a
        # flat-bottomed tool extruded from the tangent plane cuts deepest in the middle and tapers
        # to nothing at the edges, so P25's recess in the domed motor pod is only 58% of glyph
        # area x depth. For that case there is a second, curvature-aware test -- is the patch now
        # as solid as the blank surface immediately either side of it? Measured on P25: the blank
        # pod 14 mm along reads 77.9% and 83.3%, and the fill reaches 77%. Only the NEAREST
        # patches are usable as a reference; 28 mm away the pod is flat and reads 100%, which no
        # fill near a curved edge can match.
        filled, how, fchk, after, used = None, "none", "FAILED", 0.0, 0.0
        for f in (1.06, 1.02, 1.0, 1.12, 1.20):
            t = inflate(ltb, f) if f > 1.0 else ltb
            t = t.transformGeometry(lm).extrude(V(linto.x, linto.y, linto.z).multiply(DEPTH))
            t = t.mirror(V(0, 0, 0), V(0, 0, 1))
            cand, chow, cchk = fuse_clean(sh, t)
            if cand is None or cchk != "clean" or len(cand.Solids) != 1:
                continue
            cadd = (abs(cand.Volume) - sh.Volume) / 1000.0
            cafter = skin(cand, pm)[0]
            if ((cafter - frac) > 0.15
                    and (cadd > 0.6 * fwant or cafter >= base - 0.05)):
                filled, how, fchk, after, used = cand, chow, cchk, cafter, f
                break
        fadd = 0.0 if filled is None else (abs(filled.Volume) - sh.Volume) / 1000.0
        fok = filled is not None
        print("  %-20s %-6s %-24s %7.3f cm3 %7.3f cm3  fill %s %.0f%%->%.0f%% of %.0f%%%s"
              % (name, ltext, "filling the mirrored glyphs (x%.2f)" % used, fadd, fwant, fchk,
                 100 * frac, 100 * after, 100 * base, "" if fok else "   <-- FILL REFUSED"))
        if not fok:
            missed += 1
            continue
        if not DRY:
            o.Shape = filled
        sh = filled

    v0 = sh.Volume
    cut = sh.cut(tool)
    removed = (v0 - cut.Volume) / 1000.0
    want = sum(f.Area for f in faces) * DEPTH / 1000.0
    try:
        cut.check(True)
        chk = "clean"
    except Exception:
        chk = "SELF-INTERSECT"
    ok = 0.35 * want < removed < 1.8 * want and chk == "clean" and len(cut.Solids) == 1
    print("  %-20s %-6s %-24s %7.3f cm3 %7.3f cm3  %s%s"
          % (name, text, "(%.0f, %.0f, %.0f) h%.0f" % (pt.x, pt.y, pt.z, h),
             removed, want, chk, "" if ok else "   <-- MISSED"))
    if not ok:
        missed += 1
        continue
    if DRY:
        continue
    o.Shape = cut
    registry[name] = {"text": text, "point": [round(v, 3) for v in (pt.x, pt.y, pt.z)],
                      "normal": [round(v, 4) for v in (nrm.x, nrm.y, nrm.z)],
                      "mode": rec["mode"], "axis": axis, "height": h}
    done += 1

print()
print("  cut %d, skipped %d, %d missed or refused, of %d considered"
      % (done, skipped, missed, len(ONLY) if ONLY else len(left)))
if DRY:
    print("DRY RUN -- nothing cut, nothing saved.")
else:
    doc.recompute()
    doc.save()
    json.dump(registry, open(DST_REG, "w"), indent=1, sort_keys=True)
    print("  %d marks recorded in %s" % (len(registry), os.path.basename(DST_REG)))
    print("  Verify with tools/readmark.py (do the glyphs read forwards?) and 413 (is each mark")
    print("  still hidden?). A reflected site is a claim about where the surface is, and neither")
    print("  the removed volume nor a clean solid says anything about either question.")
