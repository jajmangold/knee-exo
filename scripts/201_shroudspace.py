# -*- coding: utf-8 -*-
"""Per 15 deg sector at the belt Z band: the minimum radius, GREATER than the belt's
outer radius, reached by any moving (shank-side) part over the ROM. That is the inner
edge of the sweeping structure, and the gap above the belt is what a STATIC shroud gets."""
import math, json, FreeCAD
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]; BIN,BOUT=K["belt_x"]; BZ=tuple(K["belt_z"])
MOVING=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","HW_JointBolts"]
O=lambda n: doc.getObject(n)
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
pts=[]
for n in MOVING:
    o=O(n)
    if not o: continue
    for v in o.Shape.Vertexes:
        if BZ[0]-4 <= v.Z <= BZ[1]+4 and math.hypot(v.X,v.Y) > BOUT+0.5:
            pts.append((v.X,v.Y,n))
print("moving vertices OUTSIDE the belt radius, in the belt Z band: %d"%len(pts))
SECT=[[1e9,""] for _ in range(24)]
for th in [s["theta"] for s in S]:
    for x,y,n in pts:
        wx,wy=rot2((x,y),th); r=math.hypot(wx,wy)
        a=math.degrees(math.atan2(wy,wx))%360; i=int(a//15)
        if r<SECT[i][0]: SECT[i]=[r,n]
print("belt outer radius %.2f ; wrap occupies 180..360 deg (distal)\n"%BOUT)
print("  sector       nearest sweeping part   free radial gap   verdict")
for i,(r,n) in enumerate(SECT):
    a0,a1=i*15,(i+1)*15
    wrap=" WRAP" if 180<=a0<360 else ""
    if r>1e8:
        print("  %3d-%3d%-5s  (clear)                 unlimited        static shroud OK"%(a0,a1,wrap))
    else:
        g=r-BOUT
        v="OK (%.1f mm)"%g if g>=6 else ("tight" if g>=3 else "NO ROOM")
        print("  %3d-%3d%-5s  %6.2f (%-20s) %+7.2f mm      %s"%(a0,a1,wrap,r,n,g,v))
