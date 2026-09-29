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
| proud of the knee skin | **80 mm** |
| knee pin | M12, SF 5.9 · PETG hub SF 3.7 |
| printed mass | structural 970 cm³ + shrouds 239 cm³ ≈ 1.54 kg PETG + 351 g rail |

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

## Guards and shrouds

| part | covers |
|---|---|
| `P20_KneeShroud` | the 180 deg belt wrap and **both nip points** - the worst pinch hazard in the machine |
| `P21_ShellAnterior` / `P22_ShellPosterior` | screw, ball nut, carriage and belt run on each side |
| `P23_DriveCover` | the twin-screw coupling at the proximal end |

The knee shroud spans 172-368 deg, overhanging each nip by 8 deg, and stands 1.88 mm clear
of the belt's outer radius. Two legs at 185 and 230 deg land on the yoke.

Fitting it needed two changes, and both were about **swept** volume rather than static shape:

- **A4's proximal end moved from Y=-45 to Y=-70.** Its inner corner used to swing at r=45,
  leaving only **3.88 mm** above the belt - no room for any guard. At -70 it swings at
  r=70.7, giving **28.9 mm** of clear annulus. The length was doing nothing: the fork bolts
  are at Y -90 to -125 and the socket engages at Y -208 to -318.
- **The yoke's disc went back to a full r=47**, with the fork outer cheek's *swept sector*
  (r 43-49, angles 241-43 deg) cut out of it. I had previously cut the disc to r=30 "to clear
  the belt wrap" - but the yoke is at Z 76-88 and the belt at Z 96-126, so radius was never
  the constraint. What actually sweeps through that annulus is the cheek.

The shells are outer wall plus top flange only - no bottom flange, since the underside faces
the limb and the thigh cuff already close it (and a bottom flange on the posterior side would
foul the cuff, which reaches X=88 at Z<=88). Each mounts into the rail's side slot at Y
positions that side's carriage never reaches: A at Y 238-278 (it travels 61-231), B at
Y 64-104 (it travels 112-283).

No inboard side plate on the knee shroud: that gap is only 2 mm - the fork cheek tops out at
Z=94 and the belt starts at Z=96 - and the pulley at r<=35.6 plus the cheek already close it.

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
