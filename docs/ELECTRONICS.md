# Electronics and control

First pass at the ODrive side. Numbers come from
[`scripts/300_drivetrain.py`](../scripts/300_drivetrain.py); nothing here is tested yet.

---

## 1. Topology

```
  [36 V pack, backpack]
        |  XT90-S, 30 A fuse, latching e-stop at the waist belt
        |  12 AWG tether, service loop at the hip
        v
  [ODrive S1] --- 3-phase --> [6374 149 Kv]  (+ onboard MA732 reads a
        |                                      diametric magnet on the shaft)
        |  brake resistor 2 R / 50 W
        |
        |  CAN 500 kbit/s
        v
  [ESP32-C3 SuperMini]  -- SPI --> [AS5048A on the knee pin]  absolute joint angle
        |                -- I2C --> [BNO085 on the thigh]     gait phase
        |
        |  ESP-NOW
        v
  [ESP32-C3 SuperMini in a pocket]  assist level, mode, disable
```

Two control loops, deliberately split:

- **Fast, dumb, on the ODrive.** Current/FOC at ~20 kHz, torque command in, motor out.
  It knows nothing about walking.
- **Slow, smart, on the ESP32.** 200–500 Hz. Reads joint angle and IMU, decides *what
  torque a knee should be making right now*, sends it over CAN.

Keeping the gait logic off the motor controller means a bug in the gait code can only ever
produce a wrong torque, never a runaway commutation.

---

## 2. Why the ODrive S1

| | S1 | Pro | Micro |
|---|---|---|---|
| Bus | 12–50 V | 12–58 V | too low for a 42 V pack |
| Continuous | 40 A | 60 A | ~7 A |
| Our peak | 21.7 A | | |

The S1 is the fit: one axis (we only have one motor), 36 V nominal / 42 V charged sits
mid-range in its window, and 21.7 A peak is half its continuous rating so it will run cool
without a fan inside a fairing. The Pro is money spent on a second axis and current headroom
we cannot use. The Micro is out on both voltage and current.

It also has the **onboard MA732 magnetic encoder**, which reads a diametric magnet glued to
the motor shaft end — no external encoder, no cable, no alignment jig for commutation.

## 3. Two encoders, and why

The motor-side encoder alone is not enough. Over the 106° range of motion the screw turns
**13.66 revolutions** (6.83 at SFU1610). A single-turn magnetic encoder on the motor cannot
tell you which of those turns you are on at power-up, so you would have to home against a
hard stop every time the device is switched on. On a patient, standing, that is a
non-starter.

So:

- **Motor side** — ODrive onboard MA732. Commutation and velocity. Fast, incremental,
  never needs to be absolute.
- **Joint side** — AS5048A, 14-bit absolute, reading a 6 mm diametric magnet sunk into the
  counterbore in the knee pin head. The counterbore is already in the model — `210_flush.py`
  recesses the pin head flush at Z = 126 with a r = 10 bore, which is exactly the pocket a
  magnet and a small PCB want.

The joint encoder is the one that matters for control: it measures the *actual* knee angle
including belt stretch and any slip, which the motor-side encoder cannot see. Resolution
at 14 bits is 0.022° — far finer than needed.

A useful side effect: comparing the two gives you a free integrity check. If the joint
angle and the motor position disagree by more than a couple of degrees, the belt has
slipped or a tooth has stripped — drop torque to zero and fault.

## 4. What the ESP32s do

The C3 SuperMini is a good fit for this. Single RISC-V core at 160 MHz is plenty for a
500 Hz control loop, and — the thing that actually decides it — the **C3 has a TWAI
peripheral**, so it speaks CAN natively with just an SN65HVD230 transceiver. No SPI CAN
controller, no extra latency.

**Leg board:**
1. Read the AS5048A over SPI at 1 kHz.
2. Read the thigh IMU over I2C at 400 Hz.
3. Run the gait state machine and the impedance law.
4. Send `Set_Input_Torque` over CAN at 200–500 Hz.
5. Kick the ODrive watchdog. Stop kicking it and the drive coasts.
6. Log to flash or stream over BLE for tuning.

**Pocket board** (this is the good use for having a pile of them): a two-button remote over
ESP-NOW — assist level up/down, and a long-press to disable. ESP-NOW because it is
connectionless and low-latency, and does not need a network. The patient should be able to
turn assist down without stopping or getting a phone out.

Three caveats on the SuperMini specifically:

- The onboard PCB antenna on these boards is weak. Buried in a PETG fairing next to an
  aluminium rail and a running motor, BLE and ESP-NOW range will disappoint. Mount the leg
  board against the **outer** face of the thigh fairing, as far from the rail as the
  packaging allows, or use a variant with a u.FL connector.
- ~11 usable GPIOs. SPI + I2C + CAN + a status LED fits, but not much else. If you want
  loadcells or FSRs in the cuffs later, plan for a second board on the same CAN bus rather
  than trying to squeeze them onto this one.
- No 5 V rail worth using. Run a small 36 V to 5 V buck off the bus for the logic, and
  give it its own fuse — you do not want a shorted ESP32 to look like a motor fault.

## 5. ODrive configuration, starting point

`odrivetool`, firmware 0.6.x. Check every identifier against the docs for your exact
firmware — the API has moved between versions.

```python
# --- motor -------------------------------------------------------------
odrv0.axis0.config.motor.motor_type        = MotorType.HIGH_CURRENT
odrv0.axis0.config.motor.pole_pairs        = 7          # 14-pole 6374
odrv0.axis0.config.motor.torque_constant   = 9.549/149  # 0.0641 N.m/A
odrv0.axis0.config.motor.current_soft_max  = 25         # 21.7 A peak + margin
odrv0.axis0.config.motor.current_hard_max  = 40

# --- bus ---------------------------------------------------------------
odrv0.config.dc_bus_overvoltage_trip_level  = 46.0      # 42 V charged + headroom
odrv0.config.dc_bus_undervoltage_trip_level = 30.0      # 10S cut-off
odrv0.config.dc_max_positive_current        =  25.0
odrv0.config.dc_max_negative_current        =  -3.0     # see section 6
odrv0.config.brake_resistance               =  2.0
odrv0.config.enable_brake_resistor          = True

# --- encoders ----------------------------------------------------------
odrv0.axis0.config.commutation_encoder = EncoderId.ONBOARD_ENCODER0
odrv0.axis0.config.load_encoder         = EncoderId.ONBOARD_ENCODER0

# --- control -----------------------------------------------------------
odrv0.axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
odrv0.axis0.controller.config.input_mode   = InputMode.TORQUE_RAMP
odrv0.axis0.controller.config.torque_ramp_rate = 2.0    # N.m/s at the motor

# --- safety ------------------------------------------------------------
odrv0.axis0.config.enable_watchdog  = True
odrv0.axis0.config.watchdog_timeout = 0.05              # 50 ms

# --- CAN ---------------------------------------------------------------
odrv0.can.config.baud_rate      = 500000
odrv0.axis0.config.can.node_id  = 0
odrv0.can.config.protocol       = Protocol.SIMPLE
```

CAN Simple frames the ESP32 needs (`cmd_id | node_id << 5`):

| ID | Message | Direction |
|---|---|---|
| `0x001` | Heartbeat | ODrive to ESP32 |
| `0x002` | Estop | ESP32 to ODrive |
| `0x003` | Get_Error | poll |
| `0x007` | Set_Axis_State | ESP32 to ODrive |
| `0x009` | Get_Encoder_Estimates | ODrive to ESP32 |
| `0x00E` | Set_Input_Torque | ESP32 to ODrive, the hot path |
| `0x00F` | Set_Limits | ESP32 to ODrive |

**Torque control, never position control.** A position loop makes the device fight the
patient whenever their intent differs from the trajectory, which is most of the time and is
exactly how exo research devices hurt people. The ODrive only ever receives a torque.

## 6. Regen is the thing that will bite you

Descending stairs, sitting down, and the eccentric phase of every step all drive the knee
backwards through the transmission and turn the motor into a generator. That current has to
go somewhere.

A 36 V ebike pack's BMS will usually **not** accept reverse current through its discharge
FETs. If it blocks, the returning energy has nowhere to go but the DC bus capacitors, the
bus voltage climbs, and the ODrive trips on overvoltage — mid-step, with a patient on the
stairs. The failure is *safe* (the drive coasts and the joint free-swings, section 8) but
it is not acceptable as a routine event.

Three things together:

1. **Fit the brake resistor.** 2 Ω / 50 W, `enable_brake_resistor = True`. This is why it
   is not optional in the BOM. Mount it where it can dump heat and cannot touch the patient
   — 50 W into a PETG fairing is a burn.
2. **Clamp `dc_max_negative_current` to a few amps.** The ODrive then limits braking torque
   rather than pushing current the pack will not take.
3. **Measure your pack before trusting it.** Put a current clamp on the pack lead and hand
   back-drive the knee. If you see negative current flowing in, the BMS accepts regen and
   you can relax the clamp. If you see nothing and the bus voltage rises, it does not.

This applies to the hoverboard pack too, and hoverboard BMSes are generally the more
restrictive of the two.

## 7. Control strategy

Start with the simplest thing that helps with stairs, which is what this is for.

**Phase-scheduled impedance.** At each tick:

```
tau_cmd = K(phase) * (theta_ref(phase) - theta) - B(phase) * theta_dot + tau_ff(phase)
```

with `theta` from the joint encoder and the phase from the IMU + angle. Four phases are
enough to be useful:

| Phase | What the exo should do | Rough setting |
|---|---|---|
| Stance, knee flexing (loading) | Resist collapse | Moderate K, extension bias |
| Stance, knee extending (push-up onto the step) | **Assist extension — this is the one that matters for stairs** | Highest `tau_ff`, ramped with flexion angle |
| Swing, flexion | Small flexion torque to help foot clearance | Low K, small `tau_ff` |
| Swing, extension | Near zero, let the leg swing | K and B near zero |

Two hard clamps on top, in the ESP32, before anything reaches CAN:

- **Never command extension torque near full extension.** Hyperextension is an injury, and
  the mechanism has the authority to cause one. Taper `tau_cmd` to zero over the last 10°.
- **Absolute torque ceiling** well below the 28.2 N·m the mechanism can make. Start at
  **10%** and have the physio raise it.

Sit-to-stand is the same extension-assist law with a slower ramp, and is the right thing to
tune first because it is done seated, in one place, with something to hold.

## 8. Safety

The good news first: **the failure mode is benign by construction.** A 10 mm-lead ball
screw backdrives at ~89% efficiency, so loss of power, a blown fuse, a tripped drive or a
crashed ESP32 all leave a free-swinging passive brace, not a locked leg. Nothing in the
design can jam the knee. That is worth protecting — do not "improve" it later by adding a
self-locking screw or a fail-engaged brake.

Layered limits, each independent of the others:

| Layer | Limit | Fails to |
|---|---|---|
| Gait code | 10% assist ceiling, hyperextension taper | wrong torque, bounded |
| ODrive | `current_soft_max` 25 A, torque ramp rate | current trip, coast |
| Watchdog | 50 ms without CAN traffic | idle, coast |
| Mechanical | hard stops at −2° and +104° | hard stop |
| E-stop | latching NC at the waist belt, cuts power | dead, coast |
| Fuse | 30 A at the pack | dead, coast |

Testing progression, and do not skip steps:

1. Bench, no limb, screws driven by hand — check the two encoders agree across the range.
2. Bench, powered, torque commands only, joint loaded with a weight.
3. Worn, seated, sit-to-stand only, 10% assist, hand on a rail.
4. Level walking, parallel bars or a handrail, spotter.
5. Stairs, handrail, spotter.

This is not a certified device and should not be treated as one. Get the physio involved
before step 3, and keep the assist ceiling under their control rather than the patient's.

## 9. Bring-up order

1. ODrive on the bench, motor unloaded, `AXIS_STATE_MOTOR_CALIBRATION` and encoder offset
   calibration. Confirm smooth torque control by hand.
2. Add the brake resistor. Spin the motor by hand fast and confirm the resistor gets warm
   rather than the bus voltage spiking.
3. Regen test on the actual pack (section 6, item 3). Set `dc_max_negative_current` from
   what you measure.
4. ESP32 on CAN — heartbeat in, `Set_Input_Torque` out, watchdog kicking. Verify the drive
   coasts when you unplug the ESP32. **Verify this before it ever goes near a leg.**
5. AS5048A in the knee pin. Sweep the joint by hand and check joint angle against motor
   position over the full range — they should track to within a degree.
6. IMU and gait phase, logging only, no torque. Walk with it dead and check the phase
   classifier on the logs.
7. Only then enable torque, at 10%.
