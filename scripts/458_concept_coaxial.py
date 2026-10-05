# -*- coding: utf-8 -*-
"""Concept 2: motor coaxial on the screw, no link belt. It buys a lot and costs the one thing.

"knee concept test 2.FCStd" from the bench, with cuts for the belt and screws not yet made. It is
a whole thigh, not a knee detail, and it changes the drivetrain rather than the joint:

    motor            Flipsky 6374 190 Kv, Y -75..32, on the screw's own axis at X 0 Z 124
    coupling         FlexCoupler_8_8 at Y 17..42 -- DIRECT. No link belt, no 38T, no 20T, no pod
    screw            Y 32..210, 178 mm, X 0 Z 124
    capstan          dia 74 (29.1 teeth) at Y 273 -- the right size
    idlers           TWO, dia 30 (11.8 teeth), 24 mm wide, at X +-25, Y -92
    gantry           8 V-wheels on a 2040, nut at Y 64..118

WHAT IT BUYS IS REAL AND SHOULD BE SAID FIRST. Deleting the link belt deletes BOM D6, D7, D7a,
D7b, D7c, the motor pod P25, the controller mount P27's whole mounting problem, the 54T belt, the
flange coupling, the two printed pulleys and the 0.2 mm pod interference 446 found. It also drops
the motor current from 23.5 A to 13.8, which is thinner wire, less heat and a smaller fuse.

AND IT COSTS EXACTLY ONE NUMBER, which is the number this entire machine is organised around.

    python scripts/458_concept_coaxial.py
"""
import math

# measured out of the concept document
R_CAP = 37.0                    # dia 74 capstan
R_IDLER = 15.0                  # dia 30
IDLER_W = 24.0
BELT_W = 30.0
KV = 190.0                      # Flipsky 6374-190KV, against the C6374 170 Kv the BOM owns
PITCH = 8.0

# the machine as it stands
LEAD_BOUGHT = 5.0               # the SFU1605 that arrived
LEAD_OLD = 10.0                 # the SFU1610 that could not be sourced
LINK = 38 / 20.0
TAU_KNEE = 28.2
ETA = 0.90 * 0.97
J_ROTOR, J_LIMB = 3.10e-4, 0.30
KV_OWNED = 170.0
I_CONT = 40.0


def kt(kv):
    return 9.549 / kv


def row(label, r_cap, lead, link, kv):
    n = (2 * math.pi * r_cap / lead) / link
    j = J_ROTOR * n ** 2
    amps = TAU_KNEE / (n * ETA) / kt(kv)
    f_belt = TAU_KNEE * 1000.0 / r_cap
    teeth = 2 * math.pi * r_cap / PITCH
    per = f_belt / (teeth / 2.0)
    return label, n, j, j / J_LIMB, amps, f_belt, per


print("=" * 98)
print("1.  THE ONE NUMBER")
print("=" * 98)
print("  %-34s %8s %9s %9s %8s %9s %9s"
      % ("", "N total", "refl J", "vs limb", "amps", "belt N", "N/tooth"))
rows = [
    row("as built: 29T + 38T:20T link", 36.923, LEAD_BOUGHT, LINK, KV_OWNED),
    row("THIS CONCEPT: coaxial, 5 mm lead", R_CAP, LEAD_BOUGHT, 1.0, KV),
    row("coaxial on the 10 mm lead", R_CAP, LEAD_OLD, 1.0, KV),
    row("coaxial, 5 mm, capstan shrunk to 15T", 15 * PITCH / (2 * math.pi), LEAD_BOUGHT, 1.0, KV),
]
for label, n, j, vs, amps, fb, per in rows:
    flag = ""
    if vs > 1.0:
        flag = "   <-- the leg feels %.0f%% heavier" % (100 * vs)
    elif per > 2.0 * rows[0][6]:
        flag = "   <-- %.1fx the tooth load" % (per / rows[0][6])
    elif amps > I_CONT:
        flag = "   <-- over %.0f A" % I_CONT
    print("  %-34s %7.1f:1 %9.3f %8.2fx %7.1f A %8.0f %8.0f%s"
          % (label, n, j, vs, amps, fb, per, flag))
print()
print("  Reflected inertia goes as the SQUARE of the ratio, and the link belt is the only thing")
print("  in the chain that divides the ratio without touching the capstan. Take it out and the")
print("  screw's own 46.5:1 arrives undivided: %.2fx the limb's own inertia, against %.2fx today."
      % (rows[1][3], rows[0][3]))
print()
print("  WHAT THAT MEANS IN THE ROOM. 404_link_ratio.py rejected a 4:1 reduction at 9x the limb.")
print("  446_sfu1605_set.py called 0.87x 'the leg feels 87% heavier unpowered' and used it to")
print("  choose a 38T over a 32T. This is %.2fx -- the leg swings like %.1f of itself with the"
      % (rows[1][3], 1 + rows[1][3]))
print("  power off, which for a post-operative patient is not a preference, it is what happens")
print("  when the battery dies mid-stride.")

print()
print("=" * 98)
print("2.  THE TWO WAYS OUT, AND WHY NEITHER IS OPEN")
print("=" * 98)
print("  A 10 mm LEAD fixes it completely -- %.2fx, %.0f A, tooth load unchanged. That row is"
      % (rows[2][3], rows[2][4]))
print("  already in BOM's own comparison table as 'SFU1610, 1:1 link'. It is also the screw that")
print("  443_screw_sourcing.py spent a page failing to buy, and the 5 mm lead one is now on the")
print("  bench. Coaxial drive and the screw you own are not compatible.")
print()
print("  A SMALLER CAPSTAN fixes the inertia and breaks the teeth. 15T gets to %.2fx, and that is"
      % (rows[3][3]))
print("  444_capstan_size.py's exact finding: force per tooth goes as 1/T^2, so %.0f N per tooth"
      % rows[3][6])
print("  against today's %.0f -- %.1fx -- on PRINTED teeth whose profile 421_pulley_teeth.py is"
      % (rows[0][6], rows[3][6] / rows[0][6]))
print("  explicit is an approximation of an unpublished curve, still waiting on the coupon.")
print()
print("  So the link belt is not overhead. It is the thing that lets the capstan be big ENOUGH")
print("  for printed teeth and the reflection be small ENOUGH to swing. One stage, two jobs.")

print()
print("=" * 98)
print("3.  THE IDLERS WILL DESTROY THE BELT")
print("=" * 98)
t_idler = 2 * math.pi * R_IDLER / PITCH
print("  dia %.0f is %.1f teeth. HTD-8M wants about 22 teeth minimum on a toothed pulley and"
      % (2 * R_IDLER, t_idler))
print("  something like dia 50-65 on a FLAT back-bend idler; %.0f is under both." % (2 * R_IDLER))
print("  A belt forced round that radius loses tooth engagement, works its cords hard and")
print("  fatigues at the idler rather than anywhere interesting.")
print()
print("  And they are %.0f mm wide against a %.0f mm belt, so it overhangs %.0f mm each side."
      % (IDLER_W, BELT_W, (BELT_W - IDLER_W) / 2))
print("  The current design uses ONE idler and it is the SAME 29T part as the capstan -- BOM S2b,")
print("  'the same part as the knee capstan', which is what fixed the capstan's radius in the")
print("  first place. Two small ones is two new parts where the design had none.")

print()
print("=" * 98)
print("4.  WHAT ELSE THE FILE SAYS, SHORT OF THE CUTS NOT MADE")
print("=" * 98)
print("  * the MOTOR PASSES THROUGH THE RAIL -- 22.9 cm3 of Flipsky inside the 2040. Coaxial")
print("    puts the can on the screw's axis at Z 124 and the rail is at Z 83..103; a dia 63 can")
print("    reaches down to Z 92. Either the rail stops short of the motor or the screw moves up.")
print("  * TWO 2040s occupy the same space, overlapping 154 cm3. One of them is a leftover.")
print("  * a KFL08 and a 6001 are both at Y 57, 0.14 cm3 apart -- two different answers to the")
print("    screw's lower support, in the same slot. KFL08 is a dia 8 bore and SELF-ALIGNING,")
print("    which 455_concept_rev2.py ruled out for the knee and 445_screw_foot.py ruled out for")
print("    this end: the bought screw is machined for a BF12.")
print("  * the motor is a 190 Kv Flipsky where BOM D4 owns four C6374 at 170 Kv. 190 Kv is the")
print("    reason the current column above looks good -- it is a different motor.")

print()
print("=" * 98)
print("  VERDICT")
print("=" * 98)
print("  The layout is clean and most of it is an improvement -- the gantry, the straight screw")
print("  run, deleting the pod. But coaxial drive is a 10 mm-lead idea and the screw on the bench")
print("  is 5 mm, so as drawn it hands the patient a leg that swings like %.1f of itself with the"
      % (1 + rows[1][3]))
print("  power off.")
print()
od2 = (2 * math.pi * R_CAP / LEAD_BOUGHT) / 2.0
print("  IF YOU WANT THE SIMPLICITY ANYWAY, what is needed between motor and screw is a 2:1")
print("  OVERDRIVE, not a reduction -- and the difference matters at the point of sale. The screw")
print("  has to turn TWICE for each motor turn, so the motor pulley is the BIG one. N %.1f:1,"
      % od2)
print("  %.2fx the limb: identical to the 10 mm lead, because 5 mm turned twice is 10 mm."
      % (J_ROTOR * od2 ** 2 / J_LIMB))
print()
print("  So a planetary gearbox is the wrong shelf entirely -- those reduce, and fitted backwards")
print("  they are inefficient and often not backdrivable, which is the property being bought.")
print("  It is two pulleys and a short belt, which is what D6/D7 already are. The pod exists")
print("  because of where the motor had to go, not because of the belt -- and if coaxial is what")
print("  you want, an overdrive pair sits coaxially too: motor on the screw's axis, 2:1 between")
print("  them, no pod, no offset. That keeps nearly everything this concept buys.")
