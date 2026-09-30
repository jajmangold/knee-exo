# Build list

Quantities are for **one** knee unit (single leg). Prices are indicative USD from the
usual suspects (AliExpress / Amazon / ODrive) — order-of-magnitude, not quotes.

Every mechanism-derived number below comes out of
[`scripts/300_drivetrain.py`](../scripts/300_drivetrain.py). Run it before ordering,
because changing one assumption moves several lines at once.

---

## 1. Open decision you must settle before ordering

The screw lead sets the total knee-to-motor ratio, and reflected rotor inertia goes as
the **square** of that ratio. This is the most important choice in the build:

| Screw | Ratio | Reflected J | vs. limb's own J | Peak current @170 Kv | Nut OD |
|---|---|---|---|---|---|
| SFU1605 | 46.4 | 0.667 kg·m² | **2.22x** | 12.4 A | 28 mm |
| **SFU1610 — built** | 23.2 | 0.167 kg·m² | **0.56x** | 24.8 A | 36 mm |
| **SFU1616 — target** | 14.5 | 0.065 kg·m² | **0.22x** | 39.7 A | 36 mm |
| SFU1620 | 11.6 | 0.042 kg·m² | 0.14x | 49.6 A | 40 mm |

Currents are at the **170 Kv** motors actually on hand — 14% higher than the 149 Kv this
was first sized for. That costs controller amps and, because copper loss for a given
torque is independent of Kv, no motor heat at all. See
[`360_owned_hw.py`](../scripts/360_owned_hw.py).

Reflected inertia is what the patient feels **when the motor is off** — a dead battery, a
fault trip, or the free-swing phase of every step. At SFU1605 the leg would feel roughly
three times as heavy to swing as it does bare. For someone already struggling to walk,
that is a worse device than no device.

You cannot fix this by moving the reduction around: only the *total* ratio matters, so
"SFU1620 plus a 4:1 belt" is inertially identical to SFU1605 direct.

**Recommendation: SFU1610, and it fits as drawn.**

This repository previously said the 1610 nut fouled the belt by 1.1 mm and the screws
would have to move out to X = ±62, widening the pack by 8 mm. **That was wrong.** It came
from projecting the nut and the belt onto the X axis and comparing edges — 58 − 18 = 40
against the belt's outer face at 41.1 — while ignoring Y. The nut sits at `carrA + 36` and
its belt run ends at `carrA − 24`, so they are a constant **60 mm apart along the limb at
every pose, by construction**. Swept over all 107 poses, the nut/belt overlap is
**0.000 cm³ for OD 28, OD 36 and OD 40 alike**.

What does share length with the belt is the screw *shaft*, and at r = 7.9 it is clear
until |X| < 49. So there is roughly 8 mm per side of inboard slack available if you want
the pack narrower — for 1610 the binding limit becomes the nut against the extrusion
(|X| ≥ 30 + 18 = 48), so about X = ±50. Not modelled; the current ±58 is what is drawn.

**This is now built.** [`240_nut1610.py`](../scripts/240_nut1610.py) draws the nuts at
OD 36 and grows the carriage body to X 34…80, Z 84…128 so the bore is captured with a
3.8 mm wall; [`241_fixups.py`](../scripts/241_fixups.py) clears the two clashes that
caused. Screws stay at **X = ±58**. Swept clean over all 107 poses. The stale `SFU1620`
labels are corrected too.

**Order SFU1610, RH and LH.** Both from the same supplier in the same batch — mismatched
lead accuracy or nut preload between the two shows up directly as the differential
drifting, and there is no adjustment for it. Each screw only needs **162 mm of thread**
(the nut bodies live at Y 121…283); the rest is bearing seats.

---

## 2. Drive

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| D1 | Ball screw SFU1610, RH, 300 mm, machined ends | 1 | 68.3 mm stroke + nut length + bearing seats. Axis at X = −58 | 45 |
| D2 | Ball screw SFU1610, **LH**, 300 mm, machined ends | 1 | Left-hand is the whole trick, and the build's only special-order part. Confirm with the seller. If the quote or lead time is bad, [`370_no_lh_screw.py`](../scripts/370_no_lh_screw.py) has two ways to use a second RH screw instead — and [`380_one_screw.py`](../scripts/380_one_screw.py) argues the second screw should not exist | 70 |
| D3 | SFU1610 **flangeless** ball nut | 2 | Usually supplied with the screw. A flanged nut drives 15 mm into the rail | inc. |
| D4 | BLDC outrunner C6374, **170 Kv**, 8 mm shaft | 1 | **Owned — 4 of them, $32–40 each.** 24.8 A peak at SFU1610. ~800 g, the heaviest single item | 38 |
| D5 | Diametric magnet 6 x 2.5 mm | 1 | Glued to the motor shaft end for the drive's onboard AS5047P | 3 |
| D6 | HTD-5M belt, 9 mm wide, closed loop | 1 | 1:1 loop linking the two screw tops. Length set by the ±58 mm spacing | 8 |
| D7 | HTD-5M 20T pulleys, 8 mm bore | 3 | Two screws plus motor. All three turn the **same** way — LH/RH does the opposing | 15 |
| D8 | KP08 / KFL08 bearing blocks | 4 | Two per screw, top and bottom | 20 |
| D9 | Rigid shaft coupler 8 to 10 mm | 1 | Only if you mount the motor coaxial with screw A instead of belting it | 8 |

## 3. Knee transmission

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| K1 | HTD-8M open-ended belt, 30 mm wide | ~0.6 m | The capstan run. 764 N differential over 30 mm = 25.5 N/mm, well inside spec | 20 |
| K2 | M12 x 70 shoulder bolt or hardened dowel | 1 | The knee pin, in the flush counterbore. SF 5.9 | 10 |
| K3 | M12 flanged bronze or igus bushing | 2 | One each side of the hub | 8 |
| K4 | Compression spring, ~500 N/mm, 3 mm working travel | 1 | Sprung anchor on carriage B. Takes up belt bedding-in, not pretension | 5 |

## 4. Structure

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| S1 | V-slot extrusion 20x60, **black anodised**, 230 mm | 1 | Cut to Y 58 to 284.7. ~350 g | 15 |
| S2 | **MGN7 rail** — 165 mm anterior, 145 mm posterior | 2 | Different lengths: cut to what the blocks sweep. Mounted on the **outboard** solid band of the 20 mm side face, rail centre Z = 104.5 — centred on the face its M2 screws would land in the V-slot. **MGN7, not MGN9**: an MGN9 rail stands 6.5 mm proud and cuts 0.9 mm into the belt | 20 |
| S2a | **MGN7H blocks** | 4 | Two per carriage: a single block would have to react the 18.0 N·m yaw as a moment. See [`scripts/310_guides.py`](../scripts/310_guides.py) | 32 |
| S3 | M5 T-nuts + button head cap screws | ~40 | Everything mounts to the slots | 12 |
| S4 | M3 / M4 cap screws, assorted | ~40 | Fairings, cuffs, electronics | 10 |
| S5 | Padding — 6 mm EVA + hook-and-loop straps | 1 set | Cuff liners. Do not skip: the whole load path ends at skin | 20 |

## 5. Printed parts

All 12 in [`stl/`](../stl). Blue PETG as rendered, 0.2 mm layers. The Delrin gibs are
gone — they became bought MGN7H blocks (S2a).

| Part | Qty | Suggested |
|---|---|---|
| `P1_KneeYoke` | 1 | 5 perimeters, 60% gyroid — carries the full 18.5 N·m reaction |
| `P2a_KneeHub_Pulley29T` | 1 | 6 perimeters, 60%. The tooth flanks want a fresh nozzle |
| `P3_Carriage`, `P3b_CarriageB` | 1 each | 5 perimeters, 50% |
| `P11_SprungAnchor` | 1 | 5 perimeters, 60% |
| `P5_ThighCuff`, `P7_ShankCuff`, `P6_ShankSocket` | 1 each | 4 perimeters, 30% |
| `P20_KneeCap` | 1 | 3 perimeters, 15%, cosmetic |
| `P21_FairingThigh`, `P22_DriveCap`, `P24_FairingShank` | 1 each | 3 perimeters, 15%, cosmetic |

Roughly 1.8–2.2 kg of filament including supports.

## 6. Electronics

Architecture and reasoning in [`ELECTRONICS.md`](ELECTRONICS.md).

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| E1 | Makerbase MKS XDRIVE MINI | 1 | **Owned — 4 of them, $29.48 each.** ODrive v3.6 clone, 12–56 V, ~40 A, onboard AS5047P. Ships on modified fw **0.5.1** — do not let odrivetool upgrade it | 29 |
| E1a | ST-Link V2 clone | 1 | Only to back up / recover the MINI's firmware. Buy it before you need it | 5 |
| E2 | Brake resistor, ~2 Ω 50 W | 1 | **Not optional** — see the regen section | 15 |
| E3 | ESP32-C3 SuperMini | 2 | One on the leg, one as a pocket remote. You already have these | — |
| E4 | AS5048A magnetic encoder breakout | 1 | Absolute knee angle over SPI. Removes the power-on homing routine | 12 |
| E5 | Diametric magnet 6 x 2.5 mm | 1 | Into the flush counterbore in the knee pin head | 3 |
| E6 | SN65HVD230 CAN transceiver | 1 | ESP32-C3 TWAI to ODrive CAN | 4 |
| E7 | IMU — BNO085 or ICM-42688-P | 1 | Thigh-mounted, for gait phase | 20 |
| E8 | XT90-S anti-spark connector pair | 1 | The drive's bus caps will arc a plain XT60 | 5 |
| E9 | Inline fuse holder + **15 A** blade fuse | 1 | At the pack, before anything else. 15 A, not 30 — peak BUS current is 4.9 A | 6 |
| E10 | Latching e-stop, 22 mm, NC | 1 | On the waist belt where a hand falls naturally | 10 |
| E11 | Silicone wire 12 AWG | 4 m | Pack to leg. 0.55 V drop at 22 A over 1.5 m each way | 12 |
| E12 | Cable gland, strain relief, spiral wrap | 1 set | The tether crosses the hip and must not snag | 10 |

## 7. Power

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| B1 | **A123 LiFePO4 36 V, 736 Wh (M1B module)** | 1 | **Bought.** 12S, 43.8 V full, 30 V empty — inside the S1's 12–50 V window | — |
| B2 | **7–17S LiFePO4 smart BMS, 100 A, CAN/RS485/UART, low-temp cutoff** | 1 | **Bought.** Take it on UART or RS485: the ESP32-C3 has one CAN controller and the ODrive already has it | — |
| B3 | Backpack with an internal frame | 1 | The pack is **7–8 kg** — the waist belt must carry it, not the shoulders | 60 |

Runtime from `300_drivetrain.py`, against the 736 Wh now bought:

| Use | Draw | 736 Wh |
|---|---|---|
| Stair climbing, 1 step/s | 57 W | 12.9 h |
| Level walking | 23 W | 32.0 h |
| Mixed daily use | 12 W | 61.3 h |

**Energy was never the constraint** — the 374 Wh pack originally speced already gave
31 hours of mixed use. What 736 Wh of LiFePO4 buys is chemistry, not range: no thermal
runaway, very high discharge capability from the A123 cells, and far longer cycle life.
On a device strapped to a person that is a defensible trade for the weight.

The weight is the thing to plan around. LiFePO4 runs 90–110 Wh/kg, so this is roughly
**7–8 kg** against ~2.5 kg for the Li-ion alternative. Mount it low, at the lumbar curve,
and make sure the waist belt is carrying it.

Three cautions, all expanded in `ELECTRONICS.md`:

- **LiFePO4 must not be charged below 0 °C**, and the BMS enforces that with a low-temp
  cutoff. Regen *is* charge, so on a cold morning the BMS will refuse it — outdoors, on
  stairs. The brake resistor (E2) is the only path the energy has. Not optional.
- **Regen headroom is tighter**: 43.8 V full against a 46 V trip is 2.2 V, where 10S
  Li-ion gave 4 V.
- **Confirm the series count** before setting the undervoltage trip. 12S empties at 30 V,
  11S at 27.5 V, and a trip set for the wrong one cuts out early or too late.

## 8. Backpack mounting

The internal-frame idea is right, and for the right reason: it moves ~3 kg off the leg —
where it would otherwise add to the very swing inertia the screw-lead decision is fighting
— and puts it near the body's centre of mass.

- Bolt the Hailong rail **to the frame stay**, not to fabric. Use a backing plate.
- Low and central, at the lumbar curve, not between the shoulder blades.
- Run the tether out of the **bottom** of the pack, down inside the waist belt, and anchor
  it there before it crosses the hip. Leave a service loop at the hip so full flexion
  (sitting) does not tug the connector.
- Put the e-stop on the waist belt on the *unaffected* side.

---

## Rough total

| Group | ~USD | Already owned |
|---|---|---|
| Drive | 198 | motor ($38) |
| Knee transmission | 45 | |
| Structure | 70 | |
| Filament | 45 | |
| Electronics | 130 | drive ($29), 2× ESP32-C3 |
| Power (A123 736 Wh pack + BMS + backpack) | 250 | pack and BMS, purchased |
| **Total** | **~740** | |

Two things moved this down from the ~$925 first estimated. The controller is a
**$29 MKS XDRIVE MINI** rather than a $169 ODrive S1 (§5 of
[`ELECTRONICS.md`](ELECTRONICS.md) is the price of that: an older firmware generation, and
an API that shares almost no identifiers with the S1's). And the motor is a **$38 C6374 at
170 Kv** that was already on the shelf.

Net still to spend, given the pack, BMS, motors, drives and ESP32s are already here:
roughly **$300**, most of it screws, rails, bearings and filament.

There are **4 motors and 4 drives** on hand, so a bilateral pair costs nothing extra in
electronics — see §2 of [`ELECTRONICS.md`](ELECTRONICS.md) for the CAN node-ID trap that
comes with running more than one of these boards on one bus.
