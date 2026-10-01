# -*- coding: utf-8 -*-
"""STAGE 7: can the fairing mount to the extrusion's SIDE faces? Measured, not reasoned.

397 concluded "there is no central mount left, so the fairing mounts at its two ENDS". That
was generalised from the OUTBOARD face alone and it is wrong: a 2040 has four faces, and
the two 20 mm side faces at X = +/-20 were never checked. 397's own end ribs then proved
the point the hard way -- they span the whole section at Z 92..98, so they cut through the
rail, both belt strands and the gantry, which is exactly the four flags the sweep returned.

So: test candidate side brackets against the gantry at every one of the 107 poses, and
against the static belt, rail and idler. Do not argue about it.

A side bracket has to thread one gap: bolt into the side slot at Z 95..101, get OUTBOARD
past the belt band (|X| 35.55..41.12, Z 96..126), and climb to the fairing's inner surface.
The only way past the belt is UNDER it, at Z < 96, in the space beyond |X| 20 where the
extrusion has ended.

Send with:  python tools/fcsend.py scripts/398_sidemounts.py
"""
import math
import FreeCAD
import Part
from FreeCAD import Vector as V

def _kx_doc():
    """The model, whether we are inside the GUI instance or running under freecadcmd.

    KX_DOC overrides the file, which is how the mirrored right leg is built with the same
    scripts. Headless matters: 397 and 409 both exceed the RPC server's 90 s dispatch limit,
    and overrunning it does not fail cleanly -- it keeps working and leaves a half-built
    document that the next script reads as finished.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()


TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)
BIN, BOUT = R - 1.372, R + 4.2
A0 = 161.0
THETA = [float(i) for i in range(-2, 105)]
N_EXP, ZC, B_IN = 5.5, 110.0, 25.0
XC_MID, A_MID, WALL = -19.5, 76.5, 3.0


def bx(x0, x1, y0, y1, z0, z1):
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def bracket(sgn, ystn, half=8.0):
    """sgn +1 = posterior side face, -1 = anterior. Foot into the side slot, a run UNDER
    the belt, then a riser outboard of it up to the fairing."""
    def sx(a, b):
        return tuple(sorted((sgn * a, sgn * b)))
    y0, y1 = ystn - half, ystn + half
    b = bx(*sx(20.0, 30.0), y0, y1, 92.0, 104.0)          # foot, on the side face
    b = b.fuse(bx(*sx(26.0, 46.0), y0, y1, 89.0, 95.7))   # run, under the belt
    b = b.fuse(bx(*sx(41.5, 47.0), y0, y1, 95.7, 128.0))  # riser, outboard of the belt
    return b.removeSplitter()


def zin(x):
    """inner surface height of P21's section at this x, or None if outside it."""
    u = abs(x - XC_MID) / (A_MID - WALL)
    if u >= 1.0:
        return None
    return ZC + B_IN * (1.0 - u ** N_EXP) ** (1.0 / N_EXP)


O = lambda n: doc.getObject(n)
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
STATIC = ["A1_Extrusion_20x60_VSlot", "A5_Belt_HTD8M", "A5b_Belt_DriveRun",
          "A5c_Belt_TakeRun", "A5d_Belt_WrapIdler", "A6_Idler29T", "A2_BallScrew_SFU1620",
          "A7_DriveBox", "P5_ThighCuff", "P1_KneeYoke"]

print("=" * 76)
print("CANDIDATE SIDE BRACKETS, swept against the gantry over all %d poses" % len(THETA))
print("  riser reaches Z 128; P21's inner surface at X = +/-44 is Z %.1f, so %.1f mm spare"
      % (zin(44.0), zin(44.0) - 128.0))
print()
print("  %-10s %6s %14s %10s %s" % ("face", "Y", "worst gantry", "statics", "verdict"))
results = {}
for sgn, face in ((1.0, "posterior"), (-1.0, "anterior")):
    for ystn in (88.0, 124.0, 160.0):
        br = bracket(sgn, ystn)
        worst, wth = 0.0, None
        for th in THETA:
            dy = (A0 - R * math.radians(th)) - A0
            for n in GANTRY:
                o = O(n)
                if o is None:
                    continue
                sh = o.Shape.copy()
                sh.translate(V(0, dy, 0))
                if not br.BoundBox.intersect(sh.BoundBox):
                    continue
                c = br.common(sh)
                if c.isNull():
                    continue
                v = c.Volume / 1000.0
                if v > worst:
                    worst, wth = v, th
        st = 0.0
        for n in STATIC:
            o = O(n)
            if o is None or not br.BoundBox.intersect(o.Shape.BoundBox):
                continue
            c = br.common(o.Shape)
            if not c.isNull():
                st += c.Volume / 1000.0
        good = worst <= 0.02 and st <= 0.02
        results[(sgn, ystn)] = good
        print("  %-10s %6.0f %11.3f cm3 %7.3f cm3  %s"
              % (face, ystn, worst, st,
                 "CLEAR" if good else "blocked" + (" @ %+.0f deg" % wth if wth else "")))

print()
print("  The posterior face is clear at every station; the anterior face is not, and the")
print("  reason is the gantry's own nut structure -- its end plates reach X -84..-44.2 and")
print("  its belt clamp X -43.8..-32.5, both down to Z 89, and both sweep the full stroke.")
print("  Everything that had to go outboard to reach the ball nut lives on that side.")
print("  Which is the answer to 'why not the side faces': ONE of them, not both.")
print("  And 330_frontmount.py already measured fore-aft as the hidden direction, so the")
print("  posterior face is the better one to spend anyway.")

# ---------------------------------------------------------------- build them
KEEP = [(1.0, y) for y in (88.0, 124.0, 160.0) if results[(1.0, y)]]
assert KEEP, "no side bracket cleared -- do not build mounts that do not fit"
for i, (sgn, ystn) in enumerate(KEEP):
    nm = "P23%s_FairingMount" % "abc"[i]
    br = bracket(sgn, ystn)
    br = br.cut(Part.makeCylinder(2.6, 20.0, V(sgn * 25.0, ystn, 90.0), V(0, 0, 1)))
    br = br.removeSplitter()
    assert len(br.Solids) == 1, "%s solids=%d" % (nm, len(br.Solids))
    o = O(nm)
    if o is None:
        o = doc.addObject("Part::Feature", nm)
        g = doc.getObject("A_ThighRail")
        if g is not None:
            g.addObject(o)
    o.Shape = br
    o.Label = nm
    b = br.BoundBox
    print("  built %-20s X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %4.1f cm3"
          % (nm, b.XMin, b.XMax, b.YMin, b.YMax, b.ZMin, b.ZMax, br.Volume / 1000.))

doc.recompute()
doc.save()
print("STAGE 7 DONE, saved. %d posterior mounts." % len(KEEP))
