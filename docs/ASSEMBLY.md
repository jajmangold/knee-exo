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
| Drill 5.3 | every ⌀5.2 — `P1`, `P2a`, `P5`, `P7`, `P21` (19), `P23a/b/c`, `P24` |
| **Ream** 5.0 H7 | the ⌀5.0 dowel holes in `P30` and `P31` — these set the interface alignment, so ream, do not drill |
| Ream 12.3, on a drill press | the ⌀12.3 knee-pin holes in **`P2a`** (the hub). This is the joint axis; a hole drilled crooked by hand becomes a knee that binds at one end of its travel |
| **Bore 28.2, on a drill press** | the ⌀28 bearing seat in **`P1_KneeYoke`**. 28.2 rather than 28.0 deliberately: the 6001 is **bonded**, not pressed, and 0.1 mm is the bond line |
| Melt in M5 heat-set inserts | the ⌀6.4 holes — 4 in `P6`, 6 each in `P30` and `P31`. Leave the holes as printed; an M5 insert is ⌀7.0 and wants 6.4 |
| Leave alone | the ⌀10.4 counterbores on `P5` and `P7` — the cap heads sit in them |

Then dry-fit the knee: `P1L` and `P2aL` on the pin — **bearing not yet bonded** — no belt, and swing
it. It must move freely through **−2° to +104°** with no tight spot. Fix that here, not later: once
the 6001 is bonded in, getting back out of the seat means destroying the bearing.

Full table: [`scripts/417_fastener_audit.py`](../scripts/417_fastener_audit.py), 102 holes.

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
4. Mount the **ball screw** (D1, SFU1610 RH, 330 mm) on its axis at **X = −62**: the **KP08** (D8)
   at the lower end, and at the upper end a **608-2RS bonded into the bracket's ⌀32 × 12 screw
   boss** at Y 286…298 (D8a). The nut (D3) is **flangeless and trapped axially** between two plates
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
   extrusion. **Bond the two idler bearings into their ⌀26 seats first**: a bare 10 mm axle through
   6 mm of PETG is 15.2 MPa and will bed in, where the bearing's race spreads the same 914 N to
   5.9. That substitution is what lets this part be printed at all. It carries three things:
   the 29T idler, the screw's upper bearing, and the motor.
6. Fit the **29T HTD-8M idler** (S2b) on the centreline at **X 0, Y 255**, supported top and bottom.
   Its axle reaction is up to **1828 N — the largest single load in the machine**, so both bearings,
   both ends, no exceptions.
7. Mount the **C6374 motor** (D5) with the **32T** pulley, and the **20T** on the screw. That is a
   **1:1.6 overdrive**, not 1:1 — it is what puts the total ratio at 14.5:1
   ([`404_link_ratio.py`](../scripts/404_link_ratio.py)). Close the **HTD-5M 15 mm** link belt (D6)
   over them at 61 mm centres.
8. Fit `P30L` (**KX-1 proximal interface**) to the bracket's top plate on its 4 × M4, with the
   6 × M5 inserts and 2 dowels facing out. It is the module interface; it does nothing in a
   single-knee build except exist for the next one.

## 3. Knee joint

9. `P1L_KneeYoke` to the lower end of the thigh spine. `P2aL_KneeHub_Pulley29T` is the shank-side
   capstan and the 29T the main belt wraps — handle its tooth flanks carefully, they are printed.
10. **Bond the 6001 into `P1L`'s seat** (K3) — structural methacrylate or epoxy, bearing square to
    the face, wiped clean, left to cure before anything loads it. Do **not** press it in: PETG
    creeps under hoop stress and the interference is gone within months.
11. **Knee pin** (K2 — ISO 7379 12 × 70 shoulder screw, or an ISO 8734 ⌀12 × 70 dowel) through
    `P2aL`'s lower lug, the bearing's bore, and `P2aL`'s upper lug, into the flush counterbore.
    The collars clamp the **hub** to the pin; the bearing is the only thing that rotates. Nothing
    about the device is right if this is not square.
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

## 7. Fairings, last

22. `P23aL`, `P23bL`, `P23cL` into the extrusion's **posterior** side slot at Y 88, 124 and 160 —
    one M5 each, on rubber grommets (S4a), isolating rather than rigid. All three are the same part;
    they are interchangeable, which is why they share the mark `P23L`.
23. `P21L_FairingThigh` onto those three mounts, 19 × M5.
24. `P22L_DriveCap` and `P25L_MotorNacelle` — **these two are one wall split in two**, 160.9 + 85.0
    cm³ tiling the same shell with **zero overlap and no void between them**. P22 goes on first; the
    nacelle closes over the motor pod.
25. `P20L_KneeCap` over the knee, `P24L_FairingShank` over the shank rail.
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
