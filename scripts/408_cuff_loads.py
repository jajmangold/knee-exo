# -*- coding: utf-8 -*-
"""What the cuffs actually have to do, before changing their shape.

The cuffs have had less thought than anything else on this device. They are a 165 degree
arc shell with four 5.2 mm slots in them, and the entire adjustment story in the BOM is one
line: "6 mm EVA + hook-and-loop straps, $20". Everything upstream of them -- the screw, the
bracket, the belt, the wheels -- was sized by calculation. The thing that actually touches
the patient was not.

Three questions, in the order that matters:

  1. How hard does the cuff press on the limb, and is that a pressure a person can wear?
  2. What stops the whole device rolling round the leg? This is the load nobody designs for
     and the one that makes orthoses fail in practice -- it is CONSTANT, it does not wait
     for the motor to do anything, and it is resisted only by strap tension and friction.
  3. How much adjustment does a post-operative limb need, and over what timescale?

Pure Python, no FreeCAD.
"""
import math

# ---------------------------------------------------------------- the device, as built
T_KNEE = 28.2          # N.m design assist, 30% of the 1.05 N.m/kg stair-ascent demand
M_DEV = 3.78           # kg on the limb (390_onescrew_section.py)
G = 9.81
R_LIMB_TH = 84.9       # thigh skin radius, REF_Thigh
R_LIMB_SH = 60.0       # shank skin radius, REF_Shank
Y_THC = (150.0, 260.0)  # thigh cuff span, as built
Y_SHC = (-328.0, -208.0)
WRAP = 165.0           # degrees of wrap, measured off the built shape
PAD = 6.0              # EVA liner thickness

print("=" * 78)
print("1.  CUFF PRESSURE  --  can a person wear the reaction?")
print("=" * 78)
# The thigh-side structure reacts the knee moment as a COUPLE: the thigh cuff at one end,
# the knee yoke and its flange at the other. Arm = distance from the knee axis to the cuff
# centroid.
y_c = 0.5 * (Y_THC[0] + Y_THC[1])
F_couple = T_KNEE / (y_c / 1000.0)
print("  knee moment                     %6.1f N.m" % T_KNEE)
print("  thigh cuff centroid at Y        %6.0f mm  -> couple arm %.3f m" % (y_c, y_c / 1000.))
print("  force the cuff must push with   %6.1f N" % F_couple)
print()
# Contact area. A cuff pushing in ONE direction does not load its whole wrap: the far side
# unloads completely. Treat the loaded sector as the half that faces the push, and apply a
# cosine distribution over it, which gives an effective area of 2/pi of the sector.
arc_full = math.radians(WRAP) * R_LIMB_TH
width = Y_THC[1] - Y_THC[0]
A_full = arc_full * width / 1e6
A_eff = A_full * 0.5 * (2.0 / math.pi)
print("  wrap %.0f deg at r %.1f -> arc %.0f mm, width %.0f mm, total %.0f cm2"
      % (WRAP, R_LIMB_TH, arc_full, width, A_full * 1e4))
print("  effective loaded area (half the wrap, cosine distributed) %.0f cm2" % (A_eff * 1e4))
p_peak = F_couple / A_eff / 1000.0
print("  peak contact pressure           %6.1f kPa" % p_peak)
print()
print("  against the thresholds that matter:")
for lbl, kpa, note in (("capillary closing pressure", 4.3, "32 mmHg; sustained above this risks ischaemia"),
                       ("sustained orthotic comfort", 15.0, "typical design ceiling on soft tissue"),
                       ("over bone / tendon", 8.0, "lower, and the cuff must avoid these anyway"),
                       ("pain threshold, soft tissue", 100.0, "not the limit that matters")):
    print("     %-28s %5.1f kPa   %s %s"
          % (lbl, kpa, "OK" if p_peak < kpa else "EXCEEDED", "-- " + note))
print()
print("  The assist is INTERMITTENT -- peak torque is the push-off of a stair step, not a")
print("  sustained hold -- so the 4.3 kPa capillary figure is the wrong threshold for THIS")
print("  load; it governs the resting fit, which is set by strap tension. The one that")
print("  applies is the 15 kPa comfort ceiling, and at %.1f kPa the cuff as built is OVER" % p_peak)
print("  it. Not by much, and not dangerously, but it is over -- and this is the first time")
print("  anyone has computed it.")
print()
print("  What it takes to get under. The force is fixed by the couple arm, so there are")
print("  three levers: make the cuff wider, wrap it further round, or move it proximally so")
print("  the arm is longer. Target 12 kPa, which leaves room for the fit being worse than")
print("  the model.")
print()
TARGET = 12.0
print("  %-34s %-12s %-12s %s" % ("change", "pressure", "vs 15 kPa", "cost"))


def press(width_mm, wrap_deg, yc_mm):
    f = T_KNEE / (yc_mm / 1000.0)
    a = math.radians(wrap_deg) * R_LIMB_TH * width_mm / 1e6 * 0.5 * (2.0 / math.pi)
    return f / a / 1000.0


for lbl, w, wr, yc, cost in (
        ("as built", width, WRAP, y_c, "-"),
        ("width 110 -> 140 mm", 140.0, WRAP, y_c, "30 mm more limb covered"),
        ("wrap 165 -> 200 deg", width, 200.0, y_c, "harder to don, needs a real hinge"),
        ("move proximal, centroid 205 -> 255", width, WRAP, 255.0, "runs into the drive end"),
        ("width 140 AND wrap 200", 140.0, 200.0, y_c, "both of the above")):
    pp = press(w, wr, yc)
    print("  %-34s %6.1f kPa   %-12s %s"
          % (lbl, pp, "OK" if pp < 15.0 else "over", cost))
print()
print("  Widening alone does it, and it is the cheapest of the three: it costs nothing but")
print("  shell, it does not make the cuff harder to get into, and a wider cuff is also a")
print("  better lever against the roll torque in section 2. So: WIDER, not tighter.")
print()
print("=" * 78)
print("2.  ROLL  --  the load that actually decides the design")
print("=" * 78)
# Every gram of this device hangs LATERAL of the limb. That offset weight is a constant
# torque about the limb's long axis, trying to rotate the whole brace round the leg. No
# amount of assist torque changes it; it is there when the device is switched off.
Z_COM = 95.0           # mm lateral of the limb axis; the rail is at Z 98 and the mass is
                       # spread either side of it (motor low at Z 62, bracket high at 130)
W = M_DEV * G
T_roll = W * Z_COM / 1000.0
print("  device weight                   %6.1f N  (%.2f kg)" % (W, M_DEV))
print("  centre of mass, lateral offset  %6.0f mm" % Z_COM)
print("  CONSTANT roll torque about the limb axis   %.2f N.m" % T_roll)
print()
# Resisted by friction between cuff and skin, which needs normal force, which comes from
# strap tension. For a band under tension T wrapped over an angle, the normal force on the
# limb is what the tension generates: N = T * (wrap geometry). For a simple band pulled
# tight across a cuff of radius r, total normal load ~ 2T for a full wrap; for a partial
# wrap closed by one strap, ~2T sin(wrap/2) is the clamping resultant.
MU = 0.4               # EVA foam against skin, dry. Lower when the patient sweats.
print("  resisted by friction at the cuff. Two cuffs share it, each at its own radius.")
print()
print("  %-14s %-10s %-14s %-16s %s" % ("cuff", "radius", "friction force", "normal force", "strap tension"))
tot = 0.0
for lbl, r, share in (("thigh", R_LIMB_TH, 0.6), ("shank", R_LIMB_SH, 0.4)):
    F_fric = T_roll * share / (r / 1000.0)
    N_req = F_fric / MU
    T_strap = N_req / (2.0 * math.sin(math.radians(WRAP) / 2.0))
    tot += T_strap
    print("  %-14s %5.1f mm   %6.1f N        %6.1f N           %6.1f N"
          % (lbl, r, F_fric, N_req, T_strap))
print()
print("  So roughly %.0f N of strap tension per cuff, with mu = %.1f. That is a firm pull --" % (T_strap, MU))
print("  about the tension of a well-done ski boot buckle -- and it has to be REPEATABLE,")
print("  because if it is not, the device sits at a different roll angle each day and the")
print("  knee axis stops lining up with the patient's.")
print()
print("  This is the number that kills hook-and-loop. Velcro will hold %.0f N once; what it" % T_strap)
print("  will not do is land on the same tension twice, or survive being pulled to that")
print("  tension twice a day for months, or be pulled to it one-handed by someone on")
print("  crutches. The adjustment mechanism is a load-bearing part, not a convenience.")

print()
print("=" * 78)
print("3.  HOW MUCH ADJUSTMENT  --  a post-operative limb is not one size")
print("=" * 78)
print("  This brace is for a post-operative patient, so the limb it has to fit changes")
print("  under it. Reported thigh circumference changes after knee surgery:")
print()
print("  %-34s %-16s %s" % ("", "circumference", "-> radius"))
for lbl, dc in (("first days, peak swelling", 60.0),
                ("first week", 40.0),
                ("weeks 2-6, resolving", 25.0),
                ("diurnal, morning to evening", 10.0),
                ("quadriceps atrophy over 6-12 weeks", -30.0)):
    print("  %-34s %+6.0f mm        %+6.1f mm" % (lbl, dc, dc / (2 * math.pi)))
print()
span = (60.0 - (-30.0)) / (2 * math.pi)
print("  Worst case the radius moves about %.0f mm, and the day-to-day swing is %.1f mm."
      % (span, 10.0 / (2 * math.pi)))
print("  So the mechanism needs roughly %.0f mm of radial travel, resolved finely enough" % span)
print("  that the diurnal %.1f mm is one or two clicks rather than the whole range."
      % (10.0 / (2 * math.pi)))
print()
print("  %-22s %-12s %-12s %-10s %s" % ("mechanism", "range", "increment", "1-handed", "repeatable"))
for lbl, rng, inc, hand, rep, note in (
        ("hook-and-loop", "unlimited", "stepless", "no", "no", "what is specified now"),
        ("ladder strap", "~25 mm", "~3 mm", "yes", "yes", "cheap, coarse"),
        ("ratchet buckle", "~30 mm", "3-4 mm", "yes", "yes", "ski-boot type, very strong"),
        ("BOA dial + lace", "~40 mm", "~1 mm", "yes", "yes", "used on real post-op braces")):
    print("  %-22s %-12s %-12s %-10s %-11s %s" % (lbl, rng, inc, hand, rep, note))
print()
print("  Required: %.0f mm of range, ~%.1f mm resolution, one-handed, repeatable, and good"
      % (span, 10.0 / (2 * math.pi)))
print("  for %.0f N. Only the last two rows clear all of it on range AND resolution." % T_strap)

print()
print("=" * 78)
print("4.  WHY LACE AT ALL  --  and why the lock is a separate decision")
print("=" * 78)
print("  A BOA dial IS a bootlace. It is a lace, plus a reel that does the pulling and the")
print("  locking. So the choice splits in two, and only one half is printed:")
print()
print("     the LACE PATH   -- guides, channels, eyelet positions   PRINTED, decide now")
print("     the LOCK        -- what holds the tension               BOUGHT, swap any time")
print()
print("  The lace path is worth having on its own, because of what crossings do to the")
print("  hand force. A lace zigzagging across the gap is a block and tackle: each crossing")
print("  carries the pull, so n crossings multiply it. Friction at each guide eats into")
print("  that by exp(-mu*theta) per turn.")
print()
MU_G = 0.25            # braided polyester over a printed PETG guide, no bushing
TURN = math.pi         # each guide turns the lace through roughly 180 deg
T_NEED = 31.4          # N of cuff tension, from section 2
print("  %-10s %-16s %-18s %s" % ("crossings", "ideal hand pull", "with guide friction", "verdict"))
for n in (1, 2, 3, 4, 5, 6):
    ideal = T_NEED / n
    eff = sum(math.exp(-MU_G * TURN * k) for k in range(n))
    real = T_NEED / eff if eff > 0 else float("inf")
    v = ""
    if n == 1:
        v = "a plain strap -- this is what is specified now"
    elif real < 12.0:
        v = "comfortable one-finger pull"
    elif real < 20.0:
        v = "firm but easy"
    print("  %-10d %6.1f N          %6.1f N             %s" % (n, ideal, real, v))
print()
print("  Four crossings turn a %.0f N haul into a %.0f N pull. That matters more than it" % (T_NEED, T_NEED / sum(math.exp(-MU_G * TURN * k) for k in range(4))))
print("  looks: the person doing the pulling has just had knee surgery, is on crutches, and")
print("  cannot easily bend to reach the shank cuff at all. Friction is also why the guides")
print("  want to be generous radii, not sharp printed slots -- a tight corner is a bigger")
print("  loss than an extra crossing is a gain.")
print()
print("  Now the lock, on the SAME printed part:")
print()
print("  %-24s %-9s %-11s %-11s %-9s %s"
      % ("lock", "cost", "resolution", "one-handed", "holds?", "note"))
for lbl, cost, res, hand, hold, note in (
        ("tie a bow", "$0", "stepless", "no", "yes", "two hands, fine motor, and you must reach it"),
        ("spring cord lock", "$2", "stepless", "YES", "mostly", "squeeze and slide -- drawstring hardware"),
        ("cam cleat", "$6", "stepless", "YES", "yes", "one-way, pull to tighten, lift to release"),
        ("BOA dial L6", "$25", "~1 mm", "YES", "yes", "ratchets; release by pulling the dial")):
    print("  %-24s %-9s %-11s %-11s %-9s %s" % (lbl, cost, res, hand, hold, note))
print()
print("  All four use the same lace path. So: print for lace, start with a cord lock or a")
print("  cleat for a couple of dollars, and if it creeps or your dad finds it fiddly, a BOA")
print("  drops onto the same guides without reprinting anything. That is the version of")
print("  this decision that cannot be got wrong.")
print()
print("  One thing a plain lace does NOT give you that the dial does: a repeatable NUMBER.")
print("  Section 2 cares about landing on the same tension every day. A cord lock is")
print("  stepless, which means it is also unmarked -- so print a witness scale beside the")
print("  lace tail and the patient can match yesterday's mark. That is 20 minutes of CAD")
print("  and it recovers most of what the dial was for.")
print()
print("  Note what that table does NOT do: it stops improving. Beyond four crossings the")
print("  hand force barely moves, because the tension decays geometrically along the lace")
print("  and the sum converges to 1/(1 - exp(-mu*pi)). More crossings cannot beat that")
print("  ceiling -- only a slipperier guide can:")
print()
print("  %-34s %-7s %-14s %s" % ("guide", "mu", "best possible", "hand pull at 4 crossings"))
for lbl, mu in (("printed PETG, sharp slot", 0.35),
                ("printed PETG, generous radius", 0.25),
                ("brass eyelet", 0.15),
                ("PTFE tube liner", 0.10),
                ("BOA: coated cable in a polymer guide", 0.08)):
    cap = T_NEED * (1.0 - math.exp(-mu * TURN))
    four = T_NEED / sum(math.exp(-mu * TURN * k) for k in range(4))
    print("  %-34s %.2f    %6.1f N        %6.1f N" % (lbl, mu, cap, four))
print()
print("  A %.0f cent length of PTFE tube pressed into each guide is worth more than doubling" % 20)
print("  the number of crossings. That is the whole design note: four crossings, big radii,")
print("  PTFE liners, and the lock is then whatever is cheapest that holds.")

print()
print("=" * 78)
print("5.  NYLON WEBBING  --  reconsidered properly, because section 3 was unfair to it")
print("=" * 78)
print("  Section 3 wrote off 'hook-and-loop' on repeatability. That was right about VELCRO")
print("  and wrong about WEBBING: nylon webbing through a cam buckle or a ladder lock is")
print("  repeatable, holds hundreds of newtons, and needs no fine motor control at all.")
print("  Lumping the two together was a mistake. Four things the lace analysis missed:")
print()
# --- a) what the closure itself presses on
print("  (a) THE CLOSURE HAS TO BEAR ON SOMETHING TOO.")
GAP = 100.0            # mm of arc the closure spans across the open side of the cuff
print("      The closure spans the %.0f mm of arc the shell does not cover. Whatever is in" % GAP)
print("      that gap bears on soft tissue directly:")
print()
print("      %-26s %-9s %-12s %s" % ("closure", "width", "pressure", ""))
for lbl, w in (("3.5 mm lace, bare", 3.5), ("6 mm lace, bare", 6.0),
               ("25 mm webbing", 25.0), ("38 mm webbing", 38.0)):
    pp = T_NEED / (w * GAP / 1e6) / 1000.0
    print("      %-26s %4.0f mm   %7.1f kPa  %s"
          % (lbl, w, pp, "" if pp < 15.0 else "<-- over the comfort ceiling"))
print()
print("      A bare lace cuts. Every laced brace on the market therefore has a TONGUE under")
print("      it to spread the load -- which is an extra printed part, an extra thing to")
print("      align, and an extra thing to lose. Webbing IS its own tongue.")
print()
# --- b) mechanical advantage
print("  (b) WEBBING GETS MECHANICAL ADVANTAGE TOO, and more cheaply than lacing does.")
print("      Route the tail through a D-ring and back to a cam buckle and it is a 2:1")
print("      purchase over a smooth 25 mm bar, where friction is far lower than a lace in")
print("      a printed slot:")
print()
print("      %-34s %-7s %s" % ("routing", "mu", "hand pull"))
for lbl, n, mu in (("single strap, direct", 1, 0.0),
                   ("2:1 through a D-ring", 2, 0.12),
                   ("lace, 4 crossings, printed guide", 4, 0.25),
                   ("lace, 4 crossings, PTFE lined", 4, 0.10)):
    eff = sum(math.exp(-mu * TURN * k) for k in range(n))
    print("      %-34s %.2f    %6.1f N" % (lbl, mu, T_NEED / eff))
print()
print("      2:1 webbing lands within a newton or two of PTFE-lined lacing, for less work.")
print()
# --- c) the one nobody costs
print("  (c) GETTING IT OFF IN A HURRY. This is a POWERED device: %.0f N.m at the knee of a" % T_KNEE)
print("      post-operative patient. If the firmware faults, or a belt jumps, or the limb")
print("      simply hurts, the question is how fast the thing comes off -- one-handed, by")
print("      someone sitting down who cannot bend well.")
print()
print("      %-28s %s" % ("closure", "to release"))
for lbl, t in (("side-release buckle", "one squeeze, both cuffs free in ~2 s"),
               ("cam buckle", "flip the lever, ~3 s"),
               ("spring cord lock", "find it, squeeze, drag the lace out, ~8 s"),
               ("BOA dial", "pull the dial up, ~3 s, but the lace stays threaded"),
               ("tied lace", "two hands and good light")):
    print("      %-28s %s" % (lbl, t))
print()
print("      Nothing else in this analysis is a safety argument. This one is, and it points")
print("      at webbing with a quick-release buckle.")
print()
# --- d) hygiene
print("  (d) IT IS WORN AGAINST SKIN FOR MONTHS. Webbing unthreads in seconds and goes in")
print("      the wash; it is a consumable you replace for a few dollars when it frays. Lace")
print("      through PTFE-lined guides is fiddlier to strip and re-thread, and the guides")
print("      themselves trap what comes off the skin.")
print()
print("  VERDICT. Webbing wins on bearing area, on emergency release, on hygiene, and ties")
print("  on hand force once it is routed 2:1. Lacing wins only on resolution -- stepless")
print("  against a cam buckle, which is also stepless. The lace case was built on a hand-")
print("  force advantage that a D-ring erases.")
print()
print("  So: NYLON WEBBING, 38 mm, 2:1 through a D-ring into a cam buckle, with a side-")
print("  release buckle in the loop so the whole thing drops off in one squeeze. The printed")
print("  cuff needs webbing slots and a D-ring anchor instead of lace guides -- and the")
print("  slots are easier to print than the guides were.")

print()
print("=" * 78)
print("6.  THE FIT  --  which turns out to be the real problem, and makes section 1")
print("    OPTIMISTIC rather than pessimistic")
print("=" * 78)
print("  Sections 1-5 all assumed the cuff touches the limb across its whole width. It does")
print("  not, and the reason is that BOTH limb phantoms are CONES and BOTH cuffs are")
print("  CYLINDERS:")
print()
print("     REF_Thigh   cone  r 62.0 at Y  +15  ->  r 85.0 at Y +300   slope %.4f" % ((85.-62.)/285.))
print("     REF_Shank   cone  r 60.0 at Y  -20  ->  r 38.0 at Y -380   slope %.4f" % ((60.-38.)/360.))
print("     P5 shell    cylinder, inner r 84.0, constant")
print("     P7 shell    cylinder, inner r 64.0, constant")
print()


def r_thigh(y):
    return 62.0 + (85.0 - 62.0) * (y - 15.0) / 285.0


def r_shank(y):
    return 60.0 - (60.0 - 38.0) * (abs(y) - 20.0) / 360.0


for lbl, fn, ys, rin in (("THIGH  P5", r_thigh, (150, 261, 22), 84.0),
                         ("SHANK  P7", r_shank, (-328, -207, 24), 64.0)):
    print("  %s, shell inner r %.0f, EVA pad %.0f mm nominal" % (lbl, rin, PAD))
    print("     %-7s %-9s %-8s %s" % ("Y", "limb r", "gap", "what the pad does"))
    contact = []
    for y in range(ys[0], ys[1], ys[2]):
        g = rin - fn(float(y))
        if g < PAD:
            note = "compressed %.0f%%" % (100.0 * (PAD - g) / PAD)
            contact.append(y)
        else:
            note = "FLOATS -- %.1f mm of air" % (g - PAD)
        print("     %-7d %-9.1f %-8.1f %s" % (y, fn(float(y)), g, note))
    print()

print("  The thigh cuff therefore bears on a narrow band at its PROXIMAL RIM and floats")
print("  over the rest. The shank cuff does not reach the limb anywhere -- its shell is")
print("  15-23 mm off a limb that the 6 mm pad can bridge none of. FreeCAD agrees:")
print("  distToShape(P7, REF_Shank) = 7.78 mm, and the 107-pose sweep has never once")
print("  flagged P7 against REF_Shank, while it flags P5 at 0.836 cm3 every run. The data")
print("  was there the whole time; nobody read the absence as information.")
print()
# what the real pressure is, on the band that does touch
y_on = 15.0 + 285.0 * (84.0 - PAD - 62.0) / 23.0
band = Y_THC[1] - y_on
F = T_KNEE / (0.5 * (Y_THC[0] + Y_THC[1]) / 1000.0)
arc = math.radians(WRAP) * 80.0
A = arc * band / 1e6 * 0.5 * (2.0 / math.pi)
print("  What that does to section 1's number. Contact starts where the gap closes to the")
print("  pad thickness, at Y %.0f, so the bearing band is %.0f mm of the %.0f mm width:"
      % (y_on, band, Y_THC[1] - Y_THC[0]))
print("     section 1 assumed  %3.0f mm of width  ->  %5.1f kPa" % (Y_THC[1] - Y_THC[0], p_peak))
print("     actually bearing   %3.0f mm of width  ->  %5.1f kPa" % (band, F / A / 1000.0))
print()
print("  %.0f kPa is not a comfort problem, it is a pressure sore. On a post-operative limb" % (F / A / 1000.0))
print("  with compromised circulation, held for a walk, at the PROXIMAL RIM where the shell")
print("  edge is -- that is exactly where and how braces injure people.")
print()
print("  So the answer to 'make the cuffs better' is not a nicer strap. It is:")
print("     1. CONICAL SHELLS matching the limb taper, so the whole width bears")
print("     2. WIDER, to get the uniform pressure under the 15 kPa ceiling")
print("     3. ROLLED RIMS, because the edge is where the concentration lands")
print("     4. and only then, the webbing and buckles from section 5")
print()
print("  Widening a CYLINDRICAL cuff -- which is what section 1 recommended -- would have")
print("  made this worse, because a longer cylinder on a cone diverges further at both ends.")

print()
print("=" * 78)
print("7.  A NEOPRENE SLEEVE UNDER THE CUFFS  --  what it fixes and what it does not")
print("=" * 78)
T_SLEEVE = 3.0         # mm, typical thigh/calf sleeve; 5 mm exists but is hot
print("  Putting a %.0f mm neoprene sleeve on the limb and clamping the cuff over it changes" % T_SLEEVE)
print("  four of the numbers above, three of them for the better.")
print()
print("  (a) FRICTION, which is the one that matters most. Section 2 needed %.0f N of strap" % T_NEED)
print("      tension per cuff, and that came straight out of mu = %.1f for EVA on skin." % MU)
print("      Neoprene is the reason a wetsuit stays where you put it. There are now TWO")
print("      interfaces in series and the WEAKER one governs:")
print()
print("      %-30s %-7s %s" % ("interface", "mu", "strap tension needed"))
rows = [("EVA foam on skin (as specified)", 0.40),
        ("printed PETG on neoprene", 0.70),
        ("neoprene on skin, dry", 0.85),
        ("neoprene on skin, sweating", 0.60)]
for lbl, mu in rows:
    F_fric = T_roll * 0.6 / (R_LIMB_TH / 1000.0)
    t = (F_fric / mu) / (2.0 * math.sin(math.radians(WRAP) / 2.0))
    print("      %-30s %.2f    %6.1f N" % (lbl, mu, t))
mu_gov = 0.60
t_new = (T_roll * 0.6 / (R_LIMB_TH / 1000.0) / mu_gov) / (2.0 * math.sin(math.radians(WRAP) / 2.0))
print()
print("      Governing case is a sweating limb at mu %.2f -> %.1f N, against %.1f N on bare" % (mu_gov, t_new, T_NEED))
print("      EVA. That is a %.0f%% cut in how hard the strap has to be pulled, and it comes" % (100 * (1 - t_new / T_NEED)))
print("      free. With 2:1 webbing the hand pull is %.1f N -- a light tug." % (t_new / 2.0 * 1.12))
print()
print("  (b) EDGE PRESSURE. Section 6 put 40 kPa on a narrow band at the shell rim. A")
print("      continuous elastic layer bridges a rim instead of letting it dig: the sleeve")
print("      carries tension across the edge and spreads the step over its own thickness.")
print("      It does not make the number 40 -> 12, but it turns a hard edge into a ramp,")
print("      and edge pressure is what injures skin.")
print()
print("  (c) SHEAR. The other way braces hurt people, and the one nobody measures. Skin")
print("      tears from rubbing, not only from pressure. With a sleeve the cuff slides on")
print("      NEOPRENE and the neoprene moves with the skin, so the sliding interface is")
print("      moved off the patient entirely.")
print()
print("  (d) HYGIENE. The sleeve becomes the only thing touching skin, and it washes. That")
print("      retires most of section 5(d) -- the webbing no longer has to be the washable")
print("      part, so it can be chosen for strength and release instead.")
print()
print("  WHAT IT DOES NOT FIX, and this is the important half:")
print()
for lbl, fn, ys, rin in (("thigh", r_thigh, (150.0, 260.0), 84.0),
                         ("shank", r_shank, (-328.0, -208.0), 64.0)):
    g0 = rin - fn(ys[0]) - T_SLEEVE
    g1 = rin - fn(ys[1]) - T_SLEEVE
    print("     %-6s gap after a %.0f mm sleeve:  %5.1f mm at one end, %5.1f at the other"
          % (lbl, T_SLEEVE, min(g0, g1), max(g0, g1)))
print()
print("     A %.0f mm sleeve cannot bridge a %.0f mm gap. The shank cuff still does not reach"
      % (T_SLEEVE, 64.0 - r_shank(-328.0) - T_SLEEVE))
print("     the limb, and the thigh cuff still bears only at its proximal rim. The taper")
print("     mismatch is geometry; a compliant layer cannot fix geometry, it can only make")
print("     the part of the cuff that DOES touch hurt less.")
print()
print("  REVISED TARGET for the rebuild: shells CONICAL on the limb taper, inner surface at")
print("  limb + %.0f mm sleeve + %.0f mm air for donning, wider per section 1, rolled rims," % (T_SLEEVE, 1.0))
print("  and no EVA pad at all -- the sleeve replaces it, which also drops a BOM line.")
print()
print("  One caveat worth putting in writing, because it is the patient and not the device:")
print("  a sleeve goes over a CLOSED, dry incision, not a fresh one, and neoprene contact")
print("  dermatitis from thiourea accelerators is common enough to plan for. Worth one")
print("  question to whoever is running his rehab, and a nylon-faced or neoprene-free")
print("  sleeve is the fallback. That is a question for them, not a thing to design around.")
