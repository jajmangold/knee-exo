# -*- coding: utf-8 -*-
"""Replace the Delrin L-gibs with MGN7H recirculating guides on the 20 mm side faces.

Why: the guide reaction is only 176 N, so capacity was never the question -- every rail on
the market is 10x over. The question is friction, and specifically that acetal on aluminium
is SLIDING contact: ~70 N, 7.7% of the belt pull, with stick-slip, a breakaway force
different from the running force, and a mu that wanders with wear and temperature. On a
device whose control plan is to start at 10% assist and creep up under a physio's
supervision, notchy low-level torque is the thing that makes it untunable. Rolling contact
takes that to 1.4 N.

Placement: the 20 mm SIDE faces, rail centre Z = 98, so the block spans Z 88..108 --
exactly flush with the extrusion.

Getting here took two wrong answers, both from checks that were too small:

  * "the side faces clash with the belt" came from placing the rail at mid-face (Z ~98
    centre was never tried) and, worse, from assuming the belt runs share length with the
    blocks. They never do. Run A spans Y 0..carrA-24 and carriage A's first block starts
    at carrA-18, so there is a constant 6 mm gap at every pose -- the same construction
    that keeps the ball nut clear of the belt. Swept over all 107 poses the block/belt
    overlap is 0.00 cm3 at every rail height tried.
  * "it clears the cuff" came from testing the ANTERIOR block only. The posterior side is
    tighter, because the cuff's neck -- where its mounting band joins its limb wrap --
    crosses X 29..36 at Z 76..88. That rules out a low rail on the posterior side but not
    a high one.

MGN7, not MGN9, and the reason is 0.9 mm. The blocks never share length with the belt --
run A ends at carrA-24 and carriage A's first block starts later, the same construction
that keeps the ball nut clear -- but the RAIL is continuous, so it does. The belt's inner
face is at |X| 35.6 and the side face at |X| 30, leaving 5.6 mm: an MGN9 rail stands
6.5 mm proud and cuts 0.9 mm into the belt, an MGN7 stands 4.8 and clears by 0.8.

Three further things the posterior side needs, none of which apply to the anterior:
  * the blocks move distal of the sprung anchor (Y0+34 and Y0+68 rather than Y0+6 and
    Y0+57), because the anchor occupies Y0..Y0+32 at X 34..43;
  * the anchor itself shifts outboard to X 35.6..44.2, clearing the rail by 0.8 mm;
  * the tension spring rises to Z 113 so the block passes under it.
Block spacing drops to 34 mm as a result, so the 18.0 N.m yaw becomes 529 N per block
against MGN7H's ~1.0 kN dynamic rating -- a 1.9x margin on a peak, not a continuous, load.

The rail centre is Z = 104.5, not 98. Z = 98 is straight over the extrusion's V-slot
(cut at Z 95..101), so the rail's M2 screws would have nothing to bite -- a mounting
question no interference sweep can ask. The face's outboard solid band, Z 101..108, takes
the rail and puts the block at Z 96..113.

Rail lengths are cut to what the blocks sweep rather than to the extrusion: 165 mm
anterior, 145 mm posterior. They differ because the carriages sit at different heights
and B's blocks were pushed distal of the anchor.

This keeps the lateral 60 mm face completely free, which matters if the screws ever move
round to the front.

TWO blocks per carriage, not one. The 18.0 N.m yaw would have to be reacted as a moment by
a single block, and an MGN9H is rated around 9-13 N.m. Spaced 51 mm apart along Y it
becomes a force couple of ~353 N per block, against a 1.86 kN dynamic rating.

This supersedes the carriage pockets from 240_nut1610.py -- the nuts there are unchanged.
P10a..P10d change from machined Delrin gibs to bought MGN9H blocks; they keep their object
names so the pose and sweep groups still pick them up, but the labels change and
219_stl.py no longer exports them.

Run after 240_nut1610.py and 241_fixups.py.
"""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V

def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration when no document is open, which
    surfaces from freecadcmd as the unhelpful "<unknown exception data>" -- and is why these
    older build scripts could not be re-run without the GUI at all.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace(chr(92), "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()

t = globals().get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
globals()["_kx_timer"] = None

for o in doc.Objects:
    if o.TypeId.startswith("Part::"):
        o.Placement = FreeCAD.Placement()
doc.recompute()

O = lambda n: doc.getObject(n)


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

# ---- MGN9 geometry -------------------------------------------------------
RAIL_W, RAIL_H = 7.0, 4.8        # MGN7: across the face (Z), proud of the face (X)
BLK_W, BLK_H = 17.0, 8.0         # MGN7H: 17 across, 8 total assembly height
FACE_X = 30.0                    # the extrusion's 20 mm side faces
# Rail centre. It cannot be 98 -- that is straight over the V-slot, which 194_layout.py
# cuts at Z 95..101, so every M2 mounting screw would drop into the slot with nothing to
# grip and M2 T-nuts do not exist for a 6 mm slot. The face leaves two solid bands, Z
# 88..95 and Z 101..108, each 6.9 mm against the rail's 7. The inboard band puts the block
# at Z 83..100, back into the thigh cuff on the posterior side, so: the outboard band.
ZC = 104.5                       # rail Z 101..108, block Z 96..113
# Rail length: only what the blocks actually sweep, plus margin. They differ because the
# carriages sit at different heights and B's blocks were pushed distal of the anchor.
RAIL_Y_A = (62.0, 227.0)         # blocks sweep Y 67.0..220.8
RAIL_Y_B = (140.0, 284.7)        # blocks sweep Y 146.7..280.5
BLK_Y_A = ((6.0, 37.5), (60.0, 91.5))    # carriage A: free of the anchor, 54 mm apart
BLK_Y_B = ((34.0, 65.5), (68.0, 99.5))   # carriage B: distal of the anchor, 34 mm apart

# ---- carriage geometry, as 240 left it -----------------------------------
NUT_R, SCR_R = 18.0, 7.9
NUT_Y = (36., 78.)
PLATE = (108., 118.)
BODY_Z, BODY_X = (84., 128.), 80.0
ANC_Z = (92., 130.)


def need(sh, label, solids=1):
    assert sh.isValid(), "%s invalid" % label
    assert len(sh.Solids) == solids, "%s solids=%d" % (label, len(sh.Solids))
    assert sh.isClosed(), "%s not closed" % label
    return sh


# --------------------------------------------------------------- the rails
for nm, lab, g, RAIL_Y in (("A9_RailMGN9_A", "A9_RailMGN7H_A", -1.0, RAIL_Y_A),
                           ("A9b_RailMGN9_B", "A9b_RailMGN7H_B", 1.0, RAIL_Y_B)):
    r = bx(*rng(g * FACE_X, g * (FACE_X + RAIL_H)), RAIL_Y[0], RAIL_Y[1],
           ZC - RAIL_W / 2, ZC + RAIL_W / 2)
    o = O(nm) or doc.addObject("Part::Feature", nm)
    o.Shape = r
    o.Label = lab
    if getattr(o, "ViewObject", None) is not None:  # absent headless
        o.ViewObject.Visibility = True
    b = r.BoundBox
    print("%-16s X %+6.1f..%+6.1f  Y %+6.1f..%+6.1f = %5.1f mm  Z %+6.1f..%+6.1f"
          % (lab, b.XMin, b.XMax, b.YMin, b.YMax, b.YLength, b.ZMin, b.ZMax))

# ------------------------------------------------- blocks and the carriages
SPEC = (("A", -1., C0, "P3_Carriage", ("P10a_Slider_Delrin", "P10b_Slider_Delrin"), False, BLK_Y_A),
        ("B", 1., C1, "P3b_CarriageB", ("P10c_Slider_Delrin", "P10d_Slider_Delrin"), True, BLK_Y_B))
for tag, g, C, cname, blocks, sprung, BLK_Y in SPEC:
    Y0, Y1 = C - 24., C + 78.
    SCX = g * 58.
    ax = rng(g * (BIN - 2.5), g * (BOUT + 2.5))

    # the two MGN9H blocks
    for bn, (by0, by1) in zip(blocks, BLK_Y):
        blk = bx(*rng(g * FACE_X, g * (FACE_X + BLK_H)), Y0 + by0, Y0 + by1,
                 ZC - BLK_W / 2, ZC + BLK_W / 2)
        # a real block is an inverted U over the rail, not a solid box -- otherwise it
        # interpenetrates the rail and every sweep reports it as a clash
        blk = blk.cut(bx(*rng(g * (FACE_X - 1.), g * (FACE_X + RAIL_H + 0.5)),
                         Y0 + by0 - 1, Y0 + by1 + 1,
                         ZC - RAIL_W / 2 - 0.5, ZC + RAIL_W / 2 + 0.5))
        blk = need(blk.removeSplitter(), bn)
        ob = O(bn)
        ob.Shape = blk
        ob.Label = bn.replace("Slider_Delrin", "BlockMGN7H")

    ca = bx(*rng(g * 34., g * 17.), Y0, Y1, *PLATE)     # plate back to its original span
    ca = ca.fuse(bx(*rng(g * BODY_X, g * 34.), Y0, Y1, *BODY_Z))
    ca = ca.fuse(bx(ax[0], ax[1], Y0, Y0 + 38., *ANC_Z)).removeSplitter()
    ca = ca.cut(cy(SCR_R + 1.1, Y0 - 1, Y1 + 1, SCX, SCR_Z))
    ca = ca.cut(cy(NUT_R + 0.2, C + NUT_Y[0] - 1., C + NUT_Y[1] + 1., SCX, SCR_Z))
    # block pockets, 0.5 mm clearance -- these replace the two Delrin tongue pockets
    for by0, by1 in BLK_Y:
        ca = ca.cut(bx(*rng(g * (FACE_X - 1.), g * (FACE_X + BLK_H + 0.5)),
                       Y0 + by0 - 0.5, Y0 + by1 + 0.5,
                       ZC - BLK_W / 2 - 0.5, ZC + BLK_W / 2 + 0.5))
    # and a clearance slot for the rail itself, full length
    ca = ca.cut(bx(*rng(g * (FACE_X - 1.), g * (FACE_X + RAIL_H + 0.5)), Y0 - 1, Y1 + 1,
                   ZC - RAIL_W / 2 - 0.5, ZC + RAIL_W / 2 + 0.5))
    ca = ca.cut(bx(-31., 31., Y0 - 1, Y1 + 1, 86., PLATE[0]))     # clear the extrusion
    if sprung:
        ca = ca.cut(bx(*rng(g * (BIN + 0.0), g * (BOUT + 3.2)), Y0 - 1., Y0 + 34., 94., 128.))
        ca = ca.cut(cy(5.5, Y0 + 30., Y0 + 40., g * (BIN + BOUT) / 2, 119.))
        ca = ca.cut(bx(*rng(g * (BOUT + 2.), g * (BOUT + 8.)), Y0 + 6., Y0 + 22., 104., 116.))
    else:
        ca = ca.cut(bx(*rng(g * BIN, g * BOUT), Y0 + 6., Y0 + 13., *BZ))
        for k in range(3):
            ca = ca.cut(cz(2.1, ANC_Z[1] - 13., ANC_Z[1] + 1, g * (BIN + BOUT) / 2, Y0 + 20. + k * 7.))
    for k in range(4):
        ca = ca.cut(cz(2.1, SCR_Z + NUT_R - 4., BODY_Z[1] + 1., SCX - 9. + 6. * k, C + 42. + k * 9.))
    ca = ca.cut(O("P21_ShellAnterior").Shape).removeSplitter()
    need(ca, cname)
    O(cname).Shape = ca
    b = ca.BoundBox
    print("carriage %s  X %+6.1f..%+6.1f  Z %+6.1f..%+6.1f  %5.1f cm3  (2x MGN7H, %.0f mm apart)"
          % (tag, b.XMin, b.XMax, b.ZMin, b.ZMax, ca.Volume / 1000.,
             (BLK_Y[1][0] + BLK_Y[1][1]) / 2 - (BLK_Y[0][0] + BLK_Y[0][1]) / 2))

# ---------------- the sprung anchor moves outboard, the spring rises
g, Y0 = 1.0, C1 - 24.
blk = bx(BIN + 0.05, BOUT + 3.1, Y0, Y0 + 32., 95., 127.)
blk = blk.cut(bx(BIN, BOUT, Y0 + 5., Y0 + 12., *BZ))
for k in range(3):
    blk = blk.cut(cz(2.1, 114., 128., (BIN + BOUT) / 2, Y0 + 18. + k * 6.))
blk = need(blk.removeSplitter(), "P11_SprungAnchor")
O("P11_SprungAnchor").Shape = blk
b = blk.BoundBox
print("P11_SprungAnchor X %+.1f..%+.1f (rail reaches %+.1f)" % (b.XMin, b.XMax, 30. + RAIL_H))
# the block now reaches Z 113, so the spring has to clear it: axis 119 -> Z 114..124,
# still well inside the belt's Z 96..126 band
sp = cy(5.0, Y0 + 32., Y0 + 39., (BIN + BOUT) / 2, 119.)
O("A8_TensionSpring").Shape = sp
print("A8_TensionSpring axis Z 119 (was 111) so the block at Z 96..113 passes under it")

# the anchor moved outboard into the Hall board, so that moves too -- it still sits
# inside the carriage's existing pocket at X 43.1..49.1
hb = bx(BOUT + 3.7, BOUT + 7.7, Y0 + 7., Y0 + 21., 105., 115.)
O("P13_HallTension").Shape = hb
b = hb.BoundBox
print("P13_HallTension  X %+.1f..%+.1f  (anchor ends %+.1f, screw starts %+.1f)"
      % (b.XMin, b.XMax, BOUT + 3.1, 58.0 - 7.9))

# The cuff is left alone: the rails sit at Z 89.5..106.5, above its Z 88 top.

# ------------------------------------------------------------------ checks
ok = True
MOVERS = ["P3_Carriage", "P3b_CarriageB", "P10a_Slider_Delrin", "P10b_Slider_Delrin",
          "P10c_Slider_Delrin", "P10d_Slider_Delrin"]
STATICS = ["A1_Extrusion_20x60_VSlot", "A9_RailMGN9_A", "A9b_RailMGN9_B", "P5_ThighCuff",
           "REF_Thigh", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun", "P21_ShellAnterior"]
for a_, b_ in (("P11_SprungAnchor", "P13_HallTension"),
               ("P11_SprungAnchor", "A9b_RailMGN9_B"),
               ("P13_HallTension", "A2c_BallScrew_LH"),
               ("A8_TensionSpring", "P10c_Slider_Delrin")):
    v = O(a_).Shape.common(O(b_).Shape).Volume / 1000.
    print("  %-20s vs %-22s %7.3f cm3 %s" % (a_, b_, v, "" if v < 0.01 else "<-- FAIL"))
for m in MOVERS:
    for s in STATICS:
        if m == s:
            continue
        a, b_ = O(m), O(s)
        if not a or not b_ or not a.Shape.BoundBox.intersect(b_.Shape.BoundBox):
            continue
        v = a.Shape.common(b_.Shape).Volume / 1000.
        # a block is SUPPOSED to envelop its rail
        if v > 0.01:
            ok = False
            print("  FAIL %-22s vs %-24s %7.3f cm3" % (m, s, v))
for bn in ("P10a_Slider_Delrin", "P10c_Slider_Delrin"):
    rail = "A9_RailMGN9_A" if bn == "P10a_Slider_Delrin" else "A9b_RailMGN9_B"
    v = O(bn).Shape.common(O(rail).Shape).Volume / 1000.
    print("  %-22s vs its rail %6.3f cm3 (0 = C-section clears it)" % (bn, v))
print("  static checks: %s" % ("all clear" if ok else "SEE ABOVE"))

doc.recompute()
doc.save()
print("done")
