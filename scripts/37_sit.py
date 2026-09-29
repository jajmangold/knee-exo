# -*- coding: utf-8 -*-
"""SITTING CHECK: seated, the posterior thigh rests on the seat. Anything posterior of
the thigh's back surface gets crushed / jacks the leg up."""
import math
O = lambda n: doc.getObject(n)
pose(90.0)   # seated knee angle
R_TH = 78.0  # thigh radius -> posterior skin at X=+78
print("=== seated (knee 90 deg): protrusion BEHIND the posterior thigh line (X=+78) ===")
for n in ("P8_Motor_6374","P7_Actuator_ENVELOPE","P9_GasSpring","P2_ThighUpright_Upper",
          "P1_ThighUpright_Lower","P3_ThighCuff"):
    bb = O(n).Shape.BoundBox
    if bb.XMax > R_TH:
        print("  %-26s reaches X=%6.1f  -> %5.1f mm BEHIND the thigh  (Y %.0f..%.0f)"
              % (n, bb.XMax, bb.XMax-R_TH, bb.YMin, bb.YMax))
print("  => the 6374 alone lifts the thigh ~43 mm off the seat. Unusable.")
print()
print("=== FIX: swing the whole linkage ANTERIOR (alpha 85->110, beta0 -50->+135) ===")
LA2, R2 = 300.0, 60.0
AL2, PHI2 = 110.0, -25.0          # alpha, and (beta0-alpha)=+25 -> TENSION branch
def ab2(t):  return math.sqrt(LA2**2+R2**2-2*LA2*R2*math.cos(math.radians(25.0+t)))
def arm2(t): return LA2*R2*math.sin(math.radians(25.0+t))/ab2(t)
A2 = (LA2*math.cos(math.radians(AL2)), LA2*math.sin(math.radians(AL2)))
B2 = lambda t: (R2*math.cos(math.radians(AL2+25.0+t)), R2*math.sin(math.radians(AL2+25.0+t)))
print("  pin A = (%.1f, %.1f)   anterior thigh skin is at X=-78 -> stands %.0f mm proud"
      % (A2[0], A2[1], -78-A2[0]))
print("  pin B at 0 deg = (%.1f, %.1f)  crank now points ANTERIOR-PROXIMAL" % B2(0.0))
print("  actuator is in TENSION to extend  (ball screw takes tension fine)")
print("  singularity at theta=155 deg -> %d deg past the 105 deg stop" % (155-105))
print()
print("  %5s %8s %9s %10s | posterior-most point of the A-B line" % ("flex","arm mm","AB mm","tau@600N"))
for t in (-2,0,30,50,65,90,105):
    a_,l_ = arm2(float(t)), ab2(float(t))
    bp = B2(float(t)); xmax = max(A2[0], bp[0])
    print("  %5d %8.1f %9.1f %9.1f | X=%6.1f  %s" % (t, a_, l_, 600*a_/1000, xmax,
          "clear of seat" if xmax < R_TH else "HITS SEAT"))
print()
print("  stroke %.1f mm (was 96.5) - same actuator" % (ab2(105.0)-ab2(-2.0)))
print("  peak arm %.1f mm at ~65 deg - still lands on the stair/STS demand peak" % arm2(65.0))
print()
print("  CONSEQUENCE: a gas spring PUSHES, which in this layout drives FLEXION - wrong way.")
print("  The parallel spring must now PULL. Which is exactly your bungee, anterior, and")
print("  laterally offset at Z~108 so it never touches the patella.")
for F in (150.0, 250.0):
    print("    %3.0f N elastic -> %.1f N.m at 65 deg, %.1f N.m at 90 deg" % (F, F*arm2(65.0)/1000, F*arm2(90.0)/1000))
