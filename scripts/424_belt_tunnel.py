# -*- coding: utf-8 -*-
"""Make the gantry actually grip the belt: a toothed land in the belt tunnel, cut to the real belt.

This replaces the "belt clamp" 422_missing_features.py added, which was wrong in a way worth
recording because it passed its own check. 422 built the clamp grooves like this:

    sol = f.extrude(V(0, 0, BELT_Z[1] - BELT_Z[0]))
    sol.rotate(V(0, 0, 0), V(0, 1, 0), 90.0)          # lay the groove along X

The rotation turned the groove's DEPTH axis from X into Z and its extrusion from Z into X, so what
got cut was not five grooves across a clamp face but five elliptical tunnels bored horizontally
through the carriage at Z 96, 8 mm apart. Every one of them removed material, so cut_and_check()
reported five features added and zero landed in air, and 420's "a belt clamp" test -- two
cylindrical faces of 3..7 mm diameter -- was satisfied by the bolt holes. A hole in the wrong plane
is the same class of defect as a pulley with no teeth, committed inside the fix for it.

So this file ends with a check that measures the land's surface along Y and demands it vary by the
groove depth: a groove that is not where a groove should be now fails.

WHAT THE TUNNEL IS. The carriage already straddles the drive run through a closed rectangular
tunnel -- floor at Z 89..95.5, roof at Z 126.5..130, walls either side -- over Y 152..170. Nothing
in it gripped the belt; the belt simply passed through. Given that structure, the belt needs no
separate clamp part at all:

    the belt's teeth face inboard, toward the knee axis, so the INBOARD wall is the natural land
    cut 8 mm-pitch grooves in it and the belt's teeth sit in them
    the OUTBOARD wall stops the belt backing out of mesh
    floor and roof stop it climbing
    tension is carried by tooth shear into the carriage, not by friction and not by bolts

764 N over 5 teeth is 153 N a tooth, 1.5 MPa over a 30 x 3.45 mm groove wall against PETG's ~15
MPa sustained. So the tunnel is lengthened from 18 mm to 42 mm to get those five teeth, and
P26_BeltClamp -- the bolt-on block 422 invented -- is deleted. Seventeen printed parts again.

GEOMETRY, ALL OF IT FOLLOWING FROM 421 AND 423:

    pulley tip radius        36.237     421, standard 29T
    belt back                38.46      423
    outboard wall face      -38.70      0.24 mm behind the belt
    land face (tip plane)   -36.237     the belt's land rests here
    groove bottom           -32.787     3.45 deep; belt tooth tips reach -32.857, so 0.07 clear

It also relieves the tooth corridor everywhere else. The carriage's inboard deck edge stood at
X -35.2 along its whole length, which is inside the annulus the belt's teeth sweep -- outside the
clamp zone a belt tooth would strike it every 8 mm of travel. 423 is what found that.

    freecadcmd.exe scripts/424_belt_tunnel.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
HERE = os.path.dirname(os.path.abspath(__file__))
REFFILE = os.path.join(HERE, "..", "model", _BASE).replace("\\", "/")
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

TIP = 36.237                  # 421: standard 29T tip radius = the belt's land plane
BACK = 38.457                 # 423: belt back
ROOT = 32.857                 # 423: belt tooth tips
DEPTH, HALF_W, PITCH = 3.45, 2.65, 8.0
WALL_FACE = -(BACK + 0.24)    # -38.70
LAND_IN = -28.0               # how far inboard the land block reaches
FLOOR_Z = (89.0, 95.5)
BELT_Z = (96.0, 126.0)
SLOT_Z = (95.5, 126.5)
CLAMP_Y = (144.0, 186.0)      # 42 mm -> 5 teeth at 8 mm pitch
CARR_Y = (119.0, 203.0)
M5, M4 = 5.2, 4.2
A0 = 161.0
PRE_VOL = 71.3                # the pre-422 carriage, cm3

print("=" * 98)
print("BELT TUNNEL  --  %s" % _BASE)
print("=" * 98)

p3 = doc.getObject("P3_Carriage")
assert p3 is not None, "no carriage in this document"

# ---------------------------------------------------------------- back to before 422
# 422's bogus grooves cannot be undone by fusing their tools back: the tools stood half in air, so
# fusing them would ADD material the part never had. Restore the shape from the committed copy,
# which predates 422, and re-apply the features of 422 that were right.
ref = None
for d in FreeCAD.listDocuments().values():
    if d.FileName.replace(chr(92), "/").endswith("model/" + _BASE):
        ref = d
if ref is None:
    assert os.path.exists(REFFILE), "no pre-422 copy at %s" % REFFILE
    ref = FreeCAD.openDocument(REFFILE)
for x in ref.Objects:
    if hasattr(x, "Placement"):
        x.Placement = FreeCAD.Placement()
ref.recompute()
r3 = ref.getObject("P3_Carriage")
assert abs(r3.Shape.Volume / 1000.0 - PRE_VOL) < 1.0, \
    "the copy's carriage is %.1f cm3, expected %.1f -- wrong vintage" % (r3.Shape.Volume / 1000.0, PRE_VOL)
p3.Shape = r3.Shape
print("  restored the pre-422 carriage from model/%s: %.1f cm3" % (_BASE, p3.Shape.Volume / 1000.0))

report = []


def cut_and_check(obj, tool, what, need=0.005):
    v0 = obj.Shape.Volume
    new = obj.Shape.cut(tool)
    removed = (v0 - new.Volume) / 1000.0
    ok = removed >= need
    if ok:
        tidy = new.removeSplitter()
        try:
            tidy.check(True)
            new = tidy
        except Exception:
            pass
        obj.Shape = new
    report.append((what, removed, ok))
    return ok


def fuse_and_check(obj, tool, what):
    v0 = obj.Shape.Volume
    new = obj.Shape.fuse(tool)
    tidy = new.removeSplitter()
    try:
        tidy.check(True)
        new = tidy
    except Exception:
        pass
    added = (new.Volume - v0) / 1000.0
    obj.Shape = new
    report.append((what, added, len(new.Solids) == 1))
    return added


# ---------------------------------------------------------------- the features 422 got right
# V-wheel bolts, taken from where the wheels actually are rather than from a remembered number
wheels = []
for nm in ("P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"):
    w = doc.getObject(nm)
    if w is None:
        continue
    b = w.Shape.BoundBox
    wheels.append((nm, 0.5 * (b.XMin + b.XMax), 0.5 * (b.YMin + b.YMax)))
assert len(wheels) == 4, "expected 4 V-wheels, found %d" % len(wheels)
for nm, wx, wy in wheels:
    cut_and_check(p3, Part.makeCylinder(M5 / 2.0, 40.0, V(wx, wy, 105.0), V(0, 0, 1)),
                  "%s M5 at X %+.2f Y %.0f" % (nm[:4], wx, wy))
# the flangeless ball nut is trapped axially but nothing stops it turning: two radial M5s
for y in (A0 - 12.0, A0 + 12.0):
    cut_and_check(p3, Part.makeCylinder(M5 / 2.0, 26.0, V(-88.0, y, 106.0), V(1, 0, 0)),
                  "nut set screw at Y %.0f" % y)

# ---------------------------------------------------------------- relieve the tooth corridor
# everywhere, then put the land back only where the belt is meant to mesh
corridor = Part.makeBox(TIP - ROOT + 0.1, CARR_Y[1] - CARR_Y[0] + 2.0, BELT_Z[1] - BELT_Z[0],
                        V(-TIP - 0.05, CARR_Y[0] - 1.0, BELT_Z[0]))
cut_and_check(p3, corridor, "tooth corridor relieved over Y %.0f..%.0f" % CARR_Y, need=0.1)
# and the belt's own backing corridor, in case anything stands in it
backing = Part.makeBox(BACK - TIP, CARR_Y[1] - CARR_Y[0] + 2.0, BELT_Z[1] - BELT_Z[0],
                       V(-BACK, CARR_Y[0] - 1.0, BELT_Z[0]))
v0 = p3.Shape.Volume
p3.Shape = p3.Shape.cut(backing)
report.append(("belt backing corridor cleared", (v0 - p3.Shape.Volume) / 1000.0, True))

# ---------------------------------------------------------------- build the tunnel
cl = CLAMP_Y[1] - CLAMP_Y[0]
# The floor stops at -31.2, not at the land's -28: the canopy's inner wall stands at X -31 over
# Y 77..136, and the carriage sweeps 67 mm in Y, so a floor reaching -28 scythed through it at
# every pose past about +40 degrees. It still ties the outboard wall to the land over 5.0 mm.
FLOOR_IN = -31.2
FLOOR_W = FLOOR_IN - (WALL_FACE - 2.8)     # -31.2 - -41.50 = 10.30
LAND_W = LAND_IN + TIP                     # -28 + 36.24 =  8.24
floor = Part.makeBox(FLOOR_W, cl, FLOOR_Z[1] - FLOOR_Z[0],
                     V(WALL_FACE - 2.8, CLAMP_Y[0], FLOOR_Z[0]))
wall = Part.makeBox(2.8, cl, SLOT_Z[1] - SLOT_Z[0], V(WALL_FACE - 2.8, CLAMP_Y[0], SLOT_Z[0]))
land = Part.makeBox(LAND_W, cl, SLOT_Z[1] - SLOT_Z[0], V(-TIP, CLAMP_Y[0], SLOT_Z[0]))
print()
print("  tunnel over Y %.0f..%.0f: outboard wall face %.2f, land face %.3f, floor Z %.1f..%.1f"
      % (CLAMP_Y[0], CLAMP_Y[1], WALL_FACE, -TIP, FLOOR_Z[0], FLOOR_Z[1]))
# what else is in the space the tunnel wants?
want = floor.fuse(wall).fuse(land)
for o in doc.Objects:
    if o.TypeId != "Part::Feature" or o.Name in ("P3_Carriage",) or getattr(o, "Shape", None) is None:
        continue
    if o.Shape.isNull() or not o.Shape.Solids or o.Name.startswith(("REF_", "TEST_", "A5")):
        continue
    if not o.Shape.BoundBox.intersect(want.BoundBox):
        continue
    try:
        c = o.Shape.common(want)
    except Exception:
        continue
    if not c.isNull() and c.Volume > 20.0:
        print("   NOTE %-24s %.2f cm3 of the tunnel's space" % (o.Name, c.Volume / 1000.0))
fuse_and_check(p3, floor, "floor extended to Y %.0f..%.0f" % CLAMP_Y)
fuse_and_check(p3, wall, "outboard wall, 2.8 mm")
fuse_and_check(p3, land, "toothed land blank, %.1f mm thick" % LAND_W)

# ---------------------------------------------------------------- cut the grooves
n = int(cl / PITCH)
y_first = CLAMP_Y[0] + 0.5 * (cl - (n - 1) * PITCH)
teeth = None
for i in range(n):
    y = y_first + i * PITCH
    el = Part.Ellipse(V(0, 0, 0), DEPTH, HALF_W)       # major along X = depth, minor along Y
    sol = Part.Face(Part.Wire(el.toShape())).extrude(V(0, 0, SLOT_Z[1] - SLOT_Z[0] + 2.0))
    sol.translate(V(-TIP, y, SLOT_Z[0] - 1.0))         # NO rotation: depth stays along X
    teeth = sol if teeth is None else teeth.fuse(sol)
cut_and_check(p3, teeth, "%d HTD-8M grooves at Y %.0f..%.0f" % (n, y_first, y_first + (n - 1) * PITCH),
              need=0.2)

sh = p3.Shape
if sh.Volume < 0:
    sh.reverse()
sh.check(True)
assert len(sh.Solids) == 1, "the carriage came out as %d solids" % len(sh.Solids)
p3.Shape = sh
p3.Label = "P3_GantryPlate_Printed"

# ---------------------------------------------------------------- P26 goes away
p26 = doc.getObject("P26_BeltClamp")
if p26 is not None:
    doc.removeObject(p26.Name)
    print()
    print("  P26_BeltClamp deleted: the tunnel grips the belt, so there is no clamp part")

doc.recompute()
doc.save()

print()
print("  %-52s %10s" % ("feature", "cm3"))
bad = 0
for what, vol, ok in report:
    print("  %-52s %10.3f %s" % (what[:52], vol, "" if ok else "<-- NO MATERIAL"))
    if not ok:
        bad += 1

# ---------------------------------------------------------------- does it hold a belt?
print()
print("  VERIFICATION")
fail = []
for nm in ("A5b_Belt_DriveRun", "A5_Belt_HTD8M", "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler"):
    b = doc.getObject(nm)
    if b is None:
        continue
    c = p3.Shape.common(b.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("   %-24s overlap with the carriage %7.3f cm3" % (nm, v))
    if v > 0.02:
        fail.append("%s overlaps the carriage by %.3f cm3" % (nm, v))

# the land, measured along Y at the belt plane: this is the check 422 would have failed
zs = 0.5 * (BELT_Z[0] + BELT_Z[1])
xs = []
y = CLAMP_Y[0] + 1.0
while y <= CLAMP_Y[1] - 1.0:
    ln = Part.makeLine(V(-TIP - 0.5, y, zs), V(LAND_IN, y, zs))
    k = p3.Shape.common(ln)
    if not k.isNull() and k.Vertexes:
        # the ray runs from outside the tip plane inboard, so the land surface is the first
        # boundary it meets: the most negative X of the intersection
        xs.append((y, -min(vv.Point.x for vv in k.Vertexes)))
    y += 0.5
if xs:
    rr = [v for _, v in xs]
    print("   land surface along Y: |X| %.2f..%.2f, varies by %.2f mm (grooves are %.2f deep)"
          % (min(rr), max(rr), max(rr) - min(rr), DEPTH))
    if max(rr) - min(rr) < 0.8 * DEPTH:
        fail.append("the land varies by only %.2f mm along Y -- the grooves are not in its face"
                    % (max(rr) - min(rr)))
    # and the period should be the belt pitch
    deep = [y for y, v in xs if v < min(rr) + 0.5]
    runs = 1 + sum(1 for i in range(1, len(deep)) if deep[i] - deep[i - 1] > 2.0)
    print("   %d groove bottoms found along %.0f mm of land, %d expected at %.0f mm pitch"
          % (runs, cl, n, PITCH))
    if runs != n:
        fail.append("found %d groove bottoms, expected %d" % (runs, n))
else:
    fail.append("no land surface found at the belt plane at all")

print()
if fail or bad:
    for f in fail:
        print("  FAIL %s" % f)
    if bad:
        print("  FAIL %d feature(s) removed or added nothing" % bad)
else:
    print("  the carriage holds the belt in a %d-tooth land and touches it nowhere else" % n)
print("  carriage is now %.1f cm3" % (p3.Shape.Volume / 1000.0))
sys.stdout.flush()
sys.exit(1 if (fail or bad) else 0)
