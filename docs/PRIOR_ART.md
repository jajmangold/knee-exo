# What everyone else is actually doing

Surveyed September 2026. The short version: **the field has converged on quasi-direct
drive at the joint**, and this design already sits inside that band without having set out
to. The interesting finding is not that remote actuation is wrong — it is that the two
problems this project has been circling (torque sensing, and reflected inertia) have a
different answer than the one it was heading towards.

---

## 1. Quasi-direct drive is the current paradigm

High torque-density motor, **low** gear ratio, mounted at the joint. Backdrivability comes
from the ratio being small, not from a spring, a cable or a clutch.

| | Ratio |
|---|---|
| Soft exosuit, Bowden-driven | ~50 : 1 |
| QDD hip exo, custom planetary | 36 : 1 |
| **This design — SFU1610 screw + capstan** | **23.2 : 1** |
| QDD knee | 9 : 1 |
| QDD ankle | 8 : 1 |

Published QDD performance to benchmark against:

| | Mass | Nominal torque | Backdrive | Bandwidth |
|---|---|---|---|---|
| QDD hip exo | 3.4 kg | 17.5 N·m | 0.40 N·m | 62.4 Hz |
| QDD cable knee exo | — | — | 2.58 N·m peak resistance | — |
| conventional knee exo they benchmark against | — | — | 8.0 N·m | — |
| **this design** | 4.66 kg | 28.2 N·m | see below | not modelled |

Torque density is comparable — 6.1 N·m/kg here against 5.1 for the QDD hip. The gap is
elsewhere.

## 2. The finding that matters: QDD needs no torque sensor

> "Assistive torque control in QDD systems is achieved through **proprioceptive sensing
> instead of torque sensors**."

At a low enough ratio, transmission friction is small next to the torque being commanded,
so **motor current is a good enough measurement of joint torque**. No load cell, no series
spring, no strain gauge.

That answers a question this project spent a while on. The load cell was only ever needed
because a Bowden sheath sits between the motor and the joint and eats 20–30% of the
tension in a posture-dependent way. Keep the actuator on the limb and the problem does not
exist — which is a strong argument for *not* going remote.

## 3. Bowden friction is managed, not solved

The literature is candid: nonlinear friction between inner cable and sheath is "a major
source of hysteresis and phase delay", and cable systems "suffer from mechanical losses
due to friction, cable stretch, and hysteresis ... and require periodic maintenance".

The responses are all mitigations:

- **Learning-based repetitive control** — iterative learning that adapts the reference
  trajectory to cancel hysteresis without modelling it. Works because gait is periodic.
- **Loop routing** — reduces the effect of bending, at the cost of *higher* total friction.
- **Redirection pulleys** instead of sheath bends — lower friction, more mechanical
  complexity.

Nobody has made it go away. `scripts/340_tendon.py` in this repo computes 78% → 69%
efficiency as the hip flexes, which is consistent with all of the above.

## 4. What shipped commercially: motors at the knee

**Arc'teryx × Skip MO/GO** — a Google X spinout, four years of development, $5,000, sold as
"the world's first powered clothing". Motors **at the knees**, carbon-fibre structure
distributing load along the leg, ~40% boost walking uphill, three hours of hard uphill at
maximum assist, and it **regenerates on the descent**.

Two things to take from that:

- The commercial answer for a knee is joint-mounted, not remote — and they note the knee is
  the harder joint to do, which is why most products target the hip.
- Regenerating downhill is treated as a feature, not a hazard. This repo's
  `docs/ELECTRONICS.md` §6 reaches the same conclusion from the other direction: with
  LiFePO4 and a low-temperature cutoff the pack will sometimes refuse that energy, so the
  brake resistor is mandatory.

## 5. Where this design is actually weak

Not torque density, and not the architecture. It is **reflected inertia**, and it comes
straight from the 23.2 : 1 being at the top of the QDD band rather than the bottom:

| Knee swing acceleration | Torque from reflected inertia | Limb alone |
|---|---|---|
| 30 rad/s² | 5.0 N·m | 9.0 N·m |
| 60 rad/s² | 10.0 N·m | 18.0 N·m |
| 129 rad/s² (60° in 0.2 s) | **21.5 N·m** | 38.7 N·m |

Static backdrive is fine — about 1.8 N·m, and most of that is motor cogging multiplied by
the ratio. It is the dynamic term that hurts, and it is 0.56× the limb's own inertia at
every acceleration.

The published backdrive figures above are low-speed resistance measurements and are not
directly comparable, but the direction is clear.

## 6. So what would actually improve this device

In order of leverage:

1. **Lower the ratio.** 23.2 → 9 would cut reflected inertia by 6.6× (0.167 → 0.025 kg·m²)
   and put it at QDD-knee values. It costs motor torque: 1.39 → 3.6 N·m, which a 6374 at
   149 Kv cannot hold (it would need ~56 A). **The field buys this with motor torque
   density, not with transmission cleverness** — large-diameter, many-pole pancake motors.
   That is the change that would most improve this design, and it is a motor selection
   problem, not a mechanism problem.
2. **Keep the actuator on the limb.** It is what the commercial product does, it removes
   the need for any torque sensor, and it avoids a failure mode the literature has spent
   fifteen years managing rather than fixing.
3. **Measure backdrive on the bench** before trusting any of the above. Nothing in this
   repository has been measured on hardware.

---

## Sources

- [Quasi-Direct Drive Actuation for a Lightweight Hip Exoskeleton with High Backdrivability and High Bandwidth](https://arxiv.org/pdf/2004.00467) — Su et al., arXiv
- [A Quasi-Direct-Drive Cable Actuation System for an Intrinsically Safe Knee Exoskeleton](https://haosu-robotics.github.io/images/Paper/AQuasiDirectDriveCableActuationSystemforAnIntrinsicallySafeKneeExoskeleton.pdf)
- [Design and Validation of a Modular, Backdrivable Ankle Exoskeleton (M-BLUE)](https://pmc.ncbi.nlm.nih.gov/articles/PMC11548846/) — Zhao, Walters, Gregg
- [Design and Control of a Quasi-Direct Drive Soft Hybrid Knee Exoskeleton](https://arxiv.org/pdf/1902.07106)
- [Learning-Based Repetitive Control of a Bowden-Cable-Actuated Exoskeleton with Frictional Hysteresis](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9611146/)
- [Mechanical design and friction modelling of a cable-driven upper-limb exoskeleton](https://www.sciencedirect.com/science/article/pii/S0094114X22000234)
- [Series-elastic actuator with two degree-of-freedom PID control improves torque control in a powered knee exoskeleton](https://www.cambridge.org/core/journals/wearable-technologies/article/serieselastic-actuator-with-two-degreeoffreedom-pid-control-improves-torque-control-in-a-powered-knee-exoskeleton/FBEBF3966808F9AC51138792D3B6BF10)
- [Arc'teryx × Skip MO/GO powered pants](https://gearjunkie.com/apparel/arcteryx-skip-mogo-exoskeleton-pants) — GearJunkie
- [Skip and Arc'teryx exoskeleton pants](https://newatlas.com/technology/skip-arcteryx-powered-pants/) — New Atlas
