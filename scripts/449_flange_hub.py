# -*- coding: utf-8 -*-
"""A steel flange coupling sunk into the printed pulley, aluminium plate behind, bolted through.

Proposed at the bench: "what if we print the pulleys so one of these is cut into one side and a
~3mm thick square aluminum plate is on the other, and we screw through the 3d printed pulleys?"

447_printed_pulleys.py said print the 20T and the idler but BUY the 38T motor pulley, for one
reason and one reason only: 331 N of tangential load going into PETG through a grub screw, on the
only shaft in the machine that runs past the glass transition. The teeth were never the problem --
2.0 N each, a factor of 100.

THIS KILLS THAT OBJECTION, and the arithmetic is not close. A grub screw puts the whole torque
through one dimple at the BORE radius. A flange coupling puts it through four bolts at the BOLT
CIRCLE radius, which is two and a half times further out and shared four ways:

    grub screw   F = tau / r_bore              331 N, into a dimple in plastic
    four bolts   F = tau / (4 * r_pcd)          33 N each, into a hole in plastic

Ten times less force, in bearing against a hole rather than indentation under a point, and the
steel-to-steel grip on the shaft is now the coupling's problem -- which is what it is sold to do.
The aluminium plate on the far side is what stops the bolt heads pulling through.

AND IT GENERALISES. If the 38T can be printed then all four pulleys can, and the only bought
pulley left in the machine is none.

    python scripts/449_flange_hub.py
"""
import math

import FreeCAD
import Part

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"

# the drivetrain, post-SFU1605 + 38T:20T
R_CAP = 29 * 8.0 / (2 * math.pi)
TAU_KNEE = 28.2
N_TOT = (2 * math.pi * R_CAP / 5.0) / 1.9
TAU_MOT = TAU_KNEE / (N_TOT * 0.90 * 0.97)          # 1.323 N.m
TAU_SCREW = TAU_MOT * (20 / 38.0) * 0.97            # 0.675 N.m

# the flange coupling in the photo. MEASURE YOURS -- these are read off the picture's proportions
# against a dia 8 bore and are the only unverified numbers here.
FLANGE_OD = 25.0
FLANGE_T = 4.0
BOSS_OD = 13.0
BOSS_H = 11.0
PCD = 18.0
BOLT_D = 3.4            # M3 clearance
N_BOLT = 4
PLATE_T = 3.0           # the aluminium backing plate

# HTD-5M form, as 447
PLD5, TOOTH_H5 = 0.571, 2.16
PETG_BEARING = 40.0
PETG_TG = 80.0


def tip_r(teeth):
    return teeth * 5.0 / (2 * math.pi) - PLD5


def root_r(teeth):
    return tip_r(teeth) - TOOTH_H5


print("=" * 98)
print("1.  WHAT EACH BOLT CARRIES, AGAINST THE GRUB SCREW IT REPLACES")
print("=" * 98)
print("  %-22s %9s %7s %10s %9s %10s %9s"
      % ("", "torque", "bore", "grub screw", "per bolt", "bearing", "factor"))
for name, tau, bore, hub_t in (("38T motor pulley", TAU_MOT, 8.0, 10.0),
                               ("20T screw pulley", TAU_SCREW, 12.0, 10.0)):
    f_grub = tau * 1000.0 / (bore / 2.0)
    f_bolt = tau * 1000.0 / (N_BOLT * PCD / 2.0)
    bearing = f_bolt / (BOLT_D * hub_t)
    print("  %-22s %7.3f Nm %6.0f %8.0f N %7.0f N %8.2f MPa %8.0f"
          % (name, tau, bore, f_grub, f_bolt, bearing, PETG_BEARING / bearing))
print()
print("  %d bolts on a %.0f mm circle, bearing on %.0f mm of printed hub. The motor pulley's"
      % (N_BOLT, PCD, 10.0))
print("  worst case is %.0f N per bolt -- a factor of %.0f on PETG's bearing strength, where the"
      % (TAU_MOT * 1000.0 / (N_BOLT * PCD / 2.0),
         PETG_BEARING / (TAU_MOT * 1000.0 / (N_BOLT * PCD / 2.0) / (BOLT_D * 10.0))))
print("  grub screw straight into plastic was a factor of about 1. That is the whole argument.")
print()
print("  And the shaft grip is no longer plastic's job at all: two M4 grub screws steel-on-steel")
print("  onto a dia 8 shaft is what a rigid coupling is sold to do, rated well past %.1f N.m."
      % TAU_MOT)

print()
print("=" * 98)
print("2.  DOES THE FLANGE FIT INSIDE THE PULLEY?")
print("=" * 98)
print("  %-22s %8s %9s %10s %11s %s"
      % ("", "tip r", "root r", "flange r", "wall left", ""))
for name, teeth in (("38T motor pulley", 38), ("20T screw pulley", 20)):
    rr = root_r(teeth)
    wall = rr - FLANGE_OD / 2.0
    bolt_wall = rr - (PCD / 2.0 + BOLT_D / 2.0)
    verdict = "fits, %.1f mm of wall outboard of the bolts" % bolt_wall
    if FLANGE_OD / 2.0 > rr:
        verdict = "FLANGE IS WIDER THAN THE PULLEY -- it stands proud, see below"
    elif bolt_wall < 2.0:
        verdict = "bolts only %.1f mm from the tooth roots   <-- too thin" % bolt_wall
    print("  %-22s %6.2f %9.2f %10.2f %10.2f   %s"
          % (name, tip_r(teeth), rr, FLANGE_OD / 2.0, wall, verdict))
print()
print("  The 38T is roomy: the flange is buried in a body %.1f mm in radius with the bolt circle"
      % root_r(38))
print("  %.1f mm clear of the tooth roots." % (root_r(38) - (PCD / 2.0 + BOLT_D / 2.0)))
print()
print("  The 20T is the tight one, and it does not matter, because the 20T NEVER NEEDED THIS.")
print("  %.0f N on a dia 12 journal at room temperature was already a factor of %.0f straight"
      % (TAU_SCREW * 1000.0 / 6.0, PETG_BEARING / (TAU_SCREW * 1000.0 / 6.0 / (5.0 * 10.0))))
print("  into plastic (447). Put a grub screw in it through a heat-set insert and move on. If you")
print("  want the flange there too, a smaller coupling on a %.0f mm circle gives %.0f N per bolt."
      % (12.0, TAU_SCREW * 1000.0 / (N_BOLT * 6.0)))

print()
print("=" * 98)
print("3.  THE FAILURE MODE THIS DOES NOT FIX: CREEP IN THE SANDWICH")
print("=" * 98)
print("  Bolting through plastic, the bolt preload sits on the plastic forever. PETG creeps under")
print("  sustained compression, the preload bleeds away, and the joint goes loose -- which on a")
print("  pulley means the two steel plates start to index round against the plastic.")
print()
print("  It is not the torque that does it, it is the TORQUE SETTING. An M3 at a normal 1.2 N.m")
print("  is about 2 kN of preload; under a washer that is %.0f MPa on the plastic, five times"
      % (2000.0 / (math.pi * (8.0 ** 2 - 1.7 ** 2) / 4.0)))
print("  what it will hold without flowing.")
print()
print("  TWO FIXES, and the second is better:")
print("     a. torque them to hand-tight plus a nip, use nyloc or thread lock, and re-check them")
print("        after the first few hours like the belt.")
print("     b. put a STEEL SPACER in each bolt hole, cut 0.1 mm PROUD of the printed hub. The")
print("        flange and the aluminium plate then clamp steel-to-steel at full torque and the")
print("        plastic carries no preload at all -- only the %.0f N of bearing it is good for."
      % (TAU_MOT * 1000.0 / (N_BOLT * PCD / 2.0)))
print("        A cut length of %.0f mm OD tube, or four more grub screws used as pillars."
      % 5.0)

print()
print("=" * 98)
print("4.  HEAT, HONESTLY")
print("=" * 98)
print("  447 said the motor shaft runs past PETG's %.0f C Tg and a printed hub would creep until"
      % PETG_TG)
print("  the belt skipped. The coupling does NOT make the plastic cooler -- steel conducts, so if")
print("  anything it carries heat outward faster. What it changes is what the warm plastic has to")
print("  do: grip a shaft against %.0f N (which softening destroys) becomes bear %.0f N against"
      % (TAU_MOT * 1000.0 / 4.0, TAU_MOT * 1000.0 / (N_BOLT * PCD / 2.0)))
print("  four holes (which softening barely touches -- PETG at 70 C still holds several MPa).")
print()
print("  So: mechanically solved, thermally improved, not thermally eliminated. Fix (b) above")
print("  matters more because of the heat, not less -- creep goes up fast with temperature.")

print()
print("=" * 98)
print("5.  IS THERE ROOM IN THE POD?")
print("=" * 98)
doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}
MOT_X, MOT_Z = -104.0, 62.0
stack = FLANGE_T + BOSS_H + PLATE_T
print("  the stack is flange %.0f + boss %.0f + plate %.0f = %.0f mm, and the 15 mm belt sits"
      % (FLANGE_T, BOSS_H, PLATE_T, stack))
print("  inside it, so call it %.0f mm of Y at the motor axis." % max(stack, 15.0 + PLATE_T))
probe = Part.makeCylinder(FLANGE_OD / 2.0 + 2.0, 30.0,
                          FreeCAD.Vector(MOT_X, 176.0, MOT_Z), FreeCAD.Vector(0, 1, 0))
print()
print("  what is on the motor axis between Y 176 and 206 (below the belt plane, Path B):")
hits = 0
for o in doc.Objects:
    if not o.isDerivedFrom("Part::Feature"):
        continue
    try:
        c = o.Shape.common(probe)
    except Exception:
        continue
    if c.Volume > 50.0:
        b = c.BoundBox
        hits += 1
        print("     %-26s %7.2f cm3   Y %6.1f..%6.1f" % (o.Name, c.Volume / 1000.0, b.YMin, b.YMax))
if not hits:
    print("     nothing -- the boss can hang below the belt into the drive box's own volume.")
else:
    print()
    print("  SO THE BOSS HAS NOWHERE TO GO BUT THROUGH THE NACELLE. Upward is blocked: with the")
    print("  Path B belt at Y 206..221 and the motor plate at Y 223..231 there are 2 mm between")
    print("  them, and the boss is %.0f. Downward it meets P25_MotorNacelle's nose wall at" % BOSS_H)
    print("  Y 201..204. That wall needs a dia %.0f clearance bore on the motor axis -- which is"
          % (BOSS_OD + 3.0))
    print("  a cut in a part 434_odrive_mount.py rebuilds every run, so it belongs in 434 and not")
    print("  in a patch after it. 439's trim was silently undone once already by exactly this.")

print()
print("=" * 98)
print("  THE ANSWER: yes, and it retires the last bought pulley.")
print("=" * 98)
print("  BOM D7 goes from 'buy the 38T in aluminium' to 'print it, with a rigid flange coupling")
print("  sunk in the back and a %.0f mm plate in front'. Every pulley in the machine is then"
      % PLATE_T)
print("  printed: the capstan, the idler, the 20T and the 38T.")
print()
print("  The aluminium plate is doing a second job worth naming: at %.0f mm it is also the belt"
      % PLATE_T)
print("  FLANGE on that side, which a 15 mm belt on a 60 mm pulley wants anyway.")
print()
print("  BUY: 4 rigid flange couplings, dia 8 bore (one needed, they come in fours), and a strip")
print("  of %.0f mm aluminium. MEASURE the coupling's flange OD, thickness, boss height, bolt"
      % PLATE_T)
print("  circle and hole size before this goes into CAD -- every dimension above is read off a")
print("  product photo, which is exactly the mistake 434_odrive_mount.py is still carrying.")
