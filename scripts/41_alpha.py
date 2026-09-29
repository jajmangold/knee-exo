# -*- coding: utf-8 -*-
"""How far anterior does pin A actually need to go? DELTA (=beta0-alpha) sets the torque
curve; ALPHA just rotates the whole linkage. Find the smallest ALPHA that clears the seat
while keeping the upright VERTICAL (v1 geometry) and the bracket to pin A short."""
import math
LA2, R2, DEL = 300.0, 60.0, 25.0
def ab2(t): return math.sqrt(LA2**2+R2**2-2*LA2*R2*math.cos(math.radians(DEL+t)))
def arm2(t): return LA2*R2*math.sin(math.radians(DEL+t))/ab2(t)
print("alpha | pinA (x,y)      | bracket | max X on A-B line | motor X (ant. offset 62)")
print("------+-----------------+---------+-------------------+------------------------")
for AL in (85.0, 90.0, 95.0, 100.0, 110.0):
    A=(LA2*math.cos(math.radians(AL)), LA2*math.sin(math.radians(AL)))
    brk = abs(A[0])                       # reach from a vertical upright axis (x=0)
    xs=[]
    for t in (-2.0,0.0,30.0,60.0,90.0,105.0):
        B=(R2*math.cos(math.radians(AL+DEL+t)), R2*math.sin(math.radians(AL+DEL+t)))
        xs += [A[0], B[0]]
    mx=max(xs)
    # motor sits anterior of the screw axis by 62 mm, near pin A
    mot_x = A[0]-62.0+31.5
    print("%5.0f | (%6.1f,%6.1f) | %6.1f  | %8.1f %-8s | %6.1f %s"
          % (AL, A[0], A[1], brk, mx, "CLEAR" if mx < 60 else "SEAT", mot_x,
             "clear" if mot_x < 60 else "SEAT"))
print()
print("torque curve is identical for every row (DELTA fixed at 25 deg):")
print("  stroke %.1f mm, arm %.1f@30 %.1f@65 %.1f@90 %.1f@105"
      % (ab2(105.0)-ab2(-2.0), arm2(30.0), arm2(65.0), arm2(90.0), arm2(105.0)))
print()
AL=95.0; A=(LA2*math.cos(math.radians(AL)), LA2*math.sin(math.radians(AL)))
print("ADOPT alpha=95: pin A (%.1f, %.1f), beta0=%.0f" % (A[0], A[1], AL+DEL))
print("  upright stays VERTICAL up the lateral thigh (v1 geometry, cuffs unchanged)")
print("  bracket to pin A is only %.0f mm - not a 103 mm cantilever" % abs(A[0]))
for t in (-2.0,105.0):
    B=(R2*math.cos(math.radians(AL+DEL+t)), R2*math.sin(math.radians(AL+DEL+t)))
    print("  theta=%+4.0f  pin B=(%6.1f,%6.1f)  bearing %.0f" % (t,B[0],B[1],(AL+DEL+t)%360))
print()
print("swept-envelope bearings at r=60 (drives where plates/bumper can live):")
b0=AL+DEL
print("  crank horn  %.0f..%.0f  (+/-13.5 half-width) -> %.0f..%.0f" % (b0-2,b0+105,b0-2-13.5,b0+105+13.5))
print("  shank strut %.0f..%.0f  (+/-21.5)            -> %.0f..%.0f" % (268,375,246.5,396.5-360))
print("  actuator near-knee path bearings ~118..177 -> fork plate must skip that band")
