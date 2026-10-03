# -*- coding: utf-8 -*-
"""How much fatter a leg can this fit, and would swinging the motor pod out help?

Asked at the bench: "is there any way to make the P25_MotorNacelle adjustable easily? Like could
it swing out and lock into place further out from the leg for a fatter leg?"

Two questions again, and they want keeping apart:

  1. WHAT ACTUALLY BINDS. The nacelle is a 3 mm wall with the motor's can half a millimetre
     behind it, so moving the COVER out does nothing on its own -- the can is the part that is
     close to the leg, and the cover is only its skin. Before designing an adjustment, measure
     which part of the device is nearest the limb and by how much, every 4 mm along the whole
     thigh, so the adjustment goes where the interference is rather than where it is noticed.

  2. WHETHER THE POD CAN SWING. It can, and the reason is worth stating: a motor swung about the
     SCREW's axis keeps its centre distance to the screw constant, so the link belt's tension
     does not change at all. That is the one direction the motor is free to move in without a
     tensioner, and it happens to be roughly away from the leg.

THE LIMB IS A TAPER, NOT A CYLINDER. REF_Thigh runs r 77 at the knee end to r 85 at Y 300, so
"clearance" has to be measured against the limb's radius AT THAT STATION, not against the 84.9
nominal that 399_drivecap.py quotes for the top. A single number for the whole device would be
dominated by wherever the leg happens to be fattest.

Nothing in this file writes to the document.

    freecadcmd.exe scripts/437_leg_size.py
"""
import math
import os

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

SLEEVE = 3.0            # the neoprene sleeve, BOM S5: it is ON the limb, so it eats clearance
# the cuffs and the sleeve are MEANT to touch the leg, and the reference solids are the leg
TOUCHING = ("P5_ThighCuff", "P7_ShankCuff", "P6_ShankSocket")
STEP = 4.0              # mm along the limb
ARC = 1.0               # mm along each section's wire


def limb_radius(ref, y, lo=40.0, hi=110.0):
    """the limb's own radius at this station, measured, not assumed"""
    if not (ref.BoundBox.YMin <= y <= ref.BoundBox.YMax):
        return None
    best = None
    for ang in (0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0):
        a = math.radians(ang)
        r = lo
        hit = None
        while r <= hi:
            if ref.isInside(V(r * math.cos(a), y, r * math.sin(a)), 1e-7, True):
                hit = r
            r += 0.5
        if hit is not None and (best is None or hit > best):
            best = hit
    return best


def min_radius(sh, y):
    """how close this part comes to the limb's axis at this station"""
    try:
        ws = sh.slice(V(0, 1, 0), y)
    except Exception:
        return None
    best = None
    for w in ws:
        try:
            pts = w.discretize(Distance=ARC)
        except Exception:
            pts = [v.Point for v in w.Vertexes]
        for p in pts:
            r = math.hypot(p.x, p.z)
            if best is None or r < best:
                best = r
    return best


print("=" * 98)
print("HOW MUCH FATTER A LEG  --  %s" % _BASE)
print("=" * 98)

ref = doc.getObject("REF_Thigh")
assert ref is not None, "no REF_Thigh to measure against"
rb = ref.Shape.BoundBox
print("  the modelled thigh is a TAPER, not a cylinder, and it stops at Y %.0f:" % rb.YMax)
prof = {}
for y in [rb.YMin + 10.0 + i * 30.0 for i in range(int((rb.YLength - 20) // 30) + 1)]:
    r = limb_radius(ref.Shape, y)
    if r:
        prof[y] = r
        print("     Y %5.0f  r %5.1f   circumference %5.0f mm" % (y, r, 2 * math.pi * r))
TOP_R = max(prof.values()) if prof else 84.9
print("     widest modelled station r %.1f, so 399's nominal 84.9 is the TOP of the taper"
      % TOP_R)
print("     + the %.0f mm neoprene sleeve (BOM S5), which sits on the limb and eats clearance"
      % SLEEVE)

parts = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids
         and not o.Name.startswith("TEST_") and not o.Name.startswith("REF_")]

print()
print("  CLOSEST APPROACH TO THE LIMB, every %.0f mm over the thigh, against the limb's own" % STEP)
print("  radius at that station. Negative means the part is already inside the leg's surface.")
print()
print("     %-26s %8s %8s %8s   %s" % ("part", "gap mm", "at Y", "its r", "limb r there"))
rows = []
for o in parts:
    bb = o.Shape.BoundBox
    y0 = max(bb.YMin, rb.YMin)
    y1 = min(bb.YMax, rb.YMax)
    if y1 - y0 < STEP:
        continue
    worst = None
    n = int((y1 - y0) // STEP)
    for i in range(n + 1):
        y = y0 + 1.0 + i * STEP
        if y > y1 - 0.5:
            break
        lr = limb_radius(ref.Shape, y)
        if lr is None:
            continue
        mr = min_radius(o.Shape, y)
        if mr is None:
            continue
        gap = mr - lr
        if worst is None or gap < worst[0]:
            worst = (gap, y, mr, lr)
    if worst is not None:
        rows.append((worst[0], o.Name, worst[1], worst[2], worst[3]))
rows.sort()
for gap, nm, y, mr, lr in rows[:14]:
    tag = "  <- meant to touch" if nm in TOUCHING else ""
    print("     %-26s %8.1f %8.0f %8.1f   %6.1f%s" % (nm, gap, y, mr, lr, tag))

free = [r for r in rows if r[1] not in TOUCHING]
print()
if free:
    g, nm, y, mr, lr = free[0]
    print("  THE BINDING PART IS %s, %.1f mm clear at Y %.0f." % (nm, g, y))
    print("  Every part that is not supposed to touch the leg has at least that much, so the limb")
    print("  can grow %.1f mm in RADIUS before the first contact -- %.0f mm of circumference,"
          % (g, 2 * math.pi * g))
    print("  and the %.0f mm sleeve is already inside that budget." % SLEEVE)
    print("  As a thigh measurement: %.0f mm circumference now, %.0f mm at first contact,"
          % (2 * math.pi * TOP_R, 2 * math.pi * (TOP_R + g)))
    print("  less the sleeve -> about %.0f mm of usable range." % (2 * math.pi * (g - SLEEVE)))

# --------------------------------------------------------------- can the pod swing out?
print()
print("=" * 98)
print("  SWINGING THE POD ABOUT THE SCREW'S AXIS")
mot = doc.getObject("A3_Motor_6374")
mb = mot.Shape.BoundBox
MOT_X, MOT_Z = 0.5 * (mb.XMin + mb.XMax), 0.5 * (mb.ZMin + mb.ZMax)
MOT_R = 0.5 * mb.XLength
SCR_X, SCR_Z = -62.0, 106.0
cd = math.hypot(SCR_X - MOT_X, SCR_Z - MOT_Z)
a0 = math.atan2(MOT_Z - SCR_Z, MOT_X - SCR_X)
print("  The motor sits %.1f mm from the screw -- that is the belt's centre distance, and a motor"
      % cd)
print("  swung about the SCREW's axis keeps it exactly. The belt never changes tension, which is")
print("  what makes this the one free direction without adding a tensioner.")
print()
print("     %6s %10s %10s %10s %10s" % ("swing", "motor X", "motor Z", "axis r", "can's gap"))
for dth in (0.0, 5.0, 10.0, 15.0, 20.0, 25.0):
    a = a0 - math.radians(dth)
    mx = SCR_X + cd * math.cos(a)
    mz = SCR_Z + cd * math.sin(a)
    r = math.hypot(mx, mz)
    print("     %5.0f  %10.1f %10.1f %10.1f %10.1f"
          % (dth, mx, mz, r, r - MOT_R - TOP_R))
print()
print("  so %.0f deg of swing buys about %.0f mm of radius at the motor's own skin."
      % (10.0, (lambda a: math.hypot(SCR_X + cd * math.cos(a), SCR_Z + cd * math.sin(a)))
         (a0 - math.radians(10.0)) - math.hypot(MOT_X, MOT_Z)))

# what the swung pod would run into
print()
print("  WHAT IT WOULD RUN INTO, as a bare cylinder at each swing angle (the pod's own skin is")
print("  %.1f mm outside this, and the cladding would have to be redrawn either way):" % 3.5)
ignore = ("A3_Motor_6374", "A7b_LinkBelt", "P25_MotorNacelle", "P27_ControllerMount",
          "HW_ODrive_XDriveMini")
for dth in (10.0, 20.0):
    a = a0 - math.radians(dth)
    mx = SCR_X + cd * math.cos(a)
    mz = SCR_Z + cd * math.sin(a)
    cyl = Part.makeCylinder(MOT_R, mb.YLength, V(mx, mb.YMin, mz), V(0, 1, 0))
    hits = []
    for o in parts:
        if o.Name in ignore:
            continue
        c = cyl.common(o.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > 0.05:
            hits.append((v, o.Name))
    hits.sort(reverse=True)
    print("     %2.0f deg: %s" % (dth, ", ".join("%s %.1f cm3" % (n, v) for v, n in hits[:5])
                                  or "nothing"))
