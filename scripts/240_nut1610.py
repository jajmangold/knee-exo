# -*- coding: utf-8 -*-
"""Switch the ball nuts from OD 28 to OD 36 -- i.e. actually build the SFU1610 the
drivetrain analysis calls for -- and resize the carriages to house them.

Why this is now a free change: 311_nut_belt.py showed the "1610 nut fouls the belt by
1.1 mm" claim was an X-projection that ignored Y. The nut sits at carrA + 36 and its belt
run ends at carrA - 24, a constant 60 mm apart at every pose, so the overlap is 0.000 cm3
for OD 28, OD 36 and OD 40 alike.

What does have to move is the carriage body. At NUT_R = 18 the nut bore is 36.4 mm across,
while 196_carr.py's body is X 34..74, Z 90..124 -- the bore would breach the outboard face
and both Z faces, leaving an open channel instead of a captured bore.

Growing the body to X 34..80, Z 84..128 keeps a 3.8 mm wall on all three faces, but the
top-outboard corner then clips P21 by 0.495 cm3: a superellipse is not 84 wide everywhere,
and by Z = 128 its half-width has fallen to 83.3 and its inner wall to about 80.3. (Trap 2
in the README, again.)

Bringing the screws in 2 mm fixes that but pinches the Hall board between the sprung
anchor at X 42.6 and the screw shaft at X 48.1. So instead the carriage is simply CUT by
P21: the fairing's section is constant over the whole travel band (a=84, b=23, zc=115 from
Y 58 to 300), so one cut clears every pose, and it chamfers the corner to exactly the
fairing's inner surface rather than to a guess.

This supersedes the carriage geometry from 196_carr.py; nothing between 196 and here
touches the carriages or the nuts.

Run over the XML-RPC client:  python scripts/fc.py run scripts/240_nut1610.py
"""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V

doc = next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))

t = globals().get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
globals()["_kx_timer"] = None

for o in doc.Objects:                       # Shape bakes the placement in
    if o.TypeId.startswith("Part::"):
        o.Placement = FreeCAD.Placement()
doc.recompute()


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def cz(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1 - z0, V(x, y, z0), V(0, 0, 1))


def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1 - y0, V(x, y0, z), V(0, 1, 0))


def rng(a, b):
    return (min(a, b), max(a, b))


K = json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
C0, C1 = K["C0"], K["C1"]
BIN, BOUT = K["belt_x"]
BZ = tuple(K["belt_z"])
SCR_Z = K["screw"]["z"]

NUT_R = 18.0                    # SFU1610 flangeless, OD 36  (was 14.0 = OD 28)
SCX_ABS = 58.0                  # screw axis |X|
SCR_R = 7.9
NUT_Y = (36., 78.)
PLATE = (108., 118.)
OT_Z, ST_Z = (108., 114.), (95., 101.)
BODY_Z = (84., 128.)            # was (90., 124.) -- grown for the bigger bore
BODY_X = 80.0                   # was 74.0
ANC_Z = (92., 130.)

# --------------------------------------------------------- screws and motor
for nm, sx in (("A2_BallScrew_SFU1620", -SCX_ABS), ("A2c_BallScrew_LH", SCX_ABS)):
    doc.getObject(nm).Shape = cy(SCR_R, 110., 290., sx, SCR_Z)
mot = doc.getObject("A3_Motor_6374")
mot.Shape = cy(31.5, 314., 388., -SCX_ABS, 118.)
print("screws at X +/-%.0f, motor coaxial with screw A" % SCX_ABS)

# ------------------------------------------------------------------- the nuts
for nm, sx, C in (("A2b_BallNut_SFU1620", -SCX_ABS, C0), ("A2d_BallNut_LH", SCX_ABS, C1)):
    n = cy(NUT_R, C + NUT_Y[0], C + NUT_Y[1], sx, SCR_Z)
    n = n.cut(cy(8.5, C + NUT_Y[0] - 1, C + NUT_Y[1] + 1, sx, SCR_Z))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        n = n.cut(cz(2.1, SCR_Z + NUT_R - 3., SCR_Z + NUT_R + 1.,
                     sx + 11. * math.cos(a), C + NUT_Y[0] + 6. + k * 10.))
    n = n.removeSplitter()
    assert len(n.Solids) == 1 and n.isClosed(), nm
    doc.getObject(nm).Shape = n
    b = n.BoundBox
    print("%-22s OD %.0f  X %+6.1f..%+6.1f  Z %+6.1f..%+6.1f"
          % (nm, NUT_R * 2, b.XMin, b.XMax, b.ZMin, b.ZMax))

# -------------------------------------------------------------- the carriages
SPEC = (("A", -1., C0, "P3_Carriage", False),
        ("B", 1., C1, "P3b_CarriageB", True))
for tag, g, C, cname, sprung in SPEC:
    Y0, Y1 = C - 24., C + 78.
    SCX = g * SCX_ABS
    ax = rng(g * (BIN - 2.5), g * (BOUT + 2.5))
    ca = bx(*rng(g * 34., g * 17.), Y0, Y1, *PLATE)
    ca = ca.fuse(bx(*rng(g * BODY_X, g * 34.), Y0, Y1, *BODY_Z))
    ca = ca.fuse(bx(ax[0], ax[1], Y0, Y0 + 38., *ANC_Z)).removeSplitter()
    ca = ca.cut(cy(SCR_R + 1.1, Y0 - 1, Y1 + 1, SCX, SCR_Z))                  # screw channel
    ca = ca.cut(cy(NUT_R + 0.2, C + NUT_Y[0] - 1., C + NUT_Y[1] + 1., SCX, SCR_Z))
    ca = ca.cut(bx(*rng(g * 23., g * 17.), Y0 - 1, Y1 + 1, *OT_Z))            # outboard tongue
    ca = ca.cut(bx(*rng(g * 34., g * 30.), Y0 - 1, Y1 + 1, *ST_Z))            # side tongue
    ca = ca.cut(bx(*rng(g * 30., g * 17.), Y0 - 1, Y1 + 1, PLATE[0] - 22., PLATE[0]))
    ca = ca.cut(bx(*rng(g * 30., g * (-30.)), Y0 - 1, Y1 + 1, 86., PLATE[0]))
    if sprung:
        ca = ca.cut(bx(*rng(g * (BIN - 2.), g * (BOUT + 2.)), Y0 - 1., Y0 + 34., 94., 128.))
        ca = ca.cut(cy(5.5, Y0 + 30., Y0 + 40., g * (BIN + BOUT) / 2, (BZ[0] + BZ[1]) / 2))
        ca = ca.cut(bx(*rng(g * (BOUT + 2.), g * (BOUT + 8.)), Y0 + 6., Y0 + 22., 104., 116.))
    else:
        ca = ca.cut(bx(*rng(g * BIN, g * BOUT), Y0 + 6., Y0 + 13., *BZ))
        for k in range(3):
            ca = ca.cut(cz(2.1, ANC_Z[1] - 13., ANC_Z[1] + 1, g * (BIN + BOUT) / 2, Y0 + 20. + k * 7.))
    for k in range(4):                                       # nut flange bolts, from outboard
        ca = ca.cut(cz(2.1, SCR_Z + NUT_R - 4., BODY_Z[1] + 1., SCX - 9. + 6. * k, C + 42. + k * 9.))
    ca = ca.cut(cz(3.1, ST_Z[1] - 0.5, ST_Z[1] + 3.5, g * 32., Y0 + 50.))     # endstop magnet
    # chamfer the top-outboard corner to the fairing's own inner surface. P21's section is
    # constant over Y 58..300, which covers the whole travel band, so one cut does every pose.
    ca = ca.cut(doc.getObject("P21_ShellAnterior").Shape).removeSplitter()
    assert len(ca.Solids) == 1 and ca.isClosed() and ca.isValid(), \
        "%s solids=%d" % (cname, len(ca.Solids))
    o = doc.getObject(cname)
    o.Shape = ca
    b = ca.BoundBox
    print("carriage %s  X %+6.1f..%+6.1f  Z %+6.1f..%+6.1f  %5.1f cm3  %s"
          % (tag, b.XMin, b.XMax, b.ZMin, b.ZMax, ca.Volume / 1000.,
             "sprung anchor" if sprung else "rigid anchor"))

# ------------------------------------------------------------------- labels
# Names are immutable in FreeCAD; the labels were wrong and are what the STL export and
# the BOM read.
for nm, lab in (("A2_BallScrew_SFU1620", "A2_BallScrew_SFU1610"),
                ("A2c_BallScrew_LH", "A2c_BallScrew_SFU1610_LH"),
                ("A2b_BallNut_SFU1620", "A2b_BallNut_SFU1610"),
                ("A2d_BallNut_LH", "A2d_BallNut_SFU1610_LH")):
    o = doc.getObject(nm)
    if o:
        o.Label = lab

# ------------------------------------------------------------------- checks
nutA, nutB = doc.getObject("A2b_BallNut_SFU1620").Shape, doc.getObject("A2d_BallNut_LH").Shape
carA, carB = doc.getObject("P3_Carriage").Shape, doc.getObject("P3b_CarriageB").Shape
rail = doc.getObject("A1_Extrusion_20x60_VSlot").Shape
ok = True
# NOT nut.cut(carriage): the bore is a void, so the whole nut would read as "outside".
# Test the BORE against the body before the bore is cut.
for tag, g, C in (("A", -1., C0), ("B", 1., C1)):
    body = bx(*rng(g * BODY_X, g * 34.), C - 24., C + 78., *BODY_Z)
    bore = cy(NUT_R + 0.2, C + NUT_Y[0] - 1., C + NUT_Y[1] + 1., g * SCX_ABS, SCR_Z)
    out = bore.cut(body).Volume / 1000.
    thru = math.pi * (NUT_R + 0.2) ** 2 * 1.0 / 1000.      # the deliberate 1 mm Y overrun
    print("  carriage %s bore outside the body %6.3f cm3 (%.3f is the 1 mm Y overrun) -> %s"
          % (tag, out, thru, "contained" if out - thru < 0.02 else "BREACHES THE BODY"))
    if out - thru >= 0.02:
        ok = False
p21 = doc.getObject("P21_ShellAnterior").Shape
for nm in ("P3_Carriage", "P3b_CarriageB"):
    v = doc.getObject(nm).Shape.common(p21).Volume / 1000.
    print("  %-16s vs P21 fairing %6.3f cm3 %s" % (nm, v, "" if v < 0.01 else "<-- FAIL"))
    if v >= 0.01:
        ok = False
for lbl, a, b in (("nut A vs rail", nutA, rail), ("nut B vs rail", nutB, rail),
                  ("carriage A vs rail", carA, rail), ("carriage B vs rail", carB, rail)):
    v = a.common(b).Volume / 1000.
    if v > 0.01:
        ok = False
        print("  FAIL %s %.2f cm3" % (lbl, v))
print("  static checks: %s" % ("all clear" if ok else "SEE ABOVE"))

doc.recompute()
doc.save()
print("done")
