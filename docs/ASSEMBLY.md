# Assembly

Written to be followed with the parts in front of you, in the order they go together. Every printed
part carries its number engraved on a hidden face — `P5L` for the left leg, `P5R` for the right —
which is the only way to tell apart the two cuffs, the two halves of the drive shell and the three
identical fairing mounts once they are off the bed.

> [!WARNING]
> This is a **powered** device applying up to **28.2 N·m** to a post-operative knee. Two things are
> not optional: the side-release buckles in the strap loop (S5c), so the whole thing comes off in one
> squeeze, and a bench run through the full range of motion with the limb **out** of it before it
> goes on anybody. There is no FEA behind any printed part — only hand calculations
> ([`400_bracket_stress.py`](../scripts/400_bracket_stress.py),
> [`401_vwheel_load.py`](../scripts/401_vwheel_load.py),
> [`408_cuff_loads.py`](../scripts/408_cuff_loads.py)) and a 107-pose interference sweep.

Do not mix legs. The two sets are mirror images, not duplicates: a left shell will appear to fit the
right leg and will put the drive on the wrong side of the limb.

---

## 0. Before anything fits: finish the parts

Printed holes come off the bed 0.1–0.3 mm undersize, and in this device almost every hole runs
along the knee axis while most parts build along their length — so most holes print slightly oval
as well. Budget an hour per leg for this and do all of it before you pick up a bolt.

| Do this | To these |
|---|---|
| Drill 4.3 | every ⌀4.2 — `P1`, `P6` (16 of them), `P30`, `P31` |
| Drill 5.3 | every ⌀5.2 — `P1` (4, at X ±10), `P2a`, `P3` (4 wheel + 2 set screws), `P5`, `P7`, `P21` (19), `P23a/b/c`, `P6` (12 clamp bolts at |X| 24 + the cap's 2 axial), `P27` (4 into the motor's rear), `A7` (2 into the rail's end) |
| **Ream** 5.0 H7 | the ⌀5.0 dowel holes in `P30` and `P31` — these set the interface alignment, so ream, do not drill |
| **Bore 28.2, on a drill press** | the **two** ⌀28 bearing seats in **`P2a`**, at Z 96…104 and Z 118…126. 28.2 rather than 28.0 deliberately: the 6001s are **bonded**, not pressed, and 0.1 mm is the bond line. **Bore them in one setup without moving the part** — they are the knee axis, and two seats bored separately will not be collinear |
| Ream 12.2, on a drill press | the ⌀12.2 rod bore through **`P1_KneeYoke`**, Z 76…94. The yoke is now the rod's only clamp, so a crooked bore is a knee that points the wrong way. **The pin holes in `P2a` are gone** — the hub no longer touches the rod |
| Melt in M5 heat-set inserts | the ⌀6.4 holes — 4 in `P6`, 6 each in `P30` and `P31`. Leave the holes as printed; an M5 insert is ⌀7.0 and wants 6.4 |
| Leave alone | the ⌀10.4 counterbores on `P5` and `P7` — the cap heads sit in them |

Then dry-fit the knee: the rod through `P1L`, both 6001s dropped into `P2aL` **not yet bonded**, no
belt, and swing it. It must move freely through **−2° to +104°** with no tight spot. Fix that here,
not later: once the bearings are bonded in, getting back out of the seats means destroying them.

Full table: [`scripts/417_fastener_audit.py`](../scripts/417_fastener_audit.py), 136 holes.

---

## 1. Thigh spine and gantry

1. Cut the **20×40 V-slot** (S1) to **156 mm**, which is Y 51…207 on the model's axis. Deburr the
   slots or the T-nuts will not slide.
2. Fit the four **mini V-wheels** (S2) to the **gantry plate** (`P3_GantryPlate_Printed` — printed,
   not aluminium: [`802_no_metal.py`](../scripts/802_no_metal.py) puts it at 1.5–7.6 MPa in PETG),
   two on eccentric spacers. The four M5 bolt holes **are** drawn now, at |X| 23.36, Y 126 and 196
   ([`424_belt_tunnel.py`](../scripts/424_belt_tunnel.py) takes them from where the wheels actually
   sit rather than from a remembered number). Wheels sit on the |X| 20 corners, **70 mm apart in
   Y**, not 50: the Hertz contact at 50 mm is 107 MPa against a ~101 MPa yield onset
   ([`401_vwheel_load.py`](../scripts/401_vwheel_load.py)).
   **Mini wheels only.** A solid V-wheel reaches |X| 37.6, inside the belt's backing at 36.24…38.46;
   a mini reaches 31.0 and clears the belt's tooth tips at 32.86 by 1.86 mm.
3. Slide the plate onto the extrusion and set the eccentrics until it rolls with no rock and no
   drag. Check again after the belt is tensioned — tension changes it.
4. Mount the **ball screw** (D1, SFU1610 RH, **180 mm**) on its axis at **X = −62**: the **KP08** (D8)
   at the lower end, and at the upper end a **608-2RS bonded into the motor plate's ⌀22 × 7 seat**
   at Y 223…230 (D8a). The screw now stops just above the nut's travel instead of running past the
   motor — see step 7. The nut (D3) is **flangeless and trapped axially** between two plates
   on the gantry, not clamped radially: a 36.4 mm bore through a 40 mm housing would sever it, and
   the load is along Y anyway.
   **File a flat on the nut** and lock it against rotation with the two radial **M5 set screws**
   through the gantry's outboard wall at Y 149 and 173: trapping the nut axially carries the
   thrust, but a flangeless nut in a round pocket has nothing stopping it turning with the screw,
   and if it turns, the carriage does not move.

> The screw is **right-hand on both legs**. Do not look for a left-hand one for the right leg — the
> reflection is absorbed by one sign in firmware (section 9).

## 2. Drive bracket, motor, link belt

5. Bolt the **drive bracket** (`A7_DriveBracket_Idler` — printed, 6 mm plates) to the top of the
   extrusion: **two M5 × 16 along the limb** (S3a) through its 10 mm end plate at X ±10, Z 98,
   into the two cell cores in the rail's end face. Self-tapping into the core, or tap it. These
   holes did not exist until [`427_rail_bolts.py`](../scripts/427_rail_bolts.py) — the bracket that
   carries 1828 N had no M5 anywhere in it.

   **Bond the two idler bearings into their ⌀26 seats first**: a bare 10 mm axle through 6 mm of
   PETG is 15.2 MPa and will bed in, where the bearing's race spreads the same 914 N to 5.9. That
   substitution is what lets this part be printed at all. It carries three things: the 29T idler,
   the screw's upper bearing, and the motor.
6. Fit the **29T HTD-8M idler** (S2b) on the centreline at **X 0, Y 255**, supported top and bottom.
   Its axle reaction is up to **1828 N — the largest single load in the machine**, so both bearings,
   both ends, no exceptions.
7. Mount the **C6374 motor** (D5) **shaft down the limb** — turned over, hanging off the bracket's
   motor plate at Y 223…231, body Y 231…305 — with the **32T** pulley, and the **20T** on the screw.
   That is a **1:1.6 overdrive**, not 1:1 — it is what puts the total ratio at 14.5:1
   ([`404_link_ratio.py`](../scripts/404_link_ratio.py)). Close the **HTD-5M 15 mm** link belt (D6)
   over them at 61 mm centres, **under** the motor at Y 208…223, 5 mm clear of the carriage's
   proximal end at rest. **15 mm wide, and the CAD had it as 12** until
   [`433_drive_flip.py`](../scripts/433_drive_flip.py) rebuilt it to BOM D6 — which is why every
   Y above the belt moved up 3 mm from the first revision of this step.

   > **The link belt used to be on top, at Y 302…314, and the motor the other way up.** Turning the
   > motor over is what took the screw from 257 mm to 175 mm — 82 mm of SFU1620 that existed only
   > to reach a pulley above the motor, about **124 g** of steel off the thigh
   > ([`433_drive_flip.py`](../scripts/433_drive_flip.py)). It also frees the motor's rear end,
   > which is the only space in the pack the controller fits in.

7a. Bolt **`P27_ControllerMount`** to the motor's **rear bolt circle** (its face at Y 305) (4 × M5, same square as the
   front) and sit the **ODrive-clone XDRIVE MINI** on its four bosses. The board's **AS5047P** then
   looks straight down the motor's own shaft stub at the **⌀6 × 2.5 diametric magnet** (D5's
   magnet, BOM line D5) bonded to the shaft end:

   | surface | Y |
   |---|---|
   | shaft end | 307.0 |
   | magnet's outer face | 309.5 |
   | board's sensor face | 311.5 |

   → a **2.0 mm air gap**, inside the AS5047P's 0.5…3.0 mm. The mount is built to that chain, not
   to a stack-up guess ([`434_odrive_mount.py`](../scripts/434_odrive_mount.py)).

   > **MEASURE THE BOARD FIRST.** Every XDRIVE MINI dimension in the CAD — 63 × 58 outline, a
   > 55 × 50 M3 pattern, 10 mm of component height — is **guessed**. No mechanical drawing for this
   > clone is published anywhere, and the AS5047P's position on it decides whether the sensor sits
   > on the shaft's axis at all. The mount is a 20-minute reprint; the magnet bond is not.
8. Fit `P30L` (**KX-1 proximal interface**) to the bracket's top plate on its 4 × M4, with the
   6 × M5 inserts and 2 dowels facing out. It is the module interface; it does nothing in a
   single-knee build except exist for the next one.

## 3. Knee joint

9. `P1L_KneeYoke` to the lower end of the thigh spine, on **four M5 T-nuts at X ±10**, Y 70 and
   112. **Not six at X −20/0/+20** — that was the 20×60 rail's slot spacing and this is a 20×40;
   those six holes are filled. If you are working from an older print, check before drilling.

   `P2aL_KneeHub_Pulley29T` is the shank-side capstan and the 29T the main belt wraps — handle its
   tooth flanks carefully, they are printed, and they are an approximation of the HTD-8M form until
   the coupon says otherwise.
10. **Bond BOTH 6001s into `P2aL`** (K3, two off) — one at Z 96…104, one at Z 118…126, flush to
    each face of the belt land. Structural methacrylate or epoxy, each square to its face, wiped
    clean, left to cure before anything loads it. Do **not** press them in: PETG creeps under
    hoop stress and the interference is gone within months. **They are 22 mm apart and that span
    is what resists varus/valgus** — a bearing sitting cocked in its seat spends the span.
11. **The knee rod** (K2, ⌀12 × 60 ground) into `P1L`'s bore, Z 76…94, bonded, with the M4 grub
    through its heat-set insert as the mechanical backup. **It is a stub axle, not a pin**: the
    yoke is its only support and it cantilevers through both bearings. Set its depth so it ends
    at Z 130 — 1.5 mm short of `P20`'s inner face — and check it is square in two planes before
    the bond goes off. Nothing about the device is right if this is not square.
12. Swing the joint again, now loaded by the yoke: −2° to +104°. It should feel **free** — that is
    the point of the bearing. If it drags, the bearing is cocked in its seat or the pin is bent.

## 4. The main belt

13. **Thread** the **HTD-8M closed loop** (K1, 742 mm / 93T) through the gantry plate's belt tunnel
    first, then take it over the knee capstan and the idler. There is nothing to clamp and no belt
    end to terminate: the tunnel's inboard wall carries **five HTD-8M grooves at 8 mm pitch** over
    Y 144…186, and the belt's own teeth sit in them — the outboard wall at X −38.70 stops it
    backing out of mesh, the floor and roof stop it climbing. Slide the belt along until the teeth
    seat in all five grooves. The tooth phase sets the carriage's home position to within half a
    pitch, which is absorbed by homing. The loop is what makes **one** screw do both directions.
14. Tension it **by sliding the idler on its slotted mount** (K4's spring takes up bedding-in).
    The capstan loop carries up to **764 N** differential at peak torque over a 30 mm land; at the
    tunnel that is 153 N on each of the five teeth, 1.5 MPa across a 30 × 3.45 mm groove wall.
    Tension to the belt's spec, not by feel — this is the one place a slack belt looks fine and
    loses position under load.
15. Re-check the eccentrics (step 3) and run the gantry end to end by hand. **68.3 mm of stroke**,
    no binding, no belt climb.

## 5. Shank side

16. Cut the **20×20 V-slot** (A4) for the shank and clamp `P6L_ShankSocket` to it — 16 × M4. This is
    the part that transfers everything into the calf.
17. Fit `P31L_InterfaceDist` under `P6L` on its 6 × M4, dowels first. Its number is engraved on the
    **underside**, which beds on `P6L`: that is deliberate, it was the only covered face
    ([`413_mark_visibility.py`](../scripts/413_mark_visibility.py)).

## 6. Cuffs and the only parts that touch him

18. Put the **3 mm neoprene sleeves** (S5) on first, thigh and calf. They are the skin interface and
    a consumable. **Closed, dry incision only — ask whoever runs his rehab.** Neoprene contact
    dermatitis is common enough that a nylon-faced fallback is worth having on hand.
19. `P5L_ThighCuff` and `P7L_ShankCuff` on their 4 × M5 each. Both are **conical**, matched to the
    limb's taper, which is why they bear across their whole width at **12.5 and 12.2 kPa** instead of
    40 kPa on one narrow band ([`409_cuffs.py`](../scripts/409_cuffs.py)). They sit **4.00 mm** off
    the limb all over; that gap is the sleeve plus air, and it is uniform by construction.
20. Thread the **38 mm nylon webbing** (S5a) through the slots, **2:1 through the D-ring** into the
    cam buckle (S5b), with the **side-release buckle** (S5c) in the loop. Target **21 N** of strap
    tension with the neoprene on — about **12 N at your hand** through the 2:1. That is what holds
    the 3.52 N·m of roll torque the device's own mass applies.
21. **Practise the release.** Squeeze both side-release buckles; the whole device should come off in
    about two seconds. Do this before it is ever powered.

21a. **The two IMUs**, one into the pocket on each cuff's platform — thigh at Y 160, shank at
    Y −260, both on the +55° bearing — with `P28aL`/`P28bL` over them on 2 × M2.5 × 8 each.
    Run the cable out through the slot in the pocket's end.

    > **The pocket is the measurement.** Everything
    > [`441_posture.py`](../scripts/441_posture.py) computes — sitting against lying with the
    > knees up at 45°, standing against inverted at 180° — is an angle *in the sensor's own
    > frame*. The pocket's long axis runs along the limb, so the module's X is the segment's
    > axis and those numbers mean what they say. A module taped on at whatever angle the tape
    > allowed makes every one of them a guess, and the posture gate in ELECTRONICS §8a is
    > exactly as trustworthy as this step.

    Both modules go in **the same way up and the same way round**. Mark one corner of each
    before you fit them; "roll +180" is a real distinction and it is lost if one is flipped.

## 7. Fairings, last

22. `P23aL`, `P23bL`, `P23cL` into the extrusion's **posterior** side slot at Y 88, 124 and 160 —
    one M5 each, on rubber grommets (S4a), isolating rather than rigid. All three are the same part;
    they are interchangeable, which is why they share the mark `P23L`.
23. `P21L_FairingThigh` onto those three mounts, 19 × M5.
24. `P22L_DriveCap` and `P25L_MotorNacelle` — **these two are one wall split in two**, tiling the
    same shell with **zero overlap and no void between them**. P22 goes on first; the nacelle closes
    over the motor pod, and its proximal end now carries the **blister over the controller** — the
    nacelle no longer closes off at the motor's rear face, because that is where the board is
    ([`434_odrive_mount.py`](../scripts/434_odrive_mount.py)). Fit `P27L_ControllerMount` and the
    board (step 7a) **before** the nacelle goes on: there is no access to the magnet afterwards.
25. `P20L_KneeCap` over the knee. **There is no shank fairing.** `P24L_FairingShank` is deleted —
    the shank rail moved in-line under the knee joint, directly below the thigh rail, so it is
    behind the limb's own line and the socket wraps its proximal end
    ([`430_shank_inline_build.py`](../scripts/430_shank_inline_build.py)). Step 26 is what decides
    whether that is acceptable, not the fact that a fairing used to be there.
26. Check the cladding does what it is for: with everything on, no moving part should be reachable
    from the limb's side. That is verified in CAD at three poses with 187 rays
    ([`406_coverage.py`](../scripts/406_coverage.py)) and takes thirty seconds to confirm with a
    finger.

## 8. Electronics

See [`ELECTRONICS.md`](ELECTRONICS.md). In short: XDRIVE MINI / ODrive, the motor's own Hall sensors
for commutation, and an encoder for joint position. Route the motor phases and the encoder cable
**apart**, and keep the encoder cable off the belt run.

## 9. The one thing that differs between legs

**Invert the joint direction sign for the right leg.** Both legs use a right-hand ball screw, so for
a given motor direction the nut travels the same way — which means the knee goes the opposite way:

| | +motor rotation | nut travels | knee |
|---|---|---|---|
| left | + | distal | **extends** |
| right | + | distal | **flexes** |

One constant, in one place — the joint direction in firmware, or the axis map in the gait
controller. Getting this wrong drives the knee the wrong way under a 28.2 N·m assist, which is not a
subtle failure. [`700_handedness.py`](../scripts/700_handedness.py).

## 9a. Before the leg: the bench rig

Do this with the motor on the bench, not on him. [`440_bench_rig.py`](../scripts/440_bench_rig.py)
prints four parts that bolt the 6374 flange-down to a plate, put the magnet on the shaft end that
comes through it, and face the controller at it from a second plate on pillars. Nothing in it
depends on the motor having a stationary rear face — which is the exo's biggest unverified
assumption, and this is what settles it.

Three numbers come out of that session, and all three are things the CAD currently guesses:

1. **Does the 6374 have a usable stationary rear face at all?** If it does,
   `P27_ControllerMount` is right. If the rear is the rotating can, the controller has to hang
   off a cage from the front flange instead and §2's step 7a changes.
2. **The motor's bolt pattern.** The rig's eight radial slots take any square from 17 to 31 mm,
   so one print fits; measure what it actually is and put it in the BOM.
3. **The recess from the board's mounting face down to the AS5047P**, through the window in its
   backplate. That sets the air gap and nothing can derive it — the rig prints the arithmetic.

## 10. First power

In this order, with the limb out of the device:

1. ODrive motor and encoder calibration, device clamped to a bench.
2. **Unpowered** full-ROM sweep by hand. Listen for the belt and feel for a tight spot.
3. Powered, current limited to a quarter: command 10° steps across the whole range.
4. Full current, no limb, full range, and watch the knee axis for wander.
5. Only then, on the limb, with the straps at step 20's tension and a hand on the release.

---

## What is not verified

Honest list, so it is not discovered at the bench:

- **No FEA.** Hand calculations and a 107-pose interference sweep. The printed parts have margins
  computed by hand, not by simulation.
- **Nothing has been printed yet,** so the filament and time figures in [`PRINT.md`](PRINT.md) are
  models, and no hole has been tested against real hardware.
- **The motor's hip clearance is measured against nothing** — the reference limb model ends at the
  hip (Y = 300) and the motor sits there. Check it on the patient before printing the shells.
- **Acoustics are unmeasured.** Ball nut recirculation around 290 Hz is the likely source and the
  fairing the likely radiator. [`ELECTRONICS.md`](ELECTRONICS.md) §9.
- **Belt tooth-shear figures come from continuous-duty ratings** that carry high-speed fatigue
  derating. A slow capstan can run closer to the cord limit; check the actual belt's data.
