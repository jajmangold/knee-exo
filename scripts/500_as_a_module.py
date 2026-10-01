# -*- coding: utf-8 -*-
"""What this looks like as ONE MODULE of a full exoskeleton.

Everything so far has been a single powered knee that reacts its own torque into one limb.
That is a complete device, and it is also a dead end if the plan is a full exoskeleton,
because three of its load-bearing assumptions stop being true the moment there is a second
joint above or below it.

This asks four questions with numbers rather than adjectives:

  1. Can a full exo be eight of these? (No, and the margin is not close.)
  2. How much room is there to interconnect at each end? (Less than you would guess.)
  3. What is actually reusable, and what is knee-specific?
  4. What has to be decided NOW because it is expensive to retrofit?

Pure Python, no FreeCAD.
"""
import math

BW = 80.0          # kg, the design subject
HT = 1.75          # m
ASSIST = 0.30      # the project's target: top up 30%, do not replace
G = 9.81

print("=" * 88)
print("1.  CAN A FULL EXO BE EIGHT OF THESE?")
print("=" * 88)
# peak sagittal/frontal joint moments in level walking and stairs, N.m/kg of body mass
JOINTS = [
    ("ankle plantarflexion", 1.60, 3.50, 2),
    ("knee flex/extension",  1.05, 1.00, 2),
    ("hip  flex/extension",  1.10, 1.80, 2),
    ("hip  ab/adduction",    1.00, 0.60, 2),
]
print("  %-24s %-10s %-11s %-9s %-10s %s"
      % ("joint", "N.m/kg", "peak N.m", "30% N.m", "peak W", "count"))
tot_t = tot_p = 0.0
for nm, nmkg, wkg, n in JOINTS:
    t = nmkg * BW
    p = wkg * BW
    tot_t += ASSIST * t * n
    tot_p += ASSIST * p * n
    print("  %-24s %6.2f    %7.1f     %7.1f   %7.0f    x%d"
          % (nm, nmkg, t, ASSIST * t, ASSIST * p, n))
print()
print("  The knee is the SMALLEST of the four. The ankle wants %.0f N.m at 30%% assist against"
      % (ASSIST * 1.60 * BW))
print("  the knee's %.0f, and nearly four times the peak power." % (ASSIST * 1.05 * BW))
print()

M_KNEE = 3.78
print("  Mass, if each joint is built the way this knee is built (%.2f kg on the limb):" % M_KNEE)
n_joints = sum(n for _, _, _, n in JOINTS)
naive = M_KNEE * n_joints
print("     %d actuated joints x %.2f kg = %.1f kg carried on the legs" % (n_joints, M_KNEE, naive))
print()
print("  What that costs metabolically, at the published penalties for added limb mass")
print("  (Browning 2007: ~1-2%%/kg at the waist, ~4%%/kg thigh, ~7%%/kg shank, ~9%%/kg foot):")
SEG = [("hip actuators, at the pelvis", 2 * M_KNEE, 1.5),
       ("knee actuators, on the thigh", 2 * M_KNEE, 4.0),
       ("ankle actuators, on the shank", 2 * M_KNEE, 7.0),
       ("hip ab/ad, at the pelvis", 2 * M_KNEE, 1.5)]
pen = 0.0
for lbl, m, rate in SEG:
    pen += m * rate
    print("     %-32s %5.2f kg x %4.1f %%/kg = %5.0f %%" % (lbl, m, rate, m * rate))
print("     %-32s %5.2f kg %14s %5.0f %%" % ("TOTAL", naive, "", pen))
print()
print("  A %.0f%% metabolic penalty against a %.0f%% assist budget is not a device, it is an"
      % (pen, 100 * ASSIST))
print("  anchor. Even a perfect exo returning every newton-metre it promises would cost more")
print("  than it gives at that mass -- it is %.1fx upside down. So the full system cannot be"
      % (pen / (100 * ASSIST)))
print("  eight of these, and that is an architectural problem, not a tuning one.")
print()
print("  There are only three ways out, and they are architectural, not incremental:")
print("     a) LOAD TO GROUND. The structure carries its own weight and the payload into")
print("        the floor, so the user never lifts it. This is what every rigid exo that")
print("        works does (ReWalk, Ekso ~23 kg, and the user does not feel most of it).")
print("        It demands a continuous load path hip -> foot, which this module has NOT")
print("        got: it terminates in cuffs that react into soft tissue.")
print("     b) REMOTE ACTUATION. Motors at the pelvis, Bowden cables to the joints. Moves")
print("        mass from %.0f %%/kg to %.1f %%/kg -- a %.0fx reduction in penalty for the"
      % (7.0, 1.5, 7.0 / 1.5))
print("        same hardware -- at the cost of friction, compliance and routing.")
print("     c) FEWER JOINTS. Assist only what pays. The ankle returns the most power per")
print("        kg of any joint in walking; the knee returns the least.")

print()
print("=" * 88)
print("2.  HOW MUCH ROOM IS THERE TO INTERCONNECT?")
print("=" * 88)
# anthropometry, Winter: thigh = 0.245*H, shank = 0.246*H
thigh = 0.245 * HT * 1000.0
shank = 0.246 * HT * 1000.0
Y_PROX = 334.0        # the drive shell's proximal end, as built
Y_DIST = -350.0       # the shank cuff's distal end, as built
print("  For a %.2f m subject (Winter segment ratios):" % HT)
print("     hip joint centre at   Y %+7.0f mm from the knee" % thigh)
print("     ankle joint centre at Y %+7.0f mm" % -shank)
print()
print("     this module reaches   Y %+7.0f proximally (drive shell)" % Y_PROX)
print("                           Y %+7.0f distally (shank cuff)" % Y_DIST)
print()
print("     room before the hip   %7.0f mm" % (thigh - Y_PROX))
print("     room before the ankle %7.0f mm" % (shank + Y_DIST))
print()
print("  So roughly %.0f mm at the top and %.0f mm at the bottom, and into those has to fit"
      % (thigh - Y_PROX, shank + Y_DIST))
print("  the NEXT joint's bearing, its structure, and the splice between the two. The hip")
print("  end is the tighter one and it is already the end the motor lives at. 402 moved the")
print("  motor anterior to buy reach; that reach is now spoken for.")
print()
print("  This is the number that is expensive to retrofit. Every millimetre the drive end")
print("  grows proximally comes straight out of the hip module's budget.")

print()
print("=" * 88)
print("3.  WHAT IS REUSABLE")
print("=" * 88)
REUSE = [
 ("the transmission topology", "high",
  "closed belt loop + ball screw + constant %.2f mm moment arm. Joint-agnostic: it is a\n"
  "       linear-to-rotary stage parameterised by torque and range, not by anatomy." % 36.92),
 ("the verification suite", "high",
  "395 pose sweep, 406 limb's-eye coverage, 410 orientation audit, 411 printability.\n"
  "       None of these know what joint they are looking at. They want a joint spec as an\n"
  "       argument instead of module-level constants -- that is a refactor, not a rewrite."),
 ("the cuff method", "high",
  "408's chain -- couple force, contact pressure, roll torque, conical shell on a tapered\n"
  "       limb -- applies unchanged to an arm, a shank or a pelvis. The NUMBERS change; the\n"
  "       method is the reusable part, and it is the part that was missing until today."),
 ("the cladding language", "high",
  "n=5.5 superellipse lofts, limb-following undersides, rolled rims. Pure style, and style\n"
  "       is what makes eight modules look like one device."),
 ("the drive hardware", "medium",
  "XDRIVE MINI + C6374 is right for the knee and the hip. The ankle wants ~%.0f N.m at 30%%\n"
  "       assist, %.1fx the knee, so it needs either a bigger reduction or a second motor."
  % (ASSIST * 1.60 * BW, 1.60 / 1.05)),
 ("the structural spine", "medium",
  "2040 V-slot is already a universal interface -- T-slots on every face. Standardising on\n"
  "       it across modules costs nothing now and makes splices trivial later."),
 ("this module's load path", "LOW",
  "it reacts into soft tissue through two cuffs. A full exo should react into the GROUND.\n"
  "       That is the one piece that does not carry forward, and it is the biggest piece."),
]
for nm, score, why in REUSE:
    print("  %-26s %-8s %s" % (nm, score, why))

print()
print("=" * 88)
print("4.  WHAT TO DECIDE NOW  (cheap today, expensive later)")
print("=" * 88)
# CAN and power budget
N_NODES = n_joints
CAN_RATE = 500000.0
FRAME_BITS = 108.0      # 11-bit identifier, 8 data bytes, stuffing allowance
CTRL_HZ = 1000.0
load = N_NODES * 2 * CTRL_HZ * FRAME_BITS / CAN_RATE
print("  (a) ONE CAN BUS -- AND THE CONTROL RATE IS NOT A FREE CHOICE.")
print("      %d nodes x 2 frames (command + feedback) x %.0f bits is %.0f bits per control"
      % (N_NODES, FRAME_BITS, N_NODES * 2 * FRAME_BITS))
print("      cycle. Against the two standard bit rates:")
print()
print("      %-14s %-14s %-14s %s" % ("control rate", "500 kbit/s", "1 Mbit/s", ""))
for hz in (1000.0, 500.0, 200.0, 100.0):
    l5 = N_NODES * 2 * hz * FRAME_BITS / 500000.0
    l1 = N_NODES * 2 * hz * FRAME_BITS / 1000000.0
    v = "impossible" if l1 > 1.0 else ("tight" if l1 > 0.5 else "comfortable at 1 Mbit/s")
    print("      %6.0f Hz       %6.0f %%        %6.0f %%        %s" % (hz, 100 * l5, 100 * l1, v))
print()
print("      So a 1 kHz host loop over one bus DOES NOT FIT, at either rate -- which is the")
print("      answer to a question that would otherwise have been discovered during")
print("      integration. It is not a problem, because it is not how these drives are meant")
print("      to be used: the XDRIVE closes current and velocity locally at tens of kHz and")
print("      the bus only carries SETPOINTS. Budget %.0f Hz on one 1 Mbit/s bus at %.0f %%"
      % (200.0, 100 * N_NODES * 2 * 200.0 * FRAME_BITS / 1000000.0))
print("      load, and if a future joint really needs kilohertz commands, split left and")
print("      right legs onto two buses rather than raising the rate.")
print()
print("      What costs nothing today and is miserable to retrofit is the PASS-THROUGH: two")
print("      connectors per module instead of one so the bus daisy-chains, node IDs allocated")
print("      from a table rather than per-module defaults, and termination at the two ends")
print("      only -- which means the END modules differ from the middle ones, so that is a")
print("      thing to design in rather than discover.")
print()
I_KNEE = 24.8
print("  (b) SHARED DC BUS, SIZED FOR SIMULTANEITY NOT FOR SUM.")
print("      This knee peaks at %.1f A. Eight joints never peak together -- in gait the ankle"
      % I_KNEE)
print("      pushes off while the contralateral hip swings -- so size for ~%.0f %% of the sum:"
      % 40)
print("      %d x %.1f A x 0.40 = %.0f A at 48 V = %.1f kW peak, and perhaps %.0f A continuous."
      % (N_NODES, I_KNEE, N_NODES * I_KNEE * 0.4, N_NODES * I_KNEE * 0.4 * 48 / 1000,
         N_NODES * I_KNEE * 0.12))
print("      Decide the bus voltage NOW. 48 V nominal keeps the XDRIVE's 56 V ceiling with")
print("      headroom for regen, and every joint added later inherits it.")
print()
print("  (c) A MODULE COORDINATE FRAME, WRITTEN DOWN.")
print("      This repo's convention is +Y proximal, Z the joint axis, +X posterior, origin AT")
print("      the joint centre. That is already the right shape for a module -- it is local, it")
print("      is joint-centred, and a parent only needs a transform to place it. Formalise it")
print("      as 'every module is built in its own frame and published with a mount transform'")
print("      and the geometry scripts barely change.")
print()
print("  (d) A STRUCTURAL INTERFACE AT BOTH ENDS, NOT CUFFS.")
print("      Today the module ends in soft tissue at both ends. Leave a defined bolt pattern")
print("      on the rail at each end -- the T-slots are already there -- and treat the cuffs")
print("      as ALIGNMENT, not reaction. The moment a hip module exists above, most of the")
print("      %.0f N the thigh cuff carries should go up the structure instead of into the leg,"
      % (28.2 / 0.190))
print("      and the cuff can shrink. Designing them as a bolt-on today costs one bracket.")
print()
print("  (e) ONE HARDWARE E-STOP LINE THROUGH THE SAME CONNECTOR.")
print("      A single joint can be switched off by its own controller. Eight cannot: a fault in")
print("      one joint with the others still driving is worse than all of them stopping. One")
print("      normally-closed loop in series through every module, breaking the drive enable.")
print("      Two extra pins, today.")
print()
print("  (f) KEEP THE VERIFICATION PARAMETRIC.")
print("      395 and 406 are the reason this thing is trustworthy, and both are currently")
print("      hard-coded to one knee's part names and pose range. Making them take a part list")
print("      and a joint range as arguments is an afternoon now and a rewrite after the")
print("      second module exists.")

print()
print("=" * 88)
print("5.  EVERY MODULE USABLE ALONE *OR* FEDERATED")
print("=" * 88)
print("  This is a stronger requirement than 'modular' and it cuts against section 1. A module")
print("  that works alone must carry its own reaction path, its own controller, its own safety")
print("  interlock and its own power. That is exactly the mass that makes eight of them")
print("  unwearable. So the architecture is not 'modular' -- it is modules that SHED when they")
print("  federate, and the shedding has to be designed, not hoped for.")
print()
print("  What a standalone knee carries that a federated one does not need:")
SHED = [("local battery pack", 900.0, "one pack at the pelvis serves all joints"),
        ("second limb cuff", 162.0, "adjacent modules SHARE the limb interface -- see below"),
        ("standalone MCU + IMU", 40.0, "the system controller issues setpoints instead"),
        ("local e-stop + link plug", 30.0, "becomes a pass-through in the chain"),
        ("its own wiring loom to a pack", 120.0, "replaced by a short bus stub")]
tot_shed = sum(m for _, m, _ in SHED)
print("  %-28s %-9s %s" % ("item", "grams", "why it goes"))
for lbl, m, why in SHED:
    print("  %-28s %7.0f   %s" % (lbl, m, why))
print("  %-28s %7.0f   = %.0f %% of this module's %.2f kg"
      % ("TOTAL SHED", tot_shed, 100 * tot_shed / (M_KNEE * 1000), M_KNEE))
print()
print("  So a federated knee is about %.2f kg against %.2f standalone. Eight federated joints"
      % (M_KNEE - tot_shed / 1000.0, M_KNEE))
print("  are %.1f kg on the limbs rather than %.1f -- still too much to carry, which is why"
      % (8 * (M_KNEE - tot_shed / 1000.0), naive))
print("  section 1's load-to-ground answer does not go away. Shedding makes the system")
print("  possible; it does not make it light.")
print()
print("  THE CUFF IS THE INTERESTING ONE. A hip module and a knee module both clamp the")
print("  THIGH. Built as self-contained units they bring a cuff each: two shells on one")
print("  segment, fighting each other for the same %.0f mm of limb and each applying its own"
      % (0.245 * HT * 1000))
print("  roll torque. Federated they should share one. That makes the cuff a COMPONENT in its")
print("  own right rather than a part of a module -- which means its mounting interface, not")
print("  its shape, is the thing to standardise now.")
print()
print("  For a full leg: %d limb segments (pelvis, thigh, shank, foot) against %d modules x 2"
      % (4, 3))
print("  cuffs = %d if each is self-contained. Sharing saves %d cuffs per leg, about %.0f g."
      % (6, 2, 2 * 180.0))
print()
print("  WHAT THE INTERFACE SPEC HAS TO PIN DOWN -- and all of it is free today:")
SPEC = [
 ("mechanical", "a bolt pattern on the 2040 rail at BOTH ends, able to carry the full "
                "couple\n                   force (%.0f N here) so a neighbour can take over "
                "from the cuff" % (28.2 / 0.190)),
 ("limb interface", "cuffs mount to that same pattern, so one cuff serves one segment "
                    "whether\n                   it is held by one module or two"),
 ("coordinate frame", "+Y proximal, Z the joint axis, origin AT the joint centre, plus a "
                      "published\n                   mount transform. Already how this repo "
                      "works -- just needs writing down"),
 ("electrical", "one connector carrying 48 V bus, CAN H/L, and a normally-closed e-stop "
                "pair,\n                   duplicated for daisy-chain. A link plug closes "
                "the chain when standalone"),
 ("control", "every module closes its own current and velocity loop and accepts "
             "setpoints.\n                   Standalone it generates its own; federated it "
             "takes them. Same firmware,\n                   one flag -- decide the message "
             "set now, not the implementation"),
 ("identity", "node ID from a table, not a per-module default, and the part number is "
              "already\n                   engraved on the part (412). Modules should be "
              "identifiable cold"),
]
for lbl, why in SPEC:
    print("  %-17s %s" % (lbl, why))
print()
print("  The single most expensive thing to retrofit is the FIRST one: a structural interface")
print("  at both ends. Everything else is a connector choice or a software convention. Adding")
print("  a bolt pattern and a bracket to this knee now is one printed part; adding it after a")
print("  hip module exists means redesigning both.")
