# -*- coding: utf-8 -*-
"""Copy the working CAD documents, mark registries and STLs into the repository.

    python tools/snapshot.py          # report what differs
    python tools/snapshot.py --write  # copy it in

The documents live outside the repository, at C:/Users/Josh/KneeExo_v6*.FCStd, because ~300
scripts hardcode that path. The repository therefore holds COPIES, and copies go stale silently:
after both legs were re-engraved, model/ and stl/ still contained the previous commit's parts --
the ones whose part numbers were mirror images -- and nothing said so. The right leg and both mark
registries were not tracked at all.

The registries matter more than they look. <doc>.marks.json is not a log: 702 reads the left leg's
registry to place the right leg's marks, 413 reads it to know what to test, and 416 reads it to
take a mark back out. Lose it and the two legs can no longer be marked in mirror-image places, and
the visibility check silently falls back to a hand-written table.

Why keep the binary .FCStd in git at all, in a repository whose point is that the scripts are the
source: because the document is NOT reproducible from the scripts alone. It is the result of ~300
of them run in an order recorded nowhere, over weeks. tools/build_headless.py reproduces the last
eight stages; everything before that exists only in the file. Until that is untrue, the file is
source.
"""
import filecmp
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
WRITE = "--write" in sys.argv

FILES = [
    (r"C:/Users/Josh/KneeExo_v6.FCStd", "model/KneeExo_v6.FCStd"),
    (r"C:/Users/Josh/KneeExo_v6_R.FCStd", "model/KneeExo_v6_R.FCStd"),
    (r"C:/Users/Josh/KneeExo_v6.marks.json", "model/KneeExo_v6.marks.json"),
    (r"C:/Users/Josh/KneeExo_v6_R.marks.json", "model/KneeExo_v6_R.marks.json"),
]
DIRS = [
    (r"C:/Users/Josh/KneeExo_v6_STL", "stl"),
    (r"C:/Users/Josh/KneeExo_v6_R_STL", "stl_R"),
]


def act(src, rel):
    dst = os.path.join(REPO, rel)
    if not os.path.exists(src):
        print("  %-34s SOURCE MISSING" % rel)
        return 0
    same = os.path.exists(dst) and filecmp.cmp(src, dst, shallow=False)
    if same:
        return 0
    state = "differs" if os.path.exists(dst) else "NEW"
    print("  %-34s %-8s %7.2f MB" % (rel, state, os.path.getsize(src) / 1048576.0))
    if WRITE:
        d = os.path.dirname(dst)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        shutil.copy2(src, dst)
    return 1


print("=" * 78)
print("SNAPSHOT  %s" % ("writing into the repository" if WRITE else "report only (--write to copy)"))
print("=" * 78)
n = 0
for src, rel in FILES:
    n += act(src, rel)
for sdir, rel in DIRS:
    if not os.path.isdir(sdir):
        print("  %-34s SOURCE DIR MISSING" % rel)
        continue
    for f in sorted(os.listdir(sdir)):
        if f.endswith(".stl"):
            n += act(os.path.join(sdir, f), "%s/%s" % (rel, f))
    # STLs that the repository has and the export no longer produces are parts that were renamed
    # or deleted; leaving them behind is how a stale set looks complete.
    rd = os.path.join(REPO, rel)
    if os.path.isdir(rd):
        live = {f for f in os.listdir(sdir) if f.endswith(".stl")}
        for f in sorted(os.listdir(rd)):
            if f.endswith(".stl") and f not in live:
                print("  %-34s STALE, not exported any more" % ("%s/%s" % (rel, f)))
                if WRITE:
                    os.remove(os.path.join(rd, f))
                n += 1
print("-" * 78)
print("  %d file(s) %s" % (n, "copied" if WRITE else "would change"))
if n and not WRITE:
    print("  Run again with --write, then commit.")
