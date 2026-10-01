# -*- coding: utf-8 -*-
"""Print each part number as the person holding the part sees it.

Nothing in this repository ever looked at a mark. 412 checked that the cut removed a plausible
volume, 413 checked that no ray escapes from it, 411 checked the mesh -- and all three passed on
12 of 14 marks that were MIRROR IMAGES, because none of them asks what the glyphs say.

This does, with no renderer and no screenshot: sample a grid of points 0.4 mm inside the
material, in the plane of the mark, oriented the way the reader is oriented, and print '#' where
there is material and ' ' where the recess has taken it away. A correct mark reads left to right.

    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe tools/readmark.py
    KX_ONLY=P6_ShankSocket freecadcmd.exe tools/readmark.py

Reads the registry 412 writes beside the document, so it checks what was actually cut rather
than what some table says should have been.
"""
import json
import os
import sys

import FreeCAD
from FreeCAD import Vector as V

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from markframe import frame                                        # noqa: E402

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
ONLY = [s for s in os.environ.get("KX_ONLY", "").split(",") if s]
REG = DOCFILE[:-6] + ".marks.json"

_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace("\\", "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

reg = json.load(open(REG))
print("=" * 96)
print("WHAT THE MARKS SAY  --  %s, %d marks" % (_BASE, len(reg)))
print("=" * 96)
for name in sorted(reg):
    if ONLY and name not in ONLY:
        continue
    rec = reg[name]
    o = doc.getObject(name)
    if o is None:
        print("  %-20s MISSING" % name)
        continue
    sh = o.Shape
    pt = V(*rec["point"])
    read, up, n, into = frame(rec.get("axis", rec["mode"]), V(*rec["normal"]))
    h = rec["height"]
    hx = 0.62 * h * len(rec["text"]) + 1.0
    hy = 0.78 * h
    ny = 11
    nx = int(ny * 2.3 * hx / hy)
    print("  %s   cut as %r at %s, %.0f mm tall:"
          % (name, rec["text"], tuple(rec["point"]), h))
    for iy in range(ny):
        b = hy - 2.0 * hy * iy / (ny - 1)
        row = ""
        for ix in range(nx):
            a = -hx + 2.0 * hx * ix / (nx - 1)
            p = V(pt.x + read.x * a + up.x * b + into.x * 0.4,
                  pt.y + read.y * a + up.y * b + into.y * 0.4,
                  pt.z + read.z * a + up.z * b + into.z * 0.4)
            row += " " if sh.isInside(p, 1e-6, True) else "#"
        print("     |" + row + "|")
