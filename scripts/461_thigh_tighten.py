# -*- coding: utf-8 -*-
"""Before redrawing the thigh as one unit: where the bulk actually is, and what more wrap buys.

Asked at the bench: make the whole thigh one cohesive unit rather than a motor box hanging off
it; be creative about placement to tighten everything; watch for snags; use plastic channels and
stacked bearings to shape the belt paths tightly; and wrap the knee pulley further than 180 deg
to get more teeth gripping and cut the per-tooth load.

Three of those are good and one of them does not work, so this measures all four before anything
is drawn. Building first and checking after is what cost the nacelle its nose this afternoon.

    freecadcmd.exe scripts/461_thigh_tighten.py
"""
import math

import FreeCAD
import Part

DOC = r"C:/Users/Josh/KneeExo_v8.FCStd"
PITCH = 8.0
R_CAP = 29 * PITCH / (2 * math.pi)
F_DIFF = 28.2 * 1000.0 / R_CAP
T_TIGHT = 914.0

# Gates PowerGrip teeth-in-mesh derating: 6 or more teeth is the full rating and there is no
# credit above it, because the belt stretches through the mesh and the first teeth to engage
# carry most of the load however many follow them.
TIM = {2: 0.20, 3: 0.40, 4: 0.60, 5: 0.80, 6: 1.00}

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}

print("=" * 98)
print("1.  MORE WRAP ON THE CAPSTAN -- the one that does not pay")
print("=" * 98)
print("  %-28s %8s %10s %10s %10s"
      % ("", "teeth", "wrap deg", "in mesh", "rating"))
for name, teeth, wrap in (("knee capstan 29T", 29, 180.0), ("idler 29T", 29, 180.0),
                          ("motor 38T", 38, 207.2), ("screw 20T", 20, 152.8)):
    n = teeth * wrap / 360.0
    f = TIM.get(int(min(6, max(2, n))), 1.0) if n < 6 else 1.00
    print("  %-28s %8d %9.0f %10.1f %9.2f%s"
          % (name, teeth, wrap, n, f, "   <-- below 6, derated" if n < 6 else ""))
print()
print("  EVERY PULLEY IN THE MACHINE IS ALREADY PAST THE POINT WHERE MORE TEETH HELP. The")
print("  derating table stops at six because the belt STRETCHES as it goes through the mesh:")
print("  the first teeth to engage take most of the load and the ones behind them take what is")
print("  left, so adding a seventh, or a twentieth, changes very little. The capstan is at 14.5.")
print()
for wrap in (180.0, 220.0, 270.0, 300.0):
    n = 29 * wrap / 360.0
    print("     %3.0f deg of wrap -> %4.1f teeth in mesh, nominal %4.1f N per tooth, rating x%.2f"
          % (wrap, n, F_DIFF / n, 1.00))
print()
print("  The nominal number falls because it is just %.0f N divided by the count, but the REAL"
      % F_DIFF)
print("  first-tooth load barely moves. You would be buying idlers, friction and -- worse -- a")
print("  BACK-BEND in the belt, which fatigues the cords harder than forward bending and needs a")
print("  larger minimum diameter than a toothed pulley does.")
print()
print("  WHERE MORE WRAP WOULD HAVE PAID: nowhere here. If the capstan ever shrinks -- 444 looked")
print("  at 15T to buy a smaller screw lead -- it would be at %.1f teeth in mesh at 180 deg, and"
      % (15 / 2.0))
print("  THEN wrap would be worth having, because %.1f is near the cliff." % (15 / 2.0))

print()
print("=" * 98)
print("2.  PLASTIC CHANNELS -- yes as containment, no as the path")
print("=" * 98)
mu = 0.3
print("  A belt sliding in a channel is a brake. The tight side carries %.0f N; at a plastic-on-"
      % T_TIGHT)
print("  rubber coefficient of about %.1f, every wrap of channel contact costs" % mu)
for deg in (30.0, 90.0, 180.0):
    rad = math.radians(deg)
    loss = T_TIGHT * (1 - math.exp(-mu * rad))
    print("     %3.0f deg of sliding contact: %5.0f N lost to friction, %4.1f%% of the tight side"
          % (deg, loss, 100.0 * loss / T_TIGHT))
print()
print("  So channels are for KEEPING THE BELT ON, with clearance, touched only when it tries to")
print("  walk -- which is exactly what 433_drive_flip.py's belt guard already is. Anything that")
print("  changes the belt's DIRECTION has to be a roller.")
print()
print("  And rollers are cheap: a back-bend idler is a bearing and a printed sleeve. The cost is")
print("  not the part, it is the bend. HTD-8M wants roughly dia 50-65 on a flat back-bend where a")
print("  toothed pulley can be 22 teeth (dia 56), so an idler that reroutes the belt is about as")
print("  big as the capstan. Two of them is most of the space a tighter layout was trying to win.")

print()
print("=" * 98)
print("3.  WHERE THE BULK ACTUALLY IS")
print("=" * 98)
STATIC = [o for o in doc.Objects if o.isDerivedFrom("Part::Feature")
          and not o.Name.startswith(("REF_", "TEST_"))]
# The TRUE reach, not the bbox corner. A shell's bounding box corner is empty air and reports a
# radius the part does not have: P21_ShellAnterior's corner says r 168 where its material stops
# at r 140. The whole point of this table is to decide what to tighten, so it has to be material.
print("  radial reach from the limb axis, by station -- material, not bounding boxes")
print("  %6s %9s %-30s %9s %9s" % ("Y", "max r", "what reaches furthest", "limb r", "stand-off"))
ref = g.get("REF_Thigh")
RS = [float(x) for x in range(190, 59, -5)]
for y in range(60, 341, 20):
    slab = Part.makeBox(600, 20.0, 600, FreeCAD.Vector(-300, y, -300))
    worst, who = 0.0, ""
    for o in STATIC:
        b = o.Shape.BoundBox
        if b.YMax < y or b.YMin > y + 20:
            continue
        try:
            c = o.Shape.common(slab)
        except Exception:
            continue
        if c.Volume < 100.0:
            continue
        cb = c.BoundBox
        hi = max(math.hypot(x, z) for x in (cb.XMin, cb.XMax) for z in (cb.ZMin, cb.ZMax))
        if hi <= worst:
            continue
        for r in RS:
            if r <= worst or r > hi:
                continue
            out = Part.makeBox(600, 20.0, 600, FreeCAD.Vector(-300, y, -300)).cut(
                Part.makeCylinder(r, 24.0, FreeCAD.Vector(0, y - 2, 0), FreeCAD.Vector(0, 1, 0)))
            if c.common(out).Volume > 50.0:
                worst, who = r, o.Name
                break
    lr = 0.0
    if ref is not None:
        rs = ref.Shape.common(slab)
        if rs.Volume > 1.0:
            lr = max(abs(rs.BoundBox.ZMax), abs(rs.BoundBox.XMax))
    if worst:
        print("  %6d %9.0f %-30s %9.1f %9s"
              % (y, worst, who, lr, "%.0f" % (worst - lr) if lr else "-"))

print()
print("=" * 98)
print("4.  THE PARTS THAT MAKE THE THIGH FIVE THINGS INSTEAD OF ONE")
print("=" * 98)
tot = 0.0
for n in ("A1_Extrusion_20x60_VSlot", "A7_DriveBox", "P21_ShellAnterior", "P22_DriveCap",
          "P25_MotorNacelle", "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount",
          "P27_ControllerMount"):
    if n not in g:
        continue
    b = g[n].Shape.BoundBox
    v = g[n].Shape.Volume / 1000.0
    tot += v
    print("  %-26s %7.1f cm3   Y %6.0f..%6.0f   r %5.1f"
          % (n, v, b.YMin, b.YMax,
             max(math.hypot(x, z) for x in (b.XMin, b.XMax) for z in (b.ZMin, b.ZMax))))
print("  %-26s %7.1f cm3  = %.0f g of PETG and aluminium doing one job in nine pieces"
      % ("TOTAL", tot, tot * 1.27))
