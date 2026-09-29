# -*- coding: utf-8 -*-
"""Knee exo slider-crank kinematics solver + verification table."""
import math

# ---- patient / task ----
M_BODY   = 80.0      # kg  (design mass; range 60-100)
ASSIST   = 0.30       # fraction of biological knee moment to supply
# peak biological knee EXTENSION moment, N.m/kg  (literature ranges)
DEMAND = {"level walk": 0.45, "stair ascent": 1.05, "stair descent": 1.15, "sit-to-stand": 1.20}

# ---- mechanism ----
LA      = 250.0       # mm  knee axis -> actuator upper pin A
R_CRANK =  60.0       # mm  knee axis -> actuator lower pin B (crank horn)
PHI0    = 135.0       # deg  angle AOB at full extension (=> singularity at theta=PHI0)
ALPHA   =  85.0       # deg  bearing of OA from +X(posterior), CCW  (A near-proximal)
BETA0   = ALPHA - PHI0  # deg bearing of OB at theta=0  => -50 deg (posterior-distal)
ROM     = (-2.0, 110.0)  # deg hard mechanical stops (hyperext. block, flexion block)
F_ACT   = 600.0       # N   actuator rated dynamic force

def ab(th):      # pin-to-pin length at flexion angle th (deg)
    phi = math.radians(PHI0 - th)
    return math.sqrt(LA*LA + R_CRANK*R_CRANK - 2*LA*R_CRANK*math.cos(phi))
def arm(th):     # actuator moment arm about knee axis (mm)
    phi = math.radians(PHI0 - th)
    return LA*R_CRANK*math.sin(phi)/ab(th)
def pin_a():
    a = math.radians(ALPHA);  return (LA*math.cos(a), LA*math.sin(a))
def pin_b(th):
    b = math.radians(BETA0 + th);  return (R_CRANK*math.cos(b), R_CRANK*math.sin(b))

L_RET, L_EXT = ab(ROM[1]), ab(ROM[0])
print(f"=== MECHANISM ===============================================")
print(f"pin A (knee-relative, X=post Y=prox) = ({pin_a()[0]:7.2f}, {pin_a()[1]:7.2f}) mm")
print(f"pin B at full extension              = ({pin_b(0)[0]:7.2f}, {pin_b(0)[1]:7.2f}) mm")
print(f"ROM {ROM[0]:+.0f}..{ROM[1]:.0f} deg   singularity (toggle) at {PHI0:.0f} deg -> margin {PHI0-ROM[1]:.0f} deg")
print(f"actuator pin-to-pin: {L_RET:.1f} (at {ROM[1]:.0f}d) .. {L_EXT:.1f} mm (at {ROM[0]:+.0f}d)  => STROKE {L_EXT-L_RET:.1f} mm")
print(f"actuator is in COMPRESSION to extend the knee (length grows as knee extends)")
print()
print(f"=== TORQUE vs FLEXION  (actuator {F_ACT:.0f} N) =================")
print(f"{'flex':>5} {'arm':>7} {'pin-pin':>8} {'stroke':>7} {'tau@600N':>9}")
for th in [-2,0,10,20,30,45,60,75,90,100,110]:
    print(f"{th:>5.0f} {arm(th):>7.1f} {ab(th):>8.1f} {ab(th)-L_RET:>7.1f} {F_ACT*arm(th)/1000:>9.1f}")
print()
print(f"=== DEMAND vs SUPPLY  (M={M_BODY:.0f} kg, target {ASSIST*100:.0f}% assist) ====")
print(f"{'task':>14} {'peak tau':>9} {'target':>8} {'F needed@60d':>13} {'F needed@90d':>13}")
for k,v in DEMAND.items():
    tau = v*M_BODY; tgt = tau*ASSIST
    print(f"{k:>14} {tau:>8.0f}N.m {tgt:>7.0f}N.m {tgt/arm(60)*1000:>12.0f}N {tgt/arm(90)*1000:>12.0f}N")
print()
# speed requirement
print(f"=== SPEED ===================================================")
for name, d0, d1, t in [("sit-to-stand (90->0d)",90,0,2.5),("stair step (60->0d)",60,0,1.4),("swing (0->60d)",0,60,0.45)]:
    ds = abs(ab(d1)-ab(d0))
    print(f"{name:>24}: {ds:5.1f} mm in {t:.2f} s  ->  {ds/t:5.1f} mm/s")
print()
print(f"=== STRUCTURE (design torque) ================================")
TAU_D = 35.0   # N.m working design torque
print(f"working design torque      {TAU_D:.0f} N.m  (= {F_ACT:.0f} N x {arm(45):.0f} mm arm at 45 deg)")
for name, L in [("thigh cuff", 230.0), ("shank cuff", 200.0)]:
    print(f"  force at {name:<11} (arm {L:.0f} mm): {TAU_D*1000/L:6.0f} N")
