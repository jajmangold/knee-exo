# -*- coding: utf-8 -*-
"""Make the shank rail a 2040, and rebuild the socket round it. Runs after 430.

431_shank_2040.py is the argument, measured off the model's own sections rather than a catalogue:

    2020 as drawn   I  9809 mm4   28.7 MPa   0.58 deg of wind-up at the ankle   164 g
    2040            I 70707 mm4    8.0 MPa   0.08 deg                           366 g

Half a degree of knee angle happens PAST the motor's encoder, so the controller cannot see it and
cannot correct it. That is the whole case; the strength was never the problem.

WHAT IT COSTS, SAID PLAINLY. +202 g of aluminium and about +50 cm3 of PETG rebuilding the socket,
so roughly +270 g on the segment that swings about the knee -- call it 13% of the reflected rotor
inertia the 14.5:1 ratio exists to keep small. Mass on the shank is the expensive kind.

WHY THE SOCKET HAS TO BE REBUILT RATHER THAN ADJUSTED. P6_ShankSocket grips a 20 mm rail between
two walls that live at |X| 12..20, and its twelve M4 clamp bolts run up through |X| 16 and 20. A
2040 is 40 mm across: its body occupies exactly where those walls and bolts are. Cutting the wider
pocket on its own leaves the socket in two pieces -- the upper block that carries the KX-1 distal
interface loses every connection to the base. So:

    new side walls   X +-(20.5..30), Z 72..96, which is what the pocket takes away
    12 x M4          |X| 16 and 20  ->  |X| 24, outboard of the rail, filled and re-drilled
    pocket           X +-20.5, Z 73.5..94.5

The socket's OUTER shape and its interfaces to the cuff and to P31 do not move, because the cuff
is shaped to the calf and the KX-1 interface plane is a module spec.

    freecadcmd.exe scripts/432_shank_2040_build.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/432_shank_2040_build.py
"""
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

M5, M4 = 5.2, 4.2
JOINT_Z = 84.0
RAIL_Y = (-300.0, -66.0)
RAIL_HX, RAIL_HZ = 20.0, 10.0
FIT = 0.3
SLEEVE_Y = (-126.0, -56.0)
WALL, CHEEK = 4.5, 5.7
CUT_BELOW = -60.0
BOLT_Z_Y = (-72.0, -120.0)
BOLT_X_Y = (-84.0, -108.0)
WINDOW_Y = ((-102.0, -90.0), (-84.0, -76.0))
CORE_X = 10.0
SOCK_BOLT_X = 24.0              # outboard of a 2040
SOCK_WALL_Z = (72.0, 96.0)      # the walls the pocket takes away
TORQUE, PETG_BEAR = 28200.0, 15.0

a4 = doc.getObject("A4_Shank2020_VSlot")
a1 = doc.getObject("A1_Extrusion_20x60_VSlot")
p2a = doc.getObject("P2a_KneeHingePlate")
p6 = doc.getObject("P6_ShankSocket")
assert a4 and a1 and p2a and p6, "missing a rail, the hub or the socket"
mirrored = p2a.Shape.BoundBox.ZMax < 0
sgn = -1.0 if mirrored else 1.0


def z(v):
    return sgn * v


def zspan(lo, hi):
    a, b = z(lo), z(hi)
    return (min(a, b), max(a, b))


print("=" * 98)
print("SHANK 2040  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)

# ---------------------------------------------------------------- the rail, as a 2040
# take the THIGH rail's own section, so this is the same bought profile and not a second drawing
ws = a1.Shape.slice(V(0, 1, 0), 150.0)
fs = [Part.Face(w) for w in ws]
outer = max(fs, key=lambda f: f.Area)
prof = outer
for f in fs:
    if f is not outer:
        prof = prof.cut(f)
prof = prof if prof.ShapeType == "Face" else prof.Faces[0]
pb = prof.BoundBox
prof.translate(V(-0.5 * (pb.XMin + pb.XMax), RAIL_Y[0] - 150.0,
                 z(JOINT_Z) - 0.5 * (pb.ZMin + pb.ZMax)))
rail = prof.extrude(V(0, RAIL_Y[1] - RAIL_Y[0], 0))
rail.check(True)
assert len(rail.Solids) == 1, "the rail came out as %d solids" % len(rail.Solids)
was = a4.Shape.Volume / 1000.0
a4.Shape = rail
a4.Label = "A4_Shank2040_VSlot"
nb = rail.BoundBox
print("  rail  X %.0f..%.0f  Z %.0f..%.0f  Y %.0f..%.0f   %.1f -> %.1f cm3 (%.0f -> %.0f g)"
      % (nb.XMin, nb.XMax, nb.ZMin, nb.ZMax, nb.YMin, nb.YMax, was, rail.Volume / 1000.0,
         was * 2.70, rail.Volume / 1000.0 * 2.70))

# ---------------------------------------------------------------- the cap, widened to suit
sh = p2a.Shape
v0 = sh.Volume
sh = sh.cut(Part.makeBox(400.0, CUT_BELOW + 400.0, 400.0, V(-200.0, -400.0, -200.0)))
tidy = sh.removeSplitter()
try:
    tidy.check(True)
    sh = tidy
except Exception:
    pass
assert len(sh.Solids) == 1, "cutting the old cap left %d solids" % len(sh.Solids)
sx = RAIL_HX + FIT + WALL
sz = zspan(JOINT_Z - RAIL_HZ - FIT - CHEEK, JOINT_Z + RAIL_HZ + FIT + CHEEK)
sh = sh.fuse(Part.makeBox(2 * sx, SLEEVE_Y[1] - SLEEVE_Y[0], sz[1] - sz[0],
                          V(-sx, SLEEVE_Y[0], sz[0])))
tidy = sh.removeSplitter()
try:
    tidy.check(True)
    sh = tidy
except Exception:
    pass
assert len(sh.Solids) == 1, "the cap did not join the hub (%d solids)" % len(sh.Solids)
pz = zspan(JOINT_Z - RAIL_HZ - FIT, JOINT_Z + RAIL_HZ + FIT)
sh = sh.cut(Part.makeBox(2 * (RAIL_HX + FIT), RAIL_Y[1] - SLEEVE_Y[0], pz[1] - pz[0],
                         V(-(RAIL_HX + FIT), SLEEVE_Y[0], pz[0])))
for wy in WINDOW_Y:
    sh = sh.cut(Part.makeBox(2 * sx + 4, wy[1] - wy[0], pz[1] - pz[0], V(-sx - 2, wy[0], pz[0])))
    sh = sh.cut(Part.makeBox(2 * (RAIL_HX + FIT), wy[1] - wy[0], sz[1] - sz[0] + 4,
                             V(-(RAIL_HX + FIT), wy[0], sz[0] - 2)))
# the leading corner, which sweeps at the knee
nz = zspan(JOINT_Z + 8.0, JOINT_Z + RAIL_HZ + FIT + CHEEK + 1.0)
sh = sh.cut(Part.makeBox(2 * sx + 2.0, 12.0, nz[1] - nz[0], V(-sx - 1.0, SLEEVE_Y[1] - 10.0, nz[0])))
print("  cap   X +-%.1f, Z %.1f..%.1f (%.1f mm walls, %.1f cheeks), Y %.0f..%.0f"
      % (sx, sz[0], sz[1], WALL, CHEEK, SLEEVE_Y[0], SLEEVE_Y[1]))

tools = []
for y in BOLT_Z_Y:
    tools.append(Part.makeCylinder(M5 / 2.0, 70.0, V(0.0, y, z(JOINT_Z - 35.0)), V(0, 0, sgn)))
for y in BOLT_X_Y:
    tools.append(Part.makeCylinder(M5 / 2.0, 80.0, V(-40.0, y, z(JOINT_Z)), V(1, 0, 0)))
for t in tools:
    sh = sh.cut(t)
    a4.Shape = a4.Shape.cut(t)
for x in (-CORE_X, CORE_X):
    sh = sh.cut(Part.makeCylinder(M5 / 2.0, 22.0, V(x, SLEEVE_Y[1] + 2.0, z(JOINT_Z)), V(0, -1, 0)))
sh.check(True)
assert len(sh.Solids) == 1, "the hub came out as %d solids" % len(sh.Solids)
p2a.Shape = sh
a4.Shape.check(True)
print("  bolts %d through cap and rail, plus 2 axial into the 2040's cell cores at X +-%.0f"
      % (len(tools), CORE_X))

# ---------------------------------------------------------------- the socket, rebuilt round it
s6 = p6.Shape
v6 = s6.Volume
by = s6.BoundBox
outer_x = abs(by.XMax)
old_holes = sorted({(round(f.Surface.Center.x, 1), round(f.Surface.Center.y, 1))
                    for f in s6.Faces
                    if f.Surface.TypeId == "Part::GeomCylinder"
                    and 4.0 <= 2 * f.Surface.Radius <= 4.4 and abs(f.Surface.Axis.z) > 0.9})

# ONE FUSE, NOT SIX. Chaining boolean after boolean onto a 160 cm3 shape with 300 faces produced
# "Unorientable shape" twice; assembling the addition out of plain boxes first and fusing it once
# does not. Same for the removals. removeSplitter is left out of this part entirely -- it has
# corrupted solids in this model four times.
wz = zspan(SOCK_WALL_Z[0], SOCK_WALL_Z[1])
tz = zspan(JOINT_Z + RAIL_HZ + 0.5, JOINT_Z + RAIL_HZ + 4.0)
add = Part.makeBox(outer_x - (RAIL_HX + 0.5), by.YLength, wz[1] - wz[0],
                   V(RAIL_HX + 0.5, by.YMin, wz[0]))
add = add.fuse(Part.makeBox(outer_x - (RAIL_HX + 0.5), by.YLength, wz[1] - wz[0],
                            V(-outer_x, by.YMin, wz[0])))
# the tie across the top: the walls stand at X 20.5..30 and the block carrying the KX-1 interface
# ends at X 20, so without this they pass each other without touching and it floats off alone
add = add.fuse(Part.makeBox(2 * outer_x, by.YLength, tz[1] - tz[0], V(-outer_x, by.YMin, tz[0])))
s6 = s6.fuse(add)
assert len(s6.Solids) == 1, "adding the socket walls gave %d solids" % len(s6.Solids)

npz = zspan(JOINT_Z - RAIL_HZ - 0.5, JOINT_Z + RAIL_HZ + 0.5)
s6 = s6.cut(Part.makeBox(2 * (RAIL_HX + 0.5), by.YLength + 4.0, npz[1] - npz[0],
                         V(-(RAIL_HX + 0.5), by.YMin - 2.0, npz[0])))
assert len(s6.Solids) == 1, "the 2040 pocket split the socket into %d" % len(s6.Solids)

# fill the old clamp holes where material remains, below the pocket and above it
fill = None
for (hx, hy) in old_holes:
    # EXACTLY the socket's own envelope. Overshooting by 1 mm at each end put 0.056 cm3 of
    # P6 inside P31 and 0.028 inside the cuff -- both found by the sweep, both invisible here.
    for lo, hi in ((by.ZMin, npz[0]), (npz[1], by.ZMax)):
        if hi - lo <= 0.1:
            continue
        c = Part.makeCylinder(M4 / 2.0, hi - lo, V(hx, hy, lo), V(0, 0, 1))
        fill = c if fill is None else fill.fuse(c)
if fill is not None:
    s6 = s6.fuse(fill)

drill = None
for (hx, hy) in old_holes:
    nx = SOCK_BOLT_X if hx > 0 else -SOCK_BOLT_X
    c = Part.makeCylinder(M4 / 2.0, by.ZLength + 6.0, V(nx, hy, by.ZMin - 3.0), V(0, 0, 1))
    drill = c if drill is None else drill.fuse(c)
s6 = s6.cut(drill)
s6.check(True)
assert len(s6.Solids) == 1, "the socket came out as %d solids" % len(s6.Solids)
p6.Shape = s6
print("  sock  walls X +-(%.1f..%.0f) + tie, pocket X +-%.1f Z %.1f..%.1f, %d bolts %s -> |X| %.0f"
      % (RAIL_HX + 0.5, outer_x, RAIL_HX + 0.5, npz[0], npz[1], len(old_holes),
         "/".join(sorted({"%.0f" % abs(h[0]) for h in old_holes})), SOCK_BOLT_X))
print("  sock  %.1f -> %.1f cm3" % (v6 / 1000.0, s6.Volume / 1000.0))

# ---------------------------------------------------------------- the bolts, for the wider cap
# 430 drew these for a cap +-14.5 wide. The 2040's cap is +-24.8, so the cross bolts stopped
# inside the rail instead of passing through it -- 0.239 cm3 of bolt buried in aluminium, which
# the sweep reported as a clash and which would have been four bolts that cannot be fitted.
hwb = doc.getObject("HW_JointBolts")
if hwb is not None:
    heads = None
    for y in BOLT_Z_Y:
        c = Part.makeCylinder(M5 / 2.0, (sz[1] - sz[0]) + 8.0, V(0.0, y, sz[0] - 4.0), V(0, 0, 1))
        heads = c if heads is None else heads.fuse(c)
    for y in BOLT_X_Y:
        c = Part.makeCylinder(M5 / 2.0, 2 * sx + 8.0, V(-sx - 4.0, y, z(JOINT_Z)), V(1, 0, 0))
        heads = heads.fuse(c)
    for x in (-CORE_X, CORE_X):
        heads = heads.fuse(Part.makeCylinder(M5 / 2.0, 26.0, V(x, SLEEVE_Y[1], z(JOINT_Z)),
                                             V(0, -1, 0)))
    hwb.Shape = heads
    hwb.Label = "HW_ShankBolts_6xM5"
    print("  hw    %d bolts redrawn to suit the +-%.1f cap" % (len(BOLT_Z_Y) + len(BOLT_X_Y) + 2, sx))

# ---------------------------------------------------------------- and the socket is overbuilt
# 105 of its 186 cm3 sat above the rail as a solid block, and the only thing up there is
# P31_InterfaceDist's eight fixings in the top face. Most of that block is my doing: moving the
# pocket down meant filling the old channel, and a fill is solid. Hollow it, and take the top
# plate back to the interface's own footprint instead of the socket's full length.
s6 = p6.Shape
v_before = s6.Volume
pb31 = doc.getObject("P31_InterfaceDist")
TOP = s6.BoundBox.ZMax
PLATE = 11.0                    # enough for a 6.4 insert and a 5.0 dowel from the top face
# The block above the rail is not hollowed, it is REMOVED: once the top comes off at the roof
# there is nothing up there to hollow. An earlier version did both, and the hollow's floor at
# 97.5 left a half-millimetre dip in the middle of the new top face -- which 502 then measured
# as the face and seated the interface plate 0.5 mm into the socket.
roof = npz[1] + 3.5
s6 = s6.cut(Part.makeBox(2 * outer_x + 4.0, by.YLength + 4.0, (TOP + 4.0) - roof,
                         V(-outer_x - 2.0, by.YMin - 2.0, roof)))
s6.check(True)
assert len(s6.Solids) == 1, "lightening the socket gave %d solids" % len(s6.Solids)
p6.Shape = s6
print("  sock  closed over the rail at Z %.1f instead of %.1f: %.1f -> %.1f cm3"
      % (roof, TOP, v_before / 1000.0, s6.Volume / 1000.0))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- verify
print()
print("  VERIFICATION")
fail = []
for a, b, lbl in ((p2a, a4, "hub vs rail"), (p2a, p6, "hub vs socket"), (a4, p6, "rail vs socket"),
                  (a4, doc.getObject("REF_Shank"), "rail vs the limb"),
                  (p6, doc.getObject("REF_Shank"), "socket vs the limb"),
                  (a4, doc.getObject("P7_ShankCuff"), "rail vs cuff"),
                  (p2a, doc.getObject("P1_KneeYoke"), "hub vs yoke")):
    if b is None:
        continue
    c = a.Shape.common(b.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("     %-22s %8.3f cm3 %s" % (lbl, v, "" if v <= 0.02 else "<-- CLASH"))
    if v > 0.02:
        fail.append("%s overlap %.3f cm3" % (lbl, v))
shroud = doc.getObject("P20_KneeShroud")
if shroud is not None:
    worst, wth = 0.0, 0.0
    for i in range(27):
        th = 104.0 * i / 26.0
        r = p2a.Shape.copy()
        r.rotate(V(0, 0, 0), V(0, 0, 1), th)
        c = r.common(shroud.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > worst:
            worst, wth = v, th
    print("     %-22s %8.3f cm3 at %+.0f deg %s"
          % ("cap vs shroud, swept", worst, wth, "" if worst <= 0.02 else "<-- CLASH"))
    if worst > 0.02:
        fail.append("cap sweeps into the shroud: %.3f cm3 at %+.0f" % (worst, wth))
# hollowing is only safe if everything that bolts to the socket still has metal to bite
if pb31 is not None:
    short = []
    for f in pb31.Shape.Faces:
        sf = f.Surface
        if sf.TypeId != "Part::GeomCylinder" or abs(sf.Axis.z) < 0.9:
            continue
        if not (3.8 <= 2 * sf.Radius <= 6.6):
            continue
        ln = Part.makeLine(V(sf.Center.x, sf.Center.y, z(60.0)), V(sf.Center.x, sf.Center.y, z(140.0)))
        k = p6.Shape.common(ln)
        depth = 0.0
        if not k.isNull() and k.Vertexes:
            zs = [vv.Point.z for vv in k.Vertexes]
            depth = max(zs) - min(zs)
        if depth < 8.0:
            short.append((sf.Center.x, sf.Center.y, 2 * sf.Radius, depth))
    print("     %-22s %d of the interface's fixings have under 8 mm of socket to bite"
          % ("P31 fixings", len(short)))
    for (hx, hy, dd, depth) in short[:6]:
        print("        dia %.1f at (%.0f, %.0f): only %.1f mm" % (dd, hx, hy, depth))
    if short:
        fail.append("%d of P31's fixings lost their depth to the hollow" % len(short))
span = abs(BOLT_Z_Y[0] - BOLT_Z_Y[1])
bear = (TORQUE / span) / 2.0 / (5.0 * CHEEK)
print("     %-22s %8.1f MPa %s" % ("cheek bearing", bear, "" if bear < PETG_BEAR else "<-- OVER"))
if bear > PETG_BEAR:
    fail.append("cheek bearing %.1f MPa" % bear)
print()
if fail:
    for x in fail:
        print("  FAIL %s" % x)
else:
    print("  the shank is a 2040 on the knee's own plane, the hub caps its end, and the socket")
    print("  wraps it on walls that clear the rail instead of walls that were inside it.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
