# -*- coding: utf-8 -*-
"""Autocrop the FreeCAD viewport captures to their content.

FreeCAD's ViewFit leaves a wide margin and the saved image aspect rarely matches the
viewport's, so every capture comes back with slack around it. The differential pair gets
a single shared crop box, otherwise the two frames would not line up and the comparison
would be meaningless.

    python scripts/crop_cad.py C:/Users/Josh/KneeExo_render/cad
"""
import sys, os, glob
from PIL import Image
import numpy as np

D = sys.argv[1] if len(sys.argv) > 1 else "."
PAIR = {"diff_flexed.png", "diff_extended.png"}
MARGIN = 22


def content_box(path, tol=10):
    a = np.asarray(Image.open(path).convert("RGB")).astype(int)
    bg = a[3, 3]
    m = (abs(a - bg).max(axis=2) > tol)
    ys, xs = m.any(axis=1), m.any(axis=0)
    if not ys.any():
        return None
    return (int(xs.argmax()), int(ys.argmax()),
            a.shape[1] - int(xs[::-1].argmax()), a.shape[0] - int(ys[::-1].argmax()))


files = sorted(glob.glob(os.path.join(D, "*.png")))
boxes = {f: content_box(f) for f in files}
pair = [boxes[f] for f in files if os.path.basename(f) in PAIR and boxes[f]]
shared = (min(b[0] for b in pair), min(b[1] for b in pair),
          max(b[2] for b in pair), max(b[3] for b in pair)) if pair else None

for f in files:
    b = boxes[f]
    if b is None:
        continue
    if os.path.basename(f) in PAIR and shared:
        b = shared
    im = Image.open(f)
    im.crop((max(0, b[0] - MARGIN), max(0, b[1] - MARGIN),
             min(im.size[0], b[2] + MARGIN),
             min(im.size[1], b[3] + MARGIN))).save(f)
    print("%-24s -> %s" % (os.path.basename(f), Image.open(f).size))
