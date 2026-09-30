# Electronics and control

The ODrive side. Numbers come from
[`scripts/300_drivetrain.py`](../scripts/300_drivetrain.py) and, for everything that
depends on the hardware actually in the box,
[`scripts/360_owned_hw.py`](../scripts/360_owned_hw.py). Nothing here is tested yet.

> **Revised for the hardware on hand.** This document was first written around an
> ODrive S1 and a 149 Kv motor, because that is what the analysis had asked for. The
> parts that arrived are **170 Kv C6374 motors** and **Makerbase MKS XDRIVE MINI**
> drives — ODrive **3.6** silicon on modified firmware **0.5.1**, not 0.6.x. Both
> changes are real and both are handled below; the one that matters most is that every
> API identifier had to change, because 0.5.1 and 0.6.x are not the same product.

---

## 1. Topology

```
  [36 V pack, backpack]
        |  XT90-S, 15 A fuse, latching e-stop at the waist belt
        |  12 AWG tether, service loop at the hip
        v
  [MKS XDRIVE MINI] - 3-phase -> [C6374 170 Kv]  (+ onboard AS5047P reads a
        |   ODrive 3.6, fw 0.5.1                     diametric magnet on the shaft)
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

## 2. The drive: MKS XDRIVE MINI, and what it costs

Four of these are already here at **$29.48 each**. They are ODrive **v3.6** clones —
STM32F405, DRV8301 gate drivers, NTMFS5C62NL MOSFETs, onboard AS5047P — in a 12–56 V
single-axis board.

| | XDRIVE MINI (owned ×4) | ODrive S1 (originally specced) |
|---|---|---|
| Silicon | ODrive v3.6 | ODrive S1 |
| Firmware | **modified 0.5.1** | 0.6.x |
| Bus | 12–**56** V | 12–50 V |
| Continuous | ~40 A realistic | 40 A |
| Onboard encoder | AS5047P, 14-bit SPI | MA732 |
| Price | $29.48 | $169 |
| Our peak at 170 Kv, SFU1610 | **24.8 A** | 24.8 A |

Three honest notes on that table.

**The 60 A / 120 A in the listing is not a board rating.** It is the MOSFET's
(60 V / 150 A). The real limit on v3.6 hardware is DRV8301 shunt scaling and the
thermal path off a small board, and the defensible figure is the same ~40 A class as an
S1. Treat it as a $29 S1 with older firmware, not as a 60 A drive.

**The one place it is genuinely better is the bus window.** 56 V against the S1's 50 V.
That matters here more than it looks, because regen pushes the bus *up* and §6 showed a
12S LiFePO4 pack charged to 43.8 V left only 2.2 V of headroom under a 46 V trip. Six
extra volts of device rating is six volts of somewhere for that energy to go.

**The firmware generation is the real cost**, and it is paid in §5.

### What 170 Kv changes, and what it does not

`Kt` goes 0.0641 → **0.0562 N·m/A**, so every torque costs **14% more current**: the
SFU1610 design point moves 21.7 A → **24.8 A**.

It does *not* make the motor run hotter. Copper loss for a given torque is
`P = 1.5·(T/Kt)²·R`, and for a given slot fill `Kt ∝ turns` while `R ∝ turns²` — the
turns cancel. **Copper loss for a given torque is independent of Kv.** A 170 Kv 6374 and
a 149 Kv 6374 sit at the same temperature making the same torque; the rewind moves the
burden onto the controller, not the motor. So 170 Kv is only ever a question about amps,
and at 24.8 A of a 40 A drive the answer is that it costs nothing.

What it *does* cost is the option of a much lower ratio, because that is where the amps
go — see the screw table in [`360_owned_hw.py`](../scripts/360_owned_hw.py):

| screw | ratio | T_motor | I @170 Kv | reflected J | vs limb | peak copper |
|---|---|---|---|---|---|---|
| SFU1605 | 46.4 : 1 | 0.70 N·m | 12.4 A | 0.667 | 2.22× | 5 W |
| **SFU1610 — built** | 23.2 : 1 | 1.39 N·m | **24.8 A** | 0.167 | **0.56×** | 18 W |
| **SFU1616 — target** | 14.5 : 1 | 2.23 N·m | **39.7 A** | 0.065 | **0.22×** | 47 W |
| SFU1620 | 11.6 : 1 | 2.78 N·m | 49.6 A | 0.042 | 0.14× | 74 W |

SFU1620 is out: 49.6 A is 83% of even the optimistic peak rating, with nothing left for
a stall. SFU1616 at 39.7 A is 66% of peak but **99% of continuous** — take it for the
0.22× inertia, but set `current_lim` where the drive stays cool rather than at the
mechanism's limit. 30 A still buys 21.3 N·m at the knee, and §7 starts the clinical
ceiling at 10% of that.

Speed was never the constraint and is even less so now: 170 Kv on 38.4 V free-runs at
6528 rpm and SFU1610 peaks at 1160.

### Four drives, four motors

| | |
|---|---|
| Owned | 4 × C6374 170 Kv ($150.62), 4 × XDRIVE MINI ($117.92) |
| A bilateral pair uses | 2 of each — 2 of each spare |
| Same silicon as 2 × ODrive S1 | $338 against $59 |

A bilateral build is now purely a mechanical parts question: 2 × 4.66 kg on the legs and
**one** pack, since 736 Wh against ~12 W mixed use was never close to binding.

Keeping two spares of each is the right call on a device with no FEA and no bench data
behind it.

**CAN with more than one board — this one bites.** The MINI reports itself as a
*dual-axis* ODrive. `axis1` does not physically exist but it still transmits heartbeats,
so four boards need **eight** distinct node IDs:

| board | `axis0.config.can_node_id` | `axis1.config.can_node_id` |
|---|---|---|
| 0 | 0 | 60 |
| 1 | 1 | 61 |
| 2 | 2 | 62 |
| 3 | 3 | 63 |

The fix quoted around the web is `axis1.can_node_id = 63`, which is a *single-board*
fix — do that on four boards and all four ghosts collide on 63. Better still, silence
them: `axis1.config.can_heartbeat_rate_ms = 0`. And terminate the bus at its two
physical ends only — two 120 Ω resistors for the whole bus, not one per board.

## 3. Two encoders, and why

The motor-side encoder alone is not enough. Over the 106° range of motion the screw turns
**13.66 revolutions** (6.83 at SFU1610). A single-turn magnetic encoder on the motor cannot
tell you which of those turns you are on at power-up, so you would have to home against a
hard stop every time the device is switched on. On a patient, standing, that is a
non-starter.

So:

- **Motor side** — the MINI's onboard **AS5047P**, 14-bit, 16384 CPR, SPI, chip select on
  GPIO 7. Commutation and velocity. Absolute over one turn, which is all commutation
  needs. **It is not enabled by the factory configuration** — the board ships set up for
  something else and §5 turns it on.
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

**Read this before plugging anything in.** The board ships with **manufacturer-modified
ODrive 0.5.1**. `odrivetool dfu` / the `upgrade` command **bricks it** — recovery needs an
ST-Link and the dumped original image. And 0.5.6 reportedly leaves the motor dead because
the DRV8301 pin assignment moved. So: stay on 0.5.1, take the backup image before doing
anything, and never let a tutorial talk you into flashing it.

0.5.1 and 0.6.x are not the same API. Everything this document originally specified for an
S1 has a different name or does not exist:

| S1 / 0.6.x (what was written) | XDRIVE MINI / 0.5.1 (what works) |
|---|---|
| `axis0.config.motor.motor_type` | `axis0.motor.config.motor_type` |
| `axis0.config.motor.torque_constant` | `axis0.motor.config.torque_constant` |
| `axis0.config.motor.current_soft_max` | `axis0.motor.config.current_lim` |
| `axis0.config.motor.current_hard_max` | `axis0.motor.config.current_lim_margin` |
| `axis0.config.commutation_encoder` | `axis0.encoder.config.mode` |
| `EncoderId.ONBOARD_ENCODER0` | `ENCODER_MODE_SPI_ABS_AMS` + `abs_spi_cs_gpio_pin = 7` |
| `ControlMode.TORQUE_CONTROL` | `CONTROL_MODE_TORQUE_CONTROL` |
| `axis0.config.can.node_id` | `axis0.config.can_node_id` |
| `Protocol.SIMPLE` | (CAN Simple is the only protocol) |

`odrivetool`, firmware 0.5.1. Verify every identifier against 0.5.1's own docs — some of
these (`enable_brake_resistor` in particular) moved between 0.5.x point releases.

```python
# --- motor -------------------------------------------------------------
odrv0.axis0.motor.config.motor_type      = MOTOR_TYPE_HIGH_CURRENT
odrv0.axis0.motor.config.pole_pairs      = 7          # VERIFY: count the magnets, halve it
odrv0.axis0.motor.config.torque_constant = 9.549/170  # 0.0562 N.m/A -- 170 Kv, measured part
odrv0.axis0.motor.config.current_lim     = 42         # 39.7 A peak at 14.5:1 + margin
odrv0.axis0.motor.config.current_lim_margin      = 10
odrv0.axis0.motor.config.requested_current_range = 60 # sets the shunt gain; must exceed the above
odrv0.axis0.motor.config.calibration_current     = 10

# --- onboard AS5047P ---------------------------------------------------
# NOT the factory default. The board does not use its own encoder until you say so.
odrv0.axis0.encoder.config.mode             = ENCODER_MODE_SPI_ABS_AMS
odrv0.axis0.encoder.config.abs_spi_cs_gpio_pin = 7
odrv0.axis0.encoder.config.cpr              = 16384   # 14-bit
odrv0.axis0.encoder.config.pre_calibrated   = True    # after a successful offset calibration

# --- bus -------------------------------------- 12S LiFePO4, see section 6a
odrv0.config.dc_bus_overvoltage_trip_level  = 46.0    # 43.8 V charged + headroom
odrv0.config.dc_bus_undervoltage_trip_level = 31.0    # 12S at 2.6 V/cell
odrv0.config.dc_max_positive_current        =  12.0   # BUS amps, not phase -- see below
odrv0.config.dc_max_negative_current        =  -3.0   # see section 6
odrv0.config.brake_resistance               =  2.0
odrv0.config.enable_brake_resistor          = True

# --- control -----------------------------------------------------------
odrv0.axis0.controller.config.control_mode = CONTROL_MODE_TORQUE_CONTROL
odrv0.axis0.controller.config.input_mode   = INPUT_MODE_TORQUE_RAMP
odrv0.axis0.controller.config.torque_ramp_rate = 2.0  # N.m/s at the motor

# --- startup: all of it OFF --------------------------------------------
# These boards throw encoder errors from supply noise at power-up. Do not let the
# drive try to calibrate or close the loop on its own -- the ESP32 asks, once the
# rails are quiet.
odrv0.axis0.config.startup_encoder_offset_calibration = False
odrv0.axis0.config.startup_closed_loop_control        = False

# --- safety ------------------------------------------------------------
odrv0.axis0.config.enable_watchdog  = True
odrv0.axis0.config.watchdog_timeout = 0.05            # 50 ms

# --- CAN ---------------------------------------------------------------
odrv0.can.config.baud_rate         = 500000
odrv0.axis0.config.can_node_id     = 0                # 0..3, one per board
odrv0.axis1.config.can_node_id     = 60               # the GHOST axis -- see section 2
odrv0.axis1.config.can_heartbeat_rate_ms = 0          # better: silence it entirely

odrv0.save_configuration()   # 0.5.1 reboots on save; reconnect after
```

Two 0.5.1-specific traps beyond the naming:

- **`requested_current_range` must be set above `current_lim`**, and set *first*. It
  chooses the shunt amplifier gain. Leave it at a default below your limit and
  calibration fails with a current-sense saturation error that does not say so.
- **Wait 100–200 ms before requesting closed loop.** The ESP32 should sit through the
  supply transient rather than racing it. This is the documented workaround for the
  startup encoder errors these boards are known for, and it is why both `startup_*`
  flags above are `False`.

And one number that was wrong here for a long time, caught while rescaling for 170 Kv:
**`dc_max_positive_current` is bus current, not phase current.** It was set to match
`current_lim`, which conflates the two. At peak torque the motor makes 1.39 N·m at
1160 rpm — 169 W mechanical plus 18 W of copper, so **188 W off a 38.4 V bus is 4.9 A of
pack current**, against 24.8 A in the phases. The drive is bucking hard: back-EMF is only
6.8 V of a 38.4 V bus. 12 A of bus limit is already 2.4× the worst real case.

The same mistake sized the **pack fuse at 30 A** (§8). 4.9 A peak bus, and at true stall
the bus draw is *lower still* because there is no mechanical power — only the 18 W of
copper. **A 15 A fuse is the right part**, and it is the layer that has to survive a
shorted motor lead. Sizing a protective device off the wrong current is how you fit a
fuse that never blows.

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

## 6. Regen is the thing that will bite you — and LiFePO4 makes it worse

Descending stairs, sitting down, and the eccentric phase of every step all drive the knee
backwards through the transmission and turn the motor into a generator. That current has to
go somewhere.

A pack's BMS will usually **not** accept reverse current through its discharge FETs. If it
blocks, the returning energy has nowhere to go but the DC bus capacitors, the bus voltage
climbs, and the ODrive trips on overvoltage — mid-step, with a patient on the stairs. The
failure is *safe* (the drive coasts and the joint free-swings, section 8) but it is not
acceptable as a routine event.

**With LiFePO4 this stops being a maybe.** LiFePO4 must not be charged below 0 °C, and the
chosen BMS has a low-temperature cutoff precisely to enforce that. Regen *is* charge. So on
a cold morning the BMS will refuse it — outdoors, on stairs, which is exactly the situation
the device exists for. The brake resistor is not a precaution here, it is the only path the
energy has.

A 12S LiFePO4 pack also leaves less headroom than the 10S Li-ion this was first sized for:
43.8 V at full charge against a 46 V trip is **2.2 V**, where 10S Li-ion gave 4 V. Size the
resistor for the full braking power, not a trickle.

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

## 6a. The pack

**A123 LiFePO4, 36 V nominal, 736 Wh** (BatteryHookup M1B module) with a 7–17S smart BMS,
100 A, CAN + RS485 + UART, low-temperature cutoff.

| | |
|---|---|
| Chemistry | LiFePO4 — 3.2 V nominal, 3.65 V max, 2.5 V min per cell |
| 12S | 38.4 V nominal, **43.8 V full**, 30 V empty |
| XDRIVE MINI window | 12–56 V — fits with 12 V above a full pack |
| BMS current | 100 A against a peak bus draw near 10 A. Enormous margin |

Three things this changes from the ebike pack originally speced:

- **Undervoltage trip** moves from 30 V to 31 V (2.6 V/cell). Confirm the pack's series
  count before setting it — an 11S module empties at 27.5 V and would trip early at 31.
- **Regen headroom shrinks** and the low-temp cutoff makes refusal routine rather than
  possible. See section 6.
- **Mass.** LiFePO4 runs about 90–110 Wh/kg, so 736 Wh is roughly **7–8 kg**, against
  ~2.5 kg for the 374 Wh Li-ion pack. `300_drivetrain.py` puts mixed daily use at 12 W, so
  374 Wh already lasted 31 hours: this is roughly twice the energy for three times the
  weight. What it buys instead is real — LiFePO4 does not go into thermal runaway, the A123
  cells take enormous discharge current, and cycle life is far longer. On something strapped
  to a person that is a defensible trade, but it is a **safety and longevity** choice, not a
  range one, and 7–8 kg in a backpack needs the waist belt taking the load.

**Wiring the BMS.** The ESP32-C3 has **one** TWAI controller and it is already carrying the
ODrive at 500 kbit/s. Do not put the BMS on that bus unless you have checked both the baud
rate and the node IDs. The clean answer is to take the BMS on **UART or RS485** — the C3 has
spare UARTs — and leave CAN to the motor controller.

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
| ODrive | `current_lim` 42 A, torque ramp rate | current trip, coast |
| Watchdog | 50 ms without CAN traffic | idle, coast |
| Mechanical | hard stops at −2° and +104° | hard stop |
| E-stop | latching NC at the waist belt, cuts power | dead, coast |
| Fuse | **15 A** at the pack — 4.9 A peak bus current, see §5 | dead, coast |

Testing progression, and do not skip steps:

1. Bench, no limb, screws driven by hand — check the two encoders agree across the range.
2. Bench, powered, torque commands only, joint loaded with a weight.
3. Worn, seated, sit-to-stand only, 10% assist, hand on a rail.
4. Level walking, parallel bars or a handrail, spotter.
5. Stairs, handrail, spotter.

This is not a certified device and should not be treated as one. Get the physio involved
before step 3, and keep the assist ceiling under their control rather than the patient's.

## 9. Noise

Not analysed, and it should be, because this is worn in public and a device that whines
marks the wearer out. Nothing here is measured — it is reasoning from component type.

Likely sources, in the order I would expect them to matter:

1. **Ball nut recirculation.** Balls entering and leaving the return tube: roughly
   15 balls × 19 rev/s ≈ **290 Hz** and harmonics at peak speed, right where hearing is
   most sensitive. Choosing SFU1610 over 1605 already halved screw speed to 1160 rpm,
   and recirculation noise rises steeply with rpm. Note the 1:1.6 overdrive does **not**
   help here: it slows the *motor* to 725 rpm and leaves the screw at 1160. An SFU1616
   would halve this, which is the one thing it would still do better than the overdrive.
2. **The fairings as a soundboard.** Possibly worse than the source. `P21` was a 284 mm
   canopy of ~3 mm PETG on a **rigid spine** straight into the rail's middle slot — a
   direct structure-borne path into a large thin panel. **That spine no longer exists**:
   the one-screw rebuild put the gantry and the idler on the rail's outboard face, leaving
   nowhere for it, and the canopy now hangs on three grommeted mounts into the posterior
   side face. The layout forced the mitigation listed below before it was ever chosen.
3. **Motor** — FOC and 24 kHz PWM are both inaudible, but torque ripple at 6× electrical
   lands near **800 Hz** at peak speed.
4. **The 1:1 linking belt**, ~390 Hz tooth passage.
5. **Mini V-wheels** — Delrin on aluminium, rolling. Quieter than the MGN7H blocks they
   replaced, but watch for flats: [`401_vwheel_load.py`](../scripts/401_vwheel_load.py)
   puts the flank contact at 91 MPa against a ~101 MPa yield onset even at the widened
   70 mm spacing.
6. **The 1:1.6 link belt**, 20T at 725 rpm ≈ 242 Hz tooth passage — new, and low.

The capstan barely contributes: the HTD-8M belt is anchored at both ends and only lays
onto and peels off the same 180° wrap, so tooth passage is ~24 Hz. A geared or belted
reduction at the knee would be far worse.

Mitigations, cheapest first — **isolate the fairings** (rubber grommets instead of the
rigid spine; highest leverage and it costs grams — and as of the one-screw rebuild this is
no longer optional, it is simply how the canopy mounts), **constrained-layer damping** on the
inside of the canopy, and **correct screw preload and grease**. The instinct to stiffen
the fairing mounts against rattle is backwards here.

Treat all of that as provisional until step 2 below.

## 10. Bring-up order

0. **Back up the firmware before anything else.** `odrivetool` will offer to upgrade the
   board and that bricks it. Pull the image with an ST-Link, or at minimum keep the
   community dump to hand, *then* connect. Also: open a motor, count the magnets in the
   bell, halve it, and set `pole_pairs` to that. C63xx ships as both 14-pole and 12-pole
   and a wrong count makes calibration fail or commutation run rough — two minutes now
   against an afternoon of chasing a phantom fault.
1. ODrive on the bench, motor unloaded, `AXIS_STATE_MOTOR_CALIBRATION` and encoder offset
   calibration. Set `requested_current_range` *before* `current_lim`. Confirm smooth torque
   control by hand.
2. Add the brake resistor. Spin the motor by hand fast and confirm the resistor gets warm
   rather than the bus voltage spiking. **While the drivetrain is on the bench, run it
   unloaded through the speed range and measure the noise** — even a phone SPL app will
   do. The fairing mounting design depends on the answer and is cheap to change now and
   expensive later.
3. Regen test on the actual pack (section 6, item 3). Set `dc_max_negative_current` from
   what you measure.
4. ESP32 on CAN — heartbeat in, `Set_Input_Torque` out, watchdog kicking. Verify the drive
   coasts when you unplug the ESP32. **Verify this before it ever goes near a leg.** With
   more than one board on the bus, confirm the ghost `axis1` heartbeats are silenced or
   uniquely numbered first (§2), otherwise you will chase a bus fault that is really two
   boards claiming one ID.
5. AS5048A in the knee pin. Sweep the joint by hand and check joint angle against motor
   position over the full range — they should track to within a degree.
6. IMU and gait phase, logging only, no torque. Walk with it dead and check the phase
   classifier on the logs.
7. Only then enable torque, at 10%.
