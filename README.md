# Powered knee orthosis — belt capstan with differential lead screws

A 3D-printed knee exoskeleton for a post-operative patient who is a year out from
surgery and struggling with walking and stairs. Parametric FreeCAD model, driven and
verified entirely from scripts.

> **Not a validated medical device.** No FEA has been run — every number below is a hand
> calculation. Cuffs are sized nominally for 1.75 m / 80 kg. Do not fit this to anyone
> without a clinician in the loop and a bench test under the loads listed.

## What it does

Targets **~30% assist of peak biological knee moment**: stair ascent 1.05 N·m/kg,
descent 1.15, sit-to-stand 1.20 — so **28.2 N·m** at 80 kg. Range of motion −2° to 104°.

## Current architecture

A **belt capstan** at the knee driven by **two opposed lead screws**:

- **29T HTD-8M pulley** concentric with the knee pin, integral with the shank hinge fork
- **180° belt wrap**, both runs parallel to the thigh rail at X = ±36.9
- **Two carriages** on one 20×60 V-slot rail, one per belt run, moving in *opposite*
  senses via **right-hand and left-hand SFU1620 screws on a common shaft**
- **Delrin L-gib sliders** — one tongue in the rail's outboard slot, one in the side slot
- 6374 BLDC + ODrive

### Why the differential is exact, not approximate

Belt length is `Ya + πR + Yb = const`. With a fixed 180° wrap that reduces to
`Ya + Yb = const`. Two equal-pitch LH/RH screws on one shaft give exactly `dYa = −dYb`.
That **is** the constraint — verified constant at 242.00 mm across all 107 poses.

This only works because both runs are parallel. With an angled run, `Ya + Yb` is
nonlinear and the two rigid screws fight the belt.

### Key figures

| | |
|---|---|
| moment arm | 36.92 mm, **constant at every angle** |
| belt tension | 764 N + 150 N pretension |
| motor | 0.70 N·m, 16 A |
| carriage travel | 68.3 mm each, opposed |
| proud of the knee skin | **86 mm** with fairings (80 mm bare) |
| knee pin | M12, SF 5.9 · PETG hub SF 3.7 |
| printed mass | structural 967 cm³ + fairings 275 cm³ ≈ 1.38 kg PETG + 351 g rail |

## Verification

`scripts/vlow.py` runs a **full pairwise interference sweep with no skip list** — 107
poses, every part against every other, in six chunks (the sweep exceeds FreeCAD's 90 s
GUI dispatch limit in one call). Current state: **zero hard-part clashes**. The only
remaining overlaps are the reference limb cones intersecting each other and 0.84 cm³ of
thigh-cuff foam compression.

A skip list hid six real clashes earlier in this project, including a carriage bore cut
along the wrong axis and a telescoping joint that did not telescope. Do not reintroduce one.

## Architecture history

Each was built and measured, not discarded on paper:

| approach | why it was dropped |
|---|---|
| Single rigid rod + rod ends to a clevis | Clevis joint put **1269 N of tension** on two M5 T-nuts (SF 1.16). Load crossed two bolted joints over a 75 mm path. |
| Pure belt drive, motor→knee | Single stage cannot give the ratio: 65T/14T = 4.67:1 needs 6.04 N·m from a motor that peaks at 3.5. |
| Screw + belt + constant-force spring | Spring was 119 N of pure loss; unpowered 4.2 N·m flexion bias; tooth skip loses position permanently. |
| C-Beam 80×40 rail | Belt cannot pass beside it — runs are 71 mm apart and the half-width is 40 mm — so the belt had to be **lifted**, giving a 57 mm hub cantilever: **M10 pin at 633 MPa (SF 1.01) and the PETG hub at SF 0.51, failing**. |

Two findings worth keeping:

- **The seat law.** Any shank point swings to roughly its own radius posteriorly at 90°
  flexion. That caps the rod pivot radius and is why a pulley of R ≤ 52 never protrudes
  behind the knee when sitting, while the old rod pivot at R = 74.7 did.
- **Both belt runs leave the pulley proximally, so their tensions add** — 1091 N net into
  the knee pin. This is what made the lifted-belt layout fail.

## Belt tension cannot be servo-controlled

The shaft fixes `Ya + Yb`, so turning the motor changes tension not at all — there is no
control authority, and no sensor can close that loop. Pretension is also invisible at the
motor: it pulls both carriages distally and opposite screw hands cancel the torques.

Worse, the differential is **too stiff to hold pretension**: 150 N is only 0.27–0.53 mm of
belt stretch, while a new HTD belt beds in 0.7–1.8 mm. So carriage B carries a **sprung
anchor** — 3 mm travel at ~500 N/mm, which absorbs bedding-in in 1/20th the travel the
constant-force drum needed. Lost motion 1.58 mm = 2.45° of knee, and a Hall sensor on the
slide reads its deflection as **live belt tension**.

## Fairings

| part | covers |
|---|---|
| `P20_KneeCap` | closed nose over the pulley and the 180 deg belt wrap, including both nip points |
| `P21_FairingThigh` | one canopy Y 28..312 over screws, nuts, carriages, belt runs and the coupling |
| `P24_FairingShank` | the shank member below the knee |

Sections are **superellipses at exponent 5.5** - a rounded rectangle, not a slab. The thigh
fairing flares 58 -> 84 mm half-width over Y 28..58 on a smoothstep, carries 8 vent slots,
and mounts on a **central spine into the rail's middle outboard slot at X=0** - the one
channel nothing else uses (the carriages take X=+/-20 outboard and X=+/-30 side), so the
mounts are never swept. The knee pin head is recessed **flush** into the hub at Z=126.

The enabling fact: the pulley's *inside* is what swings. Measured, nothing moving occupies
r 41..70 at Z 96..126, and nothing at all sits above Z=126 once the pin is recessed - so the
belt and the pulley's outer face can be fully enclosed by static covers tied into the thigh
fairing.

Two changes were needed first, both about **swept** volume rather than static shape:

- **A4's proximal end moved from Y=-45 to Y=-70.** Its inner corner swung at r=45, leaving
  only 3.88 mm above the belt. At -70 it swings at r=70.7, giving **28.9 mm**. The length was
  doing nothing: the fork bolts are at Y -90..-125, the socket engages at -208..-318.
- **The yoke's disc went back to a full r=47** with the fork outer cheek's *swept sector*
  (r 43-49, angles 241-43 deg) cut out. An earlier r=30 was cut "to clear the belt wrap", but
  the yoke is at Z 76-88 and the belt at Z 96-126 - radius was never the constraint.

### Three modelling traps worth recording

1. **Spline lofts overshoot.** `makeLoft(..., ruled=False)` bulged sections to X +/-129 instead
   of +/-83 and self-intersected. Use `ruled=True` with closer stations.
2. **A superellipse narrows in Z at its X extremes.** Containing a box of half-size (W,H)
   needs `(W/a)^n + (H/b)^n <= 1`. At n=3.4, b=22 the carriage needed **a=108**; a=80 was used,
   so carriages, cuff, rail and belt all poked through the walls - eight clashes, one cause.
3. **An inner loft must overrun the outer at both ends**, or `outer - inner` leaves a closed
   end wall. Setting the shank fairing's inner to start at Y=-102 (distal of the outer's -100)
   produced a wall A4 passed straight through - a constant 0.441 cm3 at every pose, which is
   the signature of a static error rather than a sweep problem.

### Limits

The fairing is **open below Z=92**: the thigh cuff tops out at 88 and the carriage bottom is
at 90, so there is no room for a wall between them. The underside faces the limb.

The shank fairing **cannot start closer than Y=-100**. A shell from -66 swings to world
X 57.7..70.3 at 104 deg, where the thigh fairing is already 63.5 wide. So **Y -45..-100 is a
moving gap that no rigid part can bridge** - that needs a fabric gaiter, standard orthotic
practice. The motor at the hip is also uncovered.

## Sensing

- **Knee reference** — magnet in the fork cheek at (0, −25), Hall in the yoke disc. Both
  at Z ≤ 91, so it costs **zero lateral build**. Reads at 30° flexion.
- **Tooth-skip detection** — one tooth is 8 mm of belt = **12.9° of knee angle**. Compare
  the knee reference against screw position; a skip is unmissable. This is the monitor for
  the failure mode that matters (sudden loss of assist mid-stair).
- **Endstops** — magnet pockets in each carriage's side wall. Hard limits plus
  auto-*calibration* of the screw↔knee map. They do not, and cannot, tension anything.

## Layout

```
model/       FreeCAD source (internal document name is KneeExo_v4)
stl/         printed parts (PETG) and Delrin slider stock
kinematics/  kin_low.json — current pose law; legacy slider-crank solution kept for reference
scripts/     chronological build and verification scripts, run over FreeCAD's XML-RPC
```

`scripts/fc.py` is the FreeCAD client (`PORT = 9880`). Scripts are numbered in the order
they were run; the live chain for the current design is **194 → 195 → 196 → 197**, then
`vlow.py` to verify, `198_anim.py` to animate and `199_stl.py` to export. Earlier numbers
are the design history, including the rejected architectures above.

Two FreeCAD gotchas that cost real time, both worth reading before editing geometry:

1. `obj.Shape` returns geometry **with placement applied**. A read-modify-write while a
   part is posed bakes the pose in. Stop any animation timer and zero every placement first.
2. A boolean that severs a part returns a *valid* shape with `len(Shape.Solids) > 1`
   rather than an error. Always assert `solids == 1 and isClosed()` after cutting.

## Open items

- No FEA. Hand calculations only.
- The motor sits at the hip, where the reference limb model ends (Y = 300) — its 100 mm
  clearance is measured against nothing and needs a fitting check on the patient.
- Printed mass **1.54 kg** is the largest unresolved issue. `P2a` (145 cm³), `P5` (167 cm³),
  `P6` (165 cm³) and `P1` (131 cm³) are the structural candidates. The 239 cm³ of shrouds
  should print at 2 walls / low infill - nearer 130 g than 303 g - since they carry no load.
- Knee reference is single-point, not continuous. A full absolute encoder needs the pin's
  outboard end and ~6 mm more lateral.
- Belt tooth-shear figures are from continuous-duty power ratings, which carry fatigue
  derating for high-speed running. A slow capstan can run closer to the cord limit —
  check against the actual belt's data before committing.
- ODrive firmware and control not written.
- The rendered assembly video in the project history shows the **retired rigid-rod**
  architecture and is not included here.
