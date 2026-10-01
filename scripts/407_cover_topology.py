# -*- coding: utf-8 -*-
"""Why the drive-end cover is TWO lobes, and why they are ONE wall.

Two separate questions got settled together, and both answers are counter-intuitive
enough to be worth keeping as arithmetic rather than as a note.

Q1. Can the cap and the motor pod be one lofted section? No. Three independent reasons,
    any one of which is fatal.
Q2. Then should they be two independent shells? Also no -- v2 built them as two shells
    that each cut themselves back to the other, which deletes every point lying in both
    walls from BOTH parts. They are two PRINTED PARTS of one wall instead.

Pure Python, no FreeCAD.
"""
import math

LEG_R = 84.9
COMFORT = 3.0
MOT_X, MOT_Z, MOT_R = -104.0, 62.0, 31.5
WALL = 3.0
N = 5.5

print("=" * 78)
print("Q1a.  IS THERE ROOM FOR A COVER BETWEEN THE MOTOR AND THE THIGH?")
print("=" * 78)
ax = math.hypot(MOT_X, MOT_Z)
print("  motor axis from the leg axis            %6.1f mm" % ax)
print("  nearest point on the can  (axis - %.1f)  %6.1f" % (MOT_R, ax - MOT_R))
print("  thigh surface + %.1f comfort clearance   %6.1f" % (COMFORT, LEG_R + COMFORT))
print("  room for cover wall                     %6.1f mm   <- needs %.1f" % (
    ax - MOT_R - LEG_R - COMFORT, WALL))
print()
POD_OUT_R = MOT_R + 3.5
print("  So the cover cannot keep its comfort clearance there. It fits only by spending it:")
print("  a tube of outer radius %.1f (a %.1f mm wall plus %.1f of bore clearance) reaches in"
      % (POD_OUT_R, WALL, POD_OUT_R - WALL - MOT_R))
print("  to %.1f, which is %.1f mm off a nominal thigh and %.1f short of the %.1f standoff"
      % (ax - POD_OUT_R, ax - POD_OUT_R - LEG_R,
         LEG_R + COMFORT - (ax - POD_OUT_R), COMFORT))
print("  the rest of the cladding gets. That is what P25 is, and it is the only thing that")
print("  fits. Tucking the motor this hard is what bought the reach measured in 402, and")
print("  this is the bill: the motor cover skims the quadriceps. It wants a tape measure on")
print("  the patient, not another boolean.")

print()
print("=" * 78)
print("Q1b.  A BIG SECTION LOSES ITS FLOOR WHERE A SMALL ONE KEEPS IT")
print("=" * 78)
print("  The limb cut removes everything inside r %.1f. A section floor sits at zc - b, so"
      % (LEG_R + COMFORT,))
print("  the bigger b is, the lower the floor, and the more of it the cut deletes.")
print()
print("    %-24s %-14s %-12s %-10s" % ("section", "floor Z", "limb cut Z", "verdict"))
XS = [-40.0, -55.0, -70.0]
for lbl, zc, b in (("small cap  zc108 b30", 108.0, 30.0),
                   ("merged     zc 83 b61", 83.0, 61.0)):
    for x in XS:
        zl = math.sqrt(max(0.0, (LEG_R + COMFORT) ** 2 - x * x))
        ok = "survives" if zc - b > zl else "DELETED"
        print("    %-24s %6.1f (X%+5.0f) %8.1f     %s" % (lbl, zc - b, x, zl, ok))
print()
print("  Near the centreline (X -40) BOTH lose the floor, and that is fine -- the limb is")
print("  3 mm away there and there is no room for a wall, which is the argument 217 made.")
print("  X -55 is where they differ, and it is the one that matters: the ball screw runs at")
print("  Z 98..114 the whole length of the device, and the floor at X -55 is the only thing")
print("  between it and the leg.")
print("  406_coverage.py scored the merged section at 16 exposed rays against 0 for the")
print("  pair -- the screw at -28 deg and the motor at -56 and -70 deg, over Y 202..238,")
print("  identical at every pose because the exposure is static.")

print()
print("=" * 78)
print("Q1c.  NO SUPERELLIPSE CLEARS THE THIGH AT THAT BEARING EITHER")
print("=" * 78)
print("  An n=%.1f section is WIDER than a circle on its diagonals -- that is the whole" % N)
print("  point of the formal language. For a pod that has to contain the can, the diagonal")
print("  is pointed at the thigh. The section must also be CENTRED on the can: offsetting it")
print("  outboard to protect the inboard diagonal forces the inboard half-size up by the")
print("  same amount, so the diagonal gets worse, not better. Centred is optimal, which is")
print("  why a brute-force search over centre AND exponent returns nothing.")
print()
print("    %-6s %-11s %-13s %-11s %-10s" % ("n", "half-size", "diagonal", "+%.0fmm wall" % WALL, "pod face"))
for n in (2.0, 2.5, 3.0, 4.0, N):
    s_ = MOT_R + 0.5                       # inner surface: the can plus bore clearance
    diag = s_ * 2.0 ** (0.5 - 1.0 / n)     # the superellipse 45 deg point
    face = ax - (diag + WALL)              # OUTER surface, which is what has to clear
    print("    %-6.1f %-11.1f %-13.1f %-11.1f %-10.1f %s"
          % (n, s_, diag, diag + WALL, face,
             "" if face > LEG_R else "<- inside the thigh"))
print()
print("  A circle is the only section whose worst bearing is its half-size, and it clears")
print("  by 1.2 mm. Even n=2.5 is already inside the limb once the wall is counted -- the")
print("  earlier version of this table showed the INNER surface and so understated it.")
print("  So the pod is round, and coherence has to come from the junction and the end caps,")
print("  which is what the faired foot and the domed nose are for.")

print()
print("=" * 78)
print("Q2.   TWO SHELLS THAT INTERSECT LEAVE A VOID BELONGING TO NEITHER")
print("=" * 78)
print("  v2 built:      cap = lo - li - POD_O")
print("                 pod = POD_O - POD_I - lo")
print()
print("  Take a point p in BOTH walls, i.e. p in (lo - li) and p in (POD_O - POD_I):")
print("     p is inside POD_O  -> cut from the cap")
print("     p is inside lo     -> cut from the pod")
print("  ...so p is in neither part. That region is a thin void running the length of the")
print("  seam. Nothing in this repository was watching for it: an interference sweep looks")
print("  for material in two places at once, and this is material in NO place.")
print()
print("  v4 builds one wall and splits it:")
print("                 wall = (lo U POD_O) - (li U POD_I)")
print("                 P22  = wall - POD_O         P25 = wall n POD_O")
print("  which partitions the wall exactly -- the build reports 160.2 + 82.9 = 243.1 cm3,")
print("  100.0 %% accounted, 0.0000 cm3 overlap -- and the seam becomes a real shared face")
print("  instead of a gap. Same two printed parts, same two print beds, no void.")
print()
print("  The general lesson, and the fifth instance of it this week: the asserts in this")
print("  repository catch parts that get SEVERED (solids != 1) and parts that OVERLAP.")
print("  Nothing was watching for parts that are MISSING or surfaces that are not there.")
print("  That class of defect has cost: a deleted motor mount, an open nacelle bore, two")
print("  limb-facing floor openings, the bracket windows, and this seam.")


print()
print("=" * 78)
print("Q3.   DOES THE FAIRED FOOT ACTUALLY SOFTEN THE SEAM?")
print("=" * 78)
print("  The thing you see at a junction like this is the CREASE -- the dihedral between")
print("  the two surfaces where they cross. A tube driven through a flank at a steep angle")
print("  makes a hard edge; the flare works by swinging the pod's surface round to leave at")
print("  a shallower angle. (The naive probe -- outer radius about the motor axis -- is")
print("  useless here: the cap is not centred on that axis, so a ray at +10 deg grazes down")
print("  its long axis and exits at r 161, which looks like a 126 mm step and is not one.)")
print()

MOT_R_POD, FL0, FL1 = 35.0, 12.0, 100.0


def win(deg):
    d = deg % 360.0
    if not (FL0 < d < FL1):
        return 0.0
    return 0.5 - 0.5 * math.cos(2.0 * math.pi * (d - FL0) / (FL1 - FL0))


def lerp(a, b, f):
    return tuple(x + (y - x) * f for x, y in zip(a, b))


CAP = lerp((-21.0, 77.5, 29.0, 110.0), (-21.5, 78.0, 30.0, 108.0), (250.0 - 220.0) / 80.0)
XC, A, B, ZC = CAP


def fcap(x, z):
    return (abs(x - XC) / A) ** N + (abs(z - ZC) / B) ** N


def pod_pt(deg, F):
    t = math.radians(deg)
    r = MOT_R_POD + F * win(deg)
    return MOT_X + r * math.cos(t), MOT_Z + r * math.sin(t)


def crease(F):
    """bearings where the pod surface crosses the cap surface, and the dihedral at each."""
    out, h = [], 0.02
    prev = None
    for k in range(0, 36000):
        d = k / 100.0
        v = fcap(*pod_pt(d, F)) - 1.0
        if prev is not None and prev * v < 0.0:
            x, z = pod_pt(d, F)
            # pod tangent, by central difference along the bearing parameter
            x1, z1 = pod_pt(d - h, F)
            x2, z2 = pod_pt(d + h, F)
            tp = math.atan2(z2 - z1, x2 - x1)
            # cap tangent, perpendicular to the implicit gradient
            gx = N * (abs(x - XC) / A) ** (N - 1) / A * (1 if x > XC else -1)
            gz = N * (abs(z - ZC) / B) ** (N - 1) / B * (1 if z > ZC else -1)
            tc = math.atan2(-gx, gz)
            a = math.degrees(abs(tp - tc)) % 180.0
            out.append((d, min(a, 180.0 - a)))
        prev = v
    return out


print("  %-24s %-28s %s" % ("", "seam bearing / crease", "worst crease"))
for lbl, F in (("bare tube  (v2)", 0.0), ("faired foot (v4)", 12.0)):
    cr = crease(F)
    txt = "   ".join("%+.0f deg: %2.0f deg" % (d, a) for d, a in cr)
    worst = max(a for _, a in cr) if cr else 0.0
    print("  %-24s %-28s %.0f deg" % (lbl, txt, worst))
print()
print("  0 deg would be tangent -- surfaces leaving each other smoothly -- and 90 deg is a")
print("  tube stabbed squarely through a wall. So the flare is a TRADE, not a free win: it")
print("  flattens the outboard seam and sharpens the inboard one. What it does unambiguously")
print("  is fill the concave corner where the tube meets the flank, by 3.5 mm at the inboard")
print("  seam and 5.1 at the outboard, and a groove between two bodies is the thing that")
print("  reads as bolted-on. A crease where a blister leaves a surface does not.")
print()
print("  It costs nothing either way: the whole window lies above +12 deg, where a ray")
print("  leaving the motor axis never reaches the thigh, so limb clearance is 86.1 mm with")
print("  or without it. Whether the trade is the right one is a question for the render,")
print("  not for this script.")
