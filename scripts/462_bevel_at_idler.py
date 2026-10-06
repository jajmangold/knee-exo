# -*- coding: utf-8 -*-
"""Motor at the top idler, 2:1 bevel instead of the link belt, screw on the rail's centreline.

Asked at the bench: "can we put the motor in the top idler if we use a 2:1 bevel gear set
instead of 5m pulley if we move the screw to the middle of the 2040?"

Three separate moves, and they have to be judged separately because only one of them is free:

  A  SCREW TO THE RAIL'S CENTRELINE. The screw sits at X -62 today, 42 mm outboard of the rail's
     edge, which is most of why the drive end is as wide as it is.
  B  MOTOR AT THE IDLER. The idler is at X 0, Y 255, axis along Z -- the top of the thigh, on
     the centreline, and the one place in the machine with a big round hole already in it.
  C  2:1 BEVEL instead of the HTD-5M pair. Bevels turn a corner, which is the only reason to
     want them: they let the motor's axis be perpendicular to the screw's.

    freecadcmd.exe scripts/462_bevel_at_idler.py
"""
import math

import FreeCAD
import Part
from FreeCAD import Vector as V

DOC = r"C:/Users/Josh/KneeExo_v8.FCStd"
MOTOR_D, MOTOR_L = 63.0, 74.0           # C6374 can
TAU_KNEE = 28.2
R_CAP = 29 * 8.0 / (2 * math.pi)
LEAD = 5.0
N_SCREW = 2 * math.pi * R_CAP / LEAD
ETA_SCREW, ETA_BELT, ETA_BEVEL = 0.90, 0.97, 0.95
J_ROTOR, J_LIMB = 3.10e-4, 0.30

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}

print("=" * 98)
print("A.  MOVING THE SCREW TO THE RAIL'S CENTRELINE")
print("=" * 98)
rail = g["A1_Extrusion_20x60_VSlot"].Shape.BoundBox
scr = g["A2_BallScrew_SFU1620"].Shape.BoundBox
sx, sz = (scr.XMin + scr.XMax) / 2, (scr.ZMin + scr.ZMax) / 2
print("  rail   X %6.1f..%6.1f  Z %6.1f..%6.1f   centre X %.1f" % (rail.XMin, rail.XMax, rail.ZMin, rail.ZMax, (rail.XMin + rail.XMax) / 2))
print("  screw  axis X %.1f Z %.1f -- %.0f mm outboard of the rail's centre" % (sx, sz, abs(sx)))
belt = g["A5b_Belt_DriveRun"].Shape.BoundBox
print("  belt   drive run at X %.1f..%.1f, take run at the mirror of it" % (belt.XMin, belt.XMax))
print()
print("  THE SCREW CANNOT GO TO X 0 AT ITS PRESENT Z: the rail is there, X %.0f..%.0f at"
      % (rail.XMin, rail.XMax))
print("  Z %.0f..%.0f. It has to go ABOVE the rail, which is what the bench concept drew:"
      % (rail.ZMin, rail.ZMax))
for z in (118.0, 124.0, 130.0):
    probe = Part.makeCylinder(9.0, 150.0, V(0, 60.0, z), V(0, 1, 0))
    hits = []
    for o in doc.Objects:
        if not o.isDerivedFrom("Part::Feature") or o.Name.startswith(("REF_", "A2_", "A2b")):
            continue
        try:
            c = o.Shape.common(probe)
        except Exception:
            continue
        if c.Volume > 200.0:
            hits.append("%s %.1f" % (o.Name.split("_")[0], c.Volume / 1000.0))
    print("     screw at X 0, Z %5.1f  ->  %s" % (z, ", ".join(hits) if hits else "CLEAR"))
print()
print("  and what it buys: the carriage currently spans X %.0f..%.0f because it has to reach"
      % (g["P3_Carriage"].Shape.BoundBox.XMin, g["P3_Carriage"].Shape.BoundBox.XMax))
print("  from the nut at X %.0f out to the belt it clamps at X %.1f. Centre the screw and that"
      % (sx, belt.XMax))
print("  reach becomes symmetric instead of a %.0f mm cantilever."
      % abs(sx - (belt.XMin + belt.XMax) / 2))

print()
print("=" * 98)
print("B.  IS THERE ROOM FOR A MOTOR AT THE IDLER?")
print("=" * 98)
idl = g["A6_Idler29T"].Shape.BoundBox
ix, iy, iz = (idl.XMin + idl.XMax) / 2, (idl.YMin + idl.YMax) / 2, (idl.ZMin + idl.ZMax) / 2
print("  idler  X %.1f Y %.1f Z %.1f, dia %.1f, %.0f mm wide, axis along Z"
      % (ix, iy, iz, idl.XLength, idl.ZLength))
print("  motor  dia %.0f x %.0f long -- it FITS the idler's diameter (%.0f < %.0f) and is"
      % (MOTOR_D, MOTOR_L, MOTOR_D, idl.XLength))
print("         %.0f mm longer than the idler is wide, so it must stick out somewhere."
      % (MOTOR_L - idl.ZLength))
print()
print("  along the idler's own axis (Z, medial-lateral) the motor would reach:")
for off in (0.0, 15.0, 30.0):
    lo, hi = iz - MOTOR_L / 2 + off, iz + MOTOR_L / 2 + off
    print("     centred %+5.1f mm:  Z %6.1f .. %6.1f   (the limb's lateral surface is Z 52;"
          % (off, lo, hi))
    print("                         today's widest hardware is Z 133)")
print()
print("  THAT IS THE PROBLEM WITH PUTTING IT AT THE IDLER. The idler's axis is the ONE axis")
print("  that points across the leg, and a %.0f mm motor on it adds its whole length to the"
      % MOTOR_L)
print("  machine's width. The drive end is already the widest thing on the thigh.")

print()
print("=" * 98)
print("C.  THE 2:1 BEVEL, ON ITS MERITS")
print("=" * 98)
n_belt = N_SCREW / 1.9
n_bev = N_SCREW / 2.0
tau_belt = TAU_KNEE / (n_belt * ETA_SCREW * ETA_BELT)
tau_bev = TAU_KNEE / (n_bev * ETA_SCREW * ETA_BEVEL)
print("  %-34s %9s %9s %10s %9s" % ("", "ratio", "motor Nm", "refl/limb", "stage eta"))
print("  %-34s %8.1f:1 %9.3f %9.2fx %9.2f"
      % ("38T:20T HTD-5M as built", n_belt, tau_belt, J_ROTOR * n_belt ** 2 / J_LIMB, ETA_BELT))
print("  %-34s %8.1f:1 %9.3f %9.2fx %9.2f"
      % ("2:1 bevel", n_bev, tau_bev, J_ROTOR * n_bev ** 2 / J_LIMB, ETA_BEVEL))
for m in (1.0, 1.5, 2.0):
    t_big, t_small = 40, 20
    r_big = m * t_big / 2.0
    f = tau_bev * 1000.0 / r_big
    print("     module %.1f, %dT:%dT -> pitch dia %.0f / %.0f, %3.0f N tangential"
          % (m, t_big, t_small, m * t_big, m * t_small, f))
print()
print("  THE LOAD IS NOTHING -- tens of newtons on gears that would be sized for hundreds. What")
print("  a bevel pair actually costs is in two places a belt does not charge:")
print()
print("     MOUNTING DISTANCE. A bevel pair's tooth contact depends on both gears sitting at the")
print("     right distance from the common cone apex, to roughly a tenth of a millimetre. A belt")
print("     does not care: 433's centre distance is whatever the idler slot is set to. This")
print("     machine's structure is PRINTED PETG, which moves with temperature and creeps under")
print("     load, and 418_knee_bearing.py already refuses press fits in it for that reason.")
print("     Bevels in printed housings need shims and a way to measure the contact pattern.")
print()
print("     NOISE. Straight bevels whine, and this is worn on a person all day. The belt is the")
print("     quietest element in the drivetrain.")
print()
print("  And it buys %.2f efficiency against %.2f -- slightly WORSE than the belt it replaces."
      % (ETA_BEVEL, ETA_BELT))

print()
print("=" * 98)
print("  WHAT I WOULD TAKE AND WHAT I WOULD LEAVE")
print("=" * 98)
print("  TAKE A -- NO. THIS RECOMMENDATION WAS WRONG AND IS RETRACTED. The carriage does")
print("  not reach from the nut to the RAIL, it reaches from the nut to the one belt strand it")
print("  clamps, at X -37.3. The screw sits at X -62, so that reach is 24.7 mm. Centring it on")
print("  the rail moves it AWAY from the strand: 37.3 mm, half as much again. The move that")
print("  would actually zero it is the screw IN LINE with the strand at X -37.3 -- which the")
print("  belt itself occupies at Z 96..126, so it would have to go above or below it.")
print()
print("  LEAVE B. The idler's axis is the across-the-leg one. Hanging a %.0f mm motor on it"
      % MOTOR_L)
print("  trades a box that sticks out BEHIND the thigh for one that sticks out BESIDE it, and")
print("  beside is the direction that decides whether the legs pass each other.")
print()
print("  LEAVE C, but not because of the gears. A 2:1 bevel is mechanically fine and barely")
print("  loaded. It is the mounting tolerance in printed plastic, and the noise, and that the")
print("  only reason to turn a corner is to put the motor somewhere -- and B is where it would")
print("  have gone.")
print()
print("  THE MOTOR WANTS TO LIE ALONG THE THIGH, not across it and not behind it. Its axis")
print("  parallel to the screw, tucked against the rail, inside one shell -- which keeps the")
print("  HTD-5M pair, keeps the tolerance that a belt forgives, and is what 'one cohesive")
print("  thigh' actually asks for.")
