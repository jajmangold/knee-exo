# -*- coding: utf-8 -*-
"""Shrink the knee capstan to pay for a 5 mm lead? The ratio works. The belt is what stops it.

Asked at the bench: "can't we lower the screw speed by making the knee smaller".

Yes, exactly -- and the arithmetic is unusually clean, because the capstan is a toothed pulley:

    2*pi*R = T * 8          (T teeth of 8 mm pitch)
    N_screw = 2*pi*R / lead = T * 8 / lead

So the capstan's TOOTH COUNT and the screw's LEAD trade one for one. A 15T capstan on a 5 mm
lead gives exactly the ratio a 29T capstan gives on a 10 mm lead. The screw turns at the same
speed, the motor sees the same reflected inertia, and the whole sourcing problem evaporates.

WHAT IT COSTS IS THE ONE LOOP THIS PROJECT HAS ALREADY REFUSED TO LOAD. 403_stepped_idler.py put
it plainly: the capstan loop "carries 764 N, and multiplying it breaks the belt, the nut and the
bracket at once". That force is tau/R, so shrinking R multiplies it -- and it gets worse than
linear, because a smaller pulley also has fewer teeth in mesh to share it.

    force per tooth  =  (tau / R) / (T / 2)      at a 180 degree wrap

and with 2*pi*R = 8T that is proportional to 1/T^2. Halve the capstan and each tooth takes four
times the load -- on PRINTED PETG teeth whose profile 421_pulley_teeth.py describes as an
approximation of the HTD curvilinear form, still waiting on the coupon test.

    python scripts/444_capstan_size.py
"""
import math

PITCH = 8.0
TAU_KNEE = 28.2
ETA_S, ETA_B = 0.90, 0.97
J_ROTOR, J_LIMB = 3.10e-4, 0.30
KT = 9.549 / 170.0
I_CONT = 40.0
BELT_W = 30.0                   # mm, HTD-8M
PIN_D, COLLAR_D = 12.3, 20.0    # the capstan's bore and its collar counterbore
TOOTH_H, PLD = 3.38, 0.686


def radius(t):
    return t * PITCH / (2 * math.pi)


def root(t):
    return radius(t) - PLD - TOOTH_H


print("=" * 100)
print("SHRINKING THE KNEE CAPSTAN")
print("=" * 100)
print("  2*pi*R = T*8, so N_screw = T*8/lead exactly. 29T on a 10 mm lead and 15T on a 5 mm")
print("  lead are the SAME ratio -- the capstan's teeth and the screw's lead are interchangeable.")
print()
base_t, base_lead, od = 29, 10.0, 32 / 20.0
base_f = TAU_KNEE * 1000.0 / radius(base_t)
base_tooth = base_f / (base_t / 2.0)
base_n = base_t * PITCH / base_lead / od
print("  as built: %dT, %.0f mm lead, %.1f:1 link  ->  %.1f:1 total, %.0f N in the belt,"
      % (base_t, base_lead, od, base_n, base_f))
print("            %.0f N per tooth over %.1f teeth in mesh, %.3f kg.m2 reflected (%.2fx limb)"
      % (base_tooth, base_t / 2.0, J_ROTOR * base_n ** 2, J_ROTOR * base_n ** 2 / J_LIMB))
print()
print("  %-28s %7s %8s %9s %9s %8s %8s"
      % ("5 mm lead, capstan + link", "N tot", "refl J", "vs limb", "belt N", "N/tooth", "idler N"))
rows = []
for t in (29, 27, 25, 23, 21, 19, 17, 15):
    for mt in (32, 38):
        o = mt / 20.0
        n = t * PITCH / 5.0 / o
        f = TAU_KNEE * 1000.0 / radius(t)
        per = f / (t / 2.0)
        j = J_ROTOR * n ** 2
        amps = TAU_KNEE / (n * ETA_S * ETA_B) / KT
        rows.append((t, mt, n, j, f, per, amps))
        flag = ""
        if per > 2.0 * base_tooth:
            flag = "  <-- %.1fx the tooth load" % (per / base_tooth)
        elif j / J_LIMB > 0.5:
            flag = "  <-- %.2fx the limb" % (j / J_LIMB)
        elif amps > I_CONT:
            flag = "  <-- over %.0f A" % I_CONT
        print("  %-28s %6.1f:1 %8.3f %8.2fx %8.0f %8.0f %8.0f%s"
              % ("%dT capstan + %dT:20T" % (t, mt), n, j, j / J_LIMB, f, per, 2 * f, flag))

print()
print("=" * 100)
print("  THE FLOOR, which is not the ratio")
for t in (17, 15, 13):
    print("     %2dT: pitch radius %.1f, tooth root at r %.1f, and the hub has to clear a %.1f mm"
          % (t, radius(t), root(t), COLLAR_D))
    print("          collar on a %.1f mm pin -- %.1f mm of material between the collar and the"
          % (PIN_D, root(t) - COLLAR_D / 2.0))
    print("          tooth roots" + ("" if root(t) - COLLAR_D / 2.0 > 3.0 else "   <-- too thin"))
print()
print("  And the belt itself: %.0f N over %.0f mm is %.1f N/mm as built. The same torque on a"
      % (base_f, BELT_W, base_f / BELT_W))
for t in (19, 15):
    f = TAU_KNEE * 1000.0 / radius(t)
    print("  %dT capstan is %.0f N -- %.1f N/mm, with %.1f teeth in mesh instead of %.1f."
          % (t, f, f / BELT_W, t / 2.0, base_t / 2.0))

print()
print("=" * 100)
print("  WHAT I WOULD ACTUALLY DO")
print()
print("  Nothing here is free, but the costs are in different currencies. A smaller capstan pays")
print("  for the lead in BELT TOOTH LOAD, on printed teeth that have never been tested -- the")
print("  tooth coupon exists precisely because that profile is an approximation. A bigger motor")
print("  pulley pays for it in REFLECTED INERTIA, which is measured, understood and recoverable")
print("  later by changing one bought pulley.")
print()
print("  A middle option is real, though: 23T with a 38T:20T link lands at %.1f:1 and %.2fx the"
      % ([r for r in rows if r[0] == 23 and r[1] == 38][0][2],
         [r for r in rows if r[0] == 23 and r[1] == 38][0][3] / J_LIMB))
print("  limb, for %.0fx the tooth load rather than %.0fx. That is the knee hub, the idler, the"
      % ([r for r in rows if r[0] == 23 and r[1] == 38][0][5] / base_tooth,
         [r for r in rows if r[0] == 15 and r[1] == 32][0][5] / base_tooth))
print("  belt length and the gantry's tunnel all redrawn -- the most verified part of the")
print("  machine -- so it is worth it only if the coupon test says the printed teeth are strong.")
print()
print("  Print the coupon first. It decides this.")
