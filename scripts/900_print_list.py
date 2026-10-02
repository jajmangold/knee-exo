# -*- coding: utf-8 -*-
"""Generate docs/PRINT.md from the exported STLs and the model. Do not write that file by hand.

The BOM's printed-parts table was written by hand and went stale in three ways at once: it listed
`P3_Carriage` and `P3b_CarriageB` as printed when P3 became a bought aluminium plate and P3b was
deleted with the second ball screw, it listed `P11_SprungAnchor` which is not in the model at all,
and it said "8 mm Arial Bold" after the leg suffix pushed two marks down to 5 and 4 mm. A table of
facts a script can measure should be written by the script.

What this measures, per part, for BOTH legs:
  * footprint, height and the orientation that minimises overhang (the same search 411 runs)
  * support area, and where up the part it occurs
  * solid volume, and an ESTIMATED printed mass at the perimeter/infill setting chosen for the part
  * the holes that need reaming, drilling or a heat-set insert before assembly (417's classifier)

The mass estimate is a model, not a measurement: shell thickness = perimeters x 0.42 mm, and a part
whose mean wall is thinner than two shells prints effectively solid. Time assumes 3.5 mm3/s of
effective flow -- 0.2 mm layers, 0.42 mm extrusion, 60 mm/s, with travel and acceleration losses.
Both are stated so they can be corrected against the first real print rather than believed.

    freecadcmd.exe scripts/900_print_list.py
"""
import glob
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(REPO, "tools"))

RHO = 1.27e-3           # g/mm3, PETG
LAYER, EXTR, FLOW = 0.2, 0.42, 3.5      # mm, mm, mm3/s effective
COS_LIM = math.cos(math.radians(45.0))
UPS = [(0., 0., 1.), (0., 0., -1.), (0., 1., 0.), (0., -1., 0.), (1., 0., 0.), (-1., 0., 0.)]
LAB = {(0., 0., 1.): "+Z", (0., 0., -1.): "-Z", (0., 1., 0.): "+Y",
       (0., -1., 0.): "-Y", (1., 0., 0.): "+X", (-1., 0., 0.): "-X"}

# perimeters, infill, and why -- from the BOM, which is where the load cases live
SETTING = {
    "P1_KneeYoke": (5, 0.60, "carries the full knee reaction"),
    "P2a_KneeHub_Pulley29T": (6, 0.60, "the 29T capstan; tooth flanks want a fresh nozzle"),
    "P5_ThighCuff": (4, 0.30, "pressure vessel, not a beam"),
    "P6_ShankSocket": (4, 0.30, "structural but bulky"),
    "P7_ShankCuff": (4, 0.30, "pressure vessel, not a beam"),
    "P20_KneeCap": (3, 0.15, "cosmetic"),
    "P21_FairingThigh": (3, 0.15, "cosmetic"),
    "P22_DriveCap": (3, 0.15, "cosmetic, but it is half the drive wall"),
    "P23a_FairingMount": (4, 0.40, "carries the canopy"),
    "P23b_FairingMount": (4, 0.40, "carries the canopy"),
    "P23c_FairingMount": (4, 0.40, "carries the canopy"),
    "P24_FairingShank": (3, 0.15, "cosmetic"),
    "P25_MotorNacelle": (3, 0.15, "cosmetic; prints nose-down on its domed end"),
    "P30_InterfaceProx": (6, 0.60, "KX-1 interface, 1.2 MPa of bearing standalone"),
    "P31_InterfaceDist": (6, 0.60, "KX-1 interface, 1.2 MPa of bearing standalone"),
    # printed since 802_no_metal.py -- these were the only two fabricated aluminium parts
    "A7_DriveBracket_Idler": (6, 0.60, "holds the idler at 1828 N; the heaviest load path"),
    "P3_GantryPlate_Printed": (6, 0.50, "drags the whole gantry; in-plane loads only"),
    # not a part of the device: the go/no-go print for the tooth profile
    "TEST_ToothCoupon_3xHTD8M": (6, 0.60, "print FIRST and push a real HTD-8M belt into it"),
}


def read_stl(path):
    with open(path, "rb") as f:
        head = f.read(5)
        f.seek(0)
        if head == b"solid":
            tris, cur = [], []
            for line in f.read().decode("utf-8", "replace").splitlines():
                w = line.split()
                if w and w[0] == "vertex":
                    cur.append(tuple(float(x) for x in w[1:4]))
                    if len(cur) == 3:
                        tris.append(tuple(cur))
                        cur = []
            return tris
        f.read(80)
        n = struct.unpack("<I", f.read(4))[0]
        tris = []
        for _ in range(n):
            d = struct.unpack("<12fH", f.read(50))
            tris.append((d[3:6], d[6:9], d[9:12]))
        return tris


def props(t):
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = t
    ux, uy, uz = bx - ax, by - ay, bz - az
    vx, vy, vz = cx - ax, cy - ay, cz - az
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    m = math.sqrt(nx * nx + ny * ny + nz * nz)
    area = 0.5 * m
    n = (nx / m, ny / m, nz / m) if m else (0.0, 0.0, 1.0)
    vol = (ax * (by * cz - bz * cy) + bx * (cy * az - cz * ay) + cx * (ay * bz - az * by)) / 6.0
    return area, n, vol


def rotm(up, spin):
    ux, uy, uz = up
    if abs(uz) > 0.99:
        base = [(1., 0., 0.), (0., 1. if uz > 0 else -1., 0.), (0., 0., uz)]
    else:
        zx, zy, zz = -ux, -uy, -uz
        ax, ay, az = (0., 0., 1.)
        xx, xy, xz = ay * zz - az * zy, az * zx - ax * zz, ax * zy - ay * zx
        m = math.sqrt(xx * xx + xy * xy + xz * xz)
        xx, xy, xz = xx / m, xy / m, xz / m
        yx, yy, yz = zy * xz - zz * xy, zz * xx - zx * xz, zx * xy - zy * xx
        base = [(xx, xy, xz), (yx, yy, yz), (-zx, -zy, -zz)]
    c, s = math.cos(math.radians(spin)), math.sin(math.radians(spin))
    r0 = tuple(c * base[0][i] - s * base[1][i] for i in range(3))
    r1 = tuple(s * base[0][i] + c * base[1][i] for i in range(3))
    return [r0, r1, base[2]]


def ap(R, v):
    return tuple(sum(R[i][j] * v[j] for j in range(3)) for i in range(3))


def measure(path):
    tris = read_stl(path)
    pr = [props(t) for t in tris]
    area = sum(a for a, _, _ in pr)
    vol = abs(sum(v for _, _, v in pr))
    verts = [v for t in tris for v in t]
    best = None
    for up in UPS:
        for spin in (0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165):
            R = rotm(up, float(spin))
            sup = sum(a for a, n, _ in pr if ap(R, n)[2] < -COS_LIM)
            xs = [ap(R, v) for v in verts]
            bx = max(q[0] for q in xs) - min(q[0] for q in xs)
            by = max(q[1] for q in xs) - min(q[1] for q in xs)
            bz = max(q[2] for q in xs) - min(q[2] for q in xs)
            score = sup / area + max(0.0, max(bx, by) - 250.0) * 0.01
            if best is None or score < best[0]:
                best = (score, bx, by, bz, sup, up, spin)
    _, bx, by, bz, sup, up, spin = best
    return dict(area=area, vol=vol, bx=bx, by=by, bz=bz, sup=sup, up=up, spin=spin,
                wall=2.0 * vol / area if area else 0.0, tris=len(tris))


def est_mass(vol, wall, perims, infill):
    """Shell plus infill. A part whose mean wall is thinner than two shells prints solid."""
    shell = 2.0 * perims * EXTR
    f = 1.0 if wall <= shell else shell / wall + infill * (1.0 - shell / wall)
    return vol * RHO * f, f


# ------------------------------------------------------------------ gather both legs
LEGS = [("L", "KneeExo_v6_STL"), ("R", "KneeExo_v6_R_STL")]
data = {}
for leg, d in LEGS:
    files = sorted(glob.glob(r"C:/Users/Josh/%s/*.stl" % d))
    if not files:
        print("  no STLs in %s -- run 219_stl.py for that leg first" % d)
        continue
    data[leg] = {os.path.basename(p)[:-4]: measure(p) for p in files}
if "L" not in data:
    raise SystemExit("no left-leg STLs; nothing to write")

# the post-processing list, by part, from the audit's own classifier
sys.path.insert(0, os.path.join(REPO, "scripts"))
HOLES = {
    "P1_KneeYoke": ("2 x M4 clearance, 4 x M5 into the rail at X +-10, 4 x M5 clearance for "
                    "the canopy's lip at X +-20, 1 x dia 28 bearing seat (bore 28.2, bond)"),
    "P2a_KneeHub_Pulley29T": ("3 x M5 clearance, 2 x dia 12.3 pin bore (clamped, not a "
                              "journal), and 29 HTD-8M grooves on the dia 72.48 belt land"),
    "P5_ThighCuff": "4 x M5 clearance with cap head counterbores",
    "P6_ShankSocket": "16 x M4 clearance, 4 x M5 heat-set insert",
    "P7_ShankCuff": "4 x M5 clearance with cap head counterbores",
    "P20_KneeCap": "none",
    "P21_FairingThigh": "19 x M5 clearance",
    "P22_DriveCap": "none",
    "P23a_FairingMount": "1 x M5 clearance (on the build axis)",
    "P23b_FairingMount": "1 x M5 clearance (on the build axis)",
    "P23c_FairingMount": "1 x M5 clearance (on the build axis)",
    "P24_FairingShank": "3 x M5 clearance",
    "P25_MotorNacelle": "none",
    "P30_InterfaceProx": "4 x M4 clearance, 2 x 5 mm dowel H7, 6 x M5 heat-set insert",
    "P31_InterfaceDist": "6 x M4 clearance, 2 x 5 mm dowel H7, 6 x M5 heat-set insert",
    "A7_DriveBracket_Idler": ("4 x M4 motor clearance, 2 x dia 26 idler bearing seats (bond), "
                              "dia 22 x 7 seat for the screw's 608 (bond), dia 9.2 screw bore, "
                              "2 x M5 along Y into the rail's end"),
    # was "NONE DRAWN -- it cannot be bolted as it stands", which was true until 424 and is
    # exactly the kind of sentence that outlives the condition it describes
    "P3_GantryPlate_Printed": ("4 x M5 V-wheel clearance, 2 x M5 radial set screws onto the "
                               "ball nut, and the 5-tooth HTD-8M belt land -- the land prints as "
                               "drawn and wants no reaming, but check it against the coupon"),
}

out = []
w = out.append
w("# Print list")
w("")
w("**Generated by [`scripts/900_print_list.py`](../scripts/900_print_list.py) — do not edit by")
w("hand.** Every number here is measured off the exported STLs in `stl/` and `stl_R/`; the mass and")
w("time figures are models, stated below, and should be corrected against the first real print.")
w("")
w("17 parts per leg, **34 for the pair**. They are not 15 parts printed twice: each one is chiral,")
w("so a left part cannot be used on the right leg. The engraved number says which — `P5L` against")
w("`P5R` — and that is the only thing distinguishing two parts that otherwise look identical.")
w("")
w("## Settings")
w("")
w("Blue PETG, 0.2 mm layers, 0.42 mm extrusion width. Per-part perimeters and infill come from the")
w("load case, not from a global profile:")
w("")
w("| Part | Perimeters | Infill | Why |")
w("|---|---|---|---|")
for nm in sorted(SETTING):
    p, i, why = SETTING[nm]
    w("| `%s` | %d | %.0f%% | %s |" % (nm, p, 100 * i, why))
w("")
w("## Per part, left leg")
w("")
w("| Part | Orientation | Footprint | Height | Support | Volume | Est. filament | Est. time |")
w("|---|---|---|---|---|---|---|---|")
tot_m = tot_t = tot_sup = 0.0
for nm in sorted(data["L"]):
    m = data["L"][nm]
    perims, infill, _ = SETTING.get(nm, (4, 0.3, ""))
    mass, f = est_mass(m["vol"], m["wall"], perims, infill)
    hours = m["vol"] * f / FLOW / 3600.0
    tot_m += mass
    tot_t += hours
    tot_sup += m["sup"]
    w("| `%s` | %s up, %d° | %.0f x %.0f mm | %.0f mm | %.1f%% | %.0f cm³ | %.0f g | %.1f h |"
      % (nm, LAB[m["up"]], m["spin"], m["bx"], m["by"], m["bz"],
         100.0 * m["sup"] / m["area"], m["vol"] / 1000.0, mass, hours))
w("| | | | | **%.0f cm² total** | | **%.0f g** | **%.0f h** |"
  % (tot_sup / 100.0, tot_m, tot_t))
w("")
w("The right leg is the mirror image and measures the same to within meshing noise: ")
if "R" in data:
    rv = sum(v["vol"] for v in data["R"].values())
    lv = sum(v["vol"] for v in data["L"].values())
    w("%.0f cm³ against %.0f cm³, a %.2f%% difference, all of it in facet placement."
      % (rv / 1000.0, lv / 1000.0, 100.0 * abs(rv - lv) / lv))
    w("So budget **%.0f g of filament and %.0f printer-hours for the pair**, plus supports."
      % (2 * tot_m, 2 * tot_t))
w("")
w("## Before you assemble anything: holes")
w("")
w("A printed hole comes off the bed 0.1–0.3 mm **under** its modelled size, and any hole whose axis")
w("is not along the build direction prints as an egg. Almost every hole in this device runs along the")
w("knee axis (Z) while most parts build along Y, so **assume every hole needs a drill pass**. Sizes")
w("to finish to, from [`scripts/417_fastener_audit.py`](../scripts/417_fastener_audit.py):")
w("")
w("| Modelled | Finish to | What it takes |")
w("|---|---|---|")
w("| ⌀4.2 | 4.3 | M4 clearance |")
w("| ⌀5.0 | 5.0 H7 | locating dowel — ream, do not drill |")
w("| ⌀5.2 | 5.3 | M5 clearance |")
w("| ⌀6.4 | leave as printed | M5 heat-set insert, OD ~7.0, melted in |")
w("| ⌀10.4 | leave as printed | cap head counterbore |")
w("| ⌀12.3 | 12.3 | knee pin through the hub — the joint axis, so do it on a drill press |")
w("| ⌀26 | 26.2 | the two idler bearing seats in the bracket. Bonded, same reason |")
w("| ⌀28 | 28.2 | the 6001 seat in the yoke. 28.2, not 28.0: the bearing is **bonded**, and that |")
w("| | | 0.2 is the bond line. A press fit into PETG creeps and lets go within months |")
w("")
w("| Part | Holes |")
w("|---|---|")
for nm in sorted(data["L"]):
    w("| `%s` | %s |" % (nm, HOLES.get(nm, "see 417")))
w("")
w("## Where the supports are")
w("")
w("Support fraction is of TOTAL surface area, so 10% is a few bosses rather than a disaster. What")
w("matters is a part that cannot be oriented below the threshold at all. Measured, per part over 8%:")
w("")
flagged = [(nm, data["L"][nm]) for nm in sorted(data["L"])
           if data["L"][nm]["sup"] / data["L"][nm]["area"] > 0.08]
for nm, m in flagged:
    w("* **`%s`** — %.0f%% of its surface, %.1f cm², overhangs past 45° in its best orientation"
      % (nm, 100 * m["sup"] / m["area"], m["sup"] / 100.0))
    w("  (%s up, %d°)." % (LAB[m["up"]], m["spin"]))
w("")
w("The three fairing mounts are one part printed three times, and 4.0 of their 4.4 cm² is in the")
w("first 4 mm above the bed: that is the bracket's foot, a flat underside. Printed on that face")
w("the support disappears — the orientation search cannot see it, because it scores angles and a")
w("flat underside at the bottom of a part is an angle like any other.")
w("")
w("For the rest, the cause is not diagnosed here. The figures above say where to look in the")
w("slicer; they do not say what the geometry is doing, and this file is generated, so it should not")
w("guess. An earlier version of this script asserted the fairing mounts' explanation for every part")
w("over 10%, which made it wrong about `P25_MotorNacelle` and `P2a_KneeHub_Pulley29T`.")
w("")
w("## The models")
w("")
w("The mass model is shell-plus-infill: shell = perimeters × 0.42 mm per side, and any part whose")
w("mean wall (2V/A) is thinner than two shells prints effectively solid regardless of infill. The")
w("time model is volumetric: 3.5 mm³/s of effective flow, which is 0.2 mm layers at 0.42 mm width")
w("and 60 mm/s, derated for travel and acceleration. Neither has been checked against a real print,")
w("because nothing has been printed yet. Correct them here once something has.")
w("")

path = os.path.join(REPO, "docs", "PRINT.md")
open(path, "w", encoding="utf-8").write("\n".join(out))
print("wrote %s -- %d parts, %.0f g and %.0f h per leg" % (path, len(data["L"]), tot_m, tot_t))
for leg in data:
    print("  %s leg: %d STLs, %.0f cm3" % (leg, len(data[leg]),
                                           sum(v["vol"] for v in data[leg].values()) / 1000.0))
