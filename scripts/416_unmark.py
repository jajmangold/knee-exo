# -*- coding: utf-8 -*-
"""Take the part numbers back out, using the registry rather than a search.

Filling a mark needs the tool that cut it. 412 can do that, but it re-derives the site by firing
~2000 rays per part, which takes twenty minutes for fourteen parts and -- worse -- can land
somewhere slightly different from where the cut actually went. The registry 412 writes beside the
document records every site exactly, so the fill is both exact and instant.

Two jobs here:

  * UNDO. The left leg was engraved before tools/markframe.py existed, and 12 of its 14 marks came
    out as mirror images. Those have to come out before anything else: the right leg is built by
    mirroring the left, so the mirror source must be blank or every part number on the right is
    backwards twice over.
  * A BLANK MIRROR SOURCE, as a repeatable step rather than a one-off repair. Whenever the left
    leg is re-engraved, this is how it goes back to unmarked.

KX_LEGACY=1 builds the tool on the pre-fix, left-handed frame, which is what the marks currently
in the part were cut with. Without it the fill is the mirror image of the recess and covers about
half of it -- measured: 56% solid skin going to 71% instead of 100%, and correctly refused.

    KX_DOC=C:/Users/Josh/KneeExo_v6.FCStd KX_LEGACY=1 freecadcmd.exe scripts/416_unmark.py
    KX_ONLY=P6_ShankSocket ...                 one part
    KX_DRYRUN=1 ...                            report only
"""
import json
import os
import sys

import FreeCAD
from FreeCAD import Vector as V

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from markframe import matrix as mark_matrix                        # noqa: E402
from marktool import DEPTH, SKIN, block, fuse_clean, inflate, skin  # noqa: E402

# How much the fill tool is grown to avoid sharing side walls with the recess. 1.06 is right for
# every part but P24_FairingShank, whose 4 mm text on a 3 mm wall self-intersects at that size;
# KX_INFLATE exists for it.
INFLATE = float(os.environ.get("KX_INFLATE", "1.06"))

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
ONLY = [s for s in os.environ.get("KX_ONLY", "").split(",") if s]
DRY = bool(os.environ.get("KX_DRYRUN"))
LEGACY = bool(os.environ.get("KX_LEGACY"))
REG = DOCFILE[:-6] + ".marks.json"

_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

registry = json.load(open(REG)) if os.path.exists(REG) else {}
print("=" * 94)
print("UNMARKING  %s  --  %d marks in the registry, %s frame"
      % (_BASE, len(registry), "LEGACY left-handed" if LEGACY else "current"))
print("=" * 94)
print("  %-20s %-6s %-13s %-20s %s"
      % ("part", "mark", "site", "added / expected", "skin before -> after"))

done = failed = 0
for name in sorted(list(registry)):
    if ONLY and name not in ONLY:
        continue
    rec = registry[name]
    o = doc.getObject(name)
    if o is None:
        print("  %-20s MISSING in this document" % name)
        continue
    sh = o.Shape
    axis = rec.get("axis", "r" if rec["mode"] == "r" else "P")
    pt, nrm, h = V(*rec["point"]), V(*rec["normal"]), rec["height"]
    tb, faces = block(rec["text"], h)

    # ON the surface, not 0.3 mm proud of it: the cutting tool starts outside so it cannot miss,
    # and reusing that offset to fill is what left 415 with raised glyphs to shave off.
    m, into = mark_matrix(axis, pt, nrm, standoff=0.0, legacy=LEGACY)
    pm, _ = mark_matrix(axis, pt, nrm, standoff=0.0, legacy=LEGACY)
    before, probe = skin(sh, pm)
    if before >= SKIN:
        print("  %-20s %-6s %-12s skin already %.0f%% solid -- nothing to fill"
              % (name, rec["text"], "", 100 * before))
        registry.pop(name, None)
        continue
    tool = (inflate(tb, INFLATE) if INFLATE > 1.0 else tb).transformGeometry(m).extrude(V(into.x, into.y, into.z).multiply(DEPTH))
    v0 = sh.Volume
    new, how, chk = fuse_clean(sh, tool)
    if new is None:
        print("  %-20s %-6s fuse FAILED outright" % (name, rec["text"]))
        failed += 1
        continue
    added = (abs(new.Volume) - v0) / 1000.0
    after, _ = skin(new, pm)
    want = sum(f.Area for f in faces) * DEPTH / 1000.0
    # Judge the fill on BOTH numbers, and not against 100% solid skin: a mark site is allowed to
    # contain other geometry, and the blank baselines measured on this model run 87..100% (P5's
    # bore clips a webbing slot, P30's face has its bolt holes). Demanding >95% rejected five
    # fills that had in fact restored the surface. So: most of the expected glyph volume went
    # back, and the skin improved by a wide margin.
    ok = (added > 0.6 * want and (after - before) > 0.15
          and len(new.Solids) == 1 and chk == "clean")
    print("  %-20s %-6s %-13s +%6.3f of %6.3f cm3  %3.0f%% -> %3.0f%%  %s, %s %s"
          % (name, rec["text"], "(%.0f,%.0f,%.0f)" % (pt.x, pt.y, pt.z), added, want,
             100 * before, 100 * after, how, chk, "filled" if ok else "NOT APPLIED"))
    if not ok:
        failed += 1
        continue
    if DRY:
        continue
    o.Shape = new
    registry.pop(name, None)
    done += 1

print()
print("  filled %d, failed %d, %d marks left in the registry" % (done, failed, len(registry)))
if DRY:
    print("DRY RUN -- nothing changed.")
else:
    doc.recompute()
    doc.save()
    json.dump(registry, open(REG, "w"), indent=1, sort_keys=True)
    print("  saved; registry rewritten with %d marks" % len(registry))
    if not registry:
        print("  This document is now a clean mirror source: 701_mirror_build.py can run.")
