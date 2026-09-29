# -*- coding: utf-8 -*-
import math
KV, KT, R_PH, J_ROT = 190.0, 8.27/190.0, 0.030, 2.5e-4
LEAD, ETA = 20.0, 0.90
N = (arm(60)/1000.0)/(LEAD/1000.0)*2*math.pi
print("="*74); print("1.  DOES IT BACKDRIVE?"); print("="*74)
lam = math.degrees(math.atan(LEAD/(math.pi*20.0)))
for nm, mu in (("BALL screw (rolling)",0.005), ("ACME/trapezoid (sliding)",0.20)):
    phi = math.degrees(math.atan(mu))
    bd = math.tan(math.radians(lam-phi))/math.tan(math.radians(lam)) if lam>phi else 0.0
    print("  %-26s lead angle %.1f deg vs friction angle %5.2f deg -> %s (eta_back %.2f)"
          % (nm, lam, phi, "BACKDRIVES" if lam>phi else "LOCKS - will NOT backdrive", bd))
print()
T_COG = 0.05
print("  what the patient actually feels at the knee (breakaway):")
items = [("motor cogging", T_COG*N*0.89), ("screw+seal friction", 15.0*arm(60)/1000.0),
         ("bearings + belt drag", 0.02*N*0.89)]
tot = sum(v for _,v in items)
for k,v in items: print("     %-24s %5.2f N.m" % (k, v))
print("     %-24s %5.2f N.m   (a hinged knee brace is ~1-3 N.m)" % ("TOTAL", tot))
print("  dynamic: reflected rotor inertia %.3f kg.m2 = +%.0f%% of shank swing inertia"
      % (J_ROT*N**2, J_ROT*N**2/0.29*100))
print("  -> passively backdrivable; ODrive anticogging + zero-impedance current control")
print("     cuts the %.1f N.m well below 1 N.m. Power-off = IDLE = phases open = leg free." % tot)
print("     NOTE: this is ONLY true for a BALL screw. An ACME leadscrew locks solid ->")
print("     knee frozen mid-stride on a fault. Non-negotiable spec item.")
print()
print("="*74); print("2.  YOUR IDEA: ANTERIOR BUNGEE + POSTERIOR MOTOR TENDON"); print("="*74)
STANDOFF = 50.0
for tau in (15.0, 25.0):
    F = tau*1000/STANDOFF
    print("  %2.0f N.m extension via a tendon %d mm anterior of the knee axis -> %4.0f N tension"
          % (tau, STANDOFF, F))
F25 = 25*1000/STANDOFF
print("  at 90 deg flexion the tendon wraps ~90 deg -> resultant into the patella")
print("     = 2 x %.0f x sin45 = %.0f N ON THE EXTENSOR MECHANISM (post-op tissue)" % (F25, 2*F25*math.sin(math.radians(45))))
lat = 78.5*2.0
print("  bungee capability: 10 mm latex = %.0f mm2 @ ~2 MPa = ~%.0f N each -> need %.1f in parallel"
      % (78.5, lat, F25/lat))
print("  latex hysteresis ~25%% (vs <5%% gas spring) + creep/UV -> poor energy return, drifts")
print()
print("  DIRECTION PROBLEM: your deficit is EXTENSION (quad). A posterior motor tendon makes")
print("  FLEXION, so the motor antagonises the spring - it must hold ~%.0f N.m continuously" % 18.0)
print("  just to let the patient sit down. That is the worst case for heat, not the best.")
print()
print("="*74); print("3.  SAME IDEA, BETTER PLACED: gas spring on the crank I already have"); print("="*74)
print("  a COMPRESSION spring A->B lengthens on extension, so it assists EXTENSION, and")
print("  AB shortens with flexion -> spring compresses -> force RISES exactly when needed.")
print("  %5s %8s %10s %12s %12s %10s" % ("flex","arm mm","AB mm","Fgas N","tau_spring","motor A"))
for th in (0,30,45,60,75,90,105):
    ab_t = ab(float(th)); comp = (ab(-2.0)-ab_t)
    F = 200.0*(1.0+0.30*comp/99.5)                    # 200 N gas spring, +30% progressive
    ts = F*arm(float(th))/1000.0
    need = max(0.0, 25.0-ts)
    amp = need*1000/arm(float(th))/(2*math.pi*ETA*KT/(LEAD/1000.0))
    print("  %5d %8.1f %10.1f %12.0f %12.1f %10.1f" % (th, arm(float(th)), ab_t, F, ts, amp))
print()
b = 49.0**2*R_PH*2; a2 = 24.0**2*R_PH*2
print("  motor current for 25 N.m at 60 deg: %.0f A alone -> %.0f A with the spring" % (49, 13))
print("  copper loss %.0f W -> %.0f W  (%.1fx less heat). Spring also supplies the fast" % (b, 13**2*R_PH*2, b/(13**2*R_PH*2)))
print("  transient the motor cannot, and brakes the knee on stair DESCENT for free.")
print("  COST: it resists swing-phase flexion, so keep it modest (150-200 N) or clutch it.")
print()
print("="*74); print("4.  IF YOU WANT TO DROP THE BALLSCREW: belt straight to the knee"); print("="*74)
for st, r in (("1-stage 15T->60T", 4.0), ("2-stage 15T->60T x2", 16.0), ("2-stage 14T->72T x2", 26.4)):
    tq = KT*49.0*r*0.95**2; J = J_ROT*r*r
    print("  %-22s %4.1f:1  tau=%5.1f N.m @49A  J_refl=%.3f (+%3.0f%%)  belt tension %4.0f N"
          % (st, r, tq, J, J/0.29*100, tq/0.048))
print("  constant moment arm, no toggle singularity, fully backdrivable, cheap.")
print("  needs a ~96 mm pulley concentric with the knee axis + a 2-stage housing on the thigh.")
