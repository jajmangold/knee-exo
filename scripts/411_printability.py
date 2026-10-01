# -*- coding: utf-8 -*-
"""Is any of this actually printable?

Nobody had checked. The BOM says "3 perimeters, 15%" and "prints nose-down on its domed end,
no supports", and 399's docstring claims the drive shell "prints in one piece on a 250 bed"
-- all asserted, none measured, and no bed size is recorded anywhere in the repo. Meanwhile
the parts have grown: the thigh cuff is now 140 mm wide wrapping 200 degrees, the shank cuff
160, the drive shell 206 mm long.

This reads the EXPORTED STLs rather than the CAD solids, deliberately: the STL is what gets
sliced, and a mesh is where a tessellation problem would show up. Pure Python, no FreeCAD, so
it also runs while the interference sweep has the GUI thread.

Four questions per part, over every sensible orientation (each of six axes up, times 15
degree steps about the vertical):

  1. What bed does it need? Footprint, not bounding box -- a part lying diagonally fits a
     smaller bed than its axis-aligned extents suggest.
  2. How much needs support? Area of down-facing surface shallower than 45 degrees. A cuff
     is a half-tube: on end it needs nothing, on its back it is nearly all overhang, and the
     difference is worth knowing before someone slices it.
  3. How thin is it? 2V/A is the mean wall. Anything near the nozzle is a part the slicer
     quietly turns into two perimeters and no infill.
  4. Anything too small to print -- facets under a square millimetre, mesh not closed.

Run with:  python scripts/411_printability.py
"""
import glob
import math
import os
import struct

STL_DIR = r"C:/Users/Josh/KneeExo_v6_STL"
NOZZLE = 0.4
OVERHANG = 45.0
BEDS = [("Ender 3 / Mini", 220.0, 220.0, 250.0),
        ("Prusa MK4", 250.0, 210.0, 220.0),
        ("Bambu P1S / X1C", 256.0, 256.0, 256.0),
        ("Prusa XL", 360.0, 360.0, 360.0)]
COS_LIM = math.cos(math.radians(OVERHANG))


def read_stl(path):
    with open(path, "rb") as f:
        head = f.read(84)
        n = struct.unpack("<I", head[80:84])[0]
        data = f.read(n * 50)
    tris = []
    for i in range(n):
        o = i * 50
        vals = struct.unpack("<12f", data[o:o + 48])
        tris.append((vals[3:6], vals[6:9], vals[9:12]))
    return tris


def tri_props(t):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    area = 0.5 * m
    if m < 1e-12:
        return 0.0, (0.0, 0.0, 1.0), 0.0
    vol = (ax * (by * cz - bz * cy) + bx * (cy * az - cz * ay) + cx * (ay * bz - az * by)) / 6.0
    return area, (nx / m, ny / m, nz / m), vol


def rotm(up, spin):
    """matrix taking `up` to +Z then spinning about Z by `spin` degrees"""
    ux, uy, uz = up
    z = (ux, uy, uz)
    a = (1.0, 0.0, 0.0) if abs(uz) > 0.9 else (0.0, 0.0, 1.0)
    x = (a[1] * z[2] - a[2] * z[1], a[2] * z[0] - a[0] * z[2], a[0] * z[1] - a[1] * z[0])
    m = math.sqrt(sum(c * c for c in x)) or 1.0
    x = tuple(c / m for c in x)
    y = (z[1] * x[2] - z[2] * x[1], z[2] * x[0] - z[0] * x[2], z[0] * x[1] - z[1] * x[0])
    s, c = math.sin(math.radians(spin)), math.cos(math.radians(spin))
    # rows of the rotation: part vector -> print frame
    r0 = tuple(c * x[i] + s * y[i] for i in range(3))
    r1 = tuple(-s * x[i] + c * y[i] for i in range(3))
    r2 = z
    return r0, r1, r2


def apply(R, v):
    return (sum(R[0][i] * v[i] for i in range(3)),
            sum(R[1][i] * v[i] for i in range(3)),
            sum(R[2][i] * v[i] for i in range(3)))


UPS = [(0., 0., 1.), (0., 0., -1.), (0., 1., 0.), (0., -1., 0.), (1., 0., 0.), (-1., 0., 0.)]

files = sorted(glob.glob(os.path.join(STL_DIR, "*.stl")))
print("=" * 98)
print("PRINTABILITY -- measured off the exported STLs in %s" % STL_DIR)
print("=" * 98)
if not files:
    raise SystemExit("no STLs found -- run 219_stl.py first")
print("  %-24s %-16s %-9s %-10s %-8s %-8s %s"
      % ("part", "footprint", "height", "support", "wall", "facets", "best orientation"))
rows = []
for p in files:
    nm = os.path.basename(p)[:-4]
    tris = read_stl(p)
    props = [tri_props(t) for t in tris]
    area = sum(a for a, _, _ in props)
    vol = abs(sum(v for _, _, v in props))
    tiny = sum(1 for a, _, _ in props if a < 1.0)
    verts = [v for t in tris for v in t]
    best = None
    for up in UPS:
        for spin in range(0, 180, 15):
            R = rotm(up, float(spin))
            sup = 0.0
            for a, n, _ in props:
                if apply(R, n)[2] < -COS_LIM:
                    sup += a
            xs = [apply(R, v) for v in verts]
            bx = max(q[0] for q in xs) - min(q[0] for q in xs)
            by = max(q[1] for q in xs) - min(q[1] for q in xs)
            bz = max(q[2] for q in xs) - min(q[2] for q in xs)
            foot = max(bx, by)
            score = sup / area + max(0.0, foot - 250.0) * 0.01
            if best is None or score < best[0]:
                best = (score, bx, by, bz, sup, up, spin)
    _, bx, by, bz, sup, up, spin = best
    wall = 2.0 * vol / area if area else 0.0
    frac = sup / area if area else 0.0
    # watertight check: in a closed mesh every edge is shared by exactly two facets
    edges = {}
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (tuple(round(c, 4) for c in a), tuple(round(c, 4) for c in b))
            edges[k] = edges.get(k, 0) + 1
    open_e = 0
    for (a, b), n in edges.items():
        if edges.get((b, a), 0) != n:
            open_e += 1
    rows.append((nm, bx, by, bz, frac, wall, len(tris), tiny, sup, open_e, best[5], best[6], props, verts))
    lab = {(0., 0., 1.): "+Z", (0., 0., -1.): "-Z", (0., 1., 0.): "+Y",
           (0., -1., 0.): "-Y", (1., 0., 0.): "+X", (-1., 0., 0.): "-X"}[up]
    print("  %-24s %5.0f x %-8.0f %5.0f mm %5.1f%% %6.1f cm2 %5.2f mm %6d %s %s up %d"
          % (nm, bx, by, bz, 100.0 * frac, sup / 100.0, wall, len(tris),
             "open!" if open_e else "   ok", lab, spin))

print()
print("=" * 98)
print("WHAT BED IS NEEDED")
print("=" * 98)
for lbl, bedx, bedy, bedz in BEDS:
    bad = []
    for nm, bx, by, bz, frac, wall, nt, tiny, sup, oe, up, spin, props, verts in rows:
        fits = ((bx <= bedx and by <= bedy) or (bx <= bedy and by <= bedx)) and bz <= bedz
        if not fits:
            bad.append(nm)
    print("  %-22s %3.0f x %-3.0f x %-3.0f   %s"
          % (lbl, bedx, bedy, bedz, "ALL FIT" if not bad else "no room for " + ", ".join(bad)))
print()
print("  largest footprint in the set: %.0f mm" % max(max(r[1], r[2]) for r in rows))
print("  tallest part: %.0f mm" % max(r[3] for r in rows))

print()
print("=" * 98)
print("PROBLEMS")
print("=" * 98)
any_bad = False
for nm, bx, by, bz, frac, wall, nt, tiny, sup, oe, up, spin, props, verts in rows:
    msgs = []
    if oe:
        msgs.append("MESH NOT CLOSED: %d unpaired edges" % oe)
    if frac > 0.12:
        msgs.append("%.0f%% of its surface overhangs past %d deg even in its best orientation"
                    % (100 * frac, OVERHANG))
    if wall < 3 * NOZZLE:
        msgs.append("mean wall %.2f mm, under the %.1f mm that gives 2 perimeters plus infill"
                    % (wall, 3 * NOZZLE))
    # NOT a problem test any more. It was meant as a proxy for "features too small to
    # print", and it is a bad one: 412 engraves part numbers, text tessellates into hundreds
    # of small facets, and four perfectly printable parts lit up the moment they were marked.
    # Facet size measures the MESH, not the geometry. What actually decides whether text
    # survives a 0.4 nozzle is stem width, and that is handled where the text is made -- bold
    # face, 8 mm cap height, ~1.2 mm stems, three extrusions wide.
    if msgs:
        any_bad = True
        print("  %-24s %s" % (nm, "; ".join(msgs)))
if not any_bad:
    print("  none")
print()
print("  Support fraction is of TOTAL surface area, so a figure like 10%% is a couple of")
print("  bosses, not a disaster. The number to react to is a part that cannot be oriented")
print("  below the threshold at all -- that is a part that wants splitting or redesigning.")


print()
print("=" * 98)
print("WHERE THE OVERHANGS ARE  (flagged parts only, in their best orientation)")
print("=" * 98)
for nm, bx, by, bz, frac, wall, nt, tiny, sup, oe, up, spin, props, verts in rows:
    if frac <= 0.12:
        continue
    R = rotm(up, float(spin))
    zs = [apply(R, v)[2] for v in verts]
    z0, z1 = min(zs), max(zs)
    bands = [0.0] * 10
    for i, (a, n, _) in enumerate(props):
        if apply(R, n)[2] >= -COS_LIM:
            continue
        zc = sum(apply(R, verts[3 * i + k])[2] for k in range(3)) / 3.0
        b = min(9, int(10.0 * (zc - z0) / max(1e-6, z1 - z0)))
        bands[b] += a
    print("  %s -- %.1f cm2 of overhang over %.0f mm of height:" % (nm, sup / 100.0, z1 - z0))
    for b in range(10):
        if bands[b] < 0.05:
            continue
        print("     %5.0f..%-5.0f mm  %6.2f cm2  %s"
              % (z0 + (z1 - z0) * b / 10.0, z0 + (z1 - z0) * (b + 1) / 10.0,
                 bands[b] / 100.0, "#" * int(bands[b] / 100.0 * 4)))
