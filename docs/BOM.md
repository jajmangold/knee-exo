# Build list

Quantities are for **one** knee unit (single leg). Prices are indicative USD from the
usual suspects (AliExpress / Amazon / ODrive) — order-of-magnitude, not quotes.

Every mechanism-derived number below comes out of
[`scripts/300_drivetrain.py`](../scripts/300_drivetrain.py). Run it before ordering,
because changing one assumption moves several lines at once.

**Ordering for both legs?** Only the symmetric lines double in quantity — extrusion, belts,
pulleys, motors, drive, V-wheels, bearings, fasteners, neoprene sleeves, webbing. The printed
printed parts double in *count* but are **new part numbers, not more of the same**: 17 L + 17 R
(1655 g of filament per leg, 103 h of printing), and **no machined parts at all** since
[`802_no_metal.py`](../scripts/802_no_metal.py). Sixteen of the seventeen are engraved with their
leg letter; the 29T capstan is the exception, because 414 searched 16 stations × 36 bearings and
found nowhere on it that is hidden at an open joint. The **ball screw stays right-hand on both legs** — a mirrored screw would be left-hand,
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
against the belt's outer face, then at 41.1 and now 38.46 (423) — while ignoring Y. The nut sits at `carrA + 36` and
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
| D1 | Ball screw **SFU1605, 5 mm lead, 200 mm**, BK/BF12 machined ends | 1 | **BOUGHT — this line used to read SFU1610 / 180 mm and the lead is the whole ratio.** 5 mm doubles the screw reduction to 46.4:1 before the link belt, which is why D7's motor pulley went from 32T to 38T. 1610 at 200 mm is not stocked anywhere outside China ([`443_screw_sourcing.py`](../scripts/443_screw_sourcing.py)); 1605 is everywhere. The ends are machined ⌀10 × 11 floating / ⌀12 × 25 + M12 × 1 × 14 + ⌀10 × 15 fixed, leaving **135 mm of thread against the 110 mm the nut's travel needs** ([`446_sfu1605_set.py`](../scripts/446_sfu1605_set.py)). Historically, when it was the 1610: 68.3 mm stroke; the nut sweeps Y 73…183 so 110 mm of thread is used, the rest is bearing seats. Axis at **X = −62**, moved 4 mm outboard of the old −58 so the nut clears the return strand. **180, not the 260 this line used to say, and not the 330 before that.** The screw spanned Y 57…314 only because the link belt sat on TOP of the drive: 131 mm of shaft above the nut's travel, carrying torque and nothing else. Turning the motor over ([`433_drive_flip.py`](../scripts/433_drive_flip.py)) moves the belt under the motor to Y 208…223 and the screw stops at Y 235 — a ⌀8 journal at Y 57…71 for the KP08, thread Y 71…204, and a ⌀8 journal at Y 204…235 for the 20T pulley and the 608. 178 mm of screw, so order 180: **79 mm and about 123 g of steel less than the last revision.** **The ⌀8 journals are the model's fiction**: the vendor drawing for a real machined-end screw is ⌀10 × 15 / M12 × 1 × 14 / ⌀12 × 25, so both journals are ⌀10 and every bearing seated on them steps up with them — see D8 and D8a. [`426_screw_ends.py`](../scripts/426_screw_ends.py), [`445_screw_foot.py`](../scripts/445_screw_foot.py). **Built in v8** as Y 60…71 floating (⌀10 × 11), thread Y 71…206, ⌀12 × 25 fixed journal Y 206…231 — 171 mm of the 200 bought, 29 parted off ([`459_v8_drivetrain.py`](../scripts/459_v8_drivetrain.py)) | 32 |
| ~~D2~~ | ~~Ball screw SFU1610, **LH**~~ | **0** | **Deleted.** The closed-loop belt over two 29T pulleys makes one carriage do both jobs, so there is no left-hand thread and no special order anywhere in the build. [`390_onescrew_section.py`](../scripts/390_onescrew_section.py) | −70 |
| D3 | SFU1605 **flanged** ball nut + **DSG16H housing** — **IN THE BOX** | 1 | **This line said FLANGELESS and that was wrong**: SFU/RM nuts always carry a flange, and the set ships the aluminium DSG16H housing too — which is the bought version of everything `P3_GantryPlate_Printed` was drawn to do. The nut bolts through its flange into the housing and the housing presents flat tapped faces, in aluminium, which does not creep under 764 N the way a printed pocket does. **`P3_GantryPlate_Printed` has to be redrawn around it** and the nut's envelope grows past the 36 × 36 × 42 box the model carries. Everything below describes the flangeless nut this line used to specify and is kept only because the gantry still contains it: Trapped axially between two end plates in the gantry rather than clamped radially — a 36.4 mm bore through a 40 mm housing severs it, and the load is along Y anyway. **Axial trapping is not enough on its own**: a flangeless nut in a round pocket has nothing stopping it turning with the screw, so two radial **M5 set screws** at Y 149 and 173 bear on the nut body through the gantry's outboard wall. File a flat on the nut for them. [`424_belt_tunnel.py`](../scripts/424_belt_tunnel.py) | inc. |
| D4 | BLDC outrunner C6374, **170 Kv**, 8 mm shaft | 1 | **Owned — 4 of them, $32–40 each.** 24.8 A peak at SFU1610. ~800 g, the heaviest single item | 38 |
| D5 | Diametric magnet 6 x 2.5 mm | 1 | Glued to the motor shaft end for the drive's onboard AS5047P | 3 |
| D6 | HTD-5M belt, **270 mm / 54T**, **15 mm** wide, closed loop | 1 | **54T is exact** at the 60.8 mm centre distance with the 38T:20T of D7 — the 32T it replaced wanted 50.6T, which is no belt at all ([`446_sfu1605_set.py`](../scripts/446_sfu1605_set.py)). Motor to screw, **under** the motor at Y 208…223 since the flip — the shortened screw is what that bought. Centre distance 61 mm. 15 mm, not 9: it now carries the overdrive, ~153 N tight side. **The CAD had this belt as 12 mm wide and 13 mm longer than a 61 mm centre distance allows** — a constant-width capsule rather than the hull of the two pulleys — so the motor's plate sat 3 mm inside it, and a cover sized to that envelope would have been 13 mm bigger than the belt. Rebuilt in [`433_drive_flip.py`](../scripts/433_drive_flip.py); everything proximal of the belt moved up 3 mm | 10 |
| D7 | HTD-5M **38T** (motor) + **20T** (screw) pulleys — **PRINT BOTH** | 1 each | **The 38T came off the buy list when the hub stopped being plastic.** A **rigid flange coupling** (D7a) sunk into the back of the printed pulley and a 3 mm aluminium plate on the front, bolted through: the grub screws then grip the shaft **steel on steel**, and the torque reaches the plastic through 4 bolts on an ⌀18 circle instead of one dimple at the ⌀8 bore — **37 N per bolt, 1.08 MPa, a factor of 37**, where a grub screw into PETG was a factor of about 1. The flange is buried in a body 27.5 mm in radius with 16.8 mm of wall outboard of the bolts, and the aluminium plate doubles as the belt flange a 15 mm belt on a 60 mm pulley wants anyway ([`449_flange_hub.py`](../scripts/449_flange_hub.py)). **P25_MotorNacelle needs a ⌀16 clearance bore on the motor axis** at Y 201…204 for the coupling's boss, cut in `434_odrive_mount.py` itself and not patched after it. The previous reasoning, which was right until the coupling appeared: **the split is about hubs and heat, not teeth.** Both tooth loads are trivial — 2.0 N and 5.2 N per tooth against the printed capstan's 52.7 — but the motor pulley takes **331 N of tangential load through a grub screw into a ⌀8 shaft**, and it is the only pulley in the machine clamped to something that runs past PETG's 80 °C glass transition. A printed hub there does not break, it **creeps**, the belt skips, and the motor's encoder stops corresponding to the knee angle. Buy that one in aluminium for $8. The 20T sees 113 N on ⌀12 at room temperature and is the awkward one to buy anyway — a 20T HTD-5M in a ⌀12 bore is not a stock item ([`447_printed_pulleys.py`](../scripts/447_printed_pulleys.py)). **A 1:1.9 OVERDRIVE, and both numbers changed when the 5 mm-lead screw was bought.** 32T:20T at a 5 mm lead is 29.0:1 and **0.87× the limb's own inertia** — the leg would feel 87% heavier with the power off. 38T:20T is 24.4:1, 0.62×, 23.5 A, and it is the only pulley under the ⌀63 can that also lands on a whole belt size (54T). The screw pulley's bore is **⌀12, not ⌀8**: it sits on the bearing journal of the machined fixed end ([`446_sfu1605_set.py`](../scripts/446_sfu1605_set.py)). Was: **a 1:1.6 overdrive, not 1:1.** This is what puts the total ratio at 14.5:1 with the SFU1610 — see [`404_link_ratio.py`](../scripts/404_link_ratio.py). Gearing here is nearly free because this belt sits on the motor side of the screw's advantage and carries 85 N, not the 764 N the capstan loop carries | 14 |
| D7a | **Rigid flange shaft coupling, ⌀8 bore** | 1 (sold in 4s) | Steel, ~⌀25 flange × 4 thick, ⌀13 boss × 11, 4 bolt holes on ⌀18, 2 grub screws. It is what makes D7's motor pulley printable. **Use steel spacers in the bolt holes, cut 0.1 mm proud of the printed hub**, so the flange and the backing plate clamp steel-to-steel: PETG creeps under sustained bolt preload — an M3 at 1.2 N·m is ~42 MPa under the washer, five times what it holds without flowing — and creep runs fast at the temperature this particular shaft reaches. **Every dimension here is read off a product photo. Measure yours** | 10 |
| D7b | 3 mm aluminium plate, ~55 mm square | 1 | The backing plate of the same sandwich, and the belt flange on that face | 3 |
| D8 | **BF12 floating-end screw support** — **IN THE BOX** | 1 | The SFU1605 set bought in October 2026 ships BK12, BF12, the M12 locknut, a circlip, the nut, a DSG16H nut housing and a flexible coupler, so this line and D8a and D9 are all sourced. It still has nothing to bolt to: **P32_ScrewFoot**. Previously, and the reasoning stands: The screw's **lower** end only, and **this line was wrong twice over**. It read "KP08 / KFL08", naming two parts that are not interchangeable: KP is a foot-mounted pillow block that bolts to a face **parallel** to the shaft, KFL a two-bolt diamond flange that bolts to a face **perpendicular** to it. Choosing between them is choosing which face you have — and [`445_screw_foot.py`](../scripts/445_screw_foot.py) went to look and found **neither**: within r 40 of the lower journal there is the knee yoke's corner 32 mm away in X and 18 mm below in Z, the belt's drive run, and cladding. No boss, no bolt pattern, no block. The same defect D8a records at the other end of the same screw. Beyond that, KP/KFL are shaft blocks for plain round rail — a pressed self-aligning insert — whereas this screw is sold **"FK/FF end machined"** and the vendor drawing shows ⌀10 × 15, then M12 × 1 × 14 for a locknut, then ⌀12 × 25 for the pulley. Those ends are cut for the FK/FF (or BK/BF) screw-support family. The bottom is the **floating** end: radial load only, free to slide as the screw grows, which is what makes it the cheap one. It needs **P32_ScrewFoot** to bolt to | 6 |
| D8a | **6001-2RS bearing** (12 × 28 × 8) | 1 | **Covered by the 6001s already bought**, which K3 no longer needs now the knee runs on 6904s. The screw's **upper** end. This line used to be a second KP08 bolted to "the drive bracket's screw boss" — [`420_mockup_audit.py`](../scripts/420_mockup_audit.py) went looking for the boss and found the bracket was **air at every Y from 210 to 296** along the screw axis: there was no boss, no bolt pattern, and nothing supporting the screw's top at all, so the screw was a cantilever off its bottom block. It is now seated in the **motor plate itself**, a ⌀22 × 7 pocket at Y 223…230. It does not get a boss of its own just above the nut's travel, where it would rather be: at Y 190 the bracket is a U-channel living at X ≥ −45 and a boss there attaches to nothing. One plate holding the motor and the screw's upper bearing is what the aluminium bracket did too. **Bond it, do not press it**. **Now a 6001-2RS (12 × 28 × 8) in a ⌀28 × 8 pocket**: the bought screw's fixed end is a ⌀12 × 25 bearing journal, long enough to carry the 20T pulley and the bearing together exactly as 433 drew it — but only if the ⌀10 tip and the M12 thread are parted off, which is Path B of [`446_sfu1605_set.py`](../scripts/446_sfu1605_set.py). Used as designed, **BK12 (in the box) replaces this line entirely** and the belt plane climbs 37 mm. The ⌀8/608 pairing came from the model's invented journals | 3 |
| D4a | **M5 × 16 motor bolts** | 4 | The C6374 to the drive bracket's end plate, on a **25 mm square** about the shaft. ⌀5.2 clearance takes M4 or M5. **MEASURE YOUR MOTOR FIRST**: 19 mm and 30 mm patterns exist on motors sold under similar names, the model's motor is a featureless cylinder, and nothing in CAD can confirm the spacing. Until 428_motor_mount.py the motor had no bolts at all and 420's hole count was satisfied by the KX-1 interface's four M4, 56 mm away on another face | 2 |
| D9 | Flexible shaft coupler — **IN THE BOX, unused** | 1 | It ships with the screw set for a coaxial stepper. The motor here is belted, so this is a spare. Do not design it in: a coupler on the ⌀10 tip puts the motor in line with the screw and 404/433 both rejected that | 0 |

## 3. Knee transmission

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| K1 | HTD-8M **open-ended** belt, 30 mm wide, **1 metre** | 1 | **Cut to length on the machine.** The path is 2π·36.923 + 2·255 = 742.0 mm; 64 mm of that is clamped teeth and the rest is spare. Open-ended 8M is sold by the metre and stocked everywhere, where a 744 mm × 30 mm closed loop is a special order — and cutting it removes the quantisation: **a bought loop arrives 2.0 mm long** and the idler has to swallow 1.0 mm of centre distance out of the spring's 3 mm of travel. **The gantry already is the clamp**: the belt tunnel's inboard wall carries toothed grooves the belt's own teeth sit in, so going open-ended lengthens that channel from 5 grooves to 8 and adds a lid — **6 teeth for the 914 N tight end, 2 for the 150 N slack end, at the same 153 N/tooth and 1.5 MPa the design already accepts** ([`448_open_belt.py`](../scripts/448_open_belt.py)). The one thing given up is that a loop has no termination to fail. Previously, and this is the reasoning it replaces: a closed loop, not an open strip — no end terminations, and it is tensioned by sliding the idler instead. 764 N differential over 30 mm = 25.5 N/mm. **This length is only right because [`421_pulley_teeth.py`](../scripts/421_pulley_teeth.py) corrected the capstan**: the rim was built at 35.552 — the pitch line differential deducted twice — which puts the path at 737.7 mm, so a 742 mm belt would arrive 4.3 mm long against an idler with 3 mm of travel. The belt is gripped by a 5-tooth land in the gantry's tunnel, not clamped: see §5 and [`424_belt_tunnel.py`](../scripts/424_belt_tunnel.py) | 25 |
| K2 | **⌀20 × 70 hardened ground linear shaft, h6** | 1 | **⌀20, not ⌀12.** 457 sized this rod around a 6001 because BOM K3 and D8a were already 6001s — a parts-commonality argument that cost the shaft three quarters of its section. The printed capstan takes a 6904 with 14.3 mm of wall, so the bigger bearing was always available: **cantilever 94 MPa → 20**, the last acknowledged compromise in the joint. ⌀20 linear shaft is stocked by every 3D-printer and router supplier. Also the idler's axle. Previously ⌀12 × 60, and the reasoning below still applies to the shaft itself: **⌀20, not ⌀12, because the capstan became a bought pulley.** Its ⌀24 bore carries an 8 × 3.3 keyway reaching r 15.3, so the bearing seat must be bored past it whatever bearing goes in — and once you are boring, ⌀37 for a 6904 is the same cut as ⌀28 for a 6001. That takes the cantilever `457_knee_bearings.py` accepted from **94 MPa to 20**, the last acknowledged compromise in the joint. It is also the idler's axle. Previously ⌀12 × 60, and the reasoning below still applies to the shaft itself: The knee axis. **It is no longer a pin through a hinge — it is a stub axle.** The joint's bearings moved into the capstan ([`457_knee_bearings.py`](../scripts/457_knee_bearings.py)), so this rod is clamped in `P1_KneeYoke` over Z 76…94 (an 18 mm bonded ⌀12.2 bore plus an M4 grub through a heat-set insert) and cantilevers out through both 6001s. That deletes the two collar lines this entry used to need: the yoke IS the clamp. **h6 (0/−0.011), not the m6 of an ISO 8734 dowel** — m6 into a 6001's 0/−0.008 bore is an interference fit where this wants a hand assembly. **Not HSS**: hard and brittle, and this takes shock. Cantilevered it sees ~94 MPa; a ground rod carries that with a factor of ten | 8 |
| K3 | **6904-2RS sealed ball bearing** (20 × 37 × 9) | **4** | **Two in the printed capstan and two in the printed idler.** 69 N·m of tilt across a 21 mm span against the 6001 pair's 52, on a ⌀20 shaft instead of ⌀12, and the bond area 418 cares about goes from 704 to **1046 mm²** — the one job PETG has here gets easier. **Bond, do not press** — 418's rule stands for a plastic housing. Seat ⌀37.2 for a 0.1 mm bond line. A 6904 is a bike and RC shop part, stocked everywhere. The 6001s already bought are not wasted: D8a takes one. Previously 2 × 6001-2RS: **Two in the capstan and two in the idler**, which are now the same bought pulley (S2b), bored ⌀37. 76 N·m of tilt across a 23 mm span against the 6001 pair's 57, on a ⌀20 shaft instead of ⌀12. **Pressed into aluminium, not bonded into PETG** — 418's “a press fit into PETG does not hold” was about the plastic, not the fit. Seat 37 H7. The 6001s already bought are not wasted: D8a takes one. Previously 2 × 6001-2RS: **Two, and they are now inside the capstan** at Z 96…104 and Z 118…126 — flush to each face of the belt land, 22 mm apart, bonded into a ⌀28 seat with 6 mm of PETG wall and a ⌀26 abutment between them. The single one this line used to specify sat in the yoke at Z 80…88, **27 mm inboard of the belt it carried**: that offset is why `P2a_KneeHingePlate` spanned 58 mm and weighed 188 g to reach between load and support, and it turned the belt's 1064 N into a 28.7 N·m tilting moment taken by two printed bores. Centred, both numbers are zero and each bearing sees 532 N — a factor of 4.5 on C0, with ~52 N·m of tilt capacity across the pair. **A pair is the point**: one bearing cannot react tilt, and a self-aligning KFL/KP unit cannot either at any span ([`455_concept_rev2.py`](../scripts/455_concept_rev2.py)). **Bond, do not press** — 418's rule, and 532 N over π·28·8 mm² is 0.76 MPa. Same part as D8a | 6 |
| K4 | Compression spring, ~500 N/mm, 3 mm working travel | 1 | Now acts on the **idler carrier's slotted mount**, not a belt end. Same job — takes up belt bedding-in — one fewer printed part | 5 |

## 4. Structure

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| S1 | V-slot extrusion **20x40**, **black anodised**, 160 mm | 1 | Cut to Y 51…207. **~159 g, against 352 g for the 20×60 × 227 mm.** It ends short of the idler because a 71 mm pulley on the centreline would otherwise contain the extrusion. **Its 40 mm face has slots at X = ±10, not X = 0** — the fairing spine has to move | 12 |
| S1a | V-slot extrusion **20×40**, **black anodised**, 240 mm | 1 | **The shank member, and this line did not exist until now** — the device has always needed a second extrusion and the BOM only listed the thigh's. Cut to Y −300…−66, **in line with the thigh rail and centred on the knee's own plane at Z 84**, not offset behind it: 431_shank_2040.py measured both profiles from the model rather than a catalogue and the 2040 is **1.9× the section and 5.9× the stiffness** in the plane the knee bends. The 2020 it replaced was strong enough — 6063 yields at ~170 — but soft: most of a degree of knee angle the encoder cannot see, because it happens past the sensor. 555 mm² of section, **351 g**. Its end face has two cells, so the hub caps it on **two M5 into the core** rather than being bolted to one face: an end cap reacts the rail's torsion in the screws' shear, where a plate on one face reacts it as a couple on its bolts ([`430_shank_inline_build.py`](../scripts/430_shank_inline_build.py), [`432_shank_2040_build.py`](../scripts/432_shank_2040_build.py)) | 16 |
| S2 | **Mini V-wheel**, Delrin, OD 15.23 | 4 | On the |X| 20 corners of the 20×40, wheels 50 mm apart in Y. **Mini, not solid**: a V groove seats the corner apex at the bottom of the groove, so the centre stands off along the 45° bisector — a solid wheel reaches |X| 37.6, which is inside the belt's backing at 36.24…38.46, and a mini reaches 31.0 — clear of the belt's tooth tips at 32.86 by 1.86 mm. Spaced **70 mm apart**, not 50: OpenBuilds publishes no load rating, and a Hertz calculation ([`401_vwheel_load.py`](../scripts/401_vwheel_load.py)) puts the flank contact at 107 MPa against a ~101 MPa yield onset at 50 mm, versus 91 MPa at 70. Bench-test for play at reversal; MGN7 on the same side faces is the fallback | 12 |
| S2a | Eccentric spacers + wheel bolts | 4 | Two eccentric, two fixed, the usual V-slot gantry arrangement | 10 |
| S2b | **29T HTD-8M idler pulley**, 30 mm wide — **PRINT IT** | 1 | **Printed, and that is now a design rule rather than a cost saving.** A bought 28T × 32 aluminium pulley was specced here for a day: it retires `421`'s unproven tooth profile and lets the bearings press into metal. It was dropped because **this design is meant to be reproducible by anyone**, and “10 available from one eBay seller” is not a part — it is a window. Anything on the critical path has to be printable or a catalogue number. The bought pulley stays documented as an upgrade for whoever can source a matched pair. Everything below still holds: **The capstan AND the idler, and they must be identical** — the constraint that made `421_pulley_teeth.py` grow the capstan's rim to match a bought idler in the first place. 28T, not the 29T drawn: nobody sells 29T, and 28T lands within 4% of everything already verified — belt tension +4%, idler reaction +3%, strands move **in** 1.3 mm each side, reflected inertia 0.62 → 0.57× the limb. **Buying the capstan retires `421`'s open question** — “this is an approximation and must be proven against a real belt” — on the highest-loaded pulley in the machine, and with it most of what `TEST_ToothCoupon` is for. Bore both ⌀37. Previously printed: **It transmits no torque whatsoever** — it only turns the belt round — so the tooth load that gates every other printed pulley is identically zero here. Its bearings take 1828 N, which is a seat problem and not a tooth problem: 914 N on each of two ⌀22 × 7 seats is 5.9 MPa against PETG's ~40, a factor of 7 ([`447_printed_pulleys.py`](../scripts/447_printed_pulleys.py)). It was $25 for a job with no load in it. Gated on `TEST_ToothCoupon` like the capstan. Previously bought: **The same part as the knee capstan** — which is the constraint that fixed the capstan's radius. A bought 29T pulley measures 72.48, and the belt cannot wrap 72.48 at one end and the 71.10 the capstan was drawn at the other without the strands sitting at different distances from the centreline. On the centreline at X = 0, Y 255, which is what makes the two strands land at exactly ±36.92 — true as of [`421_pulley_teeth.py`](../scripts/421_pulley_teeth.py), not before it | 25 |
| S2c | ~~Idler axle + 2 bearings~~ — **folded into K2 and K3** | 0 | The idler now runs on the same ⌀20 shaft and the same 6904s as the knee, so this line is two fewer part numbers rather than its own. **It is also stronger**: 1828 N over two 6904s is 914 N each at 3.6× C0, where the ⌀8 axle and two 608s this line used to ask for were 1.5× — "under a 608's static rating, but only just" | 0 |
| ~~S2d~~ | ~~Aluminium gantry plate~~ → **printed, see §5** | 0 | 80.8 cm³, replacing 383 g of printed twin carriages. It **straddles** the belt rather than crossing over it: the drive run passes through a closed tunnel in the plate — floor at Z 89…95.5, roof at Z 126.5…130, outboard wall face at X −38.70 — and the tunnel's inboard wall is cut with **five HTD-8M grooves at 8 mm pitch over Y 144…186**, which is how the belt is gripped. 764 N over five teeth is 153 N a tooth, 1.5 MPa across a 30 × 3.45 mm groove wall. There is 5.5 mm between the nut's OD at X −44.0 and the belt's back at X −38.46. Owned | 15 |
| ~~S2e~~ | ~~Aluminium drive bracket~~ → **printed, see §5** | 0 | Holds the idler, the screw's top bearing and the motor. **136.8 cm³ as printed** (139.7 before the flip) (121 cm³ when it was aluminium, and 134.9 before [`422_missing_features.py`](../scripts/422_missing_features.py) added the ⌀32 × 12 screw boss the BOM had always claimed it had). 4 mm plates and 5 mm cheeks, sized by [`400_bracket_stress.py`](../scripts/400_bracket_stress.py) at 18 MPa against 240 MPa yield; it was 465 g when it was sized by eye | 25 |
| S3 | M5 T-nuts + button head cap screws | ~40 | Everything mounts to the slots — **at X ±10 on the 20×40's wide faces**, which is where its two cells put their channels. The knee yoke's pattern was at X −20/0/+20, the spacing of the 20×60 this design abandoned, so none of its six bolts could reach a slot ([`427_rail_bolts.py`](../scripts/427_rail_bolts.py)) | 12 |
| S3a | M5 × 16 into the extrusion's **end** | 2 | The drive bracket's only fixing to the rail, through its 10 mm end plate into the two cell cores at X ±10. Self-tapping, or tap the extrusion M6 and step up | 2 |
| S4 | M3 / M4 cap screws, assorted | ~40 | Fairings, cuffs, electronics | 10 |
| S4b | **Brass heat-set inserts, M3 and M5** | ~30 | **This line did not exist, and the build has assumed it throughout** — [`450_buy_list.py`](../scripts/450_buy_list.py) found it by going through the BOM line by line rather than by hitting it during assembly. P30/P31 each want 6 × M5, the printed 20T pulley wants one for its grub screw, and every printed-to-printed joint in the machine is drawn around them. A screw driven straight into printed PETG strips at a fraction of the torque | 12 |
| S4c | **Dowel pins, ⌀5 × 16** | 4 | P30/P31's two locating dowels, both legs. The six M5 carry the load; the dowels set the position | 4 |
| S4a | **Rubber grommets, M5**, + shoulder screws | 3 | The fairing's only mounts. Isolating rather than rigid — `ELECTRONICS.md` §9 names the rigid spine as the likely structure-borne noise path | 6 |
| S5 | **Neoprene sleeve, thigh and calf**, 3 mm | 2 | The skin interface, and the only thing that touches the patient. Replaces the EVA pad entirely. Raises the friction that sets strap tension from μ≈0.4 to ≈0.6 worst case, so the strap needs **21 N instead of 31 N**; bridges the shell rim instead of letting it dig; and moves the sliding interface off the skin. Washable, and a consumable. Over a **closed, dry** incision only — ask whoever runs his rehab, and note neoprene contact dermatitis is common enough to plan a nylon-faced fallback  **The drive end is now checked against it.** Every limb cut in this design is a cylinder about the limb axis and the leg is a taper, so until [`438_limb_clearance.py`](../scripts/438_limb_clearance.py) nothing asked whether 3 mm of neoprene fits under the cover: it did not — the controller's cover was 2.9 mm inside it and `P22` 0.1. Both are trimmed to the limb's measured taper plus the sleeve plus 0.5 mm of air. The motor can has 1.6 mm, the bracket exactly 0.0, and if the patient measures fatter than the nominal taper the adjustment is in the README under "How much leg this fits" | 30 |
| S5a | **Nylon webbing, 38 mm** | ~1.5 m | The cuff closure. 38 mm because at 31 N across the open side of the cuff a 3.5 mm lace is ~90 kPa on soft tissue and 38 mm webbing is 8.3 kPa — webbing is its own tongue, which is why a laced brace needs a separate one | 8 |
| S5b | **Cam buckle + D-ring**, 38 mm | 2 + 2 | Routed 2:1 through the D-ring, so the hand pull is ~12 N rather than 21. Repeatable and one-handed, which hook-and-loop is not — and repeatability is what keeps the knee axis aligned day to day | 12 |
| S5c | **Side-release buckle**, 38 mm | 2 | In the loop so the whole thing drops off in one squeeze. This is a **powered** device at 28.2 N·m on a post-operative limb; emergency doffing is the one safety argument in [`408_cuff_loads.py`](../scripts/408_cuff_loads.py) | 6 |

## 5. Printed parts

**19 per leg, 38 for the pair** — [`stl/`](../stl) is the left leg and [`stl_R/`](../stl_R) the
right. Seventeen, not fifteen, because the **drive bracket and the gantry plate are printed now**:
they were the only two parts in this build needing a workshop, and
[`802_no_metal.py`](../scripts/802_no_metal.py) shows neither was ever sized by load. The bracket
was 50× overbuilt in aluminium (4.3 MPa against 240), so in PETG the governing rule becomes creep
and bearing rather than yield — 6 mm plates at 9.8 MPa, with the idler's bearings seated in them so
the 914 N per plate presses on a 26 mm race (5.9 MPa) instead of a 10 mm axle (15.2, which beds in).
Printing both **saves 241 g**: PETG at 1.27 g/cm³ against 2.70 beats the extra section. They are not 15 parts printed twice: every one is chiral, and a left part will appear to fit
the right leg while putting the drive on the wrong side of the limb. The engraved number is how you
tell: `P5L` against `P5R`.

Blue PETG, 0.2 mm layers. Perimeters and infill per part, with the orientation, support area,
filament and time each one actually needs, are in **[`PRINT.md`](PRINT.md)**, which is generated from
the exported STLs by [`900_print_list.py`](../scripts/900_print_list.py) rather than typed here —
this table used to list `P3_Carriage`, `P3b_CarriageB` and `P11_SprungAnchor`, of which the first
became a bought aluminium plate (S2d) and the other two were deleted with the second ball screw.

| Part | Qty/leg | Suggested |
|---|---|---|
| `P1_KneeYoke` | 1 | 5 perimeters, 60% gyroid — carries the full knee reaction, and since [`457_knee_bearings.py`](../scripts/457_knee_bearings.py) it is **the knee rod's only support**: an 18 mm ⌀12.2 clamp bore over Z 76…94 through a boss that replaced the old ⌀28 bearing seat, plus an M4 grub cross-hole. The rod cantilevers out of it through both 6001s, so this bore being square in two planes is what decides whether the knee points where the leg does. 124.8 → 134.4 cm³ |
| `P2a_KneeHub_Pulley29T` | 1 | 6 perimeters, 60%. The tooth flanks want a fresh nozzle. **It is now the knee's bearing housing too** — two ⌀28 × 8 seats at Z 96…104 and Z 118…126, bored in ONE setup so they end up collinear, with a ⌀26 abutment between them. Losing the pin lugs took it from 148.1 to 134.2 cm³. **Print it with the knee axis vertical**: both seats and the belt land are then concentric by construction rather than by luck ([`457_knee_bearings.py`](../scripts/457_knee_bearings.py)) |
| `P5_ThighCuff`, `P7_ShankCuff`, `P6_ShankSocket` | 1 each | 4 perimeters, 30% |
| `P20_KneeCap` | 1 | 3 perimeters, 15%, cosmetic |
| `P21_FairingThigh`, `P22_DriveCap` | 1 each | 3 perimeters, 15%, cosmetic. the shank fairing (`P24`) **used to be here and is deleted**: the shank rail moved in-line under the knee joint ([`430_shank_inline_build.py`](../scripts/430_shank_inline_build.py)) and there was nothing left for it to fair |
| `P25_MotorNacelle` | 1 | 3 perimeters, 15%. Prints nose-down on its domed end, no supports. **Its leading face is a 77° cliff and that is a known defect** ([`464_thigh_blend.py`](../scripts/464_thigh_blend.py)): r 136.7 at Y 200 to r 158.0 at Y 205. The pod never stuck out — it starts abruptly, and a wall facing down the leg is what snags. A lofted-wedge ramp was built and reverted for looking like a fin; it wants a proper surface blend |
| `P23a/b/c_FairingMount` | 3 | 4 perimeters, 40% — they carry the canopy. All three are the **same part**, so they share one mark |
| `A7_DriveBracket_Idler` | 1 | 6 perimeters, 60% — the heaviest load path in the machine, 1828 N through the idler. **Seat the two idler bearings in its plates and bond them**; a bare axle through 6 mm of PETG is 15.2 MPa and beds in |
| `P3_GantryPlate_Printed` | 1 | 6 perimeters, 50% — in-plane loads only, 1.5–7.6 MPa. **Has no bolt holes drawn yet**, see the README's open items |
| `P30_InterfaceProx`, `P31_InterfaceDist` | 1 each | **KX-1 module interface.** 6 perimeters, 60% — structural. 6 × M5 heat-set inserts + 2 × ⌀5 dowels. Printed here because standalone this module needs 1.2 MPa of bearing; the same six holes in 6 mm aluminium carry the 1472 N load-to-ground case ([`501_interface.py`](../scripts/501_interface.py)) |
| `P27_ControllerMount` | 1 | 4 perimeters, 40%. Bolts to the motor's **rear** bolt circle and carries the XDRIVE MINI on four bosses, with the board's AS5047P 2.0 mm off a magnet on the shaft stub. **Do not print it until the board is measured** — every dimension in it is guessed ([`434_odrive_mount.py`](../scripts/434_odrive_mount.py)) |
| `P2b_Idler29T`, `P33_ScrewPulley20T`, `P34_MotorPulley38T` | 1 each | **v8 carries the two link pulleys as `A6b_ScrewPulley20T` and `A6c_MotorPulley38T`** — plain cylinders at the tip radius, which is how every bought pulley in this model is drawn; the teeth are cut when the coupon says the profile is right. The idler is still only a BOM line. Was: 6 perimeters, 60%, fresh nozzle — the tooth flanks are the whole part. The idler carries no torque at all and the 20T carries 5.2 N per tooth, both far under the capstan already committed to. **Both gated on `TEST_ToothCoupon`**, and the 20T additionally on an HTD-**5M** coupon: the 5M tooth is 2.16 mm tall where the 8M is 3.45, so 421's approximation of an unpublished curve is 60% bigger as a fraction of the tooth ([`447_printed_pulleys.py`](../scripts/447_printed_pulleys.py)) |
| `P32_ScrewFoot` | 1 | **Built in v8** (left only), 13.3 cm³. Was: 5 perimeters, 50% — it is the screw's only lower support. A ⌀10 floating-end support (D8) bolted to a 36 × 36 × 7 plate across the shaft at Y 50…57, centred on the axis at X −62, Z 106; an arm inboard at Z 88…93 that ducks under the belt's drive run with 3.0 mm to spare; and an end plate at Y 44…51 taking **2 × M5 into the rail's lower end cores at X ±10** — the same fixing S3a uses at the rail's other end. It anchors to the aluminium, not to `P1_KneeYoke`, deliberately: the yoke is already in the print-now queue and bolting to it would take it back out. It **rests** on the yoke's top face at Z 88, so the weight is in compression and not in the M5s' shear. 10.6 cm³ of envelope, nothing in the way but cladding to relieve. **Waiting on the support's own drawing** — the flange bolt pattern is the one dimension that cannot be guessed ([`445_screw_foot.py`](../scripts/445_screw_foot.py)) |
| `P28a_IMUCover`, `P28b_IMUCover` | 1 each | 3 perimeters, 20%, 2 mm. The lid over each cuff's IMU pocket. **The pocket is the measurement, not the retention** — it fixes the sensor's axes to the limb, which is what makes every angle in ELECTRONICS §3a mean something. Fit both modules the same way up and the same way round ([`442_imu_mounts.py`](../scripts/442_imu_mounts.py)) |

**~1.64 kg of filament and ~102 printer-hours per leg**, so 3.3 kg and about ten days of printing
for the pair — up from 1.38 kg because the bracket and gantry plate joined the printed set, and
down 241 g in total device mass because they left the fabricated one. Both figures are models rather than measurements — nothing has been printed yet — and
[`PRINT.md`](PRINT.md) states the models so they can be corrected against the first real print.

**Hardware does not fit a printed hole as drawn.** A hole comes off the bed 0.1–0.3 mm undersize,
and almost every hole here runs along the knee axis while most parts build along their length, so
most print slightly oval too. 136 holes, what fits each and what to do about it:
[`417_fastener_audit.py`](../scripts/417_fastener_audit.py), summarised as a drill list at the top
of [`ASSEMBLY.md`](ASSEMBLY.md).

**14 of the 15 parts are engraved with their part number and leg letter**
([`412_engrave.py`](../scripts/412_engrave.py)) — 0.8 mm recessed, Arial Bold at 8 mm where it fits
and 5 or 4 mm where the suffix made it not, on a face that is **verified hidden** and **verified to
read forwards**. `P2a_KneeHub_Pulley29T` carries no mark: 16 stations × 36 bearings found nowhere
covered, because it is the knee hub at an open joint. It is the 135 cm³ 29T pulley and nothing else
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
| fits a 220 × 220 bed | all 17 parts plus the tooth coupon — largest footprint 180 mm, tallest 182 mm |
| mesh watertight | all 18. **`P6_ShankSocket` was not**, and nothing else could see it: valid, closed, BOP-clean, one solid, and 33 faces under 0.01 mm² in a band 1.2 **nanometres** thick, which no deflection would mesh. [`436_socket_mesh.py`](../scripts/436_socket_mesh.py) |
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
| E1 | Makerbase MKS XDRIVE MINI | 1 | **Owned — 4 of them, $29.48 each.** ODrive v3.6 clone, 12–56 V, ~40 A, onboard AS5047P. Ships on modified fw **0.5.1** — do not let odrivetool upgrade it. **It cannot go in the pack**: its encoder is on the board, so it has to sit over the motor's shaft end — see ELECTRONICS §2a for the air gap that fixes its position. **63.00 × 58.00 mm on SIX ⌀3.3 holes**, two columns 56.60 apart, rows 51.50 corner to corner with the middle row 24.00 below the top — from the "Size" drawing in `Smurf/xdrive-mini-docs`, corroborated by the board in hand. That replaces a guessed four-hole 55 × 50 pattern. The AS5047P sits central, in a round window in a **backplate** on the encoder face, so the air gap is NOT measured from the board's mounting face — that recess depth is the one number still to be measured, and `440_bench_rig.py` exists partly to measure it | 29 |
| E1a | ST-Link V2 clone | 1 | Only to back up / recover the MINI's firmware. Buy it before you need it | 5 |
| E2 | Brake resistor, ~2 Ω 50 W | 1 | **Not optional** — see the regen section | 15 |
| E3 | ESP32-C3 SuperMini | 2 | One on the leg, one as a pocket remote. You already have these | — |
| E4 | AS5048A magnetic encoder breakout | 1 | Absolute knee angle over SPI. Removes the power-on homing routine | 12 |
| E5 | Diametric magnet 6 x 2.5 mm | 1 | Into the flush counterbore in the knee pin head — **which is why K2 is non-magnetic stainless and not a hardened dowel** | 3 |
| E6 | SN65HVD230 CAN transceiver | 1 | ESP32-C3 TWAI to ODrive CAN | 4 |
| E7 | IMU — **MPU-6050** | **2** | **Owned.** One on the thigh cuff, one on the shank cuff, each in the printed pocket that fixes its axes to the limb. This line used to read "BNO085 or ICM-42688-P, 1 off, thigh-mounted, for gait phase" — the BNO085 fuses on-chip and hands over a quaternion, which is worth paying for only if you need YAW, and nothing here does: the knee works in the sagittal plane and pitch/roll are gravity-referenced, so they cannot drift. The second one is the real change. Two of them give POSTURE, which no encoder in this device can give at any price — the AS5048A reads the same angle sitting in a chair as lying in bed with the knees up, and those want opposite things from a powered brace. See ELECTRONICS §3a for the separation table and §8a for the assist gate it enables. Calibrate the gyro bias at startup while the leg is still; buy spares, the part is end-of-life and the supply is full of clones | 6 |
| E8 | XT90-S anti-spark connector pair | 1 | The drive's bus caps will arc a plain XT60. **Do not add bulk capacitance to this bus without a precharge circuit**: a 47 000 µF can dumps ~45 J into the connector on mating, and buys only 4.6 J of regen headroom in the 2.2 V between a charged pack and the overvoltage trip — a fraction of one sit-down. ELECTRONICS §6b does that arithmetic. The brake resistor is the regen path, not a capacitor | 5 |
| E9 | Inline fuse holder + **15 A** blade fuse | 1 | At the pack, before anything else. 15 A, not 30 — peak BUS current is 4.9 A | 6 |
| E10 | Latching e-stop, 22 mm, NC | 1 | On the waist belt where a hand falls naturally | 10 |
| E11 | Silicone wire 12 AWG | 4 m | Pack to leg. 0.55 V drop at 22 A over 1.5 m each way | 12 |
| E12 | Cable gland, strain relief, spiral wrap | 1 set | The tether crosses the hip and must not snag | 10 |

## 7. Power

| # | Part | Qty | Notes | ~USD |
|---|---|---|---|---|
| B1 | **12S LiFePO4 pack, ≥ 25 A continuous, repacked** | 1 | **Cells owned** — the A123 736 Wh M1B module, to be broken down and re-laid out around B2 in a case shaped for this device rather than for whatever it came out of. That makes the pack a generic item anyone can build, which is the point. **What the repack MUST preserve, because the rest of the electronics is sized against it and not against the module:** 12S (43.8 V full, 30 V empty, inside the drive's 12–56 V window), ≥ 25 A continuous so the 23.5 A peak of D7 is not the limit, and the BMS's low-temperature cutoff of B2. The numbers that follow from it and would have to be redone if the series count changed: the ODrive's 46 V overvoltage / 31 V undervoltage trips, the 2 Ω 50 W brake resistor, E9's 15 A fuse and E11's 12 AWG. Was: A123 LiFePO4 36 V, 736 Wh (M1B module), 12S, 43.8 V full, 30 V empty **Bought.** 12S, 43.8 V full, 30 V empty — inside the S1's 12–50 V window | — |
| B2 | **7–17S LiFePO4 smart BMS, 100 A, CAN/RS485/UART, low-temp cutoff** | 1 | **Bought, and it is the off-the-shelf half of the repack** — B1's cells are laid out around this rather than the other way round. Take it on UART or RS485: the ESP32-C3 has one CAN controller and the ODrive already has it **Bought.** Take it on UART or RS485: the ESP32-C3 has one CAN controller and the ODrive already has it | — |
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
