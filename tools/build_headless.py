# -*- coding: utf-8 -*-
"""Run the build chain in ONE headless FreeCAD process.

    freecadcmd.exe tools/build_headless.py [stage ...]

Why one process rather than one per script: the GUI's RPC server keeps a single global
namespace across calls, and several build scripts quietly rely on it -- 396_fixes.py uses
vs_leg(), which 391 defines. Run each script in its own process and that coupling surfaces as
"name 'vs_leg' is not defined" halfway through a rebuild. Sharing one namespace here
reproduces the GUI's behaviour exactly, and as a bonus the document is opened and saved once
instead of eight times.

Headless because the RPC server's 90 s dispatch limit is not a clean failure: 397 and 409 both
exceed it, and overrunning leaves a half-built document that the next stage reads as finished.
Every half-applied state in this project has come from that.

KX_DOC selects the file, so the mirrored right leg builds through the same chain.
"""
import os
import sys
import time
import traceback

import FreeCAD

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, "..", "scripts")

CHAIN = ["393_driveend", "394_lighten_merge", "396_fixes", "397_recladding",
         "398_sidemounts", "399_drivecap", "409_cuffs", "502_interface_build"]

want = [a for a in sys.argv[1:] if not a.endswith(".py")]
chain = want or CHAIN

# Un-pose FIRST. A leftover animation pose is the one corruption that passes every check:
# shapes valid, volumes right, document saves clean -- and every boolean against a posed
# reference quietly uses the wrong geometry, because obj.Shape bakes the Placement in. The
# file arrived here frozen at 30 deg of flexion (shank side rotated, carriage back 19.33 mm),
# which is what made 409's fit check report "P7_ShankCuff: only 17 samples landed on the
# shell": the rays were fired at the cuff and missed the limb, which was no longer there.
sys.path.insert(0, HERE)
os.environ["KX_NO_MAIN"] = "1"         # we want unpose()'s function, not its CLI behaviour
from unpose import unpose as _unpose   # noqa: E402

_doc0 = None
for _d in FreeCAD.listDocuments().values():
    _doc0 = _d
if _doc0 is None:
    _doc0 = FreeCAD.openDocument(os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd"))
_moved = _unpose(_doc0)
if _moved:
    _doc0.recompute()
    _doc0.save()
    print("  un-posed %d parts before building: %s" % (len(_moved), ", ".join(_moved)))

g = {"__name__": "__main__", "__builtins__": __builtins__}
print("=" * 72)
print("HEADLESS BUILD  ->  %s" % os.environ.get("KX_DOC", "KneeExo_v6.FCStd"))
print("=" * 72)
t0 = time.time()
fail = []
for name in chain:
    p = os.path.join(SCRIPTS, name + ".py")
    t = time.time()
    try:
        exec(compile(open(p, encoding="utf-8").read(), p, "exec"), g)
        print("  %-24s ok    %6.1f s" % (name, time.time() - t))
    except Exception as e:
        fail.append(name)
        print("  %-24s FAIL  %6.1f s   %s" % (name, time.time() - t, e))
        traceback.print_exc()
print("-" * 72)
print("  %d stages, %d failed, %.1f s total" % (len(chain), len(fail), time.time() - t0))
if fail:
    print("  failed: %s" % ", ".join(fail))
    sys.exit(1)
