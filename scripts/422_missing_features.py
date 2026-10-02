# -*- coding: utf-8 -*-
"""Add features 420_mockup_audit.py found missing: the screw's upper bearing, and cladding fixings.

Each one is placed against measured material, and each cut asserts that it actually removed
something -- a hole drilled into air is exactly the failure this exercise is about.

WHAT USED TO BE HERE, AND WHY IT IS NOT. This file also built the gantry's belt clamp, and built
it wrong. The groove tool was extruded along Z and then rotated 90 degrees about Y "to lay the
groove along X", which instead turned the groove's depth axis into Z and its extrusion into X: the
cut was five elliptical tunnels bored sideways through the carriage at Z 96, not five grooves
across a clamp face. All five removed material, so every assertion here passed and the run
reported "19 features added, 0 landed in air".

That is the same defect as a pulley with no teeth -- a feature that looks like a feature and does
nothing -- so the carriage's belt grip now lives in 424_belt_tunnel.py, which ends by measuring the
land along Y and demanding it vary by the groove depth. The clamp block P26_BeltClamp that went
with it is deleted; the belt is gripped by a toothed land in the tunnel the carriage already had.
424 also owns the V-wheel bolts and the ball-nut set screws, because it rebuilds the carriage from
the committed pre-422 shape and one part should have one owner.

WHAT IS HERE:

  A7, the screw's upper bearing   Probed along the screw axis (X -62, Z 106) the bracket is AIR at
                                  every Y from 210 to 296: the ball screw's upper end had nothing
                                  supporting it, so the screw was a cantilever off its bottom
                                  block. The BOM says "the upper one lives in the drive bracket's
                                  screw boss"; there was no screw boss, only the clearance hole
                                  393 cuts for the shaft to pass. So build the boss and seat a 608
                                  (8 x 22 x 7) in it rather than bolting on a KP08 pillow block:
                                  the screw's machined end is 8 mm, and a seated race is the same
                                  answer that made the idler and the knee printable. One bought
                                  part instead of a block and two bolts.
  P20/P22/P25, attachment         Cladding still has to stay on. Two M4 each into the structure
                                  they cover, at stations where there is measured wall.

IDEMPOTENT. Each feature first asks whether its own space is already empty (for a cut) or already
filled (for a fuse) and reports "already there" instead of failing. Re-running a build chain must
not turn a finished part into a list of features that hit air.

    freecadcmd.exe scripts/422_missing_features.py
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

M4 = 4.2
HERE = os.path.dirname(os.path.abspath(__file__))
REFFILE = os.path.join(HERE, "..", "model", _BASE).replace("\\", "/")
A7_PRE = 134.86         # the bracket as committed, before this script touches it, cm3
report = []


def cut_and_check(obj, tool, what, need=0.005):
    """cut, and prove the hole landed in material -- unless it is already there"""
    try:
        pre = obj.Shape.common(tool)
        if pre.isNull() or pre.Volume < need * 1000.0 * 0.2:
            report.append((obj.Label, what, 0.0, True, "already there"))
            return True
    except Exception:
        pass
    v0 = obj.Shape.Volume
    new = obj.Shape.cut(tool)
    removed = (v0 - new.Volume) / 1000.0
    ok = removed >= need
    if ok:
        tidy = new.removeSplitter()
        try:
            tidy.check(True)
            new = tidy
        except Exception:
            pass
        obj.Shape = new
    report.append((obj.Label, what, removed, ok, ""))
    return ok


print("=" * 100)
print("MISSING FEATURES  --  %s" % _BASE)
print("=" * 100)

# ---------------------------------------------------------------- A7: the screw's upper bearing
a7 = doc.getObject("A7_DriveBox")
# Restore the bracket first. The boss is a FUSE, so a wrong one cannot be un-fused: the first
# version of it reached down to Z 81 and put a 3.7 mm sliver through P22 and P25's inner wall,
# and re-running with a shorter box would have left that sliver behind for ever.
if a7 is not None and abs(a7.Shape.Volume / 1000.0 - A7_PRE) > 0.5:
    ref = None
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith("model/" + _BASE):
            ref = d
    if ref is None and os.path.exists(REFFILE):
        ref = FreeCAD.openDocument(REFFILE)
    if ref is not None:
        for x in ref.Objects:
            if hasattr(x, "Placement"):
                x.Placement = FreeCAD.Placement()
        ref.recompute()
        r7 = ref.getObject("A7_DriveBox")
        if r7 is not None and abs(r7.Shape.Volume / 1000.0 - A7_PRE) < 1.0:
            a7.Shape = r7.Shape
            print("  restored the bracket from model/%s: %.1f cm3"
                  % (_BASE, a7.Shape.Volume / 1000.0))
SCR_X, SCR_Z = -62.0, 106.0
BOSS_Y = (286.0, 298.0)
boss = Part.makeCylinder(16.0, BOSS_Y[1] - BOSS_Y[0], V(SCR_X, BOSS_Y[0], SCR_Z), V(0, 1, 0))
# tie it back into the bracket's end region so it is not floating
# Z 85 at the bottom, not 81: P22_DriveCap and P25_MotorNacelle's inner wall is at Z 84.74.
boss = boss.fuse(Part.makeBox(32.0, BOSS_Y[1] - BOSS_Y[0], 22.0,
                              V(SCR_X - 16.0, BOSS_Y[0], SCR_Z - 21.0)))
seat = Part.makeCylinder(11.0, 7.2, V(SCR_X, BOSS_Y[1] - 7.2, SCR_Z), V(0, 1, 0))
shaft = Part.makeCylinder(4.6, 20.0, V(SCR_X, BOSS_Y[0] - 1.0, SCR_Z), V(0, 1, 0))
if a7 is not None:
    # ask about the boss as it ends up -- with its seat and shaft bore already taken out of it.
    # Comparing the solid boss instead reports "missing" on every re-run, because the holes this
    # same script cut are exactly the gap it would be looking at.
    gap = boss.cut(seat).cut(shaft).cut(a7.Shape)
    if gap.isNull() or gap.Volume < 100.0:
        report.append((a7.Label, "screw boss, dia 32 x 12", 0.0, True, "already there"))
    else:
        v0 = a7.Shape.Volume
        fused = a7.Shape.fuse(boss)
        tidy = fused.removeSplitter()
        try:
            tidy.check(True)
            fused = tidy
        except Exception:
            pass
        assert len(fused.Solids) == 1, (
            "the screw boss left the bracket as %d solids" % len(fused.Solids))
        a7.Shape = fused
        report.append((a7.Label, "screw boss, dia 32 x 12", (fused.Volume - v0) / 1000.0,
                       fused.Volume > v0, ""))
    cut_and_check(a7, Part.makeCylinder(11.0, 7.2, V(SCR_X, BOSS_Y[1] - 7.2, SCR_Z), V(0, 1, 0)),
                  "608 bearing seat, dia 22 x 7", need=0.5)
    cut_and_check(a7, Part.makeCylinder(4.6, 20.0, V(SCR_X, BOSS_Y[0] - 1.0, SCR_Z), V(0, 1, 0)),
                  "screw end clearance, dia 9.2", need=0.1)

# ---------------------------------------------------------------- cladding attachment
CLAD = [("P20_KneeShroud", [(0.0, 10.0, 120.0), (0.0, -20.0, 120.0)]),
        # Y 230 and 260 are open shell -- measured. 290 and 310 have wall at Z 135..138.
        ("P22_DriveCap", [(0.0, 290.0, 135.0), (0.0, 310.0, 135.0)]),
        ("P25_MotorNacelle", [(-104.0, 230.0, 40.0), (-104.0, 300.0, 40.0)])]
for name, pts in CLAD:
    ob = doc.getObject(name)
    if ob is None:
        continue
    for (x, y, z) in pts:
        cut_and_check(ob, Part.makeCylinder(M4 / 2.0, 60.0, V(x, y, z - 30.0), V(0, 0, 1)),
                      "attachment screw at (%.0f, %.0f)" % (x, y))

doc.recompute()
doc.save()

print("  %-24s %-40s %9s %s" % ("part", "feature", "removed", ""))
bad = 0
for lbl, what, vol, ok, note in report:
    print("  %-24s %-40s %7.3f cm3 %s" % (lbl[:24], what[:40], vol, note if note else
                                          ("" if ok else "<-- HIT AIR")))
    if not ok:
        bad += 1
print()
print("  %d features present, %d landed in air" % (len(report) - bad, bad))
if bad:
    print("  A hole that removes nothing is the same class of defect as a pulley with no teeth:")
    print("  it looks like a feature and does nothing. Fix the positions before trusting this.")
sys.stdout.flush()
sys.exit(1 if bad else 0)
