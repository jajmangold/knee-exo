# -*- coding: utf-8 -*-
"""STAGE 9: cuffs that actually touch the limb.

408_cuff_loads.py found that neither cuff fits. Both limb phantoms are CONES -- thigh
r 62 -> 85, shank r 60 -> 38 -- and both cuffs were CYLINDERS, so:

  * the thigh cuff floated over its distal half and bore on a 47 mm band at its proximal
    rim, where the 6 mm pad was crushed 63%. Real contact pressure there is ~40 kPa
    against a 15 kPa comfort ceiling: a pressure sore, at the shell edge, on a limb with
    post-operative circulation.
  * the shank cuff never reached the limb at all. 15-23 mm of air, closest approach 7.78 mm.
    The 107-pose sweep has flagged P5 against REF_Thigh at 0.836 cm3 every single run and
    has NEVER flagged P7 against REF_Shank. The absence was the finding and nobody read it.

What this rebuilds:

1. CONICAL SHELLS on the limb taper, so the whole width bears instead of one rim.
2. WIDER AND MORE WRAP, to put the uniform pressure under the ceiling. Computed here and
   asserted, not guessed -- see the table this prints.
3. SIZED FOR A NEOPRENE SLEEVE, not an EVA pad. The sleeve is the skin interface: it
   raises the friction coefficient that sets strap tension (0.4 EVA-on-skin -> 0.6 worst
   case neoprene, so 31 N -> 21 N), bridges the shell rim instead of letting it dig, moves
   the sliding interface off the patient, and washes. The EVA pad leaves the BOM.
4. ROLLED RIMS at both ends, because the edge is where concentration lands even when the
   cone matches.
5. WEBBING SLOTS, 38 mm, two stations per cuff. 38 mm because at 31 N across the open side
   a 3.5 mm lace is ~90 kPa on soft tissue and 38 mm webbing is 8.3 kPa -- webbing is its
   own tongue, which is why a laced brace needs a separate one.
6. MOUNTING THAT EXISTS. The old thigh cuff bolted to a pad spanning Y 155..255 -- but the
   rail ends at Y 207, so 48 mm of that pad was bolted to nothing. Bosses now sit inside the
   rail span only.

Send with:  python tools/fcsend.py scripts/409_cuffs.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

doc = FreeCAD.getDocument("KneeExo_v4")

T_KNEE = 28.2
SLEEVE = 3.0          # neoprene
AIR = 1.0             # donning clearance over the sleeve
WALL = 4.0
RIM = 4.0             # how far the rim rolls away from the limb
RIM_L = 10.0          # over what length
P_CEIL = 13.0         # kPa, design ceiling with margin under the 15 kPa comfort limit
WEB = 38.0            # webbing width
WEB_T = 4.0


def r_thigh(y):
    return 62.0 + (85.0 - 62.0) * (y - 15.0) / 285.0


def r_shank(y):
    return 60.0 - (60.0 - 38.0) * (abs(y) - 20.0) / 360.0


def wedge(a0, a1, R, y0, y1, n=72):
    """Angular sector as a prism -- predictable, unlike makeCylinder's angle argument."""
    pts = [V(0.0, y0, 0.0)]
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append(V(R * math.cos(a), y0, R * math.sin(a)))
    pts.append(pts[0])
    f = Part.Face(Part.makePolygon(pts))
    return f.extrude(V(0.0, y1 - y0, 0.0))


def cone(r0, r1, y0, y1):
    return Part.makeCone(r0, r1, y1 - y0, V(0.0, y0, 0.0), V(0.0, 1.0, 0.0))


def desplit(sh):
    """removeSplitter(), but only if it does not turn the solid inside out.

    It does, here. Fusing the riser box onto the conical bore leaves a face tangent to the
    cone at X = 0, and removeSplitter's attempt to merge that face flips the solid's
    orientation: volume goes +153.69 -> -153.69 cm3. Nothing complains. isValid() stays
    True, isClosed() stays True, len(Solids) stays 1, and the bounding box is unchanged --
    but every subsequent cut then ADDS material, and three separate measurements came back
    impossible before the cause was found:

        common(cuff, limb)    4876 cm3, against a 153 cm3 cuff
        distToShape           closest point at r 59.4, inside a limb whose surface is r 71.3
        the solids filter     0 solids, because a negative volume fails "> 0.5 cm3"

    An inverted solid is the same class of defect as the missing walls this repo keeps
    finding: valid, closed, well-formed, and wrong. So check the sign and keep whichever
    shape is right side out.
    """
    out = sh.removeSplitter()
    if out.Volume > 0.0:
        return out
    return sh


def cuff(name, fn, y0, y1, a0, a1, label):
    """Conical arc shell sized to limb + sleeve + air, with rolled rims."""
    ri0, ri1 = fn(y0) + SLEEVE + AIR, fn(y1) + SLEEVE + AIR
    # extend the inner cone past both ends so the cut is clean
    s = (ri1 - ri0) / (y1 - y0)
    out = cone(ri0 + WALL, ri1 + WALL, y0, y1)
    inn = cone(ri0 - s * 2.0, ri1 + s * 2.0, y0 - 2.0, y1 + 2.0)
    sh = out.cut(inn)
    # ROLLED RIMS: flare the inner surface away from the limb over the last RIM_L at each
    # end, so the edge presents a ramp rather than a step. This is the edge that the 40 kPa
    # concentration was found on.
    sh = sh.cut(cone(ri0 + RIM, ri0 + s * RIM_L, y0 - 1.0, y0 + RIM_L))
    sh = sh.cut(cone(ri1 - s * RIM_L, ri1 + RIM, y1 - RIM_L, y1 + 1.0))
    sh = sh.common(wedge(a0, a1, max(ri0, ri1) + WALL + 10.0, y0 - 1.0, y1 + 1.0))
    return sh


print("=" * 78)
print("SIZING -- pressure is computed and asserted, not chosen")
print("=" * 78)
print("  %-8s %-14s %-9s %-7s %-9s %-9s %s"
      % ("cuff", "Y span", "width", "wrap", "arm", "force", "pressure"))
SPEC = []
# a1 = 95 deg on both: just past straight-lateral, so there is shell under BOTH bolt
# positions at X +/-10. At exactly 90 the shell edge lands on X = 0 and the bosses hang in
# space -- which is what the first build did, and it reported 3 solids.
for lbl, fn, y0, y1, a0, a1 in (("thigh", r_thigh, 120.0, 260.0, -105.0, 95.0),
                                ("shank", r_shank, -350.0, -190.0, -120.0, 95.0)):
    # the shank needs 215 deg where the thigh needs 200: the calf is a smaller
    # radius, so the same wrap angle buys a much shorter arc to spread load over.
    yc = abs(0.5 * (y0 + y1))
    F = T_KNEE / (yc / 1000.0)
    wrap = a1 - a0
    w = y1 - y0
    rc = fn(0.5 * (y0 + y1))
    A = math.radians(wrap) * rc * w / 1e6 * 0.5 * (2.0 / math.pi)
    p = F / A / 1000.0
    print("  %-8s %5.0f..%-7.0f %5.0f mm  %4.0f deg %6.0f mm %7.1f N %7.1f kPa %s"
          % (lbl, y0, y1, w, wrap, yc, F, p, "" if p < P_CEIL else "<-- OVER"))
    assert p < P_CEIL, "%s cuff at %.1f kPa, ceiling %.1f" % (lbl, p, P_CEIL)
    SPEC.append((lbl, fn, y0, y1, a0, a1))
print("  (old: thigh 16.1 kPa nominal but 40 kPa on the band that actually touched;")
print("   shank did not touch at all)")

print()
print("=" * 78)
ST = doc.getObject("A1_Extrusion_20x60_VSlot")
A7 = doc.getObject("A7_DriveBox")
A4 = doc.getObject("A4_Shank2020_VSlot")

# MOUNT TARGETS. The thigh cuff bolts up into the rail's lower face at Z 88. The shank
# cuff cannot bolt to A4 at all -- A4's lower face is Z 94 and a limb-sized shank shell tops
# out near Z 52, a 42 mm gap -- so it bolts to P6_ShankSocket's underside at Z 68 on a
# riser. That gap is the whole reason the OLD shank cuff sat at r 64: it was sized to reach
# the structure, not to fit the leg, and reaching the structure is what it was optimised for.
SOCK = doc.getObject("P6_ShankSocket")
for (lbl, fn, y0, y1, a0, a1), (name, mount, zt, host, keepout) in zip(
        SPEC, (("P5_ThighCuff", (130.0, 195.0), 88.0, ST, (A7,)),
               ("P7_ShankCuff", (-290.0, -215.0), 68.0, SOCK, (A4,)))):
    sh = cuff(name, fn, y0, y1, a0, a1, lbl)

    # ---- webbing slots: two stations, one near each free circumferential edge
    # The slot is an ANGULAR SECTOR, not a rotated box. The box version needed its 40 mm
    # axis rotated onto the radial direction and I got the sense wrong -- it cut at the
    # wrong bearing and left the real slot blocked. A sector built from the axis outward
    # cannot be mis-oriented: the strap's 38 mm width lies along Y (the limb axis, because
    # the strap runs circumferentially) and its thickness is an arc of WEB_T at radius rr.
    for ys in (y0 + 0.28 * (y1 - y0), y0 + 0.72 * (y1 - y0)):
        rr = fn(ys) + SLEEVE + AIR
        d = math.degrees(0.5 * (WEB_T + 1.0) / rr)
        for a in (a0 + 9.0, a1 - 9.0):
            sh = sh.cut(wedge(a - d, a + d, rr + WALL + 10.0,
                              ys - WEB / 2.0, ys + WEB / 2.0))

    # ---- mounting risers up to the host's underside, inside the host's own Y span
    hb = host.Shape.BoundBox
    for yb in mount:
        assert hb.YMin - 1.0 <= yb <= hb.YMax + 1.0, (
            "%s riser at Y %.0f is outside %s (Y %.0f..%.0f) -- bolted to nothing"
            % (name, yb, host.Label, hb.YMin, hb.YMax))
        rr = fn(yb) + SLEEVE + AIR + WALL
        # One wide riser spanning both bolts, rooted on the shell across X -16..16 where the
        # shell definitely exists (a1 = 95 deg), not two columns perched on its edge.
        # Its flat underside sits at the shell's INNER radius, not 3 mm below the outer: a
        # flat bottom cannot follow a curved bore, so rooting it lower made it dip into the
        # sleeve -- the sampled gap went to 2.19 mm under the shank risers, a 27% compressed
        # hard spot on a cuff whose entire purpose here was to stop concentrating pressure.
        # At the inner radius the box is tangent to the bore at X = 0 and buried in the wall
        # everywhere else, so it still bonds.
        z_root = fn(yb) + SLEEVE + AIR
        assert zt > z_root + 4.0, (
            "%s riser at Y %.0f would be %.1f mm tall -- shell top %.1f, host underside %.1f"
            % (name, yb, zt - z_root, z_root, zt))
        sh = sh.fuse(Part.makeBox(32.0, 18.0, zt - z_root, V(-16.0, yb - 9.0, z_root)))
        ri = fn(yb) + SLEEVE + AIR
        for bx_ in (-10.0, 10.0):
            sh = sh.cut(Part.makeCylinder(2.6, 40.0, V(bx_, yb, zt - 18.0), V(0, 0, 1)))
            # COUNTERBORE. The bolt goes UP into the rail's T-slot, so its head sits on the
            # limb side. An M5 button head is 2.8 mm tall and the gap to the limb is 4.0 mm
            # (3 sleeve + 1 air), so an unrecessed head lands inside the neoprene at all four
            # bolts -- four hard points pressing on the leg, on a cuff whose whole purpose
            # this rebuild was to stop concentrating pressure.
            # The head recess is a BOX, not a counterbore cylinder. A cylinder cut into a
            # cone meets it along a glancing curve and OCCT made a mess of it twice: first
            # common() returned the whole limb (4876 cm3 against a 153 cm3 cuff -- not a
            # volume a boolean can produce), then distToShape put the closest point at
            # r 59.4 where the limb surface is r 71.3, i.e. inside the limb, on the plane
            # where the bolt hole started. A box has planar faces and crosses the cone
            # transversely, which is the robust version of the same recess.
            # 3.5 mm deep from the riser's own flat underside: an M5 button head is 2.8 mm,
            # so it sits flush with the bore and nothing protrudes into the sleeve.
            sh = sh.cut(Part.makeBox(11.0, 11.0, 3.5,
                                     V(bx_ - 5.5, yb - 5.5, z_root)))
            assert zt - (z_root + 3.5) > 2.5, (
                "%s head recess at Y %.0f leaves only %.1f mm of riser above it"
                % (name, yb, zt - (z_root + 3.5)))
    sh = desplit(sh)

    # ---- clear the structure it lives beside, but NOT its own host
    # P22/P25 are in here because the thigh cuff's proximal rim at Y 260 reaches r 89.8 and
    # the drive shell starts at Y 180 -- they overlapped by 0.038 cm3, which is small enough
    # to miss by eye and large enough to stop the two parts going together.
    for ob in (ST, A7, A4, SOCK, doc.getObject("P2a_KneeHingePlate"),
               doc.getObject("P1_KneeYoke"), doc.getObject("P22_DriveCap"),
               doc.getObject("P25_MotorNacelle")):
        if ob is None or ob.Name == host.Name:
            continue
        if not sh.BoundBox.intersect(ob.Shape.BoundBox):
            continue
        sh = sh.cut(ob.Shape)
    sh = desplit(sh)

    assert sh.Volume > 0.0, (
        "%s has negative volume %.1f cm3 -- the solid is inside out" % (name, sh.Volume / 1000.0))
    keep = [s for s in sh.Solids if s.Volume / 1000.0 > 0.5]
    if len(keep) != 1:
        raise AssertionError("%s has %d solids: %s" % (name, len(keep),
            " | ".join("%.1f cm3 X%.0f..%.0f Y%.0f..%.0f Z%.0f..%.0f"
                       % (s.Volume / 1000., s.BoundBox.XMin, s.BoundBox.XMax,
                          s.BoundBox.YMin, s.BoundBox.YMax,
                          s.BoundBox.ZMin, s.BoundBox.ZMax) for s in keep)))
    sh = keep[0]
    assert sh.isValid(), "%s invalid" % name

    # ---- the slots have to BE there. Face counts do not prove it and neither does a
    # picture from the wrong side; this project has lost a motor mount, a nacelle bore and
    # two bracket floors to features that silently did not get cut. Fire a radial probe
    # through each intended slot and require it to meet no material.
    nslot = 0
    for ys in (y0 + 0.28 * (y1 - y0), y0 + 0.72 * (y1 - y0)):
        rr = fn(ys) + SLEEVE + AIR
        for a in (a0 + 9.0, a1 - 9.0):
            t = math.radians(a)
            e = Part.makeLine(V((rr - 6.0) * math.cos(t), ys, (rr - 6.0) * math.sin(t)),
                              V((rr + WALL + 6.0) * math.cos(t), ys, (rr + WALL + 6.0) * math.sin(t)))
            k = sh.common(e)
            blocked = 0.0 if k.isNull() else sum(ed.Length for ed in k.Edges)
            assert blocked < 0.5, (
                "%s webbing slot at Y %.0f bearing %+.0f is BLOCKED by %.2f mm of material"
                % (name, ys, a, blocked))
            nslot += 1
    print("   %s: %d webbing slots verified open, %.0f mm wide" % (name, nslot, WEB))

    o = doc.getObject(name)
    if o is None:
        o = doc.addObject("Part::Feature", name)
    v0 = o.Shape.Volume / 1000.0
    o.Shape = sh
    o.Label = name
    b = sh.BoundBox
    print("%-14s X %7.1f..%6.1f Y %7.1f..%6.1f Z %6.1f..%6.1f  %6.1f -> %6.1f cm3  %4.0f g"
          % (name, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax,
             v0, sh.Volume / 1000.0, sh.Volume / 1000.0 * 1.27))

print()
print("=" * 78)
print("FIT CHECK -- the thing that was never checked before")
print()
# SAMPLED, not boolean. distToShape and common both misbehave on this pair: common returned
# 4876 cm3 against a 153 cm3 cuff, and distToShape put the closest point at r 59.4 where the
# limb surface is r 71.3 -- a point inside the limb, on the plane where a bolt hole started.
# Neither number is a geometry a boolean can produce, and the 1.02 mm an earlier run reported
# was never explicable either, since the design gap is a constant 4.00 mm by construction.
# Firing a ray and measuring where it crosses each surface uses only line-solid intersection,
# which has been stable throughout, and it checks the actual design claim: that the gap is
# uniform, which is the whole point of making the shells conical.
def ray_r(sh, y, deg, outer=False):
    t = math.radians(deg)
    e = Part.makeLine(V(2.0 * math.cos(t), y, 2.0 * math.sin(t)),
                      V(260.0 * math.cos(t), y, 260.0 * math.sin(t)))
    k = sh.common(e)
    if k.isNull() or not k.Vertexes:
        return None
    rr = [math.hypot(v.Point.x, v.Point.z) for v in k.Vertexes]
    return max(rr) if outer else min(rr)


for (lbl, fn, y0, y1, a0, a1), (name, lim) in zip(
        SPEC, (("P5_ThighCuff", "REF_Thigh"), ("P7_ShankCuff", "REF_Shank"))):
    c, L = doc.getObject(name).Shape, doc.getObject(lim).Shape
    gaps, rim = [], []
    for i in range(11):
        y = y0 + (y1 - y0) * (i + 0.5) / 11.0
        at_rim = (y - y0) < RIM_L + 2.0 or (y1 - y) < RIM_L + 2.0
        for j in range(13):
            a = a0 + (a1 - a0) * (j + 0.5) / 13.0
            rl, rc = ray_r(L, y, a, outer=True), ray_r(c, y, a)
            if rl is None or rc is None:
                continue
            (rim if at_rim else gaps).append(rc - rl)
    assert len(gaps) > 60, "%s: only %d samples landed on the shell" % (name, len(gaps))
    lo, hi = min(gaps), max(gaps)
    print("  %-14s %d samples off the rim: gap %.2f..%.2f mm (design %.1f)"
          % (name, len(gaps), lo, hi, SLEEVE + AIR))
    print("     %d rim samples: gap %.2f..%.2f mm -- the rolled rim, flaring away on purpose"
          % (len(rim), min(rim), max(rim)))
    print("     a %.0f mm sleeve fills %.0f%% of it; %s"
          % (SLEEVE, 100.0 * SLEEVE / hi, "BEARS" if hi <= SLEEVE + AIR + 0.6 else "TOO LOOSE"))
    assert lo > 0.3, "%s touches the limb: minimum gap %.2f mm" % (name, lo)
    assert hi <= SLEEVE + AIR + 0.6, (
        "%s gap reaches %.2f mm -- a %.0f mm sleeve cannot fill it" % (name, hi, SLEEVE))

doc.recompute()
doc.save()
print("STAGE 9 DONE, saved.")
