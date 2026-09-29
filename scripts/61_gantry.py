# -*- coding: utf-8 -*-
"""GANTRY ARCHITECTURE: extrusion along the lateral thigh, carriage C slides along it,
8 mm rod from C to pivot D on the shank cuff. Knee = hinge at origin. Slider-crank where
the CRANK IS THE SHANK ITSELF, so the moment arm is huge and grows with flexion."""
import math
M, ROMd = 80.0, (-2.0, 105.0)
def rot(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t))
    return (p[0]*c-p[1]*s, p[0]*s+p[1]*c)
def solve(xe, D0, Lrod, t):
    """carriage height s and moment arm at flexion t"""
    D=rot(D0,t); dd=Lrod*Lrod-(xe-D[0])**2
    if dd<0: return None
    s=D[1]+math.sqrt(dd)                       # carriage above the shank pivot
    C=(xe,s); L=math.hypot(C[0]-D[0],C[1]-D[1])
    ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    arm=abs(D[0]*uy-D[1]*ux)                   # perp distance from knee axis to rod line
    return s,arm,C,D
print("%-34s %8s %8s %8s %8s %8s"%("variant","travel","arm@0","arm@45","arm@90","arm@105"))
VAR=[("D 200 below knee, rail +40 post", 40.0,(30.0,-200.0)),
     ("D 160 below knee, rail +40 post", 40.0,(30.0,-160.0)),
     ("D 160 below knee, rail  0",        0.0,(30.0,-160.0)),
     ("D 120 below knee, rail +40 post", 40.0,(25.0,-120.0)),
     ("D  90 below knee, rail +40 post", 40.0,(20.0, -90.0))]
res={}
for name,xe,D0 in VAR:
    s0=solve(xe,D0,1e9,0.0)
    Lrod=math.hypot(xe-D0[0], 90.0-D0[1])      # carriage 90 mm above knee at full ext
    pts={}
    ok=True
    for t in (ROMd[0],0,45,90,105):
        r=solve(xe,D0,Lrod,float(t))
        if r is None: ok=False; break
        pts[t]=r
    if not ok: print("%-34s  no solution"%name); continue
    trav=pts[105][0]-pts[ROMd[0]][0]
    res[name]=(Lrod,xe,D0,pts,trav)
    print("%-34s %7.0f mm %7.0f %8.0f %8.0f %8.0f"
          %(name,trav,pts[0][1],pts[45][1],pts[90][1],pts[105][1]))
print()
name="D 160 below knee, rail +40 post"
Lrod,xe,D0,pts,trav=res[name]
print("=== detail: %s  (rod %.0f mm, travel %.0f mm) ==="%(name,Lrod,trav))
KT=8.27/190.0; LEAD=20.0; ETA=0.9
FA=2*math.pi*ETA*KT/(LEAD/1000.0)
J_ROT, J_LIMB = 2.5e-4, 0.29
print("%5s %8s %9s %9s %8s %9s %10s"%("flex","carr mm","arm mm","F for 25Nm","amps","n ratio","J_refl"))
for t in (0,15,30,45,60,75,90,105):
    s,arm,C,D=solve(xe,D0,Lrod,float(t))
    F=25000.0/arm; amps=F/FA
    n=(arm/1000.0)/(LEAD/1000.0)*2*math.pi
    print("%5d %8.1f %9.1f %9.0f N %7.1f %9.1f %8.3f (+%.0f%%)"
          %(t,s,arm,F,amps,n,J_ROT*n*n,J_ROT*n*n/J_LIMB*100))
print()
print("=== 8 mm stainless rod, COMPRESSION to extend ===")
I=math.pi*8**4/64; Pcr=math.pi**2*200000*I/(Lrod**2)
s,arm0,_,_=solve(xe,D0,Lrod,0.0)
print("  Pcr = %.0f N (pinned-pinned, L=%.0f)  worst load %.0f N at full extension -> SF %.0f"
      %(Pcr,Lrod,25000.0/arm0,Pcr/(25000.0/arm0)))
print()
print("=== SPEED (swing 300 deg/s) ===")
for t in (30.0,60.0,90.0):
    s,arm,_,_=solve(xe,D0,Lrod,t)
    v=arm*math.radians(300.0)
    print("  at %3.0f deg: carriage %5.0f mm/s -> ballscrew(20mm) %5.0f rpm  |  GT2-20T belt %5.0f rpm"
          %(t,v,v/LEAD*60,v/40.0*60))
print()
print("=== vs the current v3 ballscrew+crank ===")
print("  %-26s %10s %10s"%("","v3 crank","gantry"))
print("  %-26s %9.0f %10.0f"%("moment arm @60 deg (mm)",59.8,solve(xe,D0,Lrod,60.0)[1]))
print("  %-26s %9.0f %10.0f"%("force for 25 N.m @60 (N)",25000/59.8,25000/solve(xe,D0,Lrod,60.0)[1]))
print("  %-26s %9.1f %10.1f"%("amps for 25 N.m @60",25000/59.8/FA,25000/solve(xe,D0,Lrod,60.0)[1]/FA))
print("  %-26s %9.0f %10.0f"%("copper loss @that (W)",(25000/59.8/FA)**2*0.03*2,(25000/solve(xe,D0,Lrod,60.0)[1]/FA)**2*0.03*2))
n3=(59.8/1000)/(LEAD/1000)*2*math.pi; ng=(solve(xe,D0,Lrod,60.0)[1]/1000)/(LEAD/1000)*2*math.pi
print("  %-26s %9.0f%% %9.0f%%"%("added swing inertia",J_ROT*n3*n3/J_LIMB*100,J_ROT*ng*ng/J_LIMB*100))
print("  %-26s %9.0f %10.0f"%("actuator travel (mm)",96.5,trav))
