# -*- coding: utf-8 -*-
"""Record existing images against the model's CURRENT geometry fingerprint.

    freecadcmd.exe tools/record_render.py renders/anim/hero_clad.gif renders/anim/hero_open.gif

USE THIS ONLY WHEN THE CLAIM IS TRUE. Writing an entry here asserts "this image shows the model as
it is right now", and 902_doc_audit.py will believe you — that is the whole point of the manifest.
Stamping a stale image with a current fingerprint does not make it current; it breaks the one check
that would have caught it, which is strictly worse than having no check at all.

It exists for one honest case: a render that was made from the current geometry by a script that
could not record it. That happened on the first run — the animation was launched from a copy of
b7_anim.py that predated the manifest code, because Blender reads the script at launch, and the
export it rendered from predated 221 writing fingerprint.txt. The images are correct; the
bookkeeping was not yet written when they were made.

If you are not certain the geometry has not moved since the image was rendered, re-render it. It
is twelve minutes a still and fifty for the animation, which is cheaper than a README that lies.
"""
import json
import os
import sys

import FreeCAD

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fingerprint import fingerprint                                   # noqa: E402

REPO = r"C:/Users/Josh/knee-exo"
DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
BY = os.environ.get("KX_BY", "recorded by hand after the fact")

args = [a for a in sys.argv[1:] if a.endswith((".png", ".gif"))]
if not args:
    args = [os.environ.get("KX_IMAGES", "")]
    args = [a for a in args[0].split(",") if a]
if not args:
    raise SystemExit("name the images to record")

_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

fp = fingerprint(doc)
path = os.path.join(REPO, "renders", "manifest.json")
man = json.load(open(path)) if os.path.exists(path) else {}
import time                                                           # noqa: E402

n = 0
for rel in args:
    rel = rel.replace("\\", "/").strip()
    full = os.path.join(REPO, rel)
    if not os.path.exists(full):
        print("  %-40s MISSING, not recorded" % rel)
        continue
    man[rel] = {"geometry": fp, "made": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "by": BY, "src": "n/a"}
    print("  %-40s recorded against geometry %s" % (rel, fp))
    n += 1
json.dump(man, open(path, "w"), indent=1, sort_keys=True)
print("  %d recorded, %d entries in the manifest" % (n, len(man)))
