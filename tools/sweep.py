# -*- coding: utf-8 -*-
"""Drive 601_verify_fast.py across N headless FreeCAD processes and merge the results.

    python tools/sweep.py [nshards]

Defaults to cpu_count-2 shards, leaving a couple of cores for the GUI instance so the two can
coexist. Each shard is a separate freecadcmd process with its own copy of the document, so
there is no shared state to corrupt and no 90 s dispatch limit to chunk around.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

FREECADCMD = r"C:/Program Files/FreeCAD 1.0/bin/freecadcmd.exe"
SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts",
                      "601_verify_fast.py")

n = int(sys.argv[1]) if len(sys.argv) > 1 else max(1, (os.cpu_count() or 4) - 2)
tmp = tempfile.mkdtemp(prefix="kxsweep_")
outs = [os.path.join(tmp, "s%d.json" % i) for i in range(n)]

print("launching %d headless shards..." % n)
t0 = time.time()
procs = [subprocess.Popen([FREECADCMD, SCRIPT, str(i), str(n), outs[i]],
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
         for i in range(n)]
for i, p in enumerate(procs):
    out, _ = p.communicate()
    for line in out.decode("utf-8", "replace").splitlines():
        if "shard" in line:
            print("   " + line.strip())
el = time.time() - t0

worst, poses = {}, 0
for o in outs:
    if not os.path.exists(o):
        print("   shard output missing: %s" % o)
        continue
    d = json.load(open(o))
    poses += d["poses"]
    for k, v in d["worst"].items():
        if v[0] > worst.get(k, [0])[0]:
            worst[k] = v

print()
print("=" * 78)
print("%d poses across %d shards in %.1f s (%.1f min)" % (poses, n, el, el / 60.0))
print("=" * 78)
if not worst:
    print("  no pairs flagged")
for k, v in sorted(worst.items(), key=lambda x: -x[1][0]):
    at = "static" if v[1] is None else "theta %+.0f" % v[1]
    print("   %-44s %8.3f cm3  at %s" % (k, v[0], at))
print()
print("  reference: the GUI-driven 395_verify1.py takes about 32 minutes for the same sweep.")
