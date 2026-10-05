# -*- coding: utf-8 -*-
"""Delete the link belt and couple the motor straight to the screw. Measured, nothing built.

Asked at the bench: "does it even need a belt to it at that point -- can't we just move the motor
spindle directly over the shaft and just use a coupling by shuffling the big idler bracket around
a bit more?"

Two separate questions, and they have different answers, so they are kept apart here:

  1. WHAT THE BELT IS BUYING. It is not geometry and it is not torque. 404_link_ratio.py put a
     32T on the motor and a 20T on the screw to OVERDRIVE the screw 1.6x, and the only thing that
     ratio buys is reflected inertia -- which goes as the ratio SQUARED and is the number this
     whole design is organised around. Coupling 1:1 does not cost knee speed (the screw still
     turns at the same rpm; the motor turns faster) and it does not cost torque (it gains it:
     23.2:1 instead of 14.5:1, so 1.35 N.m at the motor instead of 2.16, and 24.0 A instead of
     38.5). It costs back-drivability, and that is the only thing it costs.

  2. WHETHER A COAXIAL MOTOR FITS. It does not, and the reason is one number rather than a
     packaging argument. The motor is at X -104 Z 62 and the screw at X -62 Z 106 -- diagonal
     to each other, 61 mm apart, not side by side. Coaxial, the motor's can has to pass through
     the MAIN belt's drive strand, which runs the full length of the thigh 25.8 mm from the
     screw's axis against the motor's 31.5 mm radius.

THE ANSWER, UP FRONT: the belt stays, because the motor is 5.7 mm of radius too fat to sit on
the screw. What the measurement does change is the shopping list -- a 16 mm lead coupled 1:1 is
the same 14.5:1 with no belt and no inertia penalty, so an SFU1616 is worth hunting for again,
and it would need a motor of dia 52 or less.

Nothing in this file writes to the document.

    freecadcmd.exe scripts/435_direct_couple.py
"""
import itertools
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

# --------------------------------------------------------------- the drivetrain arithmetic
TEETH, PITCH = 29, 8.0
R_CAP = TEETH * PITCH / (2 * math.pi)       # 36.92 mm, the capstan radius
TAU_KNEE = 28.2                             # N.m
ETA_S = 0.90                                # ball screw
J_ROTOR, J_LIMB = 3.10e-4, 0.30             # kg.m2
KT = 9.549 / 170.0                          # C6374 at 170 Kv
RPM_SCREW = 1160.0                          # set by the gait speed, unchanged by any of this
I_LIMIT = 40.0                              # A, the motor's continuous ceiling (350_motor_kv.py)

print("=" * 98)
print("DIRECT COUPLING: DELETE THE LINK BELT  --  %s" % _BASE)
print("=" * 98)
print("  1. WHAT THE 1:1.6 OVERDRIVE IS ACTUALLY BUYING")
print()
print("     %-26s %8s %9s %7s %9s %10s %9s"
      % ("", "N total", "T_motor", "amps", "rpm mot", "refl J", "vs limb"))
rows = []
for lbl, lead, link in (("as built: 10 mm + 1:1.6", 10.0, 0.625),
                        ("COUPLED, 10 mm lead", 10.0, 1.0),
                        ("COUPLED, 16 mm lead", 16.0, 1.0),
                        ("COUPLED, 20 mm lead", 20.0, 1.0)):
    n_screw = 2 * math.pi * R_CAP / lead
    n_tot = n_screw * link
    tau_m = TAU_KNEE / (n_tot * ETA_S)
    amps = tau_m / KT
    # motor rpm = screw rpm / the overdrive. An earlier version divided by `link` (0.625),
    # which is the overdrive's RECIPROCAL, and reported 1856 rpm for the as-built case where
    # 404_link_ratio.py says 725. The ratio and torque columns were right; only this was not.
    rpm_m = RPM_SCREW * (lead / 10.0) * link
    j = J_ROTOR * n_tot ** 2
    rows.append((lbl, n_tot, tau_m, amps, rpm_m, j))
    print("     %-26s %7.1f:1 %7.2f Nm %6.1f A %8.0f %9.3f %8.2fx %s"
          % (lbl, n_tot, tau_m, amps, rpm_m, j, j / J_LIMB,
             "" if amps <= I_LIMIT else "<-- over the motor's %.0f A" % I_LIMIT))
print()
print("     The knee's SPEED is identical in every row -- the screw turns at %.0f rpm whatever is"
      % RPM_SCREW)
print("     on the other end of it, and only the motor's own rpm changes. So coupling costs no")
print("     speed and no torque; it costs reflected inertia, and gains current headroom.")
print()
base, coup = rows[0], rows[1]
print("     Coupling the 10 mm screw: %.1f A instead of %.1f (-%.0f%% of the motor's work), and"
      % (coup[3], base[3], 100 * (1 - coup[3] / base[3])))
print("     reflected inertia %.3f instead of %.3f kg.m2 -- %.2fx the limb instead of %.2fx."
      % (coup[5], base[5], coup[5] / J_LIMB, base[5] / J_LIMB))
print("     Unpowered, the leg feels %.0f%% heavier to swing rather than %.0f%%."
      % (100 * coup[5] / J_LIMB, 100 * base[5] / J_LIMB))
print("     A 16 mm lead coupled 1:1 lands on the SAME %.1f:1 as today with no belt at all --"
      % rows[2][1])
print("     which is the SFU1616 route 404 abandoned only because the supplier search could not")
print("     confirm the part exists. Coupling makes that screw worth hunting for again.")

# --------------------------------------------------------------- does it fit?
SCREW_X, SCREW_Z = -62.0, 106.0
MOT_R, MOT_L = 31.5, 74.0
THREAD_TOP = 204.0          # 433's JOURNAL[1]: the nut must have thread under it to here
BRG = 7.0                   # the 608
COUPLING = (25.0, 30.0)     # dia x length, a jaw/bellows coupling for 8 mm to 8 mm -- BOUGHT,
                            # and the length is the number to check against a real catalogue
CPL_Y = (THREAD_TOP + BRG, THREAD_TOP + BRG + COUPLING[1])
NEW_MOT_Y = (CPL_Y[1], CPL_Y[1] + MOT_L)

print()
print("=" * 98)
print("  2. WHERE A COAXIAL MOTOR WOULD HAVE TO SIT")
print("     screw's thread ends Y %.0f, the 608 takes Y %.0f..%.0f, a %.0f mm coupling Y %.0f..%.0f,"
      % (THREAD_TOP, THREAD_TOP, THREAD_TOP + BRG, COUPLING[1], CPL_Y[0], CPL_Y[1]))
print("     so the motor is Y %.0f..%.0f on the screw's own axis, X %.1f Z %.1f"
      % (NEW_MOT_Y[0], NEW_MOT_Y[1], SCREW_X, SCREW_Z))
a3 = doc.getObject("A3_Motor_6374")
mb = a3.Shape.BoundBox
print("     against where it is now: X %.1f..%.1f Y %.0f..%.0f Z %.1f..%.1f"
      % (mb.XMin, mb.XMax, mb.YMin, mb.YMax, mb.ZMin, mb.ZMax))
print("     that is %.0f mm inboard in X, %.0f mm up in Z and %.0f mm further along the limb"
      % (SCREW_X - 0.5 * (mb.XMin + mb.XMax), SCREW_Z - 0.5 * (mb.ZMin + mb.ZMax),
         NEW_MOT_Y[1] - mb.YMax))

motor = Part.makeCylinder(MOT_R, MOT_L, V(SCREW_X, NEW_MOT_Y[0], SCREW_Z), V(0, 1, 0))
cpl = Part.makeCylinder(COUPLING[0] / 2.0, COUPLING[1], V(SCREW_X, CPL_Y[0], SCREW_Z), V(0, 1, 0))
cand = motor.fuse(cpl)

CLAD = ("P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P24_FairingShank",
        "P25_MotorNacelle", "P23a_FairingMount", "P23b_FairingMount", "P23c_FairingMount")
# The screw and the present motor and link belt are coaxial-by-definition or deleted by the
# proposal, so counting them as clashes would be counting the answer as the problem.
SKIP = ("A3_Motor_6374", "A7b_LinkBelt", "P27_ControllerMount", "HW_ODrive_XDriveMini",
        "A2_BallScrew_SFU1620", "A2b_BallNut_SFU1620")

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P31_InterfaceDist", "REF_Shank", "HW_JointBolts"]
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
MOVERS = set(SHANK) | set(GANTRY)

parts = [o for o in doc.Objects
         if o.TypeId == "Part::Feature" and getattr(o, "Shape", None) is not None
         and not o.Shape.isNull() and o.Shape.Solids
         and not o.Name.startswith("TEST_") and o.Name not in SKIP]

print()
print("     WHAT THE COAXIAL MOTOR RUNS INTO, static parts (the belt and the present motor")
print("     excluded -- they are what this deletes):")
hits = []
for o in parts:
    if o.Name in MOVERS:
        continue
    c = cand.common(o.Shape)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    if v > 0.02:
        kind = "cladding" if o.Name in CLAD else ("THE LIMB" if o.Name.startswith("REF_")
                                                  else "STRUCTURE")
        hits.append((v, o.Name, kind))
for v, nm, kind in sorted(hits, reverse=True):
    print("        %-28s %8.2f cm3   %s" % (nm, v, kind))
if not hits:
    print("        nothing at all")

# the movers, over the whole range of motion
A0 = 161.0
worst = {}
for th in [float(i) for i in range(-2, 105, 2)]:
    r = FreeCAD.Rotation(V(0, 0, 1), th)
    dy = -R_CAP * math.radians(th)
    for o in parts:
        if o.Name not in MOVERS:
            continue
        o.Placement = (FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0)) if o.Name in SHANK
                       else FreeCAD.Placement(V(0, dy, 0), FreeCAD.Rotation()))
        c = cand.common(o.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > worst.get(o.Name, (0.0, 0.0))[0]:
            worst[o.Name] = (v, th)
for o in parts:
    if o.Name in MOVERS:
        o.Placement = FreeCAD.Placement()
mv = [(v, nm, th) for nm, (v, th) in worst.items() if v > 0.02]
print()
print("     and the moving parts, swept -2..104 deg:")
for v, nm, th in sorted(mv, reverse=True):
    print("        %-28s %8.2f cm3 at %+.0f deg" % (nm, v, th))
if not mv:
    print("        nothing at all")

# --------------------------------------------------------------- the limb is the decider
print()
print("     HOW CLOSE THE LIMB IS. The motor's inboard skin would be X %.1f."
      % (SCREW_X + MOT_R))
ref = doc.getObject("REF_Thigh")
if ref is not None:
    for y in (240.0, 260.0, 280.0, 300.0, 315.0):
        xs = [x for x in [-60.0 + i * 1.0 for i in range(90)]
              if ref.Shape.isInside(V(x, y, SCREW_Z), 1e-7, True)]
        if not xs:
            print("        Y %5.0f : no limb at Z %.0f" % (y, SCREW_Z))
            continue
        print("        Y %5.0f : limb's lateral skin at X %5.1f, motor would reach X %5.1f -> %s"
              % (y, min(xs), SCREW_X + MOT_R,
                 "%.1f mm of gap" % (min(xs) - (SCREW_X + MOT_R)) if min(xs) > SCREW_X + MOT_R
                 else "%.1f mm INTO THE LEG" % ((SCREW_X + MOT_R) - min(xs))))

# --------------------------------------------------------------- the strand is the blocker
print()
print("=" * 98)
print("  3. WHY IT DOES NOT FIT, IN ONE NUMBER")
run = doc.getObject("A5b_Belt_DriveRun")
wrap = doc.getObject("A5d_Belt_WrapIdler")
rb = run.Shape.BoundBox
clear = abs(rb.XMax - SCREW_X)
print("     The MAIN belt's drive strand runs the whole length of the thigh at X %.1f..%.1f,"
      % (rb.XMin, rb.XMax))
print("     Z %.0f..%.0f -- straddling the screw, which is what the gantry's tunnel is for."
      % (rb.ZMin, rb.ZMax))
print("     Its inboard face is %.1f mm from the screw's axis. The C6374's radius is %.1f."
      % (clear, MOT_R))
print()
print("     So a motor on the screw's axis overlaps the strand by %.1f mm of radius. It is not"
      % (MOT_R - clear))
print("     a little tight: the can has to pass THROUGH the belt. A motor would fit the axis at")
print("     dia %.0f or less, against the C6374's %.0f." % (2 * clear, 2 * MOT_R))
print()
wb = wrap.Shape.BoundBox
print("     The only way past it is along the limb: the strand and its wrap over the idler")
print("     occupy every Y up to %.1f, so a coaxial motor starts at Y %.0f and ends at Y %.0f."
      % (wb.YMax, wb.YMax, wb.YMax + MOT_L))
cap = doc.getObject("P22_DriveCap").Shape.BoundBox
print("     The pack ends at Y %.0f today, so that is +%.0f mm of thigh before the controller,"
      % (cap.YMax, wb.YMax + MOT_L - cap.YMax))
print("     which then adds its own %.0f mm on top of that." % 23.0)
print()
print("     AND THE IDLER CANNOT MOVE DOWN TO HELP. Its Y is the belt's length: a closed %s"
      % "742 mm / 93T")
print("     loop over the capstan and the idler. Bringing it down needs a shorter belt, and the")
car = doc.getObject("P3_Carriage").Shape.BoundBox
idl = doc.getObject("A6_Idler29T").Shape.BoundBox
print("     carriage already comes up to Y %.0f against the idler's disc at Y %.0f -- %.1f mm"
      % (car.YMax, idl.YMin, idl.YMin - car.YMax))
print("     apart. Moving the idler UP, which a longer belt would do, pushes the strand further")
print("     along the limb and makes the motor's problem worse, not better.")

print()
print("     WHAT MOVING IT WOULD ALSO COST LATERALLY. The two axes are not in one plane:")
print("     X is anterior-posterior and Z is medial-lateral, and the motor and the screw are")
print("     diagonal to each other, %.0f mm apart."
      % math.hypot(SCREW_X - 0.5 * (mb.XMin + mb.XMax), SCREW_Z - 0.5 * (mb.ZMin + mb.ZMax)))
print("     Coaxial, the motor's skin goes from Z %.1f to Z %.1f -- %.0f mm further out to the"
      % (mb.ZMax, SCREW_Z + MOT_R, (SCREW_Z + MOT_R) - mb.ZMax))
print("     side of the thigh, and %.0f mm past the cladding's present lateral face at Z %.1f."
      % ((SCREW_Z + MOT_R) - doc.getObject("P25_MotorNacelle").Shape.BoundBox.ZMax,
         doc.getObject("P25_MotorNacelle").Shape.BoundBox.ZMax))
print("     Its distance from the limb's axis barely changes (%.0f mm now, %.0f mm coaxial), so"
      % (math.hypot(0.5 * (mb.XMin + mb.XMax), 0.5 * (mb.ZMin + mb.ZMax)),
         math.hypot(SCREW_X, SCREW_Z)))
print("     there is no mass-centralisation gain to set against it. The pack just rotates around")
print("     the limb and gets wider on the outside.")

print()
print("=" * 98)
print("  4. WHAT THE BELT IS WORTH, THEN")
belt = doc.getObject("A7b_LinkBelt")
print("     It costs: a %s closed loop, a 32T and a 20T pulley, a belt window through the"
      % "HTD-5M 15 mm")
print("     bracket, and %.0f mm of the pack's length for its plane." % 12.0)
print("     It buys: the motor off the screw's axis, which is the only reason a dia %.0f can"
      % (2 * MOT_R))
print("     exist in this pack at all -- and, separately, reflected inertia %.2fx the limb"
      % (J_ROTOR * (2 * math.pi * R_CAP / 10.0 * 0.625) ** 2 / J_LIMB))
print("     instead of %.2fx."
      % (J_ROTOR * (2 * math.pi * R_CAP / 10.0) ** 2 / J_LIMB))
print()
print("     THE ONE VERSION OF THIS THAT WOULD WORK is a smaller motor: dia %.0f or less fits"
      % (2 * clear))
print("     the axis, and coupled 1:1 to the 10 mm screw it would need %.2f N.m -- which is more"
      % (TAU_KNEE / ((2 * math.pi * R_CAP / 10.0) * ETA_S)))
print("     than a dia 50 outrunner makes continuously. The torque is why the motor is dia %.0f,"
      % (2 * MOT_R))
print("     and the diameter is why it cannot sit on the screw. That is the whole argument.")
