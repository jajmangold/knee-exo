# Build list

Quantities are for **one** knee unit (single leg). Prices are indicative USD from the
usual suspects (AliExpress / Amazon / ODrive) — order-of-magnitude, not quotes.

Every mechanism-derived number below comes out of
[`scripts/300_drivetrain.py`](../scripts/300_drivetrain.py). Run it before ordering,
because changing one assumption moves several lines at once.

**Ordering for both legs?** Only the symmetric lines double in quantity — extrusion, belts,
pulleys, motors, drive, V-wheels, bearings, fasteners, neoprene sleeves, webbing. The printed
and machined parts double in *count* but are **new part numbers, not more of the same**: 15 L +
15 R printed (2.5 kg of filament) and 2 L + 2 R aluminium (956 g), each engraved with its leg
letter. The **ball screw stays right-hand on both legs** — a mirrored screw would be left-hand,
which is a special-order premium part, and the reflection is absorbed by one sign in firmware
instead. See [`700_handedness.py`](../scripts/700_handedness.py) and the README's
"Building the pair".

---

## 1. Open decision you must settle before ordering

The screw lead sets the total knee-to-motor ratio, and reflected rotor inertia goes as
the **square** of that ratio. This is the most important choice in the build:

| Screw | Ratio | Reflected J | vs. limb's own J | Peak current @170 Kv | Nut OD |
|---|---|---|---|---|---|
| SFU1605 | 46.4 | 0.667 kg·m² | **2.22x** | 12.4 A | 28 mm |
| SFU1610, 1:1 link | 23.2 | 0.167 kg·m² | 0.56x | 24.8 A | 36 mm |
| **SFU1610 + 1:1.6 overdrive — built** | **14.5** | **0.065 kg·m²** | **0.22x** | **39.7 A** | 36 mm |
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
| D1 | Ball screw SFU1610, **RH**, 330 mm, machined ends | 1 | The only screw. 68.3 mm stroke; the nut sweeps Y 73…183 so 110 mm of thread is used, the rest is bearing seats. Axis at **X = −62**, moved 4 mm outboard of the old −58 so the nut clears the return strand | 45 |
| ~~D2~~ | ~~Ball screw SFU1610, **LH**~~ | **0** | **Deleted.** The closed-loop belt over two 29T pulleys makes one carriage do both jobs, so there is no left-hand thread and no special order anywhere in the build. [`390_onescrew_section.py`](../scripts/390_onescrew_section.py) | −70 |
| D3 | SFU1610 **flangeless** ball nut | 1 | Supplied with the screw. Trapped axially between two end plates in the gantry rather than clamped radially — a 36.4 mm bore through a 40 mm housing severs it, and the load is along Y anyway | inc. |
| D4 | BLDC outrunner C6374, **170 Kv**, 8 mm shaft | 1 | **Owned — 4 of them, $32–40 each.** 24.8 A peak at SFU1610. ~800 g, the heaviest single item | 38 |
| D5 | Diametric magnet 6 x 2.5 mm | 1 | Glued to the motor shaft end for the drive's onboard AS5047P | 3 |
| D6 | HTD-5M belt, **15 mm** wide, closed loop | 1 | Motor to screw, at Y 302…314. Centre distance 61 mm. 15 mm, not 9: it now carries the overdrive, ~153 N tight side | 10 |
| D7 | HTD-5M **32T** pulley (motor) + **20T** pulley (screw), 8 mm bore | 1 each | **A 1:1.6 OVERDRIVE, not 1:1.** This is what puts the total ratio at 14.5:1 with the SFU1610 — see [`404_link_ratio.py`](../scripts/404_link_ratio.py). Gearing here is nearly free because this belt sits on the motor side of the screw's advantage and carries 85 N, not the 764 N the capstan loop carries | 14 |
| D8 | KP08 / KFL08 bearing blocks | 2 | One screw, top and bottom. The upper one lives in the drive bracket's screw boss | 10 |
| D9 | Rigid shaft coupler 8 to 10 mm | 1 | Only if you mount the motor coaxial with screw A instead of belting it | 8 |

## 3. Knee transmission

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| K1 | HTD-8M **closed-loop** belt, 30 mm wide, **742 mm** | 1 | 2πR + 2·Y_idler. A closed loop, not an open strip: no end terminations, and it is tensioned by sliding the idler instead. 764 N differential over 30 mm = 25.5 N/mm | 25 |
| K2 | M12 x 70 shoulder bolt or hardened dowel | 1 | The knee pin, in the flush counterbore. SF 5.9 | 10 |
| K3 | M12 flanged bronze or igus bushing | 2 | One each side of the hub | 8 |
| K4 | Compression spring, ~500 N/mm, 3 mm working travel | 1 | Now acts on the **idler carrier's slotted mount**, not a belt end. Same job — takes up belt bedding-in — one fewer printed part | 5 |

## 4. Structure

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| S1 | V-slot extrusion **20x40**, **black anodised**, 160 mm | 1 | Cut to Y 51…207. **~159 g, against 352 g for the 20×60 × 227 mm.** It ends short of the idler because a 71 mm pulley on the centreline would otherwise contain the extrusion. **Its 40 mm face has slots at X = ±10, not X = 0** — the fairing spine has to move | 12 |
| S2 | **Mini V-wheel**, Delrin, OD 15.23 | 4 | On the |X| 20 corners of the 20×40, wheels 50 mm apart in Y. **Mini, not solid**: a V groove seats the corner apex at the bottom of the groove, so the centre stands off along the 45° bisector — a solid wheel reaches |X| 37.6 and fouls the belt at 35.55, a mini reaches 31.0. Spaced **70 mm apart**, not 50: OpenBuilds publishes no load rating, and a Hertz calculation ([`401_vwheel_load.py`](../scripts/401_vwheel_load.py)) puts the flank contact at 107 MPa against a ~101 MPa yield onset at 50 mm, versus 91 MPa at 70. Bench-test for play at reversal; MGN7 on the same side faces is the fallback | 12 |
| S2a | Eccentric spacers + wheel bolts | 4 | Two eccentric, two fixed, the usual V-slot gantry arrangement | 10 |
| S2b | **29T HTD-8M idler pulley**, 30 mm wide | 1 | **The same part as the knee capstan.** On the centreline at X = 0, Y 255, which is what makes the two strands land at exactly ±36.92 | 25 |
| S2c | Idler axle + 2 bearings | 1 | Supported top and bottom by the drive bracket. Reaction is 2·T_b, **up to 1828 N — the largest single load in the machine** | 10 |
| S2d | Aluminium gantry plate, 6 mm, ~116 × 84 | 1 | 71 cm³, 192 g, replacing 383 g of printed twin carriages. Crosses **over** the belt at Z 126.3, not under it — the 2.9 mm corridor between the nut and the belt is not a place for structure. Owned | 15 |
| S2e | Aluminium drive bracket | 1 | Holds the idler, the screw's top bearing and the motor. 121 cm³, **326 g — still the heaviest fabricated part.** 4 mm plates and 5 mm cheeks, sized by [`400_bracket_stress.py`](../scripts/400_bracket_stress.py) at 18 MPa against 240 MPa yield; it was 465 g when it was sized by eye | 25 |
| S3 | M5 T-nuts + button head cap screws | ~40 | Everything mounts to the slots | 12 |
| S4 | M3 / M4 cap screws, assorted | ~40 | Fairings, cuffs, electronics | 10 |
| S4a | **Rubber grommets, M5**, + shoulder screws | 3 | The fairing's only mounts. Isolating rather than rigid — `ELECTRONICS.md` §9 names the rigid spine as the likely structure-borne noise path | 6 |
| S5 | **Neoprene sleeve, thigh and calf**, 3 mm | 2 | The skin interface, and the only thing that touches the patient. Replaces the EVA pad entirely. Raises the friction that sets strap tension from μ≈0.4 to ≈0.6 worst case, so the strap needs **21 N instead of 31 N**; bridges the shell rim instead of letting it dig; and moves the sliding interface off the skin. Washable, and a consumable. Over a **closed, dry** incision only — ask whoever runs his rehab, and note neoprene contact dermatitis is common enough to plan a nylon-faced fallback | 30 |
| S5a | **Nylon webbing, 38 mm** | ~1.5 m | The cuff closure. 38 mm because at 31 N across the open side of the cuff a 3.5 mm lace is ~90 kPa on soft tissue and 38 mm webbing is 8.3 kPa — webbing is its own tongue, which is why a laced brace needs a separate one | 8 |
| S5b | **Cam buckle + D-ring**, 38 mm | 2 + 2 | Routed 2:1 through the D-ring, so the hand pull is ~12 N rather than 21. Repeatable and one-handed, which hook-and-loop is not — and repeatability is what keeps the knee axis aligned day to day | 12 |
| S5c | **Side-release buckle**, 38 mm | 2 | In the loop so the whole thing drops off in one squeeze. This is a **powered** device at 28.2 N·m on a post-operative limb; emergency doffing is the one safety argument in [`408_cuff_loads.py`](../scripts/408_cuff_loads.py) | 6 |

## 5. Printed parts

**15 per leg, 30 for the pair** — [`stl/`](../stl) is the left leg and [`stl_R/`](../stl_R) the
right. They are not 15 parts printed twice: every one is chiral, and a left part will appear to fit
the right leg while putting the drive on the wrong side of the limb. The engraved number is how you
tell: `P5L` against `P5R`.

Blue PETG, 0.2 mm layers. Perimeters and infill per part, with the orientation, support area,
filament and time each one actually needs, are in **[`PRINT.md`](PRINT.md)**, which is generated from
the exported STLs by [`900_print_list.py`](../scripts/900_print_list.py) rather than typed here —
this table used to list `P3_Carriage`, `P3b_CarriageB` and `P11_SprungAnchor`, of which the first
became a bought aluminium plate (S2d) and the other two were deleted with the second ball screw.

| Part | Qty/leg | Suggested |
|---|---|---|
| `P1_KneeYoke` | 1 | 5 perimeters, 60% gyroid — carries the full knee reaction |
| `P2a_KneeHub_Pulley29T` | 1 | 6 perimeters, 60%. The tooth flanks want a fresh nozzle |
| `P5_ThighCuff`, `P7_ShankCuff`, `P6_ShankSocket` | 1 each | 4 perimeters, 30% |
| `P20_KneeCap` | 1 | 3 perimeters, 15%, cosmetic |
| `P21_FairingThigh`, `P22_DriveCap`, `P24_FairingShank` | 1 each | 3 perimeters, 15%, cosmetic |
| `P25_MotorNacelle` | 1 | 3 perimeters, 15%. Prints nose-down on its domed end, no supports |
| `P23a/b/c_FairingMount` | 3 | 4 perimeters, 40% — they carry the canopy. All three are the **same part**, so they share one mark |
| `P30_InterfaceProx`, `P31_InterfaceDist` | 1 each | **KX-1 module interface.** 6 perimeters, 60% — structural. 6 × M5 heat-set inserts + 2 × ⌀5 dowels. Printed here because standalone this module needs 1.2 MPa of bearing; the same six holes in 6 mm aluminium carry the 1472 N load-to-ground case ([`501_interface.py`](../scripts/501_interface.py)) |

**~1.38 kg of filament and ~86 printer-hours per leg**, so 2.76 kg and about a week of printing for
the pair. Both figures are models rather than measurements — nothing has been printed yet — and
[`PRINT.md`](PRINT.md) states the models so they can be corrected against the first real print.

**Hardware does not fit a printed hole as drawn.** A hole comes off the bed 0.1–0.3 mm undersize,
and almost every hole here runs along the knee axis while most parts build along their length, so
most print slightly oval too. 102 holes, what fits each and what to do about it:
[`417_fastener_audit.py`](../scripts/417_fastener_audit.py), summarised as a drill list at the top
of [`ASSEMBLY.md`](ASSEMBLY.md).

**14 of the 15 parts are engraved with their part number and leg letter**
([`412_engrave.py`](../scripts/412_engrave.py)) — 0.8 mm recessed, Arial Bold at 8 mm where it fits
and 5 or 4 mm where the suffix made it not, on a face that is **verified hidden** and **verified to
read forwards**. `P2a_KneeHub_Pulley29T` carries no mark: 16 stations × 36 bearings found nowhere
covered, because it is the knee hub at an open joint. It is the 143 cm³ 29T pulley and nothing else
resembles it.

*Verified* matters here. The first placement rule was "the first surface a ray from the limb
axis meets", which is an **inner surface** — not the same property as **hidden**, and nothing
was checking the second one. Six marks were on show.
[`413_mark_visibility.py`](../scripts/413_mark_visibility.py) now fires a 13-ray fan out from
each marked surface and asks whether any of them escapes with the limb in place. All 14
marks: **0 of 13 escaping rays**.

The three fairing mounts share one mark (`P23`) because they are the same part printed three
times — `398` builds one shape at three stations, identical bounding boxes, interchangeable. Recessed rather than raised because on
the cuffs that face is the bore, against the neoprene: a raised character is a pressure point, a
recess under a 3 mm sleeve cannot be felt, and on a near-vertical wall a recess is just a
shallower perimeter where raised text would be a chain of 0.8 mm islands.

**Printability is measured, not assumed** ([`411_printability.py`](../scripts/411_printability.py)),
and it reads the exported STLs rather than the CAD solids, because the STL is what gets sliced:

| | |
|---|---|
| fits a 220 × 220 bed | all 15 parts — largest footprint 178 mm, tallest 185 mm |
| mesh watertight | all 15 |
| mean wall | 2.1–8.9 mm, all above the 1.2 mm two-perimeter floor |
| needs support | only `P23a/b/c`, 4.4 cm² each — one flat bracket underside, and 4.0 of the 4.4 is in the first 4 mm above the bed, so printing on that face removes it ([`PRINT.md`](PRINT.md)) |

It earns its keep: it found `P5_ThighCuff` exporting a **non-manifold mesh** that `isValid()` and
`isClosed()` both called fine, and it caught `P25` being described in this BOM as *"prints nose-down,
no supports"* when printed nose-down a 70° cone diverges upward and every layer overhangs — 41 cm².
The nose taper now runs 16 mm instead of 5.5, at 44.5°, and is self-supporting.

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
| Drive | 128 | motor ($38) |
| Knee transmission | 50 | |
| Structure | 110 | gantry plate, V-wheels |
| Filament | 40 | |
| Electronics | 130 | drive ($29), 2× ESP32-C3 |
| Power (A123 736 Wh pack + BMS + backpack) | 250 | pack and BMS, purchased |
| **Total** | **~710** | |

The one-screw rebuild moved money around more than it saved it: the left-hand screw (−$70)
and the MGN7 rails and blocks (−$52) come off, and a second 29T pulley, its axle and
bearings, and an aluminium drive bracket (+$65) go on. What it bought is not price — it is
**842 g off the limb, one screw instead of two, and no special-order part anywhere.**

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
