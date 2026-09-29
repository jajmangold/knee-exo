# -*- coding: utf-8 -*-
"""Seated, the seat plane sits under the thigh. ANY point on the shank at distance d from
the knee swings to X = d*cos(bearing0+theta) -- at 90 deg that is ~d posterior, regardless
of how it is offset. So the rod pivot distance is capped by the seat."""
import math
def Rthigh(y): return 62.0+ (85.0-62.0)*max(0.0,min(y,300.0))/300.0   # thigh radius vs height
SEAT_FROM = 60.0        # seat front edge ~60 mm proximal of the knee
def pen(D0,t):
    """max penetration of the rod line below the seat plane, at flexion t"""
    D=rot2(D0,t); s=carr2(D0,t); C=(XE,s)
    worst=0.0
    for i in range(61):
        f=i/60.0
        x=D[0]+(C[0]-D[0])*f; y=D[1]+(C[1]-D[1])*f
        if y<SEAT_FROM: continue
        worst=max(worst, x-Rthigh(y))
    return worst
def carr2(D0,t):
    L=math.hypot(XE-D0[0], 43.7-D0[1])
    D=rot2(D0,t); dd=L*L-(XE-D[0])**2
    return None if dd<0 else D[1]+math.sqrt(dd)
def arm2(D0,t):
    D=rot2(D0,t); s=carr2(D0,t)
    if s is None: return None
    C=(XE,s); L=math.hypot(C[0]-D[0],C[1]-D[1])
    return abs(D[0]*(C[1]-D[1])/L - D[1]*(C[0]-D[0])/L)
print("current design D=(30,-120), |D|=%.0f mm from the knee:"%math.hypot(30,120))
for t in (85.,90.,95.,100.,105.):
    print("   theta %3.0f: rod dips %5.1f mm below the seat plane"%(t,pen((30.0,-120.0),t)))
print()
print("=== how far below the knee can the rod pivot go? ===")
print("%6s %7s | %7s %7s %7s | %8s %8s"%("|D|","Dy","pen@90","pen@100","pen@105","arm@60","arm@90"))
ok_max=None
for mag in (60.,70.,80.,90.,100.,110.,124.):
    Dy=-math.sqrt(max(mag*mag-25.0**2,1.0)); D0t=(25.0,Dy)
    p90,p100,p105 = pen(D0t,90.), pen(D0t,100.), pen(D0t,105.)
    a60,a90 = arm2(D0t,60.), arm2(D0t,90.)
    clear = max(p90,p100,p105)<=0.0
    print("%6.0f %7.0f | %7.1f %7.1f %7.1f | %8.0f %8.0f %s"
          %(mag,Dy,p90,p100,p105,a60,a90,"CLEAR" if clear else ""))
    if clear: ok_max=(mag,Dy,a60,a90)
print()
if ok_max:
    mag,Dy,a60,a90=ok_max
    KT=8.27/190.0; FA=2*math.pi*0.9*KT/0.020
    print("largest seat-clearing pivot: |D|=%.0f mm  ->  arm@60 = %.0f mm, F=%.0f N, %.0f A"
          %(mag,a60,25000/a60,25000/a60/FA))
    print("compare v3 crank: arm@60 = 60 mm, F=418 N, 34 A")
    print("compare the 120 mm gantry (seat-fouling): arm@60 = 88 mm, F=283 N, 23 A")
print()
print("=> respecting the seat collapses the gantry's moment-arm advantage back toward v3.")
print("   its remaining wins are STRUCTURAL: off-the-shelf rail, prismatic joint carries")
print("   the bending, no crank-horn packaging, and 658 g printed vs 1196 g.")
