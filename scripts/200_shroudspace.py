# -*- coding: utf-8 -*-
"""Where is there room for a shroud? Sample, per 15 deg sector at the belt's Z band,
the MINIMUM radius reached by any shank-side (moving) part over the whole ROM, and the
maximum radius of the belt itself. The gap between them is what a static shroud can use."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]; R=K["R"]; BIN,BOUT=K["belt_x"]; BZ=tuple(K["belt_z"])
MOVING=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","HW_JointBolts"]
O=lambda n: doc.getObject(n)
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
# sample the moving parts' vertices in their LOCAL frame, then rotate
pts=[]
for n in MOVING:
    o=O(n)
    if not o: continue
    for v in o.Shape.Vertexes:
        if BZ[0]-4 <= v.Z <= BZ[1]+4:
            pts.append((v.X,v.Y,n))
print("sampled %d vertices of moving parts inside the belt Z band %.0f..%.0f"%(len(pts),*BZ))
SECT=[[1e9,""] for _ in range(24)]
for th in [s["theta"] for s in S]:
    for x,y,n in pts:
        wx,wy=rot2((x,y),th)
        r=math.hypot(wx,wy)
        if r<1.0: continue
        a=math.degrees(math.atan2(wy,wx))%360
        i=int(a//15)
        if r<SECT[i][0]: SECT[i]=[r,n]
print("\n  sector      min radius of any MOVING part   belt outer   free gap")
belt=BOUT
for i,(r,n) in enumerate(SECT):
    a0,a1=i*15,(i+1)*15
    if r>1e8:
        print("  %3d-%3d deg   (nothing moving here)            %6.2f      unlimited"%(a0,a1,belt))
    else:
        print("  %3d-%3d deg   %7.2f  (%-22s)  %6.2f    %+7.2f"%(a0,a1,r,n,belt,r-belt))
print("\nNOTE: 180..360 deg is where the belt WRAPS (distal side).")
print("      the shank points at 270 deg at theta=0 and %0.0f deg at theta=104."%((270+104)%360))
