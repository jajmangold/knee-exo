# -*- coding: utf-8 -*-
"""A short hash of the model's GEOMETRY, so an image can say which geometry it shows.

The README carried six renders that predated the drive-cover rework and the conical cuffs: a boxy
P22 and cuffs that did not match the limb, sitting at the top of the page for weeks. Nothing caught
it, because nothing checks images -- the link checker reads markdown links, and these are <img src>
tags, and in any case a file that exists is not a file that is current.

Timestamps cannot answer it: git does not preserve mtimes, so a fresh clone makes every file the
same age. Hashing the .FCStd cannot either, because saving it changes the bytes whether or not
anything moved. So: hash the thing that actually matters to a picture, which is the shape of every
part. Volumes to a thousandth of a cm3, by name, sorted. Move a part and it changes. Re-save the
document, re-run the engraver on the same sites, or rebuild from the same scripts, and it does not.

    from fingerprint import fingerprint
    fingerprint(doc)        # -> "a3f19c2b"
"""
import hashlib


def fingerprint(doc):
    """Short hash over (part name, volume) for every solid in the document."""
    rows = []
    for o in doc.Objects:
        if not o.isDerivedFrom("Part::Feature"):
            continue
        sh = getattr(o, "Shape", None)
        if sh is None or sh.isNull() or not sh.Solids:
            continue
        rows.append("%s:%.3f" % (o.Name, sh.Volume / 1000.0))
    rows.sort()
    return hashlib.sha1("|".join(rows).encode("utf-8")).hexdigest()[:8]


def write(doc, path):
    """Drop the fingerprint beside an export, for a renderer that cannot open the document."""
    fp = fingerprint(doc)
    with open(path, "w") as f:
        f.write(fp + "\n")
    return fp
