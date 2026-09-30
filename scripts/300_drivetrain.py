# -*- coding: utf-8 -*-
"""Drivetrain sizing for the belt-capstan / differential-screw knee exo.

Pure Python -- no FreeCAD. Everything downstream (BOM, ODrive config, battery)
is derived here so there is one place to change an assumption.

  knee  --HTD-8M belt, 29T capstan--  two carriages
        --LH/RH ball screws on one shaft--  motor

Run:  python scripts/300_drivetrain.py
"""
import math

# ---------------------------------------------------------------- geometry
TEETH, PITCH = 29, 8.0
R = TEETH * PITCH / (2 * math.pi)          # capstan pitch radius, mm
ROM_DEG = 106.0                            # -2 .. +104
TRAVEL = R * math.radians(ROM_DEG)         # carriage stroke, mm
BELT_W = 30.0                              # belt height in the model, Z 96..126

# ---------------------------------------------------------- design targets
# Stair ascent peak knee moment is ~1.0-1.5 N.m/kg. At 80 kg that is 80-120 N.m
# for the whole joint; we are a PARTIAL assist, not a replacement.
BODY_KG = 80.0
TAU_PEAK = 28.2                            # N.m at the knee, peak
ASSIST = TAU_PEAK / (1.2 * BODY_KG)
W_CONT = math.radians(180.0)               # rad/s, stair cadence
W_PEAK = math.radians(300.0)               # rad/s, free swing

ETA_SCREW = 0.90                           # ball screw forward efficiency
ETA_BELT = 0.97

print("=" * 68)
print("KNEE SIDE")
print("  capstan      %dT HTD-%gM   R = %.3f mm" % (TEETH, PITCH, R))
print("  ROM          %.0f deg  ->  carriage stroke %.1f mm" % (ROM_DEG, TRAVEL))
print("  peak torque  %.1f N.m  = %.0f%% of an 80 kg stair-ascent knee moment"
      % (TAU_PEAK, 100 * ASSIST))
print("  belt tension %.0f N differential over %.0f mm width = %.1f N/mm"
      % (TAU_PEAK * 1000 / R, BELT_W, TAU_PEAK * 1000 / R / BELT_W))
print("  teeth engaged at 180 deg wrap: %.1f" % (TEETH / 2.0))

# ------------------------------------------------------------ screw options
print("=" * 68)
print("SCREW LEAD TRADE  (ratio = screw rad/s per knee rad/s)")
print("  %-10s %7s %8s %8s %9s %9s" %
      ("screw", "ratio", "revs", "T_screw", "n@180d/s", "n@300d/s"))
for name, lead, nut_od in (("SFU1605", 5.0, 28.0), ("SFU1610", 10.0, 36.0),
                           ("SFU1620", 20.0, 40.0)):
    ratio = 2 * math.pi * R / lead
    tau_s = TAU_PEAK / (ratio * ETA_SCREW)
    n_c = ratio * W_CONT * 60 / (2 * math.pi)
    n_p = ratio * W_PEAK * 60 / (2 * math.pi)
    print("  %-10s %7.2f %8.2f %6.2f Nm %7.0f rpm %7.0f rpm   nut OD %.0f"
          % (name, ratio, TRAVEL / lead, tau_s, n_c, n_p, nut_od))
print("  BUILT: SFU1610, nuts at OD 36 (NUT_R=18), screws at X = +/-58. 1605 was the")
print("       first answer here and it is wrong -- see the reflected-inertia table")
print("       below, which is the section that actually decides the lead.")

LEAD = 10.0
RATIO = 2 * math.pi * R / LEAD
TAU_SCREW = TAU_PEAK / (RATIO * ETA_SCREW)
N_PEAK = RATIO * W_PEAK * 60 / (2 * math.pi)
N_CONT = RATIO * W_CONT * 60 / (2 * math.pi)

# ------------------------------------------------------------------ motor
print("=" * 68)
print("MOTOR  (direct 1:1 to the screw shaft, one 1:1 belt links the two screws)")
VBAT = 38.4                                # 12S LiFePO4 nominal; 43.8 V full
print("  shaft torque %.2f N.m peak, %.0f rpm peak, %.0f rpm at stair cadence"
      % (TAU_SCREW / ETA_BELT, N_PEAK, N_CONT))
print("  %-12s %6s %9s %9s %9s %9s" %
      ("motor", "Kv", "Kt", "I_peak", "no-load", "headroom"))
for name, kv, mass in (("6374 OWNED", 170, 800), ("6374", 149, 820),
                       ("6354", 190, 560), ("63100", 130, 1100)):
    kt = 9.549 / kv
    i = TAU_SCREW / ETA_BELT / kt
    nl = kv * VBAT
    print("  %-12s %6d %6.4f Nm/A %6.1f A %7.0f rpm %7.1fx"
          % (name, kv, kt, i, nl, nl / N_PEAK))
_tau_m = TAU_SCREW / ETA_BELT
_i170, _i149 = _tau_m / (9.549 / 170), _tau_m / (9.549 / 149)
_p_mech = _tau_m * N_PEAK * 2 * math.pi / 60.0
_p_cu = 1.5 * _i170 ** 2 * 0.020
print("  -> the motors we own are 170 Kv: %.1f A phase peak at %.2f N.m"
      % (_i170, _tau_m))
print("     was %.1f A at the 149 Kv this was first sized for -- 14%% more current for"
      % _i149)
print("     the same torque, and NO extra heat. See 360_owned_hw.py section 0.")
print("  -> BUS power, which is not V x I_phase: %.0f W mechanical + %.0f W copper"
      % (_p_mech, _p_cu))
print("     = %.0f W off a %.1f V bus = %.1f A of PACK current at peak torque."
      % (_p_mech + _p_cu, VBAT, (_p_mech + _p_cu) / VBAT))
print("     Phase current is high and bus current is low because back-EMF is only")
print("     %.1f V at %.0f rpm -- the drive is bucking hard. Fuse for the BUS."
      % (N_PEAK / 170.0, N_PEAK))

# ------------------------------------------------------- reflected inertia
# This is the one that decides the lead, not the current draw.
print("=" * 68)
print("REFLECTED INERTIA  (what the patient feels when the motor is off)")
J_ROTOR = 3.1e-4        # 6374 outrunner bell, ~0.40 kg at ~28 mm mean radius
J_LIMB = 0.30           # shank + foot about the knee, 80 kg adult
BELT_X_OUT = 41.12      # belt outer face, from kin_low.json
print("  6374 rotor J ~= %.2e kg.m2 ; shank+foot about the knee ~= %.2f kg.m2"
      % (J_ROTOR, J_LIMB))
print("  Reflected J scales with the TOTAL knee->motor ratio SQUARED, so you")
print("  cannot fix it by moving the reduction around -- only by lowering the")
print("  total ratio or using a lower-inertia rotor.")
print("  %-10s %7s %9s %9s %9s %9s %9s" %
      ("screw", "ratio", "J_refl", "vs limb", "I_peak", "nut OD", "at X=56"))
best = None
for name, lead, nut_od in (("SFU1605", 5.0, 28.0), ("SFU1610", 10.0, 36.0),
                           ("SFU1616", 16.0, 36.0), ("SFU1620", 20.0, 40.0)):
    ratio = 2 * math.pi * R / lead
    j = J_ROTOR * ratio ** 2
    tau_s = TAU_PEAK / (ratio * ETA_SCREW) / ETA_BELT
    amps = tau_s / (9.549 / 170)
    # NOT a belt-gap column: the nut sits 60 mm proximal of its belt run's end at every
    # pose, so an X-projection comparing their edges is meaningless. See 311_nut_belt.py.
    print("  %-10s %7.2f %6.3f kgm2 %7.2fx %7.1f A %7.0f mm    fits"
          % (name, ratio, j, j / J_LIMB, amps, nut_od))
print("  A ratio that makes the leg feel 2x heavier with the power off is not")
print("  acceptable on a patient who already struggles to swing the limb.")
print("  SFU1610 is the BUILD point: 0.56x the limb's own inertia, 25 A peak at 170 Kv,")
print("  comfortably inside the XDRIVE MINI, and it is what the model carries -- nuts at")
print("  OD 36, screws at X=+/-58, carriage body X 34..80, Z 84..128.")
print("  BUT THE RATIO IS NO LONGER THE SCREW'S ALONE. 404_link_ratio.py puts a 1:1.6")
print("  OVERDRIVE in the motor-to-screw belt (32T:20T HTD-5M), which lands the TOTAL at")
print("  14.5:1 -- 0.22x the limb -- with the SFU1610 and no change to the nut, the")
print("  capstan belt, the screw's column load or the idler bracket. That belt carries")
print("  85 N because it sits on the motor side of the screw's own advantage, so gearing")
print("  there is nearly free. An SFU1616 would still halve ball-nut recirculation noise,")
print("  so it is still the better part if it can be bought -- the overdrive is what stops")
print("  the design DEPENDING on it.")

# ------------------------------------------------------------- backdriving
print("=" * 68)
print("BACKDRIVING  (matters: a ball screw is never self-locking)")
eta_back = 2 - 1 / ETA_SCREW
lead_angle = math.degrees(math.atan(LEAD / (math.pi * 16.0)))
print("  lead angle %.1f deg, back-drive efficiency ~%.2f" % (lead_angle, eta_back))
print("  holding %.1f N.m statically costs the full %.1f A -- ~%.0f W continuous."
      % (TAU_PEAK, TAU_SCREW / ETA_BELT / (9.549 / 170),
         VBAT * TAU_SCREW / ETA_BELT / (9.549 / 170)))
print("  So: this is a DYNAMIC assist. For stance-phase support add a brake,")
print("      do not hold with current.")

# ------------------------------------------------------------------ energy
print("=" * 68)
print("ENERGY")
RISE = 0.17                                # stair rise, m
W_STEP_BODY = BODY_KG * 9.81 * RISE
KNEE_SHARE, EXO_SHARE, ETA_ELEC = 0.50, 0.40, 0.55
W_STEP = W_STEP_BODY * KNEE_SHARE * EXO_SHARE / ETA_ELEC
print("  lifting %.0f kg by %.0f mm = %.0f J/step; knee does ~%.0f%%;"
      % (BODY_KG, RISE * 1000, W_STEP_BODY, KNEE_SHARE * 100))
print("  exo supplies %.0f%% of that at %.0f%% wall-to-shaft = %.0f J/step electrical"
      % (EXO_SHARE * 100, ETA_ELEC * 100, W_STEP))
IDLE = 8.0                                 # ODrive + ESP32 + sensors
for label, rate, duty in (("stair climbing, 1 step/s", 1.0, 1.0),
                          ("level walking", 0.9, 0.35),
                          ("mixed daily use", 0.5, 0.15)):
    p = W_STEP * rate * duty + IDLE
    for cap, wh in (("hoverboard 36V 10Ah", 360.0), ("A123 12S LiFePO4 736Wh", 736.0)):
        print("  %-24s %5.0f W  ->  %-22s %5.1f h" % (label, p, cap, wh / p))
    label = ""
print("=" * 68)
