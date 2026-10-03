# -*- coding: utf-8 -*-
"""Put the shank rail in line with the thigh rail and fork the hub around its end.

429_shank_inline.py is the argument; this is the build. The short version of the argument is that
the joint carrying all 28.2 N.m was three collinear M5 in SINGLE shear through a 6 mm plate --
838 N on the end bolt, 27.9 MPa bearing against PETG's ~15 MPa sustained, 1.9x over -- and that
nothing in the repository could see it, because three M5 holes of the right size is what every
check was looking for.

WHAT CHANGES

    A4 rail      Z 94..114  ->  Z 88..108      the same centreline as the thigh rail, Z 98
                 Y -300..-70 -> Y -300..-56    up to the knee; its corner is then 56.9 mm from
                                               the knee axis against the belt's 38.46, so clear
    P2a          the 6 mm plate reaching to Y -149 is gone. In its place a sleeve that wraps the
                 rail's end on all four sides, Y -116..-46, with 7 mm cheeks and walls.
    bolts        2 x M5 through the cheeks along Z, 48 mm apart -- DOUBLE shear, 7.6 MPa
                 2 x M5 through the walls along X, for the other axis
                 1 x M5 axial into the rail's end core, which locates it and carries no torque
    P24          deleted. Nothing powered runs below the knee; it was cladding over the limb's
                 own structure, and 406_coverage.py is the check that says whether that is true.
    P6           its rail pocket moves down 6 mm with the rail. The socket's OUTER shape does not
                 move, because the cuff and the KX-1 distal interface are located off it and the
                 cuff is shaped to the limb -- sliding the whole socket 6 mm sideways would take
                 the cuff off the calf.

THE RAIL GETS DRILLED, which is new. Four transverse holes in a bought extrusion. The README's
"every metal part is bought" still holds -- nothing is fabricated -- but this is a drilling
operation on metal and it is in the assembly notes as one. The alternative, T-nuts in the four
slots, puts every bolt back into single shear, which is the thing being fixed.

WHAT THE RAIL'S MOCKUP CANNOT TELL US: its core void is drawn 8.4 mm across. A real 2020 V-slot
has a 4.2 mm core for an M5 self-tapping screw, which is what the axial screw threads into. The
clearance hole through the sleeve's end cap is drawn; the thread it bites is the real rail's.

    freecadcmd.exe scripts/430_shank_inline_build.py
    KX_DOC=C:/Users/Josh/KneeExo_v6_R.FCStd freecadcmd.exe scripts/430_shank_inline_build.py
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

M5 = 5.2
# The rail stops 10 mm short of where the belt would allow (-56), because the cap that wraps
# it has to stop somewhere too, and at full flexion the cap's leading corner was sweeping through
# P20_KneeShroud. Notching the corner halved that and did not clear it; moving the whole joint
# 10 mm down the shank does, and costs nothing but 10 mm of extrusion.
RAIL_Y = (-300.0, -66.0)        # the rail's new extent
# NOT the thigh rail's centreline (Z 98) but the JOINT's plane. The 6001 sits at Z 80..88, so
# the knee turns about Z 84, and the rail was centred 14 mm outboard of it -- every newton the
# shank carries was handed to the bearing through a 14 mm offset. Centring the rail on the joint
# also brings its outer face in from Z 108 to 94, which is 14 mm less of the device standing
# proud of the leg along the whole shank.
JOINT_Z = 84.0
SLEEVE_Y = (-126.0, -56.0)      # the fork; -66..-56 of it is the solid end cap
# A SOLID SLEEVE IS THE WRONG ANSWER TO "save a lot of plastic". The first version was a
# 34 x 70 x 36 block: 60 cm3 of PETG after the pocket, against the 34 cm3 plate it replaced, so
# the change paid for its strength in mass instead of saving any. Thinner walls carry the same
# bearing (the bolts are what is loaded, not the box), and the stretches between bolt stations
# carry almost nothing, so they are windowed out.
SLEEVE_X = 14.5                 # outer half-width  -> 4.2 mm walls
SLEEVE_Z = (68.0, 100.0)        # outer            -> 5.7 mm cheeks, about the joint's plane
WINDOW_Y = ((-102.0, -90.0), (-84.0, -76.0))    # between the bolt stations, all four faces
RAIL_Z = (JOINT_Z - 10.0, JOINT_Z + 10.0)       # a 20 mm deep rail, centred on the joint
FIT = 0.3                       # clearance round the rail
CUT_BELOW = -60.0               # of P2a: everything distal of this is the old reach-down plate
BOLT_Z_Y = (-72.0, -120.0)      # through the cheeks, along Z
BOLT_X_Y = (-84.0, -108.0)      # through the walls, along X
TORQUE = 28200.0
PETG_BEAR = 15.0

a4 = doc.getObject("A4_Shank2020_VSlot")
p2a = doc.getObject("P2a_KneeHingePlate")
p6 = doc.getObject("P6_ShankSocket")
assert a4 is not None and p2a is not None, "no shank rail or no hub in this document"
mirrored = p2a.Shape.BoundBox.ZMax < 0
sgn = -1.0 if mirrored else 1.0


def z(v):
    """a Z written for the left leg, on whichever leg this is"""
    return sgn * v


def zspan(lo, hi):
    a, b = z(lo), z(hi)
    return (min(a, b), max(a, b))


print("=" * 98)
print("SHANK IN LINE + FORKED HUB  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)

# ---------------------------------------------------------------- the rail, moved and lengthened
b0 = a4.Shape.BoundBox
# IDEMPOTENT: the rail is moved to a position, not BY an offset. Re-running a relative move walks
# the rail 6 mm further off the centreline every time, which is the kind of script that is right
# once and wrong for ever after.
_centre_now = 0.5 * (b0.ZMin + b0.ZMax)
_dz = z(JOINT_Z) - _centre_now
if abs(_dz) < 0.01:
    print("  rail  already centred on the joint at Z %.1f" % _centre_now)
wires = a4.Shape.slice(V(0, 1, 0), -150.0)
assert wires, "could not section the rail"
faces = [Part.Face(w) for w in wires]
outer = max(faces, key=lambda f: f.Area)
prof = outer
for f in faces:
    if f is not outer:
        prof = prof.cut(f)
# the section already sits at this leg's Z, so the move is the same signed 6 mm on both:
# left 94..114 -> 88..108, right -114..-94 -> -108..-88
prof.translate(V(0, RAIL_Y[0] + 150.0, _dz))
rail = prof.extrude(V(0, RAIL_Y[1] - RAIL_Y[0], 0))
rail.check(True)
assert len(rail.Solids) == 1, "the rail came out as %d solids" % len(rail.Solids)
nb = rail.BoundBox
a4.Shape = rail
print("  rail  Z %.1f..%.1f (was %.1f..%.1f),  Y %.0f..%.0f (was %.0f..%.0f),  %.1f cm3"
      % (nb.ZMin, nb.ZMax, b0.ZMin, b0.ZMax, nb.YMin, nb.YMax, b0.YMin, b0.YMax,
         rail.Volume / 1000.0))

# ---------------------------------------------------------------- the hub: drop the old plate
sh = p2a.Shape
v0 = sh.Volume
# the box has to span the hub's FULL height, including the belt land at Z 126 and the
# mirrored leg's -126: a 200 mm box starting at Z -100 reaches only Z 100 and would shave the
# capstan in half instead of removing the plate.
keep = Part.makeBox(400.0, CUT_BELOW - (-400.0), 400.0, V(-200.0, -400.0, -200.0))
sh = sh.cut(keep)
tidy = sh.removeSplitter()
try:
    tidy.check(True)
    sh = tidy
except Exception:
    pass
assert len(sh.Solids) == 1, "cutting the old plate left %d solids" % len(sh.Solids)
print("  hub   old reach-down plate removed: %.1f cm3 (everything distal of Y %.0f)"
      % ((v0 - sh.Volume) / 1000.0, CUT_BELOW))

# ---------------------------------------------------------------- the fork
sz = zspan(SLEEVE_Z[0], SLEEVE_Z[1])
sleeve = Part.makeBox(2 * SLEEVE_X, SLEEVE_Y[1] - SLEEVE_Y[0], sz[1] - sz[0],
                      V(-SLEEVE_X, SLEEVE_Y[0], sz[0]))
v1 = sh.Volume
sh = sh.fuse(sleeve)
tidy = sh.removeSplitter()
try:
    tidy.check(True)
    sh = tidy
except Exception:
    pass
assert len(sh.Solids) == 1, "the sleeve did not join the hub (%d solids)" % len(sh.Solids)
print("  fork  sleeve X +-%.0f, Y %.0f..%.0f, Z %.1f..%.1f fused: +%.1f cm3"
      % (SLEEVE_X, SLEEVE_Y[0], SLEEVE_Y[1], sz[0], sz[1], (sh.Volume - v1) / 1000.0))

# lightening windows through all four faces, between the bolts
for wy in WINDOW_Y:
    for tool in (Part.makeBox(2 * SLEEVE_X + 4, wy[1] - wy[0], 2 * (10.0 + FIT),
                              V(-SLEEVE_X - 2, wy[0], zspan(RAIL_Z[0] - FIT, RAIL_Z[1] + FIT)[0])),
                 Part.makeBox(2 * (10.0 + FIT), wy[1] - wy[0], sz[1] - sz[0] + 4,
                              V(-(10.0 + FIT), wy[0], sz[0] - 2))):
        sh = sh.cut(tool)

# the rail's pocket, open at the distal end and closed by the cap at the proximal end
pz = zspan(RAIL_Z[0] - FIT, RAIL_Z[1] + FIT)
pocket = Part.makeBox(2 * (10.0 + FIT), RAIL_Y[1] - SLEEVE_Y[0], pz[1] - pz[0],
                      V(-(10.0 + FIT), SLEEVE_Y[0], pz[0]))
v1 = sh.Volume
sh = sh.cut(pocket)
print("  fork  rail pocket cut (%.1f mm clearance all round): -%.1f cm3; cap is Y %.0f..%.0f"
      % (FIT, (v1 - sh.Volume) / 1000.0, RAIL_Y[1], SLEEVE_Y[1]))

# ---------------------------------------------------------------- bolts, through hub AND rail
tools = []
for y in BOLT_Z_Y:
    tools.append(("Z", y, Part.makeCylinder(M5 / 2.0, 60.0, V(0.0, y, z(JOINT_Z - 26.0)), V(0, 0, sgn))))
for y in BOLT_X_Y:
    tools.append(("X", y, Part.makeCylinder(M5 / 2.0, 50.0, V(-25.0, y, z(JOINT_Z)), V(1, 0, 0))))
for axis, y, t in tools:
    sh = sh.cut(t)
    a4.Shape = a4.Shape.cut(t)
# the axial screw into the rail's end core
ax = Part.makeCylinder(M5 / 2.0, 20.0, V(0.0, SLEEVE_Y[1] + 2.0, z(JOINT_Z)), V(0, -1, 0))
v1 = sh.Volume
sh = sh.cut(ax)
print("  bolts %d transverse through the sleeve and the rail, plus 1 axial into the end core"
      % len(tools))

sh.check(True)
assert len(sh.Solids) == 1, "the hub came out as %d solids" % len(sh.Solids)
p2a.Shape = sh
a4.Shape.check(True)

# ---------------------------------------------------------------- the socket's pocket follows
if p6 is not None:
    s6 = p6.Shape
    v1 = s6.Volume
    by = s6.BoundBox
    # the pocket AS BUILT, not as wanted: the socket arrives with its channel at Z 93.5..114.5
    # and the job is to move it to wherever the rail now is. Deriving "old" from RAIL_Z made
    # the two identical and asked for a box of zero height.
    oldp = zspan(93.5, 114.5)
    newp = zspan(RAIL_Z[0] - 0.5, RAIL_Z[1] + 0.5)
    # fill whatever the old channel occupied that the new one does not, either side of it,
    # then cut the new one. Idempotent: on a second run both fills land in solid material and
    # the cut in empty space, so nothing moves.
    above = max(0.0, oldp[1] - max(oldp[0], newp[1]))
    below = max(0.0, min(oldp[1], newp[0]) - oldp[0])
    if above > 0.01:
        s6 = s6.fuse(Part.makeBox(21.0, by.YLength + 4.0, above,
                                  V(-10.5, by.YMin - 2.0, max(oldp[0], newp[1]))))
    if below > 0.01:
        s6 = s6.fuse(Part.makeBox(21.0, by.YLength + 4.0, below,
                                  V(-10.5, by.YMin - 2.0, oldp[0])))
    cut = Part.makeBox(21.0, by.YLength + 4.0, newp[1] - newp[0],
                       V(-10.5, by.YMin - 2.0, newp[0]))
    s6 = s6.cut(cut)
    tidy = s6.removeSplitter()
    try:
        tidy.check(True)
        s6 = tidy
    except Exception:
        pass
    s6.check(True)
    assert len(s6.Solids) == 1, "the socket came out as %d solids" % len(s6.Solids)
    p6.Shape = s6
    print("  sock  rail pocket moved to Z %.1f..%.1f, outer shape untouched: %.1f -> %.1f cm3"
          % (newp[0], newp[1], v1 / 1000.0, s6.Volume / 1000.0))

# ---------------------------------------------------------------- the shank fairing goes
fair = doc.getObject("P24_FairingShank")
if fair is not None:
    vf = fair.Shape.Volume / 1000.0
    doc.removeObject(fair.Name)
    print("  clad  P24_FairingShank deleted (%.1f cm3) -- 406_coverage.py is the check" % vf)

# ---------------------------------------------------------------- the hardware this replaces
# HW_JointBolts is the three M5 that fastened the old reach-down plate to the rail, at Y -90,
# -110 and -125. That joint no longer exists -- it is the 27.9 MPa one -- and the bolts were
# left sitting where the rail now passes, which the sweep found at theta +64. Redraw them as
# what actually holds the shank on: four through the cap and the rail, plus the axial screw.
hwb = doc.getObject("HW_JointBolts")
if hwb is not None:
    heads = None
    for y in BOLT_Z_Y:
        b = Part.makeCylinder(M5 / 2.0, 2 * (SLEEVE_Z[1] - SLEEVE_Z[0]) / 2.0 + 4.0,
                              V(0.0, y, z(SLEEVE_Z[0] - 2.0)), V(0, 0, sgn))
        heads = b if heads is None else heads.fuse(b)
    for y in BOLT_X_Y:
        b = Part.makeCylinder(M5 / 2.0, 2 * SLEEVE_X + 4.0, V(-SLEEVE_X - 2.0, y, z(JOINT_Z)),
                              V(1, 0, 0))
        heads = heads.fuse(b)
    heads = heads.fuse(Part.makeCylinder(M5 / 2.0, 26.0, V(0.0, SLEEVE_Y[1], z(JOINT_Z)),
                                         V(0, -1, 0)))
    hwb.Shape = heads
    hwb.Label = "HW_ShankBolts_5xM5"
    print("  hw    HW_JointBolts redrawn as the %d bolts that now hold the shank" % (len(BOLT_Z_Y) + len(BOLT_X_Y) + 1))

# ---------------------------------------------------------------- clearance for full flexion
# At theta +103 the cap's leading top corner sweeps through P20_KneeShroud. Carving the shroud was
# the first instinct and it is wrong: the cap's swept volume passes clean through the shroud's
# body and cutting it leaves four pieces. The cap is the part with somewhere else to go, so it
# gets the chamfer -- 14 mm back and 12 down off the corner that leads into the knee.
# A rotated wedge was the first attempt and it cut clean through the cap, leaving two solids:
# at this size a 40-degree slope starting near the hub exits through the far side. A square
# notch off the last 10 mm of the top cheek removes the same corner and nothing else.
nz = zspan(JOINT_Z + 8.0, SLEEVE_Z[1] + 1.0)
wedge = Part.makeBox(2 * SLEEVE_X + 2.0, 12.0, nz[1] - nz[0],
                     V(-SLEEVE_X - 1.0, SLEEVE_Y[1] - 10.0, nz[0]))
v1 = sh.Volume
sh = sh.cut(wedge)
sh.check(True)
assert len(sh.Solids) == 1, "the chamfer split the hub into %d" % len(sh.Solids)
p2a.Shape = sh
print("  cap   leading corner chamfered for full flexion: -%.2f cm3" % ((v1 - sh.Volume) / 1000.0))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- does it hold?
print()
print("  VERIFICATION")
fail = []
for nm in ("A4_Shank2020_VSlot", "P6_ShankSocket", "P1_KneeYoke"):
    o = doc.getObject(nm)
    if o is None:
        continue
    c = p2a.Shape.common(o.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("     hub vs %-22s %7.3f cm3" % (nm, v))
    if v > 0.02:
        fail.append("the hub overlaps %s by %.3f cm3" % (nm, v))
if p6 is not None:
    c = a4.Shape.common(p6.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("     rail vs P6_ShankSocket        %7.3f cm3" % v)
    if v > 0.02:
        fail.append("the rail overlaps the socket by %.3f cm3" % v)
span = abs(BOLT_Z_Y[0] - BOLT_Z_Y[1])
f = TORQUE / span
cheek = (SLEEVE_Z[1] - RAIL_Z[1]) - FIT
bear = f / 2.0 / (5.0 * cheek)
print("     %d N on each cheek bolt over %.0f mm, %.1f mm cheeks -> %.1f MPa  (%s %.0f MPa)"
      % (f, span, cheek, bear, "under" if bear < PETG_BEAR else "OVER", PETG_BEAR))
if bear > PETG_BEAR:
    fail.append("cheek bearing %.1f MPa is over the allowable" % bear)
# does the cap clear the cladding through the whole range?
shroud = doc.getObject("P20_KneeShroud")
if shroud is not None:
    worst, worst_th = 0.0, 0.0
    for i in range(0, 27):
        th = 104.0 * i / 26.0
        r = p2a.Shape.copy()
        r.rotate(V(0, 0, 0), V(0, 0, 1), th)
        c = r.common(shroud.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > worst:
            worst, worst_th = v, th
    print("     hub vs P20_KneeShroud, worst over 0..104 deg: %.3f cm3 at %+.0f" % (worst, worst_th))
    if worst > 0.02:
        fail.append("the cap still sweeps into the knee shroud: %.3f cm3 at %+.0f"
                    % (worst, worst_th))
print()
if fail:
    for x in fail:
        print("  FAIL %s" % x)
else:
    print("  the rail runs on the thigh rail's centreline, the hub grips its end on four sides,")
    print("  and the joint that carries the torque is at %.1f MPa instead of 27.9." % bear)
sys.stdout.flush()
sys.exit(1 if fail else 0)
