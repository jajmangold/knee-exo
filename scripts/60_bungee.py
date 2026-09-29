# -*- coding: utf-8 -*-
"""Would an elastic help STAIRS? Energy accounting, ascent vs descent."""
import math
M = 80.0
# --- elastic linkage: anchor E on the upright, pin G on a second crank arm ---
L_E, B_E = 250.0, 85.0        # anchor r, bearing
R_G, B_G = 50.0, 115.0        # crank pin r, bearing at theta=0
DEL = B_G - B_E               # +30 -> length GROWS with flexion => tension assists EXTENSION
def eln(t):  return math.sqrt(L_E**2+R_G**2-2*L_E*R_G*math.cos(math.radians(DEL+t)))
def earm(t): return L_E*R_G*math.sin(math.radians(DEL+t))/eln(t)
FREE = 200.0                                    # unstretched length
def strain(t): return (eln(t)-FREE)/FREE
K = 1550.0                                      # N per unit strain (tuned below)
def force(t): return max(0.0, K*strain(t))
print("elastic geometry: anchor r%.0f@%.0f deg, crank pin r%.0f@%.0f deg, delta=%+.0f"%(L_E,B_E,R_G,B_G,DEL))
print("%5s %8s %8s %8s %9s %9s"%("flex","len mm","strain","arm mm","F N","tau N.m"))
for t in (0,15,30,45,60,75,90,105):
    print("%5d %8.1f %7.0f%% %8.1f %9.0f %9.1f"%(t,eln(float(t)),strain(float(t))*100,
          earm(float(t)),force(float(t)),force(float(t))*earm(float(t))/1000))
print()
# --- energy stored between two knee angles ---
def energy(a,b,n=400):
    tot=0.0; step=(b-a)/n
    for i in range(n):
        t=a+step*(i+0.5)
        tot += force(t)*earm(t)/1000.0 * math.radians(abs(step))
    return tot
print("=== STAIR DEMAND (80 kg, literature peaks) ===")
for k,v,rng in (("ascent",1.05,(10,75)), ("descent",1.15,(10,90))):
    print("  %-8s peak knee moment %5.1f N.m, knee works %d->%d deg"%(k,v*M,*rng))
print()
E_asc = energy(10.0,75.0); E_desc = energy(10.0,90.0)
print("=== WHAT THE ELASTIC DOES ===")
print("  ASCENT  : knee EXTENDS under load 75->10 deg, elastic returns %.1f J/step"%E_asc)
print("            but it was stretched during SWING flexion -> %.1f J taken from hip flexors"%E_asc)
print("            peak assist at 60 deg: %.1f N.m = %.0f%% of the %.0f N.m ascent demand"
      %(force(60.)*earm(60.)/1000, force(60.)*earm(60.)/10/(1.05*M), 1.05*M))
print("  DESCENT : knee FLEXES under load 10->90 deg, elastic ABSORBS %.1f J/step"%E_desc)
print("            that is eccentric braking - exactly what a deconditioned quad cannot do,")
print("            and it costs nothing: no current, no heat, instant response.")
print("            peak resist at 75 deg: %.1f N.m = %.0f%% of the %.0f N.m descent demand"
      %(force(75.)*earm(75.)/1000, force(75.)*earm(75.)/10/(1.15*M), 1.15*M))
print()
print("=== THE COST: it fights swing-phase flexion ===")
E_sw = energy(5.0,95.0)
print("  level-walk swing needs ~60 deg flexion; stair swing ~95 deg")
print("  work to stretch it through 5->95 deg: %.1f J per step, from the hip flexors"%E_sw)
print("  resisting torque at 60 deg swing: %.1f N.m (biological swing-flex moment is only ~5-15 N.m)"
      %(force(60.)*earm(60.)/1000))
print("  -> on LEVEL ground this is a real penalty. It wants a clutch.")
print()
print("=== SIZING REALITY at %.0f N peak ==="%force(105.))
Fp=force(105.)
for name,sig in (("latex bungee @44%% strain",0.60),("natural rubber cord",0.90)):
    print("  %-26s needs %6.0f mm2 = %.1f x 19 mm cords"%(name,Fp/sig,(Fp/sig)/283.5))
print("  %-26s 2 springs, ~%.0f N each, 90 mm travel - fits inside the hollow upright"
      %("steel extension springs",Fp/2))
print("  latex also has ~25%% hysteresis and creeps; steel is <5%% and stable.")
print()
print("=== vs JUST USING THE MOTOR ===")
KT=8.27/190.0; FA=2*math.pi*0.90*KT/0.020
print("  motor alone at 40 A gives %.1f N.m at 60 deg (%.0f%% of ascent demand)"
      %(FA*40*arm(60.)/1000, FA*40*arm(60.)/10/(1.05*M)))
print("  motor CAN also brake on descent and regen ~%.0f J/step - but it burns"%(E_desc*0.8))
print("  ~144 W doing it, and that is the thermal limit on repeated flights.")
