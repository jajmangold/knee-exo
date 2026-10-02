# -*- coding: utf-8 -*-
"""Could a 250 W hoverboard hub motor and belts replace the ball screw entirely?

Short answer: yes, the screw can go -- but NOT with teeth glued to the rim, and the reason is
kinematic rather than structural. Everything below is arithmetic on the project's own targets
(300_drivetrain.py) plus hub-motor numbers that are typical for a 6.5 inch wheel and MUST be
measured on the actual hardware before any of it is trusted. Every assumed number is marked.

THE TRAP. On a hoverboard wheel the OUTER SHELL rotates and the axle is the stator mount -- it is
an outrunner with the stator on the axle. So the rotating output is the rim, at ~140 mm diameter
once the airless tyre is off. A belt stage multiplies torque only when the driven pulley is LARGER
than the driver, so a 140 mm driver needs a 140 x N mm driven pulley for a reduction of N:

    3:1 from the rim  ->  420 mm pulley at the knee

which is two and a half times the width of the thigh. Glue teeth to the rim and each belt stage is
a speed INCREASE, not a reduction. A two-stage system can still reduce, but only by routing through
an intermediate shaft carrying a big pulley in and a small one out -- and then the big one is the
problem, not the small one.

WHAT WORKS INSTEAD. Put the small pulley on the motor, where a reduction wants it. The rotor's flat
outer FACE can carry an annular pulley bolted through the shell's own assembly screws, as small as
the centre boss allows -- call it 60-70 mm pitch diameter around a 12 mm axle and its bearing boss.
From there a single stage to a large knee pulley gives a real reduction inside the envelope the
device already has: the knee shroud is at r 130, so a 180 mm pulley at r 90 fits with room.

Run:  freecadcmd.exe scripts/800_hubmotor.py      (no document needed, this is arithmetic)
"""
import math

# ------------------------------------------------------------------ the targets, from 300
TAU_PEAK = 28.2                 # N.m at the knee, peak -- 29% of an 80 kg stair-ascent moment
W_CONT = math.radians(180.0)    # rad/s, stair cadence
W_PEAK = math.radians(300.0)    # rad/s, free swing
J_LIMB = 0.30                   # kg.m2, shank + foot about the knee
ROM = 106.0                     # deg
KNEE_ENV_R = 130.0              # mm, the knee shroud's outer radius -- what a pulley must live in
THIGH_HALF = 84.0               # mm, the thigh fairing's half width

# ------------------------------------------- the hub motor: ASSUMED, measure before believing
# Typical 6.5 inch hoverboard wheel, 36 V, "250 W". The label is nearly meaningless; what matters
# is Kt, phase resistance and how much heat a sealed aluminium shell with no airflow can lose.
KV_RPM_V = 16.0                 # ASSUME rpm/V  -- measure: spin it, scope the phase voltage
R_PHASE = 0.40                  # ASSUME ohm, line-to-line/2 -- measure with a milliohm meter
I_CONT = 10.0                   # ASSUME A, thermally continuous in a sealed hub
I_PEAK = 30.0                   # ASSUME A, ~10 s bursts
MASS_HUB = 2.7                  # ASSUME kg with the tyre off -- weigh it
RIM_PD = 140.0                  # ASSUME mm, rim diameter with the airless tyre removed -- measure
FACE_PD = 65.0                  # mm, the smallest annular pulley that clears the axle boss
J_ROTOR = 1.2 * 0.060 ** 2      # ASSUME kg.m2: ~1.2 kg of shell and magnets at r 60 mm
COG = 0.35                      # ASSUME N.m of cogging -- measure by hand, it is easy to feel

KT = 9.5493 / KV_RPM_V          # N.m/A
TAU_MOT_CONT = KT * I_CONT
TAU_MOT_PEAK = KT * I_PEAK
RPM_NOLOAD_36 = KV_RPM_V * 36.0

print("=" * 94)
print("A HOVERBOARD HUB MOTOR INSTEAD OF THE SCREW")
print("=" * 94)
print("  ASSUMED hub motor (6.5 in, 36 V): Kv %.0f rpm/V -> Kt %.3f N.m/A, R %.2f ohm, %.1f kg"
      % (KV_RPM_V, KT, R_PHASE, MASS_HUB))
print("    torque    %.1f N.m continuous at %.0f A,  %.1f N.m peak at %.0f A"
      % (TAU_MOT_CONT, I_CONT, TAU_MOT_PEAK, I_PEAK))
print("    copper    %.0f W at continuous, %.0f W at peak (sealed shell, no airflow)"
      % (3 * (I_CONT / math.sqrt(2)) ** 2 * R_PHASE, 3 * (I_PEAK / math.sqrt(2)) ** 2 * R_PHASE))
print("    no-load   %.0f rpm at 36 V = %.0f deg/s at the shell"
      % (RPM_NOLOAD_36, RPM_NOLOAD_36 * 6.0))
print("    the knee needs %.0f deg/s continuous and %.0f deg/s peak, so speed is never the"
      % (math.degrees(W_CONT), math.degrees(W_PEAK)))
print("    constraint below about 8:1 -- this motor is torque-poor and speed-rich for the job.")

# ------------------------------------------------------------------ the kinematic inversion
print()
print("=" * 94)
print("1.  WHY TEETH ON THE RIM GIVE A SPEED-UP, NOT A REDUCTION")
print("=" * 94)
print("  The rim rotates and the axle is fixed, so the rim is the DRIVER at %.0f mm PD."
      % RIM_PD)
print("  A stage reduces only when driven > driver, so for a reduction N the knee pulley is")
print("  %.0f x N mm:" % RIM_PD)
print()
print("    %-10s %-16s %s" % ("ratio", "knee pulley PD", "fits inside the knee shroud at r 130?"))
for n in (1.0, 1.5, 2.0, 3.0, 5.0, 9.0):
    pd = RIM_PD * n
    fits = "yes, r %.0f" % (pd / 2) if pd / 2 <= KNEE_ENV_R else "NO, r %.0f vs 130" % (pd / 2)
    print("    %-10.2f %-16.0f %s" % (n, pd, fits))
print()
print("  So one stage off the rim tops out at %.2f:1 before the pulley leaves the existing"
      % (2 * KNEE_ENV_R / RIM_PD))
print("  envelope, and a second stage off a %.0f mm driver needs a %.0f mm driven to double"
      % (RIM_PD, RIM_PD * 2))
print("  again. Two stages CAN reduce -- big-in, small-out on an intermediate shaft -- but the")
print("  big-in pulley is then %.0f mm on a %.0f mm wide thigh. That is the wall."
      % (RIM_PD * 1.4, 2 * THIGH_HALF))

# ------------------------------------------------------------------ architectures
print()
print("=" * 94)
print("2.  WHAT EACH ARCHITECTURE ACTUALLY DELIVERS")
print("=" * 94)
print("  %-34s %5s %8s %8s %9s %8s %s"
      % ("architecture", "ratio", "cont", "peak", "reflect J", "cog@knee", "verdict"))
ARCH = [
    ("direct drive, motor AT the knee", 1.0, "no belt at all: shell to thigh, axle to shank"),
    ("one stage, rim %.0f -> knee %.0f" % (RIM_PD, 2 * KNEE_ENV_R),
     2 * KNEE_ENV_R / RIM_PD, "biggest knee pulley the shroud allows"),
    ("one stage, face %.0f -> knee 180" % FACE_PD, 180.0 / FACE_PD,
     "annular pulley bolted to the rotor face"),
    ("one stage, face %.0f -> knee 240" % FACE_PD, 240.0 / FACE_PD,
     "same, at the envelope limit"),
    ("two stage via intermediate shaft", 9.5, "140->200 then 30->200, both stages inside"),
]
for name, n, note in ARCH:
    cont, peak = TAU_MOT_CONT * n * 0.97, TAU_MOT_PEAK * n * 0.97
    jr = J_ROTOR * n * n
    verdict = "PEAK MET" if peak >= TAU_PEAK else "%.0f%% of peak" % (100 * peak / TAU_PEAK)
    print("  %-34s %5.2f %6.1f Nm %5.1f Nm %6.3f %-3s %5.2f Nm  %s"
          % (name, n, cont, peak, jr, "(%.2fx)" % (jr / J_LIMB), COG * n, verdict))
    print("       %s" % note)

# ------------------------------------------------------------------ what the screw costs today
print()
print("=" * 94)
print("3.  WHAT DELETING THE SCREW TRAIN SAVES, AND WHAT THE HUB COSTS")
print("=" * 94)
# masses from the model: steel 7.85, aluminium 2.70, PETG 1.27 g/cm3
OUT = [("A2 ball screw SFU1610, 244 mm", 47.8 * 7.85),
       ("A2b ball nut + balls", 33.1 * 7.85),
       ("A6 idler 29T, aluminium", 119.1 * 2.70),
       ("A7 drive bracket, aluminium", 286.0),
       ("P3 gantry plate, aluminium", 192.0),
       ("A3 motor C6374 + mount", 850.0),
       ("P22 + P25 drive shells, PETG", (160.9 + 85.0) * 1.27),
       ("P10a-d V-wheels", 4 * 15.0),
       ("A5/A5b/A5c/A5d HTD-8M belt run", 60.0)]
IN_ = [("hub motor, tyre off", MASS_HUB * 1000.0),
       ("knee pulley, 180 mm PETG ring", 150.0),
       ("rotor-face pulley adapter, alu", 80.0),
       ("belt + tensioner", 60.0),
       ("new shroud over the hub, PETG", 220.0)]
so = sum(m for _, m in OUT)
si = sum(m for _, m in IN_)
for lbl, m in OUT:
    print("  -  %-36s %7.0f g" % (lbl, m))
print("     %-36s %7.0f g deleted" % ("", so))
print()
for lbl, m in IN_:
    print("  +  %-36s %7.0f g" % (lbl, m))
print("     %-36s %7.0f g added" % ("", si))
print()
print("  net %+.0f g. The screw train is not the heavy part -- the MOTOR is, on both sides, and"
      % (si - so))
print("  a hub motor is %.1f kg against the 6374's %.2f kg. What you actually buy is the"
      % (MASS_HUB, 0.85))
print("  deletion of the whole linear train: screw, nut, rail, carriage, four V-wheels, the")
print("  belt run and the 152 mm of stroke they exist to produce.")

# ------------------------------------------------------------------ the real arguments
print()
print("=" * 94)
print("4.  THE ARGUMENTS THAT ARE NOT ABOUT TORQUE")
print("=" * 94)
LEAD, SCREW_D = 10.0, 16.0
lead_ang = math.degrees(math.atan(LEAD / (math.pi * SCREW_D)))
print("  BACKDRIVING. The screw is at an %.1f deg lead angle, which is backdrivable, but the"
      % lead_ang)
print("  patient feels it through a 14.5:1 ratio: reflected inertia 0.065 kg.m2, 0.22x the limb's")
print("  own. A belt-only train at %.1f:1 reflects %.3f kg.m2, %.2fx the limb -- "
      % (180.0 / FACE_PD, J_ROTOR * (180.0 / FACE_PD) ** 2,
         J_ROTOR * (180.0 / FACE_PD) ** 2 / J_LIMB))
print("  the low ratio is doing that, not the motor. Direct drive reflects %.3f kg.m2 (%.3fx):"
      % (J_ROTOR, J_ROTOR / J_LIMB))
print("  power off, the knee is essentially free. That is the best thing the hub offers -- but")
print("  section 6 is what decides the architecture, and it goes the other way: the ratio that")
print("  makes a train transparent is the same ratio that makes it expensive to hold a load.")
print()
print("  COGGING cuts the other way, and it is why a big ratio is not simply better. %.2f N.m"
      % COG)
print("  of cogging at the rotor becomes %.2f N.m at %.1f:1 and %.2f N.m at 9.5:1 -- the second"
      % (COG * 180.0 / FACE_PD, 180.0 / FACE_PD, COG * 9.5))
print("  is %.0f%% of peak assist, felt as notches when the patient moves the joint themselves."
      % (100 * COG * 9.5 / TAU_PEAK))
print()
print("  NOISE AND WEAR. A ball screw at 300 deg/s knee speed turns at %.0f rpm and whines;"
      % (math.degrees(W_PEAK) / 360.0 * 60 * 14.5))
print("  it also needs grease and keeps a wiper seal clean on a device worn at ankle height.")
print("  Belts need neither. Against that: belts need tension, and tension needs a tensioner")
print("  that holds %.0f N on a 180 mm pulley at peak torque." % (TAU_PEAK * 1000 / 90.0))
print()
print("  PRINTED TEETH are fine mechanically, wherever they go. At peak the belt carries")
T_BELT = TAU_PEAK * 1000.0 / 90.0
print("  %.0f N. On a 180 mm HTD-5M pulley that is %.0f teeth in mesh at 180 deg wrap, so"
      % (T_BELT, 180.0 * math.pi / 5.0 / 2))
print("  %.1f N per tooth; a 15 mm wide PETG tooth shears at ~%.0f N. The weak point is never"
      % (T_BELT / (180.0 * math.pi / 5.0 / 2), 15 * 2 * 25.0))
print("  the tooth, it is how the toothed ring is attached: BOLT it through the rotor's own")
print("  assembly screws rather than gluing, and the %.1f N.m at the rotor face is %.0f N on a"
      % (TAU_MOT_PEAK, TAU_MOT_PEAK * 1000 / 30.0))
print("  4-bolt circle at r 30 -- %.0f N per M4, trivial. Epoxy alone on an anodised rim is the"
      % (TAU_MOT_PEAK * 1000 / 30.0 / 4))
print("  one joint in this whole idea with no inspectable failure mode.")

# ------------------------------------------------------------------ verdict and measurements
print()
print("=" * 94)
print("5.  SO: CAN THE SCREW GO?")
print("=" * 94)
best = 180.0 / FACE_PD
print("  Yes -- with one belt stage, not two, and with the small pulley on the MOTOR rather than")
print("  teeth on the rim. Face pulley %.0f mm -> knee pulley 180 mm is %.2f:1, which gives"
      % (FACE_PD, best))
print("  %.0f N.m continuous and %.0f N.m peak against the %.1f N.m target, inside the knee"
      % (TAU_MOT_CONT * best * 0.97, TAU_MOT_PEAK * best * 0.97, TAU_PEAK))
print("  envelope that already exists, with %.2fx the limb's inertia reflected instead of 0.22x."
      % (J_ROTOR * best * best / J_LIMB))
print("  It deletes the screw, the nut, the rail, the carriage, the V-wheels and the 1:1.6 link")
print("  belt, and it costs about %.1f kg net and a cogging notch of %.2f N.m."
      % ((si - so) / 1000.0, COG * best))
print()
print("  Direct drive -- shell bolted to the thigh, axle to the shank, no belt at all -- is the")
print("  most elegant version and reflects almost nothing, but at %.0f N.m peak it is %.0f%% of"
      % (TAU_MOT_PEAK, 100 * TAU_MOT_PEAK / TAU_PEAK))
print("  the assist this device was sized for. That is a different device, not a cheaper one.")
print()
print("  SIX MEASUREMENTS DECIDE IT, and every number above is a guess until they exist:")
for i, m in enumerate([
        "rim diameter with the tyre off, and whether the rim surface is cylindrical",
        "shell OD and axial width, and the mass on a kitchen scale",
        "Kv: spin the wheel by hand at a known rpm and scope one phase (or let ODrive calibrate)",
        "phase resistance, line to line, with a milliohm meter -- this sets the thermal limit",
        "cogging: turn it slowly by hand against a luggage scale on a known radius",
        "whether the rotor's end face has a usable bolt circle, and the axle flat dimensions"]):
    print("    %d. %s" % (i + 1, m))
print()
print("  And one caution that is not mechanical: a hoverboard hub has 15 pole pairs and Hall")
print("  sensors only. Hall commutation gives 6 states per electrical revolution, which is 90")
print("  per mechanical turn -- fine for traction, coarse for a joint held still against")
print("  gravity. Plan on an encoder on the knee pulley for position, with the Halls for")
print("  commutation startup; the XDRIVE/ODrive in the BOM already supports that combination.")

# ======================================================================================
# 6.  WHICH IS ACTUALLY BETTER -- and the answer turns on heat, not torque
# ======================================================================================
# The question "can the hub motor make 28.2 N.m" is the easy one; both can. The question that
# decides it is what each one spends to HOLD that torque, because this is an assist for a
# post-operative knee: sit-to-stand is seconds of near-static load, and standing support is
# minutes of it. Copper loss for a given joint torque goes as R / (N * Kt)^2 -- the ratio enters
# SQUARED, which is why a 14.5:1 train with a cheap little motor beats a 2.8:1 train with a good
# big one, even though the hub is the better motor by every static measure.
print()
print("=" * 94)
print("6.  SCREW TRAIN vs HUB + ONE BELT: WHAT IT COSTS TO HOLD THE KNEE")
print("=" * 94)
KT_6374 = 9.5493 / 170.0        # 170 Kv, the motors actually on hand
R_6374 = 0.025                  # ASSUME ohm/phase -- typical C6374; measure it
N_SCREW, ETA_SCREW_TRAIN = 14.5, 0.90 * 0.97
N_HUB, ETA_HUB_TRAIN = 180.0 / FACE_PD, 0.97
COG_6374 = 0.05                 # ASSUME N.m -- an open outrunner cogs much less than a hub


def loss_for(tau_joint, n, kt, r, eta):
    i = tau_joint / (n * kt * eta)
    return i, 3.0 * (i / math.sqrt(2.0)) ** 2 * r


def tau_at_loss(p, n, kt, r, eta):
    i = math.sqrt(p / (3.0 * r)) * math.sqrt(2.0)
    return i * n * kt * eta


print("  Motor constant Km = Kt / sqrt(R), how much torque a motor makes per watt of heat:")
print("    C6374 170 Kv   Kt %.4f  R %.3f  ->  Km %.3f N.m/sqrt(W)"
      % (KT_6374, R_6374, KT_6374 / math.sqrt(R_6374)))
print("    hub motor      Kt %.4f  R %.3f  ->  Km %.3f N.m/sqrt(W)   %.1fx better"
      % (KT, R_PHASE, KT / math.sqrt(R_PHASE),
         (KT / math.sqrt(R_PHASE)) / (KT_6374 / math.sqrt(R_6374))))
print("  The hub is the better motor. Then the ratio squares, and the comparison inverts:")
print()
print("  %-28s %8s %9s %10s" % ("holding 28.2 N.m at the knee", "current", "copper", "vs screw"))
i_s, p_s = loss_for(TAU_PEAK, N_SCREW, KT_6374, R_6374, ETA_SCREW_TRAIN)
i_h, p_h = loss_for(TAU_PEAK, N_HUB, KT, R_PHASE, ETA_HUB_TRAIN)
print("  %-28s %6.1f A %7.0f W %10s" % ("screw train, 14.5:1", i_s, p_s, "--"))
print("  %-28s %6.1f A %7.0f W %9.1fx" % ("hub + one belt, %.2f:1" % N_HUB, i_h, p_h, p_h / p_s))
print()
print("  Turned round: the joint torque each can hold at a sustainable loss. A 6374 inside the")
print("  sealed P25 nacelle and a sealed hub shell are both bad at losing heat; call it 40 W for")
print("  the smaller motor and 80 W for the hub's 0.1 m2 of aluminium.")
print()
print("  %-28s %10s %14s" % ("", "loss budget", "holds at the knee"))
print("  %-28s %8.0f W %11.1f N.m" % ("screw train, 14.5:1", 40.0,
      tau_at_loss(40.0, N_SCREW, KT_6374, R_6374, ETA_SCREW_TRAIN)))
print("  %-28s %8.0f W %11.1f N.m" % ("hub + one belt, %.2f:1" % N_HUB, 80.0,
      tau_at_loss(80.0, N_HUB, KT, R_PHASE, ETA_HUB_TRAIN)))
print("  %-28s %8.0f W %11.1f N.m" % ("hub, direct drive", 80.0,
      tau_at_loss(80.0, 1.0, KT, R_PHASE, 1.0)))
print()
print("  So the screw train holds the full %.1f N.m on a 40 W budget with margin, the hub needs"
      % TAU_PEAK)
print("  %.0f W to do the same, and direct drive cannot do it at all. For a device whose hardest"
      % p_h)
print("  duty is a slow stand from a chair, that is the whole argument.")
print()
print("  WHERE THE HUB STILL WINS, honestly:")
print("    reflected inertia   %.3f kg.m2 (%.2fx limb) against the screw's 0.065 (0.22x)"
      % (J_ROTOR * N_HUB ** 2, J_ROTOR * N_HUB ** 2 / J_LIMB))
print("    part count          deletes screw, nut, rail, carriage, 4 V-wheels, the link belt")
print("    maintenance         no grease, no wiper seal, no lead-angle wear at the nut")
print("    cost                the wheels are already owned; so is the 6374, so this is a wash")
print("  AND WHERE IT LOSES:")
print("    holding heat        %.1fx the copper loss for the same joint torque" % (p_h / p_s))
print("    mass               %+.0f g, concentrated at the knee rather than along the thigh"
      % (si - so))
print("    width at the knee   a %.0f mm disc at the one place that catches chairs and doorways"
      % (RIM_PD + 25))
print("    cogging             %.2f N.m at the knee against the 6374 train's %.2f -- near a wash"
      % (COG * N_HUB, COG_6374 * N_SCREW))
print("    feedback            Hall-only commutation, 90 steps/turn, on a joint held static")
print("    schedule            a verified device exists today; this is a napkin with six")
print("                        unmeasured numbers in it")
