# -*- coding: utf-8 -*-
"""Copy rendered images into the repository, carrying their provenance with them.

    python tools/install_renders.py C:/Users/Josh/KneeExo_render/out_p00 renders/extended_0deg
    python tools/install_renders.py C:/Users/Josh/KneeExo_render/cad      renders/cad

The renderers record what they wrote, by its real path (scripts/b6_stills.py, b7_anim.py). This
moves both the file and its manifest entry, so a picture in renders/ always carries the fingerprint
of the geometry it was actually rendered from.

WHY THE SPLIT. The record used to be written against the destination path, on the assumption that
whatever was rendered would end up there. Then a 15% scale diagnostic run -- into a scratch
directory, to reproduce a crash -- stamped six full-quality images in the repository as current
geometry without ever touching them, and 902_doc_audit.py passed on it. A provenance record that
can be written by something other than the act of rendering is not provenance; it is a rumour.
Hence: record where you wrote, and prove it again when you move it.

An image with no record in the source is copied but NOT given one. Unprovenanced images are the
audit's problem to report, not this tool's to invent.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
MAN = os.path.join(REPO, "renders", "manifest.json")

if len(sys.argv) < 3:
    raise SystemExit(__doc__)
SRC = sys.argv[1].replace("\\", "/").rstrip("/")
DST = sys.argv[2].replace("\\", "/").rstrip("/")
dstdir = os.path.join(REPO, DST)
if not os.path.isdir(dstdir):
    os.makedirs(dstdir)
man = json.load(open(MAN)) if os.path.exists(MAN) else {}

copied = carried = orphan = 0
for f in sorted(os.listdir(SRC)):
    if not f.lower().endswith((".png", ".gif")):
        continue
    src = os.path.join(SRC, f).replace("\\", "/")
    shutil.copy2(src, os.path.join(dstdir, f))
    copied += 1
    rec = man.get(src)
    if rec is None:
        orphan += 1
        print("  %-34s copied, NO RECORD at source -- the audit will flag it" % f)
        continue
    man["%s/%s" % (DST, f)] = dict(rec, installed=True)
    carried += 1
json.dump(man, open(MAN, "w"), indent=1, sort_keys=True)
print("  %d copied into %s, %d with provenance, %d without" % (copied, DST, carried, orphan))
if carried:
    geoms = sorted({man["%s/%s" % (DST, f)]["geometry"]
                    for f in os.listdir(dstdir) if "%s/%s" % (DST, f) in man})
    print("  geometry recorded: %s" % ", ".join(geoms))
