# -*- coding: utf-8 -*-
"""Can every pulley be printed? Three of the four, and the teeth were never the reason.

Asked at the bench: "can't we just print all the pulleys".

THE PREMISE IS ALREADY HALF TRUE. P2a_KneeHub_Pulley29T is printed -- 6 perimeters, 60%, and
421_pulley_teeth.py cuts its 29 HTD-8M grooves. It is the pulley that carries the capstan loop's
764 N differential, which 403_stepped_idler.py calls the load that "breaks the belt, the nut and
the bracket at once". So the question is not whether a printed pulley can work here. It is
whether the three remaining ones are harder than the one already committed, and they are not:
the link belt carries a seventeenth of the capstan's force.

WHAT ACTUALLY DECIDES IT, THEN. Not the tooth stress -- every number below is two orders under
PETG. Three other things:

  * THE HUB. A pulley on a shaft has to get its torque in through a grub screw into printed
    plastic. The capstan does not have this problem, because it bolts to the knee plate on a
    pattern. The motor pulley has it worst.
  * THE PROFILE, which is 421's open question and the reason TEST_ToothCoupon exists. HTD is a
    curvilinear form whose defining arcs are not published, so both 421 and this are cutting an
    approximation. At 5M pitch that approximation is proportionally coarser than at 8M: the same
    modelling error over a tooth 2.1 mm tall instead of 3.5.
  * HEAT, and this one is specific to exactly one of the four.

    python scripts/447_printed_pulleys.py
"""
import math

# ---------------------------------------------------------------- the drivetrain, post-SFU1605
TAU_KNEE = 28.2                 # N.m
R_CAP = 29 * 8.0 / (2 * math.pi)
F_CAP = TAU_KNEE * 1000.0 / R_CAP          # 764 N, the capstan loop differential
T_IDLER = 1828.0                           # N, BOM S2c: the idler axle's reaction, 2 x tight side
ETA_B = 0.97
N_TOT = (2 * math.pi * R_CAP / 5.0) / 1.9  # SFU1605 + 38T:20T
TAU_MOT = TAU_KNEE / (N_TOT * 0.90 * ETA_B)
C_LINK = 60.83
RPM_MOT = 1160.0 * 2.0 / 1.9

# PETG as printed, conservative: in-plane tensile is the direction a tooth is loaded
PETG_TENSILE = 40.0             # MPa
PETG_SHEAR = 25.0               # MPa
PETG_BEARING = 40.0             # MPa
PETG_TG = 80.0                  # degC

# tooth form, scaled from 421_pulley_teeth.py's half-ellipse approximation of HTD-8M
FORM = {8.0: dict(pld=0.686, h=3.45, groove=5.30),
        5.0: dict(pld=0.571, h=3.45 * 5 / 8.0, groove=5.30 * 5 / 8.0)}


def tip_r(teeth, pitch):
    return teeth * pitch / (2 * math.pi) - FORM[pitch]["pld"]


def land(teeth, pitch):
    """circumferential width of one pulley tooth at the tip circle"""
    return 2 * math.pi * tip_r(teeth, pitch) / teeth - FORM[pitch]["groove"]


def mesh(t_small, t_large, c, small=True):
    r1, r2 = t_large * 5.0 / (2 * math.pi), t_small * 5.0 / (2 * math.pi)
    d = math.asin(min(1.0, (r1 - r2) / c))
    wrap = (math.pi - 2 * d) if small else (math.pi + 2 * d)
    return (t_small if small else t_large) * wrap / (2 * math.pi), math.degrees(wrap)


F_LINK = TAU_MOT * 1000.0 / (38 * 5.0 / (2 * math.pi))     # N in the link belt

print("=" * 98)
print("THE FOUR PULLEYS, AND WHAT EACH TOOTH ACTUALLY CARRIES")
print("=" * 98)
print("  link belt force %.1f N, from %.3f N.m at the 38T.  Capstan loop %.0f N."
      % (F_LINK, TAU_MOT, F_CAP))
print()
print("  %-26s %6s %6s %7s %8s %8s %8s %8s"
      % ("", "pitch", "width", "belt N", "in mesh", "N/tooth", "shear", "bending"))
rows = []
for name, teeth, pitch, width, force, n_mesh in (
        ("P2a knee capstan 29T", 29, 8.0, 30.0, F_CAP, 14.5),
        ("A6 idler 29T", 29, 8.0, 30.0, 0.0, 14.5),
        ("motor pulley 38T", 38, 5.0, 15.0, F_LINK, mesh(20, 38, C_LINK, False)[0]),
        ("screw pulley 20T", 20, 5.0, 15.0, F_LINK, mesh(20, 38, C_LINK, True)[0])):
    w = land(teeth, pitch)
    h = FORM[pitch]["h"]
    per = force / n_mesh if n_mesh else 0.0
    shear = per / (w * width)
    bend = (per * h / 2.0) / (width * w ** 2 / 6.0)
    rows.append((name, teeth, pitch, width, per, shear, bend, w, h))
    print("  %-26s %5.0fM %5.0f %7.0f %8.1f %8.1f %7.2f %8.2f"
          % (name, pitch, width, force, n_mesh, per, shear, bend))
print()
print("  against PETG as printed: %.0f MPa shear, %.0f MPa in-plane tensile. The worst tooth in"
      % (PETG_SHEAR, PETG_TENSILE))
worst = max(rows, key=lambda r: r[6])
print("  the machine is the %s at %.2f MPa bending -- a safety factor of %.0f, and it is the"
      % (worst[0], worst[6], PETG_TENSILE / worst[6]))
print("  one that is ALREADY PRINTED. The link-belt pulleys are %.0fx and %.0fx under that."
      % (worst[6] / rows[2][6], worst[6] / rows[3][6]))
print()
print("  So the teeth are not the question, and they never were. 444_capstan_size.py worried")
print("  about tooth load because it was proposing to SHRINK the capstan, where load goes as")
print("  1/T^2. Nothing here shrinks anything.")

print()
print("=" * 98)
print("THE HUB, WHICH IS THE REAL QUESTION")
print("=" * 98)
print("  A printed pulley on a shaft gets its torque in through a grub screw into plastic.")
print()
print("  %-26s %9s %7s %10s %10s" % ("", "torque", "bore", "tangential", "how"))
for name, tau, bore, how in (
        ("P2a knee capstan 29T", TAU_KNEE, None, "bolted to the knee plate on a pattern"),
        ("A6 idler 29T", 0.0, 10.0, "no torque at all -- it only turns the belt round"),
        ("motor pulley 38T", TAU_MOT, 8.0, "grub screw into the 6374's shaft"),
        ("screw pulley 20T", TAU_MOT * (20 / 38.0) * ETA_B, 12.0, "grub screw into the journal")):
    if bore is None:
        print("  %-26s %7.2f Nm %7s %10s   %s" % (name, tau, "--", "--", how))
        continue
    tang = tau * 1000.0 / (bore / 2.0) if tau else 0.0
    print("  %-26s %7.3f Nm %6.0f %9.0f N   %s" % (name, tau, bore, tang, how))
print()
print("  %.0f N tangential on a dia 8 shaft is the number to beat. An M4 brass heat-set insert in"
      % (TAU_MOT * 1000.0 / 4.0))
print("  PETG holds roughly 400 N of pull-out and rather less in a cyclic tangential bearing")
print("  load, so it is a factor of about 1, not 5. Two inserts at 90 degrees onto a FLAT on the")
print("  shaft, with a 20 mm long hub, is the version of this that works. The screw pulley's")
print("  %.0f N on dia 12 is a third of the problem and needs none of that care."
      % (TAU_MOT * (20 / 38.0) * ETA_B * 1000.0 / 6.0))

print()
print("=" * 98)
print("HEAT, AND IT ONLY AFFECTS ONE OF THEM")
print("=" * 98)
print("  PETG's glass transition is about %.0f C. A C6374 worked hard runs its stator past that,"
      % PETG_TG)
print("  and the pulley is clamped to the shaft that leaves the middle of it. Every other pulley")
print("  here is bolted to something at room temperature.")
print()
print("  A printed hub does not fail at Tg, it CREEPS -- the grub screw's dimple deepens, the")
print("  hub loses its grip, and the belt skips. On this machine a skipped link belt means the")
print("  motor's encoder no longer corresponds to the knee angle, and the controller confidently")
print("  drives a leg that is not where it thinks it is. That is the one failure mode in the")
print("  drivetrain that is worse than simply stopping.")
print()
print("  ASA or PC would take it. The project prints PETG.")

print()
print("=" * 98)
print("  THE ANSWER")
print("=" * 98)
print("  PRINT the 20T screw pulley. %.1f N per tooth against the capstan's %.1f, a dia 12 bore"
      % (rows[3][4], rows[0][4]))
print("  with 113 N of tangential load, and nothing near it gets warm. It is also the awkward")
print("  part to buy -- a 20T HTD-5M in a dia 12 bore is not a stock item, and reaming a dia 8")
print("  one out to 12 leaves %.1f mm of wall at the tooth root." % (tip_r(20, 5.0) - FORM[5.0]["h"] - 6.0))
print()
print("  PRINT the 29T idler. It transmits no torque whatsoever. Its bearings take %.0f N, which"
      % T_IDLER)
print("  is a seat problem, not a tooth problem: %.0f N on each of two dia 22 x 7 seats is %.1f"
      % (T_IDLER / 2, T_IDLER / 2 / (22 * 7.0)))
print("  MPa of bearing stress against PETG's %.0f, a factor of %.0f. That is BOM S2b, 25 dollars,"
      % (PETG_BEARING, PETG_BEARING / (T_IDLER / 2 / (22 * 7.0))))
print("  bought for a job with no load in it.")
print()
print("  BUY the 38T motor pulley. Not for its teeth -- they are %.0fx under the capstan's -- but"
      % (rows[0][6] / rows[2][6]))
print("  because it is the only one with a grub screw taking %.0f N into plastic, on the only"
      % (TAU_MOT * 1000.0 / 4.0))
print("  shaft in the machine that gets hot. An aluminium one is 8 dollars and in stock.")
print()
print("  ALL OF IT IS STILL GATED ON TEST_ToothCoupon. 421 is explicit that the HTD form here is")
print("  an approximation of an unpublished curve, and printing three more pulleys from the same")
print("  approximation multiplies that one unknown rather than testing it. Cut the coupon, push a")
print("  real belt into it, and print an HTD-5M coupon too -- the 5M tooth is %.2f mm tall where"
      % FORM[5.0]["h"])
print("  the 8M is %.2f, so the same modelling error is %.0f%% bigger as a fraction of the tooth."
      % (FORM[8.0]["h"], 100 * (FORM[8.0]["h"] / FORM[5.0]["h"] - 1)))
