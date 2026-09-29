# -*- coding: utf-8 -*-
"""Same measurement, but with the animation timer STOPPED and placements zeroed first --
otherwise Shape.Vertexes returns a live animation pose that then gets rotated again."""
import math, json, FreeCAD
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
t=g.get("_kx_timer")
if t is not None:
    try: t.stop(); print("timer stopped")
    except Exception: pass
g["_kx_timer"]=None
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
bad=[o.Name for o in doc.Objects if hasattr(o,"Placement") and not o.Placement.isIdentity()]
print("non-identity placements:", bad or "none")
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
print("moving vertices outside the belt radius, in the belt Z band: %d"%len(pts))
SECT=[[1e9,""] for _ in range(24)]
for th in [s["theta"] for s in S]:
    for x,y,n in pts:
        wx,wy=rot2((x,y),th); r=math.hypot(wx,wy)
        a=math.degrees(math.atan2(wy,wx))%360; i=min(int(a//15),23)
        if r<SECT[i][0]: SECT[i]=[r,n]
print("belt outer radius %.2f ; wrap = 180..360 deg (distal)\n"%BOUT)
print("  sector        nearest sweeping part    free gap    verdict")
for i,(r,n) in enumerate(SECT):
    a0,a1=i*15,(i+1)*15; wrap="W" if 180<=a0<360 else " "
    if r>1e8:
        print("  %3d-%3d %s     (clear)                unlimited   static shroud OK"%(a0,a1,wrap))
    else:
        gp=r-BOUT
        v="OK" if gp>=6 else ("tight" if gp>=3 else "NO ROOM")
        print("  %3d-%3d %s   %6.2f (%-19s) %+6.2f mm   %s"%(a0,a1,wrap,r,n,gp,v))
doc.save()
