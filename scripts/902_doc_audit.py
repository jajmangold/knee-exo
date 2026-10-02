# -*- coding: utf-8 -*-
"""Check the documentation against the model. Staleness should be a failing test, not an audit.

Asked whether the README was current, the answer was no in five places, and every one was a fact a
script can measure that had been typed in by hand: a sweep that no longer worked that way, parts
that no longer existed, a nut that had already been redrawn, guides that were no longer sliding, a
document name two versions out of date. Finding them took a session. Finding them again should take
twelve seconds.

What it checks:
  1. every part name mentioned in the docs exists in the model (bar an explicit allowlist of
     "this no longer exists" notes, which are the point)
  2. every "Pxx ... N cm3" claim is within 5% of the part's actual volume
  3. every relative link resolves
  4. the printed-part count the docs claim matches the printed set
  5. the engraved-mark count matches the registry beside the document
  6. every STL in stl/ and stl_R/ corresponds to a part in the model, and vice versa
  7. every <img src> resolves, AND shows the CURRENT geometry -- see tools/fingerprint.py. This
     is the check that was missing when six renders of a boxy P22 and non-conical cuffs sat at
     the top of the README for weeks: the link checker reads markdown links, these are HTML img
     tags, and a file that exists is not a file that is current.

    freecadcmd.exe scripts/902_doc_audit.py          # exit 1 if anything is stale
"""
import glob
import json
import os
import re
import sys

import FreeCAD

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
DOCS = ["README.md", "docs/BOM.md", "docs/PRINT.md", "docs/ASSEMBLY.md",
        "docs/ELECTRONICS.md", "docs/PRIOR_ART.md"]

# Part names the docs mention precisely BECAUSE they are wrong or gone. A name quoted as an EXAMPLE
# of an error is indistinguishable, to a regex, from a name asserted as fact -- this checker's own
# paragraph in the README quotes `P2a_KneeHub` as the stale abbreviation it caught, and the checker
# then dutifully caught itself. Two kinds of entry, kept apart because they are different claims:
#   deleted  -- the part existed and was removed, and the docs explain why the mass figure moved
#   quoted   -- the name is wrong and the surrounding text says so
GHOSTS_OK = {"P3b_CarriageB", "P11_SprungAnchor", "P2b_RodClevisBlock", "P4_Rod_8mm",
             "P8_RodEndHousing_PETG", "P3b_Carriage", "P2b_Clevis",
             "P2a_KneeHub"}
PRINTED = 17      # 15 + the drive bracket and gantry plate, printed since 802
ALLOW_VOL = 0.05

_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

vol, live, short = {}, set(), {}
for o in doc.Objects:
    if not o.isDerivedFrom("Part::Feature") or o.Shape is None or o.Shape.isNull():
        continue
    for n in (o.Name, o.Label):
        vol[n] = o.Shape.Volume / 1000.0
        live.add(n)
        short.setdefault(n.split("_")[0], n)

fail = []
print("=" * 92)
print("DOC AUDIT  --  %d documents against %s" % (len(DOCS), _BASE))
print("=" * 92)

# 1 + 2 ------------------------------------------------------------------ names and volumes
ghosts, vols = [], []
for d in DOCS:
    path = os.path.join(REPO, d)
    if not os.path.exists(path):
        fail.append("%s is missing" % d)
        continue
    txt = open(path, encoding="utf-8").read()
    for m in re.finditer(r"\b(P\d+[a-z]?)_(\w+)", txt):
        tok = m.group(0)
        if tok in live or tok in GHOSTS_OK or m.group(1) in live:
            continue
        ghosts.append((d, txt[:m.start()].count("\n") + 1, tok))
    # "cm³" or "cm3" only -- "cm²" is a support area and means something else entirely
    for m in re.finditer(r"`?(P\d+[a-z]?)(?:_\w+)?`?[^.\n]{0,60}?(\d+(?:\.\d+)?)\s*cm[³3]\b", txt):
        name = short.get(m.group(1))
        if name is None:
            continue
        claim, actual = float(m.group(2)), vol[name]
        # a claim far BELOW the part's volume is usually an intersection or a clearance, which is
        # a different quantity; only flag claims in the same order of magnitude
        if claim < 0.5 * actual:
            continue
        if abs(claim - actual) / actual > ALLOW_VOL:
            vols.append((d, txt[:m.start()].count("\n") + 1, m.group(1), claim, actual))
print("  1. part names that are not in the model, and not on the deleted-on-purpose list: %d"
      % len(ghosts))
for d, l, t in ghosts:
    print("       %-20s line %-5d %s" % (d, l, t))
print("  2. volume claims off by more than %.0f%%: %d" % (100 * ALLOW_VOL, len(vols)))
for d, l, t, c, a in vols:
    print("       %-20s line %-5d %s claims %.1f, model says %.1f" % (d, l, t, c, a))
fail += ["%s line %d: %s is not in the model" % (d, l, t) for d, l, t in ghosts]
fail += ["%s line %d: %s claims %.1f cm3, model says %.1f" % (d, l, t, c, a)
         for d, l, t, c, a in vols]

# 3 ------------------------------------------------------------------------------- links
broken = []
for d in DOCS:
    path = os.path.join(REPO, d)
    if not os.path.exists(path):
        continue
    base = os.path.dirname(path)
    txt = open(path, encoding="utf-8").read()
    for m in re.finditer(r"\]\((?!https?://)([^)#]+)\)", txt):
        t = m.group(1).strip()
        if not os.path.exists(os.path.normpath(os.path.join(base, t))):
            broken.append((d, txt[:m.start()].count("\n") + 1, t))
print("  3. broken relative links: %d" % len(broken))
for d, l, t in broken:
    print("       %-20s line %-5d -> %s" % (d, l, t))
fail += ["%s line %d: link %s does not resolve" % (d, l, t) for d, l, t in broken]

# 4 + 6 --------------------------------------------------------------------- the printed set
stl_l = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(REPO, "stl", "*.stl"))}
stl_r = {os.path.basename(p)[:-4] for p in glob.glob(os.path.join(REPO, "stl_R", "*.stl"))}
print("  4. printed parts: stl/ has %d, stl_R/ has %d, the docs claim %d"
      % (len(stl_l), len(stl_r), PRINTED))
if len(stl_l) != PRINTED or len(stl_r) != PRINTED:
    fail.append("printed set is %d/%d, docs claim %d" % (len(stl_l), len(stl_r), PRINTED))
if stl_l != stl_r:
    d = (stl_l ^ stl_r)
    print("       the two legs do not hold the same parts: %s" % ", ".join(sorted(d)))
    fail.append("stl/ and stl_R/ differ: %s" % ", ".join(sorted(d)))
orphans = [s for s in stl_l if s not in live]
print("  6. STLs with no part of that name in the model: %d" % len(orphans))
for s in sorted(orphans):
    print("       %s" % s)
fail += ["stl/%s.stl has no part in the model" % s for s in orphans]

# 7 ------------------------------------------------------------------------------ images
sys.path.insert(0, os.path.join(REPO, "tools"))
from fingerprint import fingerprint                                  # noqa: E402

now_fp = fingerprint(doc)
man_path = os.path.join(REPO, "renders", "manifest.json")
man = json.load(open(man_path)) if os.path.exists(man_path) else {}
missing_img, stale_img, unrecorded = [], [], []
for d in DOCS:
    path = os.path.join(REPO, d)
    if not os.path.exists(path):
        continue
    base = os.path.dirname(path)
    txt = open(path, encoding="utf-8").read()
    for m in re.finditer(r'<img\s+src="([^"]+)"', txt):
        rel = m.group(1).strip()
        line = txt[:m.start()].count(chr(10)) + 1
        full = os.path.normpath(os.path.join(base, rel))
        if not os.path.exists(full):
            missing_img.append((d, line, rel))
            continue
        key = rel if rel.startswith("renders/") else "renders/" + rel.split("renders/")[-1]
        rec = man.get(key)
        if rec is None:
            unrecorded.append((d, line, rel))
        elif rec.get("geometry") != now_fp:
            stale_img.append((d, line, rel, rec.get("geometry"), rec.get("made", "?")))
# ...and every image IN the repository, not only the ones a document embeds. The audit passed
# clean while renders/extended_0deg held six images of superseded geometry, simply because no
# document happened to <img> them. A published artefact is a claim whether or not it is linked.
shipped_stale, shipped_unrec = [], []
for root, _dirs, files in os.walk(os.path.join(REPO, "renders")):
    for f in sorted(files):
        if not f.lower().endswith((".png", ".gif")):
            continue
        rel = os.path.relpath(os.path.join(root, f), REPO).replace(chr(92), "/")
        rec = man.get(rel)
        if rec is None:
            shipped_unrec.append(rel)
        elif rec.get("geometry") != now_fp:
            shipped_stale.append((rel, rec.get("geometry")))
print("  7. images: %d broken, %d of unknown provenance, %d showing older geometry than the model"
      % (len(missing_img), len(unrecorded), len(stale_img)))
print("     in renders/: %d files, %d unrecorded, %d of older geometry"
      % (sum(1 for r, _d, fs in os.walk(os.path.join(REPO, "renders"))
             for f in fs if f.lower().endswith((".png", ".gif"))),
         len(shipped_unrec), len(shipped_stale)))
for rel in shipped_unrec:
    print("       NO RECORD  %s" % rel)
for rel, g in shipped_stale:
    print("       STALE      %s -- geometry %s" % (rel, g))
fail += ["renders/ holds %s with no provenance" % r for r in shipped_unrec]
fail += ["renders/ holds %s, rendered from geometry %s, model is %s" % (r, g, now_fp)
         for r, g in shipped_stale]
print("     model geometry fingerprint is %s" % now_fp)
for d, l, t in missing_img:
    print("       MISSING   %-14s line %-5d %s" % (d, l, t))
for d, l, t in unrecorded:
    print("       NO RECORD  %-14s line %-5d %s" % (d, l, t))
for d, l, t, g, w in stale_img:
    print("       STALE     %-14s line %-5d %s -- rendered from geometry %s on %s"
          % (d, l, t, g, w))
fail += ["%s line %d: image %s does not exist" % (d, l, t) for d, l, t in missing_img]
fail += ["%s line %d: image %s shows geometry %s, model is %s" % (d, l, t, g, now_fp)
         for d, l, t, g, _ in stale_img]
fail += ["%s line %d: image %s has no provenance in renders/manifest.json" % (d, l, t)
         for d, l, t in unrecorded]

# 5 ------------------------------------------------------------------------------- marks
for leg, f in (("left", DOCFILE[:-6] + ".marks.json"),
               ("right", DOCFILE[:-6] + "_R.marks.json")):
    if not os.path.exists(f):
        alt = os.path.join(REPO, "model", os.path.basename(f))
        f = alt if os.path.exists(alt) else f
    if not os.path.exists(f):
        print("  5. %s leg: no mark registry found" % leg)
        fail.append("%s leg has no mark registry" % leg)
        continue
    reg = json.load(open(f))
    n = len(reg)
    ok = all(v["text"].endswith("L" if leg == "left" else "R") for v in reg.values())
    print("  5. %s leg: %d marks, suffixes %s" % (leg, n, "consistent" if ok else "MIXED"))
    if n != PRINTED - 1:
        fail.append("%s leg has %d marks, expected %d" % (leg, n, PRINTED - 1))
    if not ok:
        fail.append("%s leg has marks with the wrong leg letter" % leg)

print("-" * 92)
if fail:
    print("  %d PROBLEM(S):" % len(fail))
    for f in fail:
        print("     %s" % f)
    sys.stdout.flush()
    sys.exit(1)
print("  documentation agrees with the model.")
