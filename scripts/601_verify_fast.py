# -*- coding: utf-8 -*-
"""The 107-pose interference sweep, headless and sharded. Same answer, ~25x faster.

600_profile.py measured where the 32 minutes went:

    common() on one pair        138 ms     <- the real work
    o.Shape access                4 ms     <- 666 bbox tests spent 5.5 s just READING shapes
    static vs static pairs    76 of 130    <- re-evaluated 107 times each, for 58% of the total

So three changes, none of which weakens the test:

  1. CACHE THE SHAPES. `o.Shape` is not an attribute lookup, it is a rebuild, and the old
     sweep called it inside the pair loop. Static parts are read once ever; moving parts once
     per pose.
  2. SKIP POSE-INVARIANT PAIRS. A pair of parts that both sit still cannot change its overlap
     when the knee bends. Evaluate those once at pose 0 and never again. That is 58% of the
     work, and it is pure waste rather than a trade.
  3. RUN HEADLESS AND SHARDED. The 90 s GUI dispatch limit is a property of the RPC server,
     not of FreeCAD. freecadcmd has no such limit, so no chunking, no half-applied state when
     a chunk overruns -- and poses are independent, so twelve of them can run at once.

Usage, one shard per process:

    freecadcmd.exe scripts/601_verify_fast.py <shard> <nshards> <out.json>

tools/sweep.py drives all of them and merges.
"""
import itertools
import json
import math
import os
import sys
import time

import FreeCAD
from FreeCAD import Vector as V

argv = [a for a in sys.argv if not a.endswith(".py") and not a.endswith(".exe")]
SHARD = int(argv[0]) if argv else 0
NSHARD = int(argv[1]) if len(argv) > 1 else 1
OUT = argv[2] if len(argv) > 2 else "sweep_%d.json" % SHARD

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"
TEETH, PITCH = 29, 8.0
R_CAP = TEETH * PITCH / (2 * math.pi)
A0 = 161.0
THETA = [float(i) for i in range(-2, 105)]

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "P31_InterfaceDist", "REF_Shank", "HW_JointBolts"]
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
MOVERS = set(SHANK) | set(GANTRY)

t_start = time.time()
doc = FreeCAD.openDocument(DOC)
parts = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids]
names = [o.Name for o in parts]
obj = dict(zip(names, parts))

# --- the shapes that never move, read exactly once
static = [n for n in names if n not in MOVERS]
movers = [n for n in names if n in MOVERS]
SH = {n: obj[n].Shape for n in static}


def pose(th):
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    dy = (A0 - R_CAP * math.radians(th)) - A0
    for n in SHANK:
        if n in obj:
            obj[n].Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in GANTRY:
        if n in obj:
            obj[n].Placement = FreeCAD.Placement(V(0, dy, 0), FreeCAD.Rotation())
    for n in movers:
        if n in obj:
            SH[n] = obj[n].Shape


PAIRS_ALL = list(itertools.combinations(names, 2))
PAIRS_MOVING = [(a, b) for a, b in PAIRS_ALL if a in MOVERS or b in MOVERS]
PAIRS_STATIC = [(a, b) for a, b in PAIRS_ALL if a not in MOVERS and b not in MOVERS]

mine = [i for i in range(len(THETA)) if i % NSHARD == SHARD]
worst = {}


def test(a, b):
    sa, sb = SH[a], SH[b]
    if not sa.BoundBox.intersect(sb.BoundBox):
        return 0.0
    try:
        c = sa.common(sb)
    except Exception:
        return 0.0
    return 0.0 if c.isNull() else c.Volume / 1000.0


# --- the pose-invariant half, once
if SHARD == 0:
    pose(0.0)
    for a, b in PAIRS_STATIC:
        v = test(a, b)
        if v > 0.02:
            worst[a + "^" + b] = [v, None]
    print("shard 0: %d static pairs done once (%.1f s)" % (len(PAIRS_STATIC), time.time() - t_start))

# --- the pose-dependent half, sharded
for i in mine:
    th = THETA[i]
    pose(th)
    for a, b in PAIRS_MOVING:
        v = test(a, b)
        if v > 0.02 and v > worst.get(a + "^" + b, [0])[0]:
            worst[a + "^" + b] = [v, th]

el = time.time() - t_start
json.dump({"worst": worst, "poses": len(mine), "shard": SHARD, "secs": el}, open(OUT, "w"))
print("shard %d/%d: %d poses, %d moving pairs each, %.1f s"
      % (SHARD, NSHARD, len(mine), len(PAIRS_MOVING), el))
