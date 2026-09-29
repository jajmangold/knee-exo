# -*- coding: utf-8 -*-
"""Pick rail offset xe, rod pivot D, and carriage start s0 to minimise extrusion length
(hip clearance when seated) while keeping arm@0 usable and arm@60 high."""
import math
ROMd=(-2.0,105.0); HIP=429.0
def rot(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
def geom(xe,D0,s0):
    Lrod=math.hypot(xe-D0[0], s0-D0[1]); out={}
    for t in (ROMd[0],0,30,60,90,105):
        D=rot(D0,t); dd=Lrod*Lrod-(xe-D[0])**2
        if dd<0: return None
        s=D[1]+math.sqrt(dd); C=(xe,s)
        L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
        out[t]=(s, abs(D[0]*uy-D[1]*ux))
    return Lrod,out
KT=8.27/190.0; FA=2*math.pi*0.9*KT/0.020; J=2.5e-4
NUTB, MOT = 55.0, 90.0          # nut+bearing allowance above the carriage top, motor+coupling
print("%3s %5s %5s | %6s %6s %6s %6s | %6s %7s %6s %6s"
      %("xe","Dy","s0","trav","arm0","arm60","arm105","ext_top","%thigh","F@60","+inert"))
best=None
for xe in (40.0,55.0,70.0):
    for Dy in (-120.0,-140.0,-160.0):
        for s0 in (45.0,60.0,75.0):
            r=geom(xe,(30.0,Dy),s0)
            if r is None: continue
            Lrod,o=r
            trav=o[105][0]-o[ROMd[0]][0]
            top=o[105][0]+NUTB+MOT
            a0,a60,a105=o[0][1],o[60][1],o[105][1]
            n=(a60/1000.0)/0.020*2*math.pi
            F60=25000.0/a60
            ok = a0>=28 and top<=370 and F60<=420
            print("%3.0f %5.0f %5.0f | %5.0f %6.0f %6.0f %6.0f | %6.0f %6.0f%% %6.0f %5.0f%% %s"
                  %(xe,Dy,s0,trav,a0,a60,a105,top,top/HIP*100,F60,J*n*n/0.29*100,"OK" if ok else ""))
            if ok and (best is None or top<best[0]): best=(top,xe,Dy,s0,Lrod,o,trav)
print()
top,xe,Dy,s0,Lrod,o,trav=best
print("=== ADOPTED ===")
print("  rail offset xe=%.0f mm posterior of knee axis; rod pivot D=(30,%.0f); rod %.1f mm"%(xe,Dy,Lrod))
print("  carriage %.0f -> %.0f mm (travel %.0f)   extrusion top ~%.0f mm = %.0f%% up the thigh"
      %(o[ROMd[0]][0],o[105][0],trav,top,top/HIP*100))
print("  %5s %9s %9s %10s %8s"%("flex","carr mm","arm mm","F@25N.m","amps"))
for t in (-2,0,30,60,90,105):
    s,a=o[t]; print("  %5d %9.1f %9.1f %9.0f N %7.1f"%(t,s,a,25000/a,25000/a/FA))
I=math.pi*8**4/64
print("\n  8 mm rod: Pcr=%.0f N, worst %.0f N -> SF %.0f"%(math.pi**2*200000*I/Lrod**2,25000/o[0][1],
      (math.pi**2*200000*I/Lrod**2)/(25000/o[0][1])))
print("  swing 300 deg/s at 90 deg: carriage %.0f mm/s -> %.0f rpm on a 20 mm ballscrew"
      %(o[90][1]*math.radians(300), o[90][1]*math.radians(300)/20*60))
import json
open("v4geom.json","w").write(json.dumps(dict(xe=xe,Dy=Dy,s0=s0,Lrod=Lrod,trav=trav,top=top,
     carr=[o[ROMd[0]][0],o[105][0]])))
print("\n  geometry written to v4geom.json")
