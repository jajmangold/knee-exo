# -*- coding: utf-8 -*-
"""Two clashes the SFU1610 carriage rebuild introduced, both found by the 107-pose sweep.

1. P3b_CarriageB vs P5_ThighCuff, 8.67 cm3 at X 34..70, Z 84..88. The carriage body had
   to drop to Z=84 to capture the OD 36 nut, and the thigh cuff tops out at Z=88 --
   but only on the +X side, where it wraps further round the limb, which is why carriage
   A is clean and only B clashes. The carriage cannot come back up (the nut needs the
   room), so the cuff gets a corridor cut out of it. The cuff's job is to wrap the limb
   and it bolts to the rail's medial face at |X| < 30; the material at X 32..82 and
   Z > 83 is wrap-around it does not need.

The Hall board is untouched: an earlier attempt moved the screws in to X=+/-56 to solve a
different clash, which put the screw shaft at X=48.1 and pinched P13 between it and the
sprung anchor at X=42.6. The screws stayed at +/-58 instead.

Run after 240_nut1610.py.
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

for o in doc.Objects:
    if o.TypeId.startswith("Part::"):
        o.Placement = FreeCAD.Placement()
doc.recompute()

O = lambda n: doc.getObject(n)


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def rng(a, b):
    return (min(a, b), max(a, b))


K = json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
C1 = K["C1"]
BIN, BOUT = K["belt_x"]

# --------------------------------------------- 1. corridor through the cuff
# Carriage B sweeps Y (C1-24) .. (C1+78) over 68 mm of travel, so the corridor has to
# cover the whole band, not just the neutral pose.
cuff = O("P5_ThighCuff")
before = cuff.Shape.Volume / 1000.
if cuff.Shape.BoundBox.ZMax > 83.5:
    cut = bx(32.0, 82.0, 100.0, 300.0, 83.0, 95.0)
    trimmed = cuff.Shape.cut(cut).removeSplitter()
    assert trimmed.isValid(), "cuff invalid"
    assert len(trimmed.Solids) == 1, "cuff severed into %d solids" % len(trimmed.Solids)
    cuff.Shape = trimmed
    b = trimmed.BoundBox
    print("P5_ThighCuff  %.1f -> %.1f cm3   X %+.1f..%+.1f  Z %+.1f..%+.1f"
          % (before, trimmed.Volume / 1000., b.XMin, b.XMax, b.ZMin, b.ZMax))
else:
    print("P5_ThighCuff already trimmed")

# ------------------------------ P13 back where 196_carr.py put it (idempotent)
# The +/-56 experiment moved it; 240 rebuilds the carriage but not the board.
g = 1.0
Y0 = C1 - 24.
hb = bx(*rng(g * (BOUT + 2.5), g * (BOUT + 7.5)), Y0 + 7., Y0 + 21., 105., 115.)
O("P13_HallTension").Shape = hb
b = hb.BoundBox
print("P13_HallTension  X %+.1f..%+.1f  (anchor ends at %+.1f, screw starts at %+.1f)"
      % (b.XMin, b.XMax, BOUT + 1.5, 58.0 - 7.9))

# ------------------------------------------------------------------- checks
ok = True
pairs = [("P3b_CarriageB", "P5_ThighCuff"), ("P3_Carriage", "P5_ThighCuff"),
         ("P13_HallTension", "A2c_BallScrew_LH"), ("P13_HallTension", "P11_SprungAnchor"),
         ("P3_Carriage", "P21_ShellAnterior"), ("P3b_CarriageB", "P21_ShellAnterior"),
         ("P5_ThighCuff", "A1_Extrusion_20x60_VSlot")]
for a, b_ in pairs:
    oa, ob = O(a), O(b_)
    if not oa or not ob:
        continue
    v = oa.Shape.common(ob.Shape).Volume / 1000.
    flag = "" if v < 0.01 else "  <-- FAIL"
    if v >= 0.01:
        ok = False
    print("  %-22s vs %-24s %7.3f cm3%s" % (a, b_, v, flag))
print("  static checks: %s" % ("all clear" if ok else "SEE ABOVE"))

doc.recompute()
doc.save()
print("done")
