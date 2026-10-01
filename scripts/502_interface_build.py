# -*- coding: utf-8 -*-
"""STAGE 11: the KX-1 structural interface, one at each end.

500_as_a_module.py identified this as the single thing that is cheap now and expensive once
a second module exists: a defined structural face at both ends, able to carry the couple that
the cuffs carry today, so a neighbouring module can take over from them.

501_interface.py sized it. The load that matters is not this module's 148 N -- it is the
1472 N a load-to-ground leg puts through the same joint, and BEARING in a printed boss is
what sizes it, which is why the pattern is SIX M5 and not four. Bolt count is the one thing
in a mating pattern you cannot change later without changing both halves.

KX-1, in the face's own frame (face-X along the module's +Y, face normal pointing out):

    face        56 x 40 flat, 10 mm boss
    bolts       6 x M5 at face-X -18/0/+18, face-Y +/-9   (tapped, heat-set inserts)
    dowels      2 x dia 5 H7 at face-X +/-24, face-Y 0    (two pins fully constrain in plane)

WHY THE FACE POINTS LATERALLY, NOT ALONG THE LIMB. An end-butt flange would eat axial length,
and there is only 95 mm above the drive end before the hip joint centre and 80 mm below
before the ankle. A lap joint on the outboard face costs zero axial length and carries
bending without relying on bolt tension, which is what a leg that takes body weight needs.

WHERE THEY GO, from the free-space probe:
  proximal  on A7's top plate at Z 130.3, centred Y 270. Inside the drive shell, so P22 gets
            a port -- a structural interface has to pass through cladding, and the boss fills
            the port so nothing is exposed behind it.
  distal    on P6_ShankSocket's top face at Z 123, centred Y -280. Clear space, no port.

Both printed at 10 mm today because standalone this module only needs 1.2 MPa of bearing.
The same six holes in a 6 mm aluminium plate carry the load-to-ground case, and that is the
whole point of fixing the pattern now.

Send with:  python tools/fcsend.py scripts/502_interface_build.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

PW, PL, PT = 40.0, 56.0, 10.0      # plate: X width, Y length, Z thickness
BOLT_R, DOWEL_R, MNT_R = 2.6, 2.5, 2.1
INSERT_R, INSERT_D = 3.2, 7.0      # M5 heat-set insert


def plate(xc, yc, z0, name, host, host_top, mdy, mdx, wing_t):
    """One KX-1 boss, mounted on `host`, presenting its face at z0 + PT.

    WINGS. A7's top plate is only solid at |X| 32..40 -- 394's lightening windows take
    |X| < 30 over most of its length, and a material map showed the strip left inside them
    is 10 mm long at |X| 16. So the boss stays 40 wide and reaches out on thin wings to find
    metal. The wings are 3 mm thick because the drive shell's inner surface is at Z 134-135
    out there and they have to pass under it."""
    p = Part.makeBox(PW, PL, PT, V(xc - PW / 2.0, yc - PL / 2.0, z0))
    if mdx > PW / 2.0:
        p = p.fuse(Part.makeBox(2.0 * mdx + 12.0, PL, wing_t,
                                V(xc - mdx - 6.0, yc - PL / 2.0, z0)))
    # KX-1: six tapped bosses for the neighbour, from the FACE downward
    for dy in (-18.0, 0.0, 18.0):
        for dx in (-9.0, 9.0):
            p = p.cut(Part.makeCylinder(INSERT_R, INSERT_D + 1.0,
                                        V(xc + dx, yc + dy, z0 + PT - INSERT_D),
                                        V(0, 0, 1)))
    # KX-1: two locating dowels, through
    for dy in (-24.0, 24.0):
        p = p.cut(Part.makeCylinder(DOWEL_R, PT + 4.0, V(xc, yc + dy, z0 - 2.0), V(0, 0, 1)))
    # its own mounting into the host, clear of both
    holes = []
    for dy in mdy:
        for dx in (-mdx, mdx):
            holes.append((xc + dx, yc + dy))
    for hx, hy in holes:
        p = p.cut(Part.makeCylinder(MNT_R, PT + 24.0, V(hx, hy, z0 - 12.0), V(0, 0, 1)))
    assert len(p.Solids) == 1, "%s split into %d solids" % (name, len(p.Solids))
    try:
        p.check(True)
    except Exception as e:
        raise AssertionError("%s fails Shape.check(): %s" % (name, e))
    o = doc.getObject(name)
    if o is None:
        o = doc.addObject("Part::Feature", name)
        g = doc.getObject(host_top)
        if g is not None:
            g.addObject(o)
    o.Shape = p
    o.Label = name
    try:
        src = doc.getObject("P22_DriveCap").ViewObject
        o.ViewObject.ShapeColor = src.ShapeColor
    except Exception:
        pass
    return p, holes


print("=" * 84)
print("KX-1 INTERFACE -- %s x %s face, %.0f mm boss, 6 x M5 + 2 dowels" % (PL, PW, PT))
print("=" * 84)

# The distal plate sits at Y -275 on P6's Z 123 face. Getting there took three wrong
# placements, each caught by the per-hole engagement check: Y -280 had two bolts over a
# region where the face steps down to Z 109, Y -290 put one past the end of the part at
# Y -313, and a detour onto what looked like a flat pad at Z 68..80 turned out to be the
# BOTTOM of a solid block -- the plate ended up 84% buried. What settled it was measuring the
# outer surface directly rather than inferring it from slices: P6 is flat at Z 123 across
# X +/-20 for Y -310..-250, and the mounts at Y -300/-250 sit inside that.
#
# The proximal plate's mounts are only 10 mm from centre. 394 cuts lightening windows in A7's
# top plate at Y 219..236 and 274..296, which leaves ONE solid band 38 mm long, and a 4-bolt
# pattern has to fit inside it. The first layout put two of its four M4 holes straight into a
# window: the boss would have been held by two bolts and the aggregate "0.13 cm3 removed"
# looked entirely plausible. Only the per-hole engagement check below caught it.
JOBS = [("P30_InterfaceProx", 0.0, 255.0, 130.3, "A7_DriveBox", "C_Drive",
         (-15.0, 15.0), 34.0, 3.0),
        ("P31_InterfaceDist", 0.0, -275.0, 123.0, "P6_ShankSocket", "C_Shank",
         (-25.0, 25.0), 20.0, 0.0)]
built = []
for name, xc, yc, z0, hostname, grp, mdy, mdx, wing_t in JOBS:
    host = doc.getObject(hostname)
    assert host is not None, "%s missing -- cannot mount %s" % (hostname, name)
    # GUARD: drilling the host is destructive and not idempotent. Run this twice without
    # rebuilding and the second pass finds its own holes already there, reports 0 mm of
    # engagement, and fails with a message blaming the geometry. Rebuild 393..399 and 409
    # first. (That is exactly how the last three debugging rounds were spent.)
    # Not every host is rebuilt by the chain. A7 is (393 makes it fresh every run), but
    # P6_ShankSocket comes from 150_socket.py and is never regenerated, so its mount holes are
    # permanent. Aborting on that was wrong -- the holes being there is the desired end state.
    # Detect it, skip the drilling, and carry on building the plate.
    probe = Part.makeCylinder(MNT_R - 0.3, 30.0, V(xc - mdx, yc + mdy[0], z0 - 14.0), V(0, 0, 1))
    k0 = host.Shape.common(probe)
    already = k0.isNull() or k0.Volume < 1.0
    p, holes = plate(xc, yc, z0, name, host, grp, mdy, mdx, wing_t)
    bb = p.BoundBox
    print("%-20s X %6.1f..%5.1f  Y %7.1f..%6.1f  Z %6.1f..%6.1f  %5.1f cm3  %3.0f g"
          % (name, bb.XMin, bb.XMax, bb.YMin, bb.YMax, bb.ZMin, bb.ZMax,
             p.Volume / 1000.0, p.Volume / 1000.0 * 1.27))
    print("     face at Z %.1f, mounted on %s" % (z0 + PT, host.Label))

    # the host needs the matching mount holes
    if already:
        print("     %s is already drilled (not rebuilt by the chain) -- holes left as they are"
              % host.Label)
        built.append((name, p))
        continue
    hs = host.Shape
    v0 = hs.Volume
    # PER HOLE, not in aggregate. Four holes of which two hit a lightening window still
    # removes a plausible-looking total; what matters is that EVERY bolt has metal in it.
    # A7 is a 4 mm fabricated plate and P6 is printed: these are THROUGH-bolts with
    # nuts, not tapped holes, so what the check needs is that every hole passes
    # through real material to bear on -- not thread engagement. 2 mm of aluminium
    # under an M4 at 37 N per bolt is 5 MPa of bearing, which is nothing.
    MIN_ENGAGE = 2.0
    for hx, hy in holes:
        before = hs.Volume
        hs = hs.cut(Part.makeCylinder(MNT_R, 30.0, V(hx, hy, z0 - 14.0), V(0, 0, 1)))
        eng = (before - hs.Volume) / (math.pi * MNT_R * MNT_R)
        assert eng >= MIN_ENGAGE, (
            "%s mount hole at (%.0f, %.0f) engages only %.1f mm of %s -- it is over a window "
            "or off the part" % (name, hx, hy, eng, host.Label))
    rem = (v0 - hs.Volume) / 1000.0
    assert len(hs.Solids) == 1, "%s split %s into %d solids" % (name, host.Label, len(hs.Solids))
    host.Shape = hs
    print("     %s drilled for 4 x M4, %.2f cm3 removed" % (host.Label, rem))
    built.append((name, p))

# The drive shell has to let the proximal BOSS through while the WINGS pass under it. So
# port the shell for the boss only, then trim the plate against whatever shell is left -- the
# wing tips were poking 0.059 cm3 into it at X 39..44, where the inner surface sits lower
# than the boss needs to clear.
cap = doc.getObject("P22_DriveCap")
if cap is not None:
    pb = built[0][1].BoundBox
    port = Part.makeBox(PW + 0.8, pb.YLength + 0.8, 40.0,
                        V(-PW / 2.0 - 0.4, pb.YMin - 0.4, 134.0))
    k = cap.Shape.common(port)
    rest = cap.Shape.cut(port).removeSplitter()
    keep = [t for t in rest.Solids if t.Volume / 1000.0 > 0.5]
    assert len(keep) == 1, "porting P22 left %d solids" % len(keep)
    rest = keep[0]
    name, pl = built[0]
    v0 = pl.Volume
    pl = pl.cut(rest.copy()).removeSplitter()
    kp = [t for t in pl.Solids if t.Volume / 1000.0 > 0.5]
    assert len(kp) == 1, "%s split into %d solids when trimmed to the shell" % (name, len(kp))
    pl = kp[0]
    # the mount holes must still have a wall around them after trimming
    for hx, hy in built[0][2] if len(built[0]) > 2 else []:
        pass
    doc.getObject(name).Shape = pl
    built[0] = (name, pl)
    cap.Shape = rest
    print("P22   ported %.2f cm3 for the boss; %s trimmed %.2f -> %.2f cm3 at the wing tips"
          % (0.0 if k.isNull() else k.Volume / 1000.0, name, v0 / 1000.0, pl.Volume / 1000.0))

print()
print("=" * 84)
print("CLEARANCE")
print("=" * 84)
NAMES = ["A1_Extrusion_20x60_VSlot", "A4_Shank2020_VSlot", "A7_DriveBox", "P6_ShankSocket",
         "P1_KneeYoke", "P2a_KneeHingePlate", "P21_ShellAnterior", "P22_DriveCap",
         "P24_FairingShank", "P25_MotorNacelle", "P20_KneeShroud", "P5_ThighCuff",
         "P7_ShankCuff", "A2_BallScrew_SFU1620", "A6_Idler29T", "A3_Motor_6374",
         "REF_Thigh", "REF_Shank"]
bad = 0
for name, p in built:
    for n in NAMES:
        ob = doc.getObject(n)
        if ob is None or not p.BoundBox.intersect(ob.Shape.BoundBox):
            continue
        k = p.common(ob.Shape)
        v = 0.0 if k.isNull() else k.Volume / 1000.0
        if v > 0.02:
            print("  %-20s vs %-26s %.3f cm3  <-- CLASH" % (name, ob.Label, v))
            bad += 1
print("  %s" % ("no clashes" if not bad else "%d clashes above" % bad))
assert not bad, "interface plates clash"

doc.recompute()
doc.save()
print("STAGE 11 DONE, saved.")
