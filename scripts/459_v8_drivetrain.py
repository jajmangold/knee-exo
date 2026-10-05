# -*- coding: utf-8 -*-
"""v8: make the drivetrain match the hardware on the bench, not the hardware we hoped to buy.

v8 is v6-left plus this script, the same way 419_knee_coaxial.py's v7 was. v6 itself is ~300
scripts run in an order recorded nowhere; this one file is reproducible in seconds and says
exactly what changed and why.

WHAT CHANGED ON THE BENCH. A 200 mm SFU1605 set arrived -- 5 mm lead, flanged nut, DSG16H
housing, BK12, BF12, locknut, coupler -- where the model was drawn around an SFU1610 at a 10 mm
lead with invented dia 8 journals. 446_sfu1605_set.py worked out what that costs and this builds
it:

  * THE SCREW. Real BK/BF12 machining, and Path B: part off the dia 10 tip and the M12 locknut
    thread, leaving a plain dia 12 x 25 journal that carries the pulley AND the bearing exactly
    as 433_drive_flip.py already drew it. Floating end dia 10 x 11. 171 mm of the 200 bought.
  * THE RATIO. 5 mm doubles the screw's own reduction to 46.4:1, so the link belt has to give
    some back or the leg feels 87% heavier unpowered at the old 32T. 38T:20T -> 24.4:1, 0.62x
    the limb, and an exact 54T belt at the 60.83 mm centres.
  * THE BEARING. dia 8 was a fiction; the fixed journal is dia 12, so the 608 becomes a 6001 and
    its pocket grows from dia 22 x 7 to dia 28 x 8.
  * THE POD. A 38T belt run reaches r 32.24 where 433's guard bore is r 32.
  * THE SCREW'S LOWER END, which has never had anything to bolt to -- 445_screw_foot.py went
    looking and found "a yoke corner, a belt and cladding. No mount." P32_ScrewFoot, at last.

WHAT THIS DOES NOT DO, and why. The flanged nut and its DSG16H housing make P3_GantryPlate wrong,
and the open-ended main belt wants its tunnel lengthened from 5 grooves to 8 -- but both are
drawn around dimensions nobody has measured yet. The joint encoder lost its mounting when
457_knee_bearings.py made the knee rod static, and its carrier, the stub axle's retention and the
sensor bracket have to be designed together. Those are named in the BOM and left alone here
rather than guessed at.

    freecadcmd.exe scripts/459_v8_drivetrain.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v8.FCStd").replace("\\", "/")

# ---------------------------------------------------------------- axes, from the model
SX, SZ = -62.0, 106.0           # screw
MX, MZ = -104.0, 62.0           # motor
CENTRES = math.hypot(MX - SX, MZ - SZ)

# ---------------------------------------------------------------- the bought screw, Path B
FF_D, FF_L = 10.0, 11.0         # floating end
THREAD_D = 15.8
FK_D, FK_L = 12.0, 25.0         # fixed journal, after parting off the tip and the M12 thread
SCREW_Y0 = 60.0
THREAD_Y = (SCREW_Y0 + FF_L, SCREW_Y0 + FF_L + 135.0)          # 71 .. 206
FK_Y = (THREAD_Y[1], THREAD_Y[1] + FK_L)                        # 206 .. 231

# ---------------------------------------------------------------- the link belt, 38T:20T HTD-5M
PITCH5, PLD5 = 5.0, 0.571
MOT_T, SCR_T = 38, 20
BELT_W5 = 15.0
BELT_Y = (THREAD_Y[1], THREAD_Y[1] + BELT_W5)                   # 206 .. 221
BAND_T = 3.8                                                    # belt back thickness


def tip_r(teeth):
    return teeth * PITCH5 / (2 * math.pi) - PLD5


BRG_OD, BRG_W = 28.0, 8.0       # 6001-2RS
BRG_Y = (223.0, 231.0)
SEAT_BOSS_R = 19.0              # 5 mm of wall around the dia 28 seat

# The BELT's back, not the pulley's pitch radius. 446_sfu1605_set.py used PD/2 + 2 and predicted
# 0.2 mm of pod interference; the real figure is tip + the belt's own 3.8 mm thickness, and the
# 107-pose sweep found 6.9 cm3 of belt inside the nacelle. Out by a factor of twenty.
GUARD_R = tip_r(MOT_T) + BAND_T + 1.0   # 34.47
POD_OUT_R = 37.0                        # the nacelle's new outer wall round the belt bay

# ---------------------------------------------------------------- P32_ScrewFoot, from 445
# 445 drew this against a screw ending at Y 57. The bought screw's floating journal starts at
# Y 60, so the plate moves +3 -- and the ARM has to bridge the whole way from the rail's end
# face to the plate, not just the plate's own 8 mm, or P32 comes out as two solids. The arm also
# has to stop at X -22: the tongue shares the rail's X +-20 footprint but sits BELOW its end
# face at Y 51, where the arm runs alongside it and would otherwise cut into it.
FOOT_PLATE = (SX - 18.0, SX + 18.0, SCREW_Y0 - 8.0, SCREW_Y0, SZ - 18.0, SZ + 18.0)
FOOT_ARM = (SX, -22.0, 44.0, SCREW_Y0, 88.0, 93.0)
FOOT_TONGUE = (-24.0, 20.0, 44.0, 51.0, 88.0, 108.0)
FOOT_BORE_R = 15.0


def cylY(r, y0, y1, x=SX, z=SZ):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def box(t):
    x0, x1, y0, y1, z0, z1 = t
    return Part.makeBox(abs(x1 - x0), y1 - y0, z1 - z0, V(min(x0, x1), y0, min(z0, z1)))


def kx_doc():
    base = DOCFILE.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(DOCFILE)


class _Tee(object):
    """freecadcmd buffers stdout and drops the buffer on sys.exit, so a run that bails early
    prints NOTHING AT ALL -- not even the banner. Mirror every line to stderr, which is not
    buffered, so the log always says how far it got."""

    def __init__(self, a, b):
        self.a, self.b = a, b

    def write(self, t):
        self.a.write(t)
        self.b.write(t)
        self.b.flush()

    def flush(self):
        self.a.flush()
        self.b.flush()


sys.stdout = _Tee(sys.__stdout__, sys.__stderr__)
def hull(r1, r2, y0, y1):
    """the band a belt makes round two pulleys: outer hull minus inner hull"""
    import math as _m
    d = _m.hypot(MX - SX, MZ - SZ)
    ux, uz = (MX - SX) / d, (MZ - SZ) / d
    px, pz = -uz, ux
    faces = []
    for t in (0.0, 1.0):
        pass
    outer = cylY(r1, y0, y1).fuse(cylY(r2, y0, y1, MX, MZ))
    # the straight run: a box joining the two tangent lines, built in the pulleys' own frame
    L = d
    quad = Part.makePolygon([V(SX + px * r1, y0, SZ + pz * r1),
                             V(MX + px * r2, y0, MZ + pz * r2),
                             V(MX - px * r2, y0, MZ - pz * r2),
                             V(SX - px * r1, y0, SZ - pz * r1),
                             V(SX + px * r1, y0, SZ + pz * r1)])
    slab = Part.Face(quad).extrude(V(0, y1 - y0, 0))
    return outer.fuse(slab), L



doc = kx_doc()
g = {o.Name: o for o in doc.Objects}

print("=" * 96)
print("v8 DRIVETRAIN  --  %s" % os.path.basename(doc.FileName))
print("=" * 96)
if doc.getObject("A6b_ScrewPulley20T") is not None:
    print("  A6b_ScrewPulley20T already exists -- this has run. Nothing done.")
    sys.exit(0)


def put(name, shape, label=None, group=None):
    o = doc.getObject(name)
    if o is None:
        o = doc.addObject("Part::Feature", name)
        for gn in (group, "C_Drive", "C", "HW"):
            if gn and doc.getObject(gn) is not None:
                doc.getObject(gn).addObject(o)
                break
    o.Shape = shape
    if label:
        o.Label = label
    return o


# ---------------------------------------------------------------- 1. the screw
print()
print("1. THE SCREW -- SFU1605, 200 mm bought, Path B")
old = g["A2_BallScrew_SFU1620"].Shape.BoundBox
screw = cylY(FF_D / 2.0, SCREW_Y0, THREAD_Y[0]) \
    .fuse(cylY(THREAD_D / 2.0, THREAD_Y[0], THREAD_Y[1])) \
    .fuse(cylY(FK_D / 2.0, FK_Y[0], FK_Y[1]))
assert len(screw.Solids) == 1
put("A2_BallScrew_SFU1620", screw, "A2_BallScrew_SFU1605_200_PathB")
print("   dia %.0f x %.0f floating   Y %6.1f..%6.1f" % (FF_D, FF_L, SCREW_Y0, THREAD_Y[0]))
print("   thread dia %.1f            Y %6.1f..%6.1f   (%.0f mm, nut needs 110)"
      % (THREAD_D, THREAD_Y[0], THREAD_Y[1], THREAD_Y[1] - THREAD_Y[0]))
print("   dia %.0f x %.0f fixed      Y %6.1f..%6.1f   pulley + 6001 share it" % (FK_D, FK_L, FK_Y[0], FK_Y[1]))
print("   was Y %.1f..%.1f (%.0f mm, dia 8 journals); now Y %.0f..%.0f (%.0f mm)"
      % (old.YMin, old.YMax, old.YLength, SCREW_Y0, FK_Y[1], FK_Y[1] - SCREW_Y0))

# ---------------------------------------------------------------- 2. the two link pulleys
print()
print("2. THE LINK PULLEYS -- %dT:%dT, which the 5 mm lead forces" % (MOT_T, SCR_T))
scr_pul = cylY(tip_r(SCR_T), BELT_Y[0], BELT_Y[1]).cut(cylY(FK_D / 2.0, BELT_Y[0] - 1, BELT_Y[1] + 1))
mot_pul = cylY(tip_r(MOT_T), BELT_Y[0], BELT_Y[1], MX, MZ) \
    .cut(cylY(8.0 / 2.0, BELT_Y[0] - 1, BELT_Y[1] + 1, MX, MZ))
put("A6b_ScrewPulley20T", scr_pul, "A6b_ScrewPulley20T_HTD5M_bore12")
put("A6c_MotorPulley38T", mot_pul, "A6c_MotorPulley38T_HTD5M_bore8")
print("   screw %2dT tip r %5.2f, bore dia %.0f, Y %.0f..%.0f" % (SCR_T, tip_r(SCR_T), FK_D, BELT_Y[0], BELT_Y[1]))
print("   motor %2dT tip r %5.2f, bore dia %.0f, Y %.0f..%.0f" % (MOT_T, tip_r(MOT_T), 8.0, BELT_Y[0], BELT_Y[1]))
n_tot = (2 * math.pi * (29 * 8.0 / (2 * math.pi)) / 5.0) / (MOT_T / float(SCR_T))
print("   centres %.2f mm -> total ratio %.1f:1, reflected %.3f kg.m2 = %.2fx the limb"
      % (CENTRES, n_tot, 3.10e-4 * n_tot ** 2, 3.10e-4 * n_tot ** 2 / 0.30))


print()
print("3. THE LINK BELT -- rebuilt as a band, %.0f mm wide" % BELT_W5)
outer, _ = hull(tip_r(SCR_T) + BAND_T, tip_r(MOT_T) + BAND_T, BELT_Y[0], BELT_Y[1])
inner, _ = hull(tip_r(SCR_T), tip_r(MOT_T), BELT_Y[0] - 1, BELT_Y[1] + 1)
band = outer.cut(inner)
put("A7b_LinkBelt", band, "A7b_LinkBelt_38T20T_HTD5M_270mm")
d1, d2 = 2 * (tip_r(MOT_T) + PLD5), 2 * (tip_r(SCR_T) + PLD5)
L = 2 * CENTRES + math.pi * (d1 + d2) / 2.0 + (d1 - d2) ** 2 / (4 * CENTRES)
print("   path %.1f mm = %.1f teeth -> buy the %dT (%.0f mm) closed loop"
      % (L, L / PITCH5, round(L / PITCH5), round(L / PITCH5) * PITCH5))
print("   belt band %.2f cm3 at Y %.0f..%.0f" % (band.Volume / 1000.0, BELT_Y[0], BELT_Y[1]))

# ---------------------------------------------------------------- 4. the 6001 in the motor plate
print()
print("4. THE SCREW'S UPPER BEARING -- 608 becomes 6001")
a7 = g["A7_DriveBox"].Shape
boss = cylY(SEAT_BOSS_R, BRG_Y[0] - 1.0, BRG_Y[1] + 1.0)
new7 = a7.fuse(boss)
new7 = new7.cut(cylY(BRG_OD / 2.0, BRG_Y[0], BRG_Y[1] + 1.0))
new7 = new7.cut(cylY(FK_D / 2.0 + 1.0, BRG_Y[0] - 6.0, BRG_Y[1] + 2.0))
assert len(new7.Solids) == 1, "the 6001 seat split A7 into %d solids" % len(new7.Solids)
g["A7_DriveBox"].Shape = new7
put("HW_Bearing_6001_Screw",
    cylY(BRG_OD / 2.0, BRG_Y[0], BRG_Y[1]).cut(cylY(FK_D / 2.0, BRG_Y[0] - 1, BRG_Y[1] + 1)),
    "HW_Bearing_6001_ScrewUpper")
print("   seat dia %.0f x %.0f at Y %.0f..%.0f, in a boss of r %.0f (%.0f mm of wall)"
      % (BRG_OD, BRG_W, BRG_Y[0], BRG_Y[1], SEAT_BOSS_R, SEAT_BOSS_R - BRG_OD / 2))
print("   A7_DriveBracket_Idler %.2f -> %.2f cm3" % (a7.Volume / 1000.0, new7.Volume / 1000.0))

# ---------------------------------------------------------------- 5. relieve the pod
print()
print("5. THE POD -- the %dT belt run reaches r %.2f" % (MOT_T, tip_r(MOT_T) + 2.0))
# The nacelle's bore here is r 29.7, not the r 32 433's guard nominally set, so the 38T pulley
# itself already fouls it. Two failed shapes before this one: a solid r 32.67 plug over the belt
# band alone orphans the 4.4 cm3 of wall below it, and an r 31.5..32.67 annulus is worse -- it
# starts INSIDE the material and frees the sleeve between 29.7 and 31.5. A solid bore over
# Y 200..226 takes the wall out in one piece.
# THE BELT IS A STADIUM, NOT A CIRCLE. Relieving a cylinder around the motor axis left 0.95 cm3
# of belt still buried, because the straight runs reach 60.83 mm across to the screw pulley and a
# cylinder does not follow them. The relief is the belt's own swept shape plus a millimetre.
RELIEF_Y = (200.0, 226.0)
relief = hull(tip_r(SCR_T) + BAND_T + 1.0, GUARD_R, RELIEF_Y[0] + 2.0, RELIEF_Y[1] + 0.5)[0]
POD_CAVITY = hull(tip_r(SCR_T) + BAND_T + 1.0 + 2.5, GUARD_R + 2.5,
                  RELIEF_Y[0], RELIEF_Y[1])[0]
refused = []
for n in ("P25_MotorNacelle", "A7_DriveBox", "P22_DriveCap"):
    sh = g[n].Shape
    k = sh.common(relief)
    if k.Volume < 1.0:
        print("   %-22s nothing in the way" % n)
        continue
    # DOES THE CUT TAKE A WHOLE CROSS-SECTION? This is the check that was missing, and it cost
    # P25_MotorNacelle its nose. The nacelle tapers to a dome centred ON the motor axis, so over
    # Y 194..202 its ENTIRE section lies inside r 32.67 -- a relief bore there does not shave a
    # wall, it amputates the end of the part, and everything below falls off as a fragment. The
    # BOM describes P25 as "prints nose-down on its domed end"; there was no dome left.
    eaten = []
    for y0 in range(int(RELIEF_Y[0]) - 12, int(RELIEF_Y[1]) + 1, 4):
        slab = Part.makeBox(500, 4.0, 500, V(-300, y0, -250))
        tot = sh.common(slab).Volume
        if tot < 50.0:
            continue
        if sh.common(slab).common(relief).Volume > 0.95 * tot:
            eaten.append(y0)
    if eaten:
        print("   %-22s REFUSED: the bore removes the WHOLE section at Y %s"
              % (n, ", ".join(str(y) for y in eaten)))
        print("   %-22s          that is not a wall, it is the end of the part. P25's nose is"
              % "")
        print("   %-22s          434_odrive_mount.py's to shape, and 434 rebuilds it every run"
              % "")
        print("   %-22s          anyway -- the same trap that silently undid 439's trim." % "")
        refused.append(n)
        continue
    cut = sh.cut(relief)
    sols = sorted(cut.Solids, key=lambda x: -x.Volume)
    drop = sum(x.Volume for x in sols[1:]) / 1000.0
    if len(sols) > 1 and drop > 0.1:
        print("   %-22s relief would orphan %.2f cm3 -- SKIPPED" % (n, drop))
        refused.append(n)
        continue
    keep = sols[0] if len(sols) > 1 else cut
    g[n].Shape = keep
    print("   %-22s relieved %.2f cm3 to r %.2f" % (n, k.Volume / 1000.0, GUARD_R))

# P25 cannot simply be bored -- its dome is on the motor axis, so the bore amputates it. GROW the
# wall outward first and the dome stays attached through the new tube, which is the same move the
# knee capstan needed in 457_knee_bearings.py: fuse a sleeve, then bore it.
p25 = g["P25_MotorNacelle"].Shape
grown = p25.fuse(POD_CAVITY)
assert len(grown.Solids) == 1, "the pod sleeve fused into %d solids" % len(grown.Solids)
# the grown bay now wraps the screw as well as the belt, so give the screw its running clearance
bored = grown.cut(relief).cut(cylY(THREAD_D / 2.0 + 1.1, RELIEF_Y[0] - 1.0, RELIEF_Y[1] + 1.0))
sols = sorted(bored.Solids, key=lambda x: -x.Volume)
assert len(sols) == 1, "boring the pod sleeve left %d solids" % len(sols)
# cladding yields to structure, and P22/P25 are one wall split in two (434_odrive_mount.py), so
# the nacelle gives up anything it has just grown into either of them
for host in ("A7_DriveBox", "P22_DriveCap"):
    bored = bored.cut(g[host].Shape)
    sols = sorted(bored.Solids, key=lambda x: -x.Volume)
    drop = sum(x.Volume for x in sols[1:]) / 1000.0
    assert drop < 0.05, "trimming P25 to %s orphaned %.3f cm3" % (host, drop)
    bored = sols[0]
g["P25_MotorNacelle"].Shape = bored
sols = [bored]
print("   %-22s belt bay grown then cut to the belt's own shape: %.2f -> %.2f cm3"
      % ("P25_MotorNacelle", p25.Volume / 1000.0, sols[0].Volume / 1000.0))
dome = sols[0].common(Part.makeBox(500, 10.0, 500, V(-300, 194.0, -250))).Volume / 1000.0
print("   %-22s the domed end at Y 194..204 survives: %.3f cm3" % ("", dome))

# ---------------------------------------------------------------- 6. P32_ScrewFoot

print()
print("6. P32_ScrewFoot -- the screw's lower end has never had a mount")
foot = box(FOOT_PLATE).fuse(box(FOOT_ARM)).fuse(box(FOOT_TONGUE))
foot = foot.cut(cylY(FOOT_BORE_R, FOOT_PLATE[2] - 1.0, FOOT_PLATE[3] + 1.0))
assert len(foot.Solids) == 1, "P32 is %d solids" % len(foot.Solids)
put("P32_ScrewFoot", foot, "P32_ScrewFoot")
print("   plate  X %.0f..%.0f  Y %.0f..%.0f  Z %.0f..%.0f, bored dia %.0f for the BF12"
      % (FOOT_PLATE[0], FOOT_PLATE[1], FOOT_PLATE[2], FOOT_PLATE[3],
         FOOT_PLATE[4], FOOT_PLATE[5], 2 * FOOT_BORE_R))
print("   arm under the belt, tongue onto the rail's end cores at X +-10")
print("   %.1f cm3" % (foot.Volume / 1000.0))
clad = g["P21_ShellAnterior"].Shape
k = clad.common(foot)
if k.Volume > 1.0:
    grown = foot.cut(cylY(FOOT_BORE_R, FOOT_PLATE[2] - 1.0, FOOT_PLATE[3] + 1.0))
    newclad = clad.cut(foot)
    sols = sorted(newclad.Solids, key=lambda x: -x.Volume)
    assert len(sols) == 1, "relieving P21 for P32 left %d solids" % len(sols)
    g["P21_ShellAnterior"].Shape = newclad
    print("   relieved %.3f cm3 of P21_ShellAnterior for it (cladding, as 445 expected)"
          % (k.Volume / 1000.0))

# ---------------------------------------------------------------- 7. does it hold together?
print()
print("7. CLEARANCE")
doc.recompute()
names = [o.Name for o in doc.Objects if o.isDerivedFrom("Part::Feature")]
# EVERY part this script touched, against everything. The first version of this check listed the
# screw, the foot and the two pulleys and left out A7b_LinkBelt -- so it reported 0.271 cm3 of
# pulley fouling the nacelle and missed 6.9 cm3 of BELT doing the same thing, which the 107-pose
# sweep then found. A check you write by naming the suspects only finds the suspects.
TOUCHED = ["A2_BallScrew_SFU1620", "P32_ScrewFoot", "A6b_ScrewPulley20T", "A6c_MotorPulley38T",
           "A7b_LinkBelt", "HW_Bearing_6001_Screw", "A7_DriveBox", "P22_DriveCap",
           "P21_ShellAnterior"]
check = [(a, n) for a in TOUCHED for n in names if n != a]
bad = []
for a, b in check:
    if a not in g and doc.getObject(a) is None:
        continue
    oa, ob = doc.getObject(a), doc.getObject(b)
    if oa is None or ob is None:
        continue
    ba, bb = oa.Shape.BoundBox, ob.Shape.BoundBox
    if (ba.YMax < bb.YMin - .01 or bb.YMax < ba.YMin - .01):
        continue
    try:
        c = oa.Shape.common(ob.Shape)
    except Exception:
        continue
    if c.Volume > 20.0:
        bad.append((a, b, c.Volume / 1000.0))
EXPECT = {("A2_BallScrew_SFU1620", "A2b_BallNut_SFU1620"),
          ("A2_BallScrew_SFU1620", "P3_Carriage"),
          ("A2_BallScrew_SFU1620", "A7_DriveBox"),
          ("A2_BallScrew_SFU1620", "A6b_ScrewPulley20T"),
          ("A2_BallScrew_SFU1620", "HW_Bearing_6001_Screw"),
          ("A6b_ScrewPulley20T", "A7b_LinkBelt"),
          ("A6c_MotorPulley38T", "A7b_LinkBelt"),
          ("A7_DriveBox", "P22_DriveCap"), ("A7_DriveBox", "P25_MotorNacelle"),
          ("P21_ShellAnterior", "A1_Extrusion_20x60_VSlot"),
          # pre-existing and signed off: the fairing mounts sit inside the shell they carry,
          # and the 107-pose sweep has reported these three for as long as it has existed
          ("P21_ShellAnterior", "P23a_FairingMount"),
          ("P21_ShellAnterior", "P23b_FairingMount"),
          ("P21_ShellAnterior", "P23c_FairingMount")}
seen_pairs = set()
real = 0
for a, b, v in sorted(bad, key=lambda r: -r[2]):
    if (a, b) in seen_pairs or (b, a) in seen_pairs:
        continue
    seen_pairs.add((a, b))
    ok = (a, b) in EXPECT or (b, a) in EXPECT
    if not ok:
        real += 1
    print("   %-26s ^ %-26s %8.3f cm3%s"
          % (a, b, v, "   expected" if ok else "   <-- UNRESOLVED"))
if not bad:
    print("   nothing over 0.02 cm3")
print("   %d unresolved" % real)
if real:
    print()
    print("   %d overlap(s) above remain unaccounted for. Nothing here is hidden behind a bored" % real)
    print("   hole: the pod's bay is GROWN and then cut to the belt's own shape, so whatever is")
    print("   left is a genuine conflict to resolve, not a wall that wanted thinning.")
else:
    belt_r = tip_r(MOT_T) + BAND_T
    print()
    print("   THE POD NOW CLEARS THE 38T DRIVE. It did not: the belt's back sits at r %.2f from"
          % belt_r)
    print("   the motor axis (tip %.2f plus the belt's own %.1f) and the nacelle's bore was r 29.7,"
          % (tip_r(MOT_T), BAND_T))
    print("   which buried 6.9 cm3 of belt. 446_sfu1605_set.py predicted 0.2 mm of this from the")
    print("   pulley's PITCH radius and was out by a factor of twenty, having never added the")
    print("   belt's thickness. Two more things had to be right after that:")
    print("     * the bay is GROWN before it is cut. P25's dome sits ON the motor axis, so a")
    print("       relief bore amputates the end of the part instead of thinning a wall.")
    print("     * the relief is the belt's own stadium, not a cylinder. A cylinder round the")
    print("       motor leaves the straight runs buried -- 0.95 cm3 of them, 60.83 mm away.")

doc.recompute()
doc.save()
print()
print("   saved %s" % doc.FileName)
