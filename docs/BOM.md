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

| Screw | Ratio | Reflected J | vs. limb's own J | Peak current | Nut OD | Belt gap at X=+/-58 |
|---|---|---|---|---|---|---|
| SFU1605 | 46.4 | 0.667 kg·m² | **2.22x** | 10.9 A | 28 mm | 2.9 mm, clear |
| SFU1610 | 23.2 | 0.167 kg·m² | 0.56x | 21.7 A | 36 mm | −1.1 mm, CLASH |
| SFU1620 | 11.6 | 0.042 kg·m² | 0.14x | 43.5 A | 40 mm | −3.1 mm, CLASH |

Reflected inertia is what the patient feels **when the motor is off** — a dead battery, a
fault trip, or the free-swing phase of every step. At SFU1605 the leg would feel roughly
three times as heavy to swing as it does bare. For someone already struggling to walk,
that is a worse device than no device.

You cannot fix this by moving the reduction around: only the *total* ratio matters, so
"SFU1620 plus a 4:1 belt" is inertially identical to SFU1605 direct.

**Recommendation: SFU1610.** It is the only row that is both comfortable to backdrive and
comfortably inside an ODrive S1. The cost: its nut is OD 36 mm, which at the current screw
position of X = ±58 mm fouls the belt by 1.1 mm. **The screws have to move out to
X = ±62 mm, widening the pack by 8 mm. That CAD change has not been made yet.**

The model as it stands is drawn for the SFU1605 nut — the CAD nut is `NUT_R = 14.0`,
i.e. OD 28 mm, despite the part being *labelled* `SFU1620`. The label is wrong; the
geometry is 1605. So: build 1605 and accept a heavy-feeling swing, or spend an hour on the
CAD and build 1610. Everything below assumes **1610 after the reposition**.

---

## 2. Drive

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| D1 | Ball screw SFU1610, RH, 300 mm, machined ends | 1 | 68.3 mm stroke + nut length + bearing seats | 45 |
| D2 | Ball screw SFU1610, **LH**, 300 mm, machined ends | 1 | Left-hand is the whole trick. Confirm with the seller — often a special order | 70 |
| D3 | SFU1610 **flangeless** ball nut | 2 | Usually supplied with the screw. A flanged nut drives 15 mm into the rail | inc. |
| D4 | BLDC outrunner 6374, 149 Kv, 8 mm shaft | 1 | 190 Kv also works (21.7 A becomes 27 A). ~800 g, the heaviest single item | 90 |
| D5 | Diametric magnet 6 x 2.5 mm | 1 | Glued to the motor shaft end for the ODrive's onboard encoder | 3 |
| D6 | HTD-5M belt, 9 mm wide, closed loop | 1 | 1:1 loop linking the two screw tops. Length set by the ±62 mm spacing | 8 |
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
| S2 | Delrin / acetal sheet 6 mm, offcut | — | The four L-gib sliders. Print in PETG to fit-check, then cut the real ones | 12 |
| S2a | *(alternative)* MGN12H rail 230 mm + 2 blocks | 1 set | Replaces S2. Cuts guide friction from ~70 N to 1.4 N at +219 g — see [`scripts/310_guides.py`](../scripts/310_guides.py). Not in the CAD yet | 35 |
| S3 | M5 T-nuts + button head cap screws | ~40 | Everything mounts to the slots | 12 |
| S4 | M3 / M4 cap screws, assorted | ~40 | Fairings, cuffs, electronics | 10 |
| S5 | Padding — 6 mm EVA + hook-and-loop straps | 1 set | Cuff liners. Do not skip: the whole load path ends at skin | 20 |

## 5. Printed parts

All 16 in [`stl/`](../stl). Blue PETG as rendered, 0.2 mm layers.

| Part | Qty | Suggested |
|---|---|---|
| `P1_KneeYoke` | 1 | 5 perimeters, 60% gyroid — carries the full 18.5 N·m reaction |
| `P2a_KneeHub_Pulley29T` | 1 | 6 perimeters, 60%. The tooth flanks want a fresh nozzle |
| `P3_Carriage`, `P3b_CarriageB` | 1 each | 5 perimeters, 50% |
| `P10a`–`P10d_Slider_Delrin` | 1 each | Print in PETG to fit-check, then machine from acetal |
| `P11_SprungAnchor` | 1 | 5 perimeters, 60% |
| `P5_ThighCuff`, `P7_ShankCuff`, `P6_ShankSocket` | 1 each | 4 perimeters, 30% |
| `P20_KneeCap` | 1 | 3 perimeters, 15%, cosmetic |
| `P21_FairingThigh`, `P22_DriveCap`, `P24_FairingShank` | 1 each | 3 perimeters, 15%, cosmetic |

Roughly 1.7–2.1 kg of filament including supports.

## 6. Electronics

Architecture and reasoning in [`ELECTRONICS.md`](ELECTRONICS.md).

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| E1 | ODrive S1 | 1 | 12–50 V, 40 A continuous. One axis is all we need | 169 |
| E2 | Brake resistor, ~2 Ω 50 W | 1 | **Not optional** — see the regen section | 15 |
| E3 | ESP32-C3 SuperMini | 2 | One on the leg, one as a pocket remote. You already have these | — |
| E4 | AS5048A magnetic encoder breakout | 1 | Absolute knee angle over SPI. Removes the power-on homing routine | 12 |
| E5 | Diametric magnet 6 x 2.5 mm | 1 | Into the flush counterbore in the knee pin head | 3 |
| E6 | SN65HVD230 CAN transceiver | 1 | ESP32-C3 TWAI to ODrive CAN | 4 |
| E7 | IMU — BNO085 or ICM-42688-P | 1 | Thigh-mounted, for gait phase | 20 |
| E8 | XT90-S anti-spark connector pair | 1 | The S1's bus caps will arc a plain XT60 | 5 |
| E9 | Inline fuse holder + 30 A blade fuse | 1 | At the pack, before anything else | 6 |
| E10 | Latching e-stop, 22 mm, NC | 1 | On the waist belt where a hand falls naturally | 10 |
| E11 | Silicone wire 12 AWG | 4 m | Pack to leg. 0.55 V drop at 22 A over 1.5 m each way | 12 |
| E12 | Cable gland, strain relief, spiral wrap | 1 set | The tether crosses the hip and must not snag | 10 |

## 7. Power

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| B1 | 36 V ebike pack, Hailong / "shark" rail mount, 10.4 Ah | 1 | 374 Wh, slide-off dovetail with a key lock | 190 |
| B2 | Hailong mounting rail / base plate | 1 | Usually supplied. Bolts to the pack frame | inc. |
| B3 | Backpack with an internal frame | 1 | Rail bolts through to the frame stay | 60 |

Your existing **hoverboard 36 V 10 Ah** pack is 360 Wh and electrically fine (10S,
30–42 V, inside the S1's 12–50 V window). Runtime from `300_drivetrain.py`:

| Use | Draw | Hoverboard 360 Wh | Ebike 504 Wh |
|---|---|---|---|
| Stair climbing, 1 step/s | 57 W | 6.4 h | 8.9 h |
| Level walking | 23 W | 15.5 h | 21.6 h |
| Mixed daily use | 12 W | 30.9 h | 43.3 h |

**Energy is not the constraint — both packs vastly outlast a day.** So buy the ebike pack
for the *mount*, not the capacity: the dovetail rail lets the patient dock and undock
without taking the backpack off or fiddling with connectors, and a Hailong ships with an
integrated BMS, a fuel gauge and a fused output. Buy the *smallest* capacity that comes on
the rail you want — 10.4 Ah / 374 Wh is plenty, and saves ~0.9 kg over 14 Ah.

Two cautions, both expanded in `ELECTRONICS.md`:

- Many ebike BMSes will not accept **regen** current back through the discharge FETs, and
  descending stairs regenerates hard. Hence the brake resistor at E2.
- Check the BMS continuous discharge rating. 22 A peak is fine for most 36 V ebike packs
  (typically 20–30 A) but sits at the top of a hoverboard BMS's range.

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

| Group | ~USD |
|---|---|
| Drive | 250 |
| Knee transmission | 45 |
| Structure | 70 |
| Filament | 45 |
| Electronics | 265 |
| Power (new ebike pack + backpack) | 250 |
| **Total** | **~925** |

Reusing the hoverboard pack and an existing backpack takes it to roughly **$675**.
