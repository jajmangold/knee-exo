# -*- coding: utf-8 -*-
"""Talk to the XDRIVE MINI from a script, never from odrivetool's interactive shell.

odrivetool offers to upgrade the firmware on connect and that bricks these clones -- they ship
on a modified 0.5.1 that is not in anyone's release list. The library does not offer anything,
so every step here is explicit and nothing happens that is not written down.

    python tools/odrv.py inspect          read-only: who is it, what state, what errors
    python tools/odrv.py config           write the bench configuration (no motion)
    python tools/odrv.py encoder [secs]   watch the encoder while you turn the shaft BY HAND
    python tools/odrv.py calibrate        MOTOR_CALIBRATION -- the motor will twitch and beep
    python tools/odrv.py offset           ENCODER_OFFSET_CALIBRATION -- the motor WILL SPIN
    python tools/odrv.py clear            clear errors

Nothing here enables closed loop. That is deliberate: closed loop on a bench with a shaft that
can whip is the step to take by hand, watching it, with a finger on the supply.
"""
import sys
import time

import odrive
from odrive.enums import *                                          # noqa: F401,F403
from odrive.utils import dump_errors


def connect(timeout=20):
    print("  looking for a board (%d s)..." % timeout)
    d = odrive.find_any(timeout=timeout)
    if d is None:
        raise SystemExit("  no ODrive found -- check USB, and that nothing else has it open")
    return d


def fw(d):
    return "%d.%d.%d" % (d.fw_version_major, d.fw_version_minor, d.fw_version_revision)


def inspect(d):
    print("  serial            %s" % format(d.serial_number, "x").upper())
    print("  firmware          %s%s" % (fw(d), "  (modified 0.5.1 is expected)"
                                        if fw(d).startswith("0.5") else "  <-- UNEXPECTED"))
    print("  hardware          %d.%d" % (d.hw_version_major, d.hw_version_minor))
    print("  bus               %.2f V, %.2f A" % (d.vbus_voltage, getattr(d, "ibus", float("nan"))))
    a = d.axis0
    print("  axis0 state       %d" % a.current_state)
    print("  motor calibrated  %s" % a.motor.is_calibrated)
    print("  encoder ready     %s   index found %s" % (a.encoder.is_ready, a.encoder.index_found))
    print("  encoder mode      %d (ENCODER_MODE_SPI_ABS_AMS = %d)"
          % (a.encoder.config.mode, ENCODER_MODE_SPI_ABS_AMS))        # noqa: F405
    print("  encoder cpr       %d" % a.encoder.config.cpr)
    print("  spi cs pin        %d" % a.encoder.config.abs_spi_cs_gpio_pin)
    print("  pos_estimate      %.4f turns   shadow %d"
          % (a.encoder.pos_estimate, a.encoder.shadow_count))
    print("  pole_pairs        %d" % a.motor.config.pole_pairs)
    print("  current_lim       %.1f A   requested_range %.1f A"
          % (a.motor.config.current_lim, a.motor.config.requested_current_range))
    print("  brake resistance  %.2f ohm   enabled %s"
          % (d.config.brake_resistance, d.config.enable_brake_resistor))
    print("  overvoltage trip  %.1f V   undervoltage %.1f V"
          % (d.config.dc_bus_overvoltage_trip_level, d.config.dc_bus_undervoltage_trip_level))
    print()
    dump_errors(d)


def config(d, bench_supply=None):
    a = d.axis0
    v = d.vbus_voltage
    print("  bus reads %.2f V" % v)
    # the startup quirks: these boards throw encoder errors from noise alone at power-up
    a.config.startup_encoder_offset_calibration = False
    a.config.startup_closed_loop_control = False
    # the encoder, which the board does NOT use by default
    a.encoder.config.mode = ENCODER_MODE_SPI_ABS_AMS                  # noqa: F405
    a.encoder.config.abs_spi_cs_gpio_pin = 7
    a.encoder.config.cpr = 16384
    # the motor
    a.motor.config.motor_type = MOTOR_TYPE_HIGH_CURRENT               # noqa: F405
    a.motor.config.torque_constant = 9.549 / 170.0
    a.motor.config.requested_current_range = 60.0      # BEFORE current_lim: it sets shunt gain
    a.motor.config.current_lim = 42.0
    a.motor.config.current_lim_margin = 10.0
    a.motor.config.calibration_current = 10.0
    # the bus. The trip levels in ELECTRONICS assume the 12S pack; on a bench supply they have
    # to follow the supply, or the bus is allowed to climb to 46 V before anything objects.
    d.config.brake_resistance = 2.0
    d.config.enable_brake_resistor = True
    top = (bench_supply if bench_supply else v) + 6.0
    d.config.dc_bus_overvoltage_trip_level = round(top, 1)
    d.config.dc_bus_undervoltage_trip_level = max(8.0, round(v * 0.6, 1))
    d.config.dc_max_negative_current = -3.0
    print("  overvoltage trip set to %.1f V (supply + 6), undervoltage %.1f V"
          % (d.config.dc_bus_overvoltage_trip_level,
             d.config.dc_bus_undervoltage_trip_level))
    print("  requested_current_range %.0f A set BEFORE current_lim %.0f A"
          % (a.motor.config.requested_current_range, a.motor.config.current_lim))
    print("  brake resistor %.1f ohm, enabled" % d.config.brake_resistance)
    print("  pole_pairs left at %d -- count the magnets in a spare bell and halve it"
          % a.motor.config.pole_pairs)
    d.save_configuration()
    print("  saved (the board reboots; reconnect for the next step)")


def encoder(d, secs=15.0):
    a = d.axis0
    print("  TURN THE SHAFT BY HAND. No current is applied.")
    print("  %8s %12s %10s" % ("t", "pos (turns)", "shadow"))
    t0 = time.time()
    lo = hi = a.encoder.pos_estimate
    last = None
    jumps = 0
    while time.time() - t0 < secs:
        p = a.encoder.pos_estimate
        lo, hi = min(lo, p), max(hi, p)
        if last is not None and abs(p - last) > 0.25:
            jumps += 1
        last = p
        print("  %8.1f %12.4f %10d" % (time.time() - t0, p, a.encoder.shadow_count))
        time.sleep(1.0)
    print()
    print("  swept %.3f turns (%.0f deg), %d discontinuities > 90 deg"
          % (hi - lo, (hi - lo) * 360.0, jumps))
    if hi - lo < 0.9:
        print("  turn it through a FULL revolution to prove the magnet all the way round")
    print("  smooth and monotonic means the magnet is centred and the gap is right.")
    print("  sticking or jumping means the GAP or the CENTRING is wrong -- change pillars or")
    print("  shims, not settings.")
    dump_errors(d)


def run_state(d, state, label, settle=30.0):
    a = d.axis0
    print("  %s ..." % label)
    a.requested_state = state
    time.sleep(1.0)
    t0 = time.time()
    while a.current_state != AXIS_STATE_IDLE and time.time() - t0 < settle:   # noqa: F405
        time.sleep(0.2)
    time.sleep(0.5)
    ok = a.motor.error == 0 and a.encoder.error == 0 and a.error == 0
    print("  %s: %s" % (label, "clean" if ok else "ERRORS"))
    dump_errors(d)
    return ok


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "inspect"
    print("=" * 78)
    print("XDRIVE MINI  --  %s" % cmd)
    print("=" * 78)
    dev = connect()
    if cmd == "inspect":
        inspect(dev)
    elif cmd == "config":
        config(dev, float(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif cmd == "encoder":
        encoder(dev, float(sys.argv[2]) if len(sys.argv) > 2 else 15.0)
    elif cmd == "calibrate":
        run_state(dev, AXIS_STATE_MOTOR_CALIBRATION, "motor calibration")       # noqa: F405
        m = dev.axis0.motor
        print("  phase resistance %.4f ohm, inductance %.6f H, calibrated %s"
              % (m.config.phase_resistance, m.config.phase_inductance, m.is_calibrated))
    elif cmd == "offset":
        ok = run_state(dev, AXIS_STATE_ENCODER_OFFSET_CALIBRATION,              # noqa: F405
                       "encoder offset calibration", settle=45.0)
        print("  encoder ready %s, offset %d"
              % (dev.axis0.encoder.is_ready, dev.axis0.encoder.config.offset))
        if not ok:
            print("  CPR_POLEPAIRS_MISMATCH here means pole_pairs is wrong: try the other of")
            print("  7 and 6, which is 14 or 12 magnets in the bell.")
    elif cmd == "clear":
        dev.clear_errors()
        print("  cleared")
        dump_errors(dev)
    else:
        raise SystemExit("unknown command %r" % cmd)
