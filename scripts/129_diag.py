# -*- coding: utf-8 -*-
import math, json, FreeCAD
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts"]
ROD=["P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage"]
O=lambda n: doc.getObject(n)
def xform(n,t):
    s=sm(t)
    if n in SHANK: return FreeCAD.Placement(V(0,0,0),FreeCAD.Rotation(V(0,0,1),t),V(0,0,0))
    if n=="P3_Carriage": return FreeCAD.Placement(V(0,s["carr"]-CARR0,0),FreeCAD.Rotation())
    if n in ROD:
        R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
        return FreeCAD.Placement(V(s["Dx"],s["Dy"],0)-R.multVec(V(D0[0],D0[1],0)),R)
    return FreeCAD.Placement()
# does the json Dx,Dy agree with rotating D0 by theta?
print("=== rod base consistency (json Dx,Dy vs rot2(D0,theta)) ===")
mx=0.0
for q in (0.,30.,60.,90.,105.):
    s=sm(q); c,si=math.cos(math.radians(q)),math.sin(math.radians(q))
    ex,ey=D0[0]*c-D0[1]*si, D0[0]*si+D0[1]*c
    d=math.hypot(s["Dx"]-ex,s["Dy"]-ey); mx=max(mx,d)
    print("  th=%5.1f json (%8.3f,%8.3f)  rot2 (%8.3f,%8.3f)  delta %.4f"%(q,s["Dx"],s["Dy"],ex,ey,d))
print("  max delta %.4f mm"%mx)
print()
for tgt,obs in (("P2b_RodClevisBlock","P9a_RodEnd_SI8_Shank"),
                ("P2b_RodClevisBlock","A2_BallScrew_SFU1620")):
    print("=== %s ^ %s ==="%(tgt,obs))
    for th in (96.,99.,102.,105.):
        Tt=xform(tgt,th); To=xform(obs,th)
        a=O(tgt).Shape.copy(); a.Placement=Tt
        b=O(obs).Shape.copy(); b.Placement=To
        if not a.BoundBox.intersect(b.BoundBox): print("  th=%5.1f  no bbox overlap"%th); continue
        cm=a.common(b)
        if cm.isNull() or cm.Volume<1e-6: print("  th=%5.1f  0"%th); continue
        # express the clash in the TARGET's local frame
        cl=cm.copy(); cl.Placement=FreeCAD.Placement(); cl=cm.transformGeometry(Tt.inverse().toMatrix())
        bb=cl.BoundBox
        print("  th=%5.1f vol %.4f cm3  local X %7.2f..%7.2f Y %7.2f..%7.2f Z %7.2f..%7.2f"%(
            th,cm.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
