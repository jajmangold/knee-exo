# -*- coding: utf-8 -*-
"""Cut 29 HTD-8M grooves into the knee capstan, at the tip radius the bought parts dictate.

420_mockup_audit.py found the capstan: sampled at the belt plane over 360 bearings, its outer
radius was 35.552 mm with a spread of 0.000. The part the belt drives the shank through was a
plain drum, and every geometric check in the repository passed it, because a drum of the right
diameter sweeps the right volume.

THE RADIUS, WHICH IS NOT A FREE CHOICE. 392/396 built the rim at 35.552, deducting the pitch line
differential twice:

    pitch diameter          29 x 8 / pi = 73.846        fixed by the belt
    pitch line differential 0.686                       HTD-8M
    standard tip radius     36.923 - 0.686 = 36.237     what a 29T HTD-8M pulley measures
    the rim as built        35.552                      0.685 under -- PLD taken off twice

The first version of this file cut from the rim as it stood, on the grounds that 0.69 mm of radius
is 1.8% of torque and the belt would simply sit deeper. That was wrong, for two reasons that have
nothing to do with the capstan itself:

  * THE IDLER IS A BOUGHT PART. BOM S2b is a 29T HTD-8M idler pulley -- "the same part as the knee
    capstan" -- and a bought 29T pulley measures 72.47 over the tips. The belt cannot wrap a 36.24
    pulley at one end and a 35.55 one at the other without the two strands sitting at different
    distances from the centreline, which is what S2b claims makes them land at +-36.92.
  * THE BELT IS A BOUGHT LENGTH. BOM K1 is a 742 mm closed loop, which is 2*pi*36.923 + 2*255 to
    0.03 mm. On a 35.552 rim the path is 737.7 mm, so a 742 mm belt arrives 4.3 mm long -- 2.2 mm
    of extra centre distance for an idler whose spring has 3 mm of working travel.

So this grows the belt land back to the standard 36.237 before cutting, and the drive torque is
what the BOM says it is rather than 1.8% under.

THE PROFILE, AND HOW MUCH OF IT IS KNOWN. HTD-8M is a curvilinear ("round tooth") form, not a
trapezoid. The published form is defined by arcs whose radii are not reproduced here, so this cuts
a HALF-ELLIPSE of 2.65 mm tangential semi-axis and 3.45 mm radial: 5.3 mm wide at the tip circle,
leaving 2.55 mm of land out of the 7.85 mm circumferential pitch. A circular arc cannot be used --
the groove is deeper than half its width, and an arc's sagitta cannot exceed its radius, which is
itself the clue that HTD is not a simple arc form.

SO THIS IS AN APPROXIMATION AND MUST BE PROVEN AGAINST A REAL BELT. Print the three-tooth coupon
this script writes and push an HTD-8M belt into it before committing 10 hours to the real part. The
tooth loads are trivial either way -- 764 N over 14.5 teeth in mesh is 53 N a tooth, 0.44 MPa over
a 30 x 4 mm root -- so this is about MESHING, not strength: a groove too narrow rides the belt out,
one too wide lets it ratchet under load.

IDEMPOTENT. It restores the belt land from the committed pre-teeth copy of the document first, so
running it twice cuts one set of grooves, not two sets at slightly different radii.

    freecadcmd.exe scripts/421_pulley_teeth.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
HERE = os.path.dirname(os.path.abspath(__file__))
REFFILE = os.path.join(HERE, "..", "model", _BASE).replace("\\", "/")
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

TEETH, PITCH = 29, 8.0
PD = TEETH * PITCH / math.pi              # 73.846
PLD = 0.686                               # pitch line differential, HTD-8M
TIP_R = PD / 2.0 - PLD                    # 36.237, the standard 29T tip radius
AS_BUILT = 35.552                         # what 392/396 drew
DEPTH = 3.45                              # groove depth below the tip circle
HALF_W = 2.65                             # tangential semi-axis of the groove
BELT_Z = (96.0, 126.0)
BELT_TOOTH_H = 3.38

o = doc.getObject("P2a_KneeHingePlate")
assert o is not None, "no capstan in this document"
mirrored = o.Shape.BoundBox.ZMax < 0
z0, z1 = (BELT_Z[0], BELT_Z[1]) if not mirrored else (-BELT_Z[1], -BELT_Z[0])

print("=" * 98)
print("CAPSTAN TEETH  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)
print("  %dT HTD-8M: pitch dia %.3f, tip dia %.3f (was built %.3f), groove %.2f deep x %.1f wide"
      % (TEETH, PD, 2 * TIP_R, 2 * AS_BUILT, DEPTH, 2 * HALF_W))
print("  circumferential pitch at the tip %.2f -> %.2f mm of land between grooves"
      % (2 * math.pi * TIP_R / TEETH, 2 * math.pi * TIP_R / TEETH - 2 * HALF_W))
print("  belt tooth tips reach R %.2f against a groove bottom at R %.2f -- %.2f mm clear"
      % (TIP_R - BELT_TOOTH_H, TIP_R - DEPTH, DEPTH - BELT_TOOTH_H))


def rim(sh, zs, step=1):
    """sample the outer radius at one height, the way the audit does"""
    rs = []
    for i in range(0, 360, step):
        t = math.radians(i)
        ln = Part.makeLine(V(15 * math.cos(t), 15 * math.sin(t), zs),
                           V(60 * math.cos(t), 60 * math.sin(t), zs))
        k = sh.common(ln)
        if k.isNull() or not k.Vertexes:
            continue
        rs.append(max(math.hypot(v.Point.x, v.Point.y) for v in k.Vertexes))
    return (min(rs), max(rs)) if rs else (None, None)


# ---------------------------------------------------------------- start from the smooth drum
zs = 0.5 * (z0 + z1)
lo, hi = rim(o.Shape, zs, 5)
if hi - lo > 1.0 or abs(hi - AS_BUILT) > 0.2:
    ref = None
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith("model/" + _BASE):
            ref = d
    if ref is None:
        assert os.path.exists(REFFILE), "no pre-teeth copy at %s to restore from" % REFFILE
        ref = FreeCAD.openDocument(REFFILE)
    for x in ref.Objects:
        if hasattr(x, "Placement"):
            x.Placement = FreeCAD.Placement()
    ref.recompute()
    r = ref.getObject("P2a_KneeHingePlate")
    rlo, rhi = rim(r.Shape, zs, 5)
    assert rhi is not None and rhi - rlo < 0.01 and abs(rhi - AS_BUILT) < 0.01, \
        "the copy at model/%s is not the smooth drum either (rim %.3f..%.3f)" % (_BASE, rlo, rhi)
    o.Shape = r.Shape
    print("  restored the smooth drum from model/%s (%.1f cm3)" % (_BASE, r.Shape.Volume / 1000.0))
    lo, hi = rim(o.Shape, zs, 5)

sh = o.Shape
v_drum = sh.Volume

# ---------------------------------------------------------------- grow the land to standard
# the collar must OVERLAP the drum, not sit tangent to it. Cutting its bore at exactly AS_BUILT
# puts two surfaces in the same place to within floating point, and the fuse returned two
# disjoint solids rather than one part.
ANN_IN = AS_BUILT - 0.25
ann = Part.makeCylinder(TIP_R, z1 - z0, V(0, 0, z0), V(0, 0, 1)) \
    .cut(Part.makeCylinder(ANN_IN, z1 - z0 + 2.0, V(0, 0, z0 - 1.0), V(0, 0, 1)))
grown = sh.fuse(ann)
tidy = grown.removeSplitter()
try:
    tidy.check(True)
    grown = tidy
except Exception:
    pass
assert len(grown.Solids) == 1, "growing the land split the capstan into %d" % len(grown.Solids)
glo, ghi = rim(grown, zs, 5)
assert abs(ghi - TIP_R) < 0.01, "the land grew to %.3f, not %.3f" % (ghi, TIP_R)
# an ideal collar is pi*(TIP_R^2 - AS_BUILT^2)*height. Much more than that means the fuse filled
# a void inside the rim rather than just adding a skin, which would add mass nobody asked for.
_ideal = math.pi * (TIP_R ** 2 - AS_BUILT ** 2) * (z1 - z0)
_got = grown.Volume - v_drum
assert 0.8 * _ideal < _got < 1.3 * _ideal, \
    "growing the land added %.2f cm3, expected about %.2f -- it filled something" \
    % (_got / 1000.0, _ideal / 1000.0)
print("  belt land grown %.3f -> %.3f mm radius, +%.2f cm3"
      % (AS_BUILT, ghi, (grown.Volume - v_drum) / 1000.0))


def groove(theta):
    """one half-elliptical groove, as a solid prism across the belt land"""
    el = Part.Ellipse(V(0, 0, 0), DEPTH, HALF_W)       # major radial, minor tangential
    f = Part.Face(Part.Wire(el.toShape()))
    sol = f.extrude(V(0, 0, z1 - z0 + 2.0))
    # built in the XY plane about the origin: move it out to the tip circle so its inner half
    # becomes the groove and its outer half sits in air beyond the rim
    sol.translate(V(TIP_R, 0, z0 - 1.0))
    sol.rotate(V(0, 0, 0), V(0, 0, 1), math.degrees(theta))
    return sol


allt = groove(0.0)
for i in range(1, TEETH):
    allt = allt.fuse(groove(2 * math.pi * i / TEETH))
cut = grown.cut(allt)
tidy = cut.removeSplitter()
try:
    tidy.check(True)
    cut, how = tidy, "merged"
except Exception:
    how = "raw cut (removeSplitter self-intersected)"
if cut.Volume < 0:
    cut.reverse()
cut.check(True)
assert len(cut.Solids) == 1, "the teeth split the capstan into %d solids" % len(cut.Solids)
o.Shape = cut
o.Label = "P2a_KneeHub_Pulley29T"

clo, chi = rim(cut, zs)
print("  %d grooves cut, %.2f cm3 removed (%s)"
      % (TEETH, (grown.Volume - cut.Volume) / 1000.0, how))
print("  rim now %.2f..%.2f, spread %.2f mm -- it was 0.000 before; part is %.1f cm3"
      % (clo, chi, chi - clo, cut.Volume / 1000.0))
assert chi - clo > 2.0, "the grooves did not reach the rim"
assert abs((chi - clo) - DEPTH) < 0.2, \
    "groove depth measured %.2f, expected %.2f" % (chi - clo, DEPTH)

# ---------------------------------------------------------------- the bought idler, same radius
a6 = doc.getObject("A6_Idler29T")
if a6 is not None:
    was = a6.Shape.BoundBox.XMax
    cy = 0.5 * (a6.Shape.BoundBox.YMin + a6.Shape.BoundBox.YMax)
    a6.Shape = Part.makeCylinder(TIP_R, z1 - z0, V(0, cy, z0), V(0, 0, 1))
    print("  A6_Idler29T is BOUGHT (BOM S2b): mockup radius %.2f -> %.2f at Y %.0f"
          % (was, TIP_R, cy))

# ---------------------------------------------------------------- the coupon
arc = Part.makeCylinder(TIP_R, 12.0, V(0, 0, 0), V(0, 0, 1)) \
    .cut(Part.makeCylinder(TIP_R - 8.0, 14.0, V(0, 0, -1), V(0, 0, 1))) \
    .common(Part.makeBox(60, 30, 20, V(0, -15, -1)))
for i in (-1, 0, 1):
    gf = Part.Face(Part.Wire(Part.Ellipse(V(0, 0, 0), DEPTH, HALF_W).toShape())) \
        .extrude(V(0, 0, 14.0))
    gf.translate(V(TIP_R, 0, -1.0))
    gf.rotate(V(0, 0, 0), V(0, 0, 1), i * 360.0 / TEETH)
    arc = arc.cut(gf)
cp = doc.getObject("TEST_ToothCoupon") or doc.addObject("Part::Feature", "TEST_ToothCoupon")
cp.Shape = arc
cp.Label = "TEST_ToothCoupon_3xHTD8M"
if getattr(cp, "ViewObject", None) is not None:
    cp.ViewObject.Visibility = False
doc.recompute()
doc.save()
print("  coupon written as TEST_ToothCoupon_3xHTD8M, %.1f cm3 -- print this FIRST and try a belt"
      % (arc.Volume / 1000.0))
print()
print("  The profile approximates the HTD-8M curvilinear form; it is not the published one. Prove")
print("  it with the coupon before printing a 10-hour part, and correct HALF_W and DEPTH here from")
print("  what the belt actually does. 423 must run after this: the belt sits on this radius.")
sys.stdout.flush()
