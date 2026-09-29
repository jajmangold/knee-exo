# -*- coding: utf-8 -*-
"""The screw/nut/tube schedule must close. Key insight: the moment arm formula is
LA*r*sin(angle)/AB, so scaling LA leaves the TORQUE CURVE AND STROKE unchanged while
buying axial room at pin B. Solve for the smallest LA that closes the schedule."""
import math
R, PHI0, AL = 60.0, 135.0, 85.0
ROMx = (-2.0, 105.0)
NUT, BLK_END, PLUG, CLR = 50.0, 50.0, 25.0, 8.0   # ball nut len, screw start, rod-end plug, clearance
def AB(LA, t): return math.sqrt(LA*LA + R*R - 2*LA*R*math.cos(math.radians(PHI0-t)))
def ARM(LA, t): return LA*R*math.sin(math.radians(PHI0-t))/AB(LA, t)
print("LA    | AB_ret AB_ext stroke | arm@60 | threadNd tip  | tang room | closes?")
print("------+---------------------+--------+---------------+-----------+--------")
pick = None
for LA in (250.0, 270.0, 290.0, 300.0, 310.0, 330.0):
    r_, e_ = AB(LA,ROMx[1]), AB(LA,ROMx[0]); st = e_-r_
    T = st + NUT + CLR                     # tube length so the nut stays on thread
    thread_end = BLK_END + st + NUT        # furthest the nut's far face reaches
    tang = r_ - thread_end - CLR           # axial room for the flat tang at full retraction
    ok = tang >= 30.0
    print("%5.0f | %6.1f %6.1f %6.1f | %6.1f | %7.1f %5.1f | %9.1f | %s"
          % (LA, r_, e_, st, ARM(LA,60.0), st+NUT, thread_end, tang, "YES" if ok else "no"))
    if ok and pick is None: pick = LA
print()
LA = pick
r_, e_ = AB(LA,ROMx[1]), AB(LA,ROMx[0]); st = e_-r_
print("ADOPT LA = %.0f mm" % LA)
print("  pin A at (%.1f, %.1f)  -> %.0f%% up a 429 mm thigh" % (LA*math.cos(math.radians(AL)), LA*math.sin(math.radians(AL)), LA*math.sin(math.radians(AL))/429*100))
print("  pin-to-pin %.1f (105 deg) .. %.1f (-2 deg), stroke %.1f mm" % (r_, e_, st))
print("  screw: support block 12-%.0f, thread %.0f-%.0f (%.0f mm)" % (BLK_END, BLK_END, BLK_END+st+NUT, st+NUT))
TUBE = st + NUT + CLR
print("  nut tube length %.0f mm; nut face travels %.0f -> %.0f" % (TUBE, r_-TUBE, e_-TUBE))
print("  tang: %.0f mm of flat blade before pin B (screw tip clears by %.0f mm)"
      % (r_ - (BLK_END+st+NUT) - CLR, r_ - (BLK_END+st+NUT)))
print()
print("  TORQUE CURVE IS UNCHANGED (this is the point):")
print("  %5s %8s %8s" % ("flex","arm mm","tau@600N"))
for t in (0,30,45,60,75,90,105):
    print("  %5d %8.1f %8.1f" % (t, ARM(LA,float(t)), 600*ARM(LA,float(t))/1000))
print()
print("  motor position: pin A rises to Y=%.0f, so the upright box must run to Y~%.0f" % (LA*math.sin(math.radians(AL)), LA*math.sin(math.radians(AL))+40))
