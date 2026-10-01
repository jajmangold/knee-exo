# -*- coding: utf-8 -*-
"""Where does the time actually go?

The 107-pose sweep takes ~25 minutes, the engraving search blew the 90 s GUI dispatch limit,
and every heavy script has to be chunked by hand. Before optimising any of that, measure it.

Runs HEADLESS under freecadcmd, which is itself the first question worth answering: the GUI
dispatch limit is a property of the RPC server, not of FreeCAD, and a headless process has no
such limit and can be run twelve at a time on this machine.

  "C:/Program Files/FreeCAD 1.0/bin/freecadcmd.exe" scripts/600_profile.py
"""
import os
import sys
import time

import FreeCAD
import Part

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"

t0 = time.time()
doc = FreeCAD.openDocument(DOC)
t_open = time.time() - t0
print("open document            %7.2f s" % t_open)

parts = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids]
print("parts                    %7d" % len(parts))

# --- touching every Shape (lazy load from the file)
t0 = time.time()
tot_faces = sum(len(o.Shape.Faces) for o in parts)
print("touch all shapes         %7.2f s   (%d faces total)" % (time.time() - t0, tot_faces))

# --- bounding box pre-test, which is what the sweep leans on
import itertools
pairs = list(itertools.combinations(parts, 2))
t0 = time.time()
near = [(a, b) for a, b in pairs if a.Shape.BoundBox.intersect(b.Shape.BoundBox)]
t_bb = time.time() - t0
print("bbox test, %5d pairs   %7.3f s   -> %d pairs survive" % (len(pairs), t_bb, len(near)))

# --- the real cost: common() on the survivors
t0 = time.time()
n = 0
for a, b in near[:120]:
    k = a.Shape.common(b.Shape)
    if not k.isNull():
        n += 1
t_common = time.time() - t0
per = t_common / max(1, len(near[:120]))
print("common() x %3d           %7.2f s   -> %.1f ms each" % (len(near[:120]), t_common, per * 1000))
print("   one full pose would be %d commons = %.1f s" % (len(near), len(near) * per))
print("   107 poses             %.0f s = %.1f min" % (107 * len(near) * per, 107 * len(near) * per / 60))

# --- how many of those pairs are STATIC vs STATIC and therefore pose-invariant
MOVING = set(["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
              "P24_FairingShank", "P31_InterfaceDist", "HW_JointBolts", "P3_Carriage",
              "A2b_BallNut_SFU1620", "P10a_VWheel", "P10b_VWheel", "P10c_VWheel",
              "P10d_VWheel"])
ss = sum(1 for a, b in near if a.Name not in MOVING and b.Name not in MOVING)
print()
print("of the %d near pairs, %d are STATIC vs STATIC" % (len(near), ss))
print("   those cannot change with pose, so 106 of their 107 evaluations are wasted:")
print("   %.0f s of the %.0f s total = %.0f %%"
      % (106 * ss * per, 107 * len(near) * per, 100.0 * 106 * ss / (107 * len(near))))

# --- ray casting, which is what 406 / 412 / 413 do thousands of times
from FreeCAD import Vector as V
big = max(parts, key=lambda o: o.Shape.Volume)
t0 = time.time()
for i in range(60):
    e = Part.makeLine(V(0, 50 + i, 0), V(300, 50 + i, 100))
    big.Shape.common(e)
t_ray = (time.time() - t0) / 60.0
print()
print("ray vs solid (common with a line)  %.1f ms each" % (t_ray * 1000))
print("   406 fires %d rays x %d parts x 3 poses = %d -> %.0f s"
      % (187, 28, 187 * 28 * 3, 187 * 28 * 3 * t_ray))

# --- tessellation, for comparison: a mesh-based ray test would pay this once
t0 = time.time()
tri = big.Shape.tessellate(0.2)
print()
print("tessellate the biggest part        %.2f s  -> %d triangles"
      % (time.time() - t0, len(tri[1])))
print("   a numpy ray/triangle test on that mesh is microseconds per ray, so the crossover")
print("   is at a handful of rays per part -- 406 fires %d." % (187 * 3))
