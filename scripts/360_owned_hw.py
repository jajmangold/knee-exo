# -*- coding: utf-8 -*-
"""The numbers redone for the hardware actually in the box.

Two things changed, and they push in opposite directions.

  * The motors are 170 Kv, not the 149 Kv assumed everywhere in this repo.
    Kt drops 12%, so every torque costs 14% more current.
  * The controllers are Makerbase MKS XDRIVE MINI -- ODrive *3.6* silicon, not an
    ODrive S1. A sixth of the price, an entirely different firmware generation, and
    an onboard AS5047P instead of an MA732.

The first makes the current worse. The second makes the price of being wrong small.
Net: the constraint that decides the screw is heat and inertia, not amps, and the
reason is in section 0.

Run:  python scripts/360_owned_hw.py
"""
import math

# ------------------------------------------------------------- what we own
KV = 170.0
KT = 9.549 / KV
KV_OLD = 149.0
KT_OLD = 9.549 / KV_OLD
N_MOTORS, N_DRIVES = 4, 4

TAU_KNEE = 28.2                 # N.m at the knee, peak
ETA = 0.90 * 0.97               # screw x linking belt
R_CAP = 36.924                  # capstan pitch radius, mm
W_PEAK = math.radians(300.0)    # rad/s, free swing
J_ROTOR = 3.10e-4               # 6374 bell, +/-25%
J_LIMB = 0.30
V_FULL, V_NOM, V_EMPTY = 43.8, 38.4, 31.0      # 12S LiFePO4

# Phase resistance scales as turns^2 and Kt as turns, so R goes as 1/Kv^2.
R_PHASE_149 = 0.026             # ohm, typical listing for a 149 Kv 6374
R_PHASE = R_PHASE_149 * (KV_OLD / KV) ** 2
DUTY_RMS = 0.40                 # I_rms / I_peak over a stair cycle, assumed

print("=" * 76)
print("0. THE TWO CONSTANTS THAT MOVED")
print("   Kt   %.4f -> %.4f N.m/A      every torque costs %.0f%% more current"
      % (KT_OLD, KT, 100 * (KT_OLD / KT - 1)))
print("   R_ph %.1f -> %.1f mohm           fewer turns, so resistance falls too"
      % (R_PHASE_149 * 1e3, R_PHASE * 1e3))
print()
print("   That second line is the whole story on heat. Copper loss for a given torque")
print("   is P = 1.5 (T/Kt)^2 R, with Kt ~ turns and R ~ turns^2, so the turns cancel:")
print("   **copper loss for a given torque is independent of Kv.** A 170 Kv 6374 and a")
print("   149 Kv 6374 run at the same temperature making the same torque. The rewind")
print("   moves the burden onto the CONTROLLER, not the motor. So the only question")
print("   170 Kv actually raises is whether the drive has the amps.")

print("=" * 76)
print("1. SCREW OPTIONS AT 170 KV")
print("   ratio = 2*pi*R/lead ; T_motor = %.2f / ratio ; I = T_motor / Kt"
      % (TAU_KNEE / ETA))
print()
print("   %-9s %6s %8s %7s %7s %8s %8s %7s %7s" %
      ("screw", "ratio", "T_motor", "I@170", "I@149", "J_refl", "vs limb",
       "Pcu pk", "Pcu rms"))
rows = []
for name, lead, nut_od in (("SFU1605", 5.0, 28.0), ("SFU1610", 10.0, 36.0),
                           ("SFU1616", 16.0, 36.0), ("SFU1620", 20.0, 40.0)):
    ratio = 2 * math.pi * R_CAP / lead
    tau_m = TAU_KNEE / (ratio * ETA)
    i170, i149 = tau_m / KT, tau_m / KT_OLD
    jr = J_ROTOR * ratio ** 2
    pk = 1.5 * i170 ** 2 * R_PHASE
    print("   %-9s %6.2f %5.2f Nm %5.1f A %5.1f A %6.3f %7.2fx %5.0f W %5.0f W"
          % (name, ratio, tau_m, i170, i149, jr, jr / J_LIMB, pk, pk * DUTY_RMS ** 2))
    rows.append((name, lead, ratio, tau_m, i170, jr, nut_od, pk))
print()
print("   (Pcu rms assumes I_rms = %.0f%% of peak over a stair cycle -- an assumption,"
      % (100 * DUTY_RMS))
print("    not a measurement. Peak is transient; the rms column is what heats the can.)")
print()
print("   Speed is still nowhere near binding. Peak knee %.0f deg/s ->"
      % math.degrees(W_PEAK))
for name, lead, ratio, tau_m, i170, jr, od, pk in rows:
    rpm = ratio * W_PEAK * 60 / (2 * math.pi)
    print("     %-9s %5.0f rpm, back-EMF %4.1f V of a %.1f V bus (%2.0f%% of no-load)"
          % (name, rpm, rpm / KV, V_NOM, 100 * rpm / (KV * V_NOM)))
print("   170 Kv on %.1f V spins %.0f rpm unloaded and we use a fraction of it. The"
      % (V_NOM, KV * V_NOM))
print("   winding is far too fast for this job, which is exactly why it wants amps.")

print("=" * 76)
print("2. WHICH CONTROLLER MAKES WHICH SCREW LEGAL")
DRIVES = [("ODrive S1 (specced, not owned)", 40.0, 80.0, 169.0),
          ("MKS XDRIVE MINI (owned, x%d)" % N_DRIVES, 40.0, 60.0, 29.48)]
print("   %-32s %7s %7s %8s  %s" % ("drive", "cont", "peak", "$ each", "screws under cont"))
for nm, ic, ip, cost in DRIVES:
    ok = [r[0] for r in rows if r[4] <= ic]
    print("   %-32s %5.0f A %5.0f A %7.2f  %s" % (nm, ic, ip, cost, ", ".join(ok)))
print()
print("   The MINI's listing claims 60 A working / 120 A peak. Do not believe it: that")
print("   is the NTMFS5C62NL MOSFET rating (60 V / 150 A), not a board rating. The real")
print("   limit on ODrive 3.6 hardware is DRV8301 shunt scaling and the thermal path,")
print("   and the honest figure is the same ~40 A class as an S1 -- at %.0f%% of the"
      % (100 * 29.48 / 169.0))
print("   price, times %d boards." % N_DRIVES)
print()
print("   So the controller does NOT change the decision. Heat and inertia do. And note")
print("   the currents below are PEAK -- %.1f N.m at the knee, reached in stair push-off"
      % TAU_KNEE)
print("   and nowhere else -- so they belong against the 60 A peak column, not the 40.")
print()
print("     SFU1620  %5.1f A pk, %3.0f W peak copper -- out. %.0f%% of even the peak"
      % (rows[3][4], rows[3][7], 100 * rows[3][4] / 60.0))
print("              rating, with nothing left for a stall or a mis-tuned loop.")
print("     SFU1616  %5.1f A pk = %.0f%% of peak rating but %.0f%% of CONTINUOUS, so it"
      % (rows[2][4], 100 * rows[2][4] / 60.0, 100 * rows[2][4] / 40.0))
print("              has no thermal margin left at the drive if a fault holds torque on.")
print("              Buys %.2fx the limb's inertia against %.2fx today -- the big prize."
      % (rows[2][5] / J_LIMB, rows[1][5] / J_LIMB))
for lim in (40.0, 30.0, 25.0):
    print("              current_lim %2.0f A -> %4.1f N.m at the knee (%3.0f%% of target)"
          % (lim, lim * KT * rows[2][2] * ETA,
             100 * lim * KT * rows[2][2] * ETA / TAU_KNEE))
print("              And the clinical ceiling starts at 10% of target anyway (section")
print("              7 of ELECTRONICS.md), so even %.0f A is more authority than the"
      % 25.0)
print("              physio will unlock for months. Build the MECHANISM for %.1f N.m;"
      % TAU_KNEE)
print("              set current_lim wherever the drive stays cool, and raise it later.")
print("     SFU1610  %5.1f A pk as built -- %.0f%% of continuous, genuinely comfortable,"
      % (rows[1][4], 100 * rows[1][4] / 40.0))
print("              and the fallback if the SFU1616 nut is not OD 36 on the drawing.")

print("=" * 76)
print("3. WHAT THE 3.6 FIRMWARE GENERATION COSTS")
print("   The board ships with MODIFIED ODrive 0.5.1. odrivetool's dfu/upgrade BRICKS")
print("   it -- recovery needs an ST-Link and the dumped original image. 0.5.6 reportedly")
print("   leaves the motor dead because the DRV8301 pin assignment moved. So: 0.5.1, and")
print("   every identifier in ELECTRONICS.md section 5 was written for the 0.6.x S1 API")
print("   and does not exist on this board:")
print()
for old, new in (("axis0.config.motor.motor_type", "axis0.motor.config.motor_type"),
                 ("axis0.config.motor.torque_constant", "axis0.motor.config.torque_constant"),
                 ("axis0.config.motor.current_soft_max", "axis0.motor.config.current_lim"),
                 ("axis0.config.motor.current_hard_max", "axis0.motor.config.current_lim_margin"),
                 ("axis0.config.commutation_encoder", "axis0.encoder.config.mode"),
                 ("EncoderId.ONBOARD_ENCODER0", "ENCODER_MODE_SPI_ABS_AMS, cs on GPIO 7"),
                 ("ControlMode.TORQUE_CONTROL", "CONTROL_MODE_TORQUE_CONTROL"),
                 ("axis0.config.can.node_id", "axis0.config.can_node_id"),
                 ("Protocol.SIMPLE", "(CAN Simple is the only protocol)")):
    print("     %-38s -> %s" % (old, new))
print()
print("   Encoder: onboard **AS5047P**, 14-bit, 16384 CPR, SPI, CS on GPIO 7. Not an")
print("   MA732, and NOT enabled by the factory config. It is absolute over one turn,")
print("   which is all commutation needs -- the AS5048A in the knee pin is still what")
print("   makes the JOINT absolute at power-up, so section 3's argument stands and only")
print("   the part number changes.")
print()
print("   Quirk to design around: these boards throw encoder errors from supply noise at")
print("   startup. Disable startup encoder-offset calibration and startup closed-loop,")
print("   and have the ESP32 wait 100-200 ms before requesting closed loop.")

print("=" * 76)
print("4. FOUR MOTORS AND FOUR DRIVES")
SPENT_M = 40.09 + 40.09 + 38.28 + 32.16
SPENT_D = N_DRIVES * 29.48
print("   owned: %d x C6374 170 Kv ($%.2f total), %d x XDRIVE MINI ($%.2f total)"
      % (N_MOTORS, SPENT_M, N_DRIVES, SPENT_D))
print("   a bilateral pair uses 2 of each and leaves 2 of each spare -- which on a")
print("   device with no FEA and no bench data is the right place for the spares to be.")
print("   2 x ODrive S1 would have been $%.2f against $%.2f." % (2 * 169.0, 2 * 29.48))
print()
print("   Mass, from 340_tendon.py's inventory: one knee is 4.66 kg, so bilateral is")
print("   %.2f kg on the legs plus one 7-8 kg pack. The pack does not double, and"
      % (2 * 4.66))
print("   736 Wh against ~12 W mixed use was never the binding constraint anyway.")
print()
print("   CAN, and this is what bites with more than one board: the MINI reports itself")
print("   as a DUAL-axis ODrive. axis1 does not physically exist but it still transmits")
print("   heartbeats. Four boards therefore need EIGHT distinct node IDs, not four:")
for i in range(N_DRIVES):
    print("     board %d   axis0.config.can_node_id = %-3d  axis1.config.can_node_id = %d"
          % (i, i, 60 + i))
print("   The commonly quoted fix is `axis1.can_node_id = 63`, which is a SINGLE-board")
print("   fix -- do that on four boards and all four ghosts collide on 63. Better, just")
print("   silence them: axis1.config.can_heartbeat_rate_ms = 0.")
print("   Terminate at the two physical ends of the bus only: two 120 ohm resistors for")
print("   the whole bus, not one per board.")

print("=" * 76)
print("5. GO COUNT THE MAGNETS")
print("   ELECTRONICS.md asserts 7 pole pairs (14-pole). C63xx outrunners ship as both")
print("   14-pole and 12-pole depending on the batch, and a wrong pole count makes")
print("   calibration fail or commutation run rough at speed. Count the magnets inside")
print("   the bell and halve it. Two minutes, and ODrive cannot do it for you.")
print()
print("   Bus: 12S LiFePO4 %.1f V full / %.1f V nom / %.1f V empty against the MINI's"
      % (V_FULL, V_NOM, V_EMPTY))
print("   12-56 V window -- %.0f V more top-end headroom than the S1's 50 V, which is"
      % (56.0 - 50.0))
print("   the one place this board is genuinely better, because regen pushes the bus UP")
print("   and section 6 of ELECTRONICS.md only had 2.2 V of margin to play with.")
print("=" * 76)
