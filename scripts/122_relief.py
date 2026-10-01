# -*- coding: utf-8 -*-
"""Measured clearance relief. Placements stay IDENTITY throughout; the obstacle is
transformed into the target part's local frame instead, so nothing gets baked in."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
for o in doc.Objects:
    if o.TypeId=="Part::Feature": o.Placement=FreeCAD.Placement()
doc.recompute()
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.); PHI0=BASE["phi"]; CARR0=BASE["carr"]
def xform(name,t):
    """world transform of `name` at flexion t"""
    s=sm(t)
    if name in ("A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
                "P7_ShankCuff","HW_JointBolts","HW_PinB_10"):
        return FreeCAD.Placement(V(0,0,0),FreeCAD.Rotation(V(0,0,1),t),V(0,0,0))
    if name=="P3_Carriage":
        return FreeCAD.Placement(V(0,s["carr"]-CARR0,0),FreeCAD.Rotation())
    if name=="P4_Rod_8mm":
        R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
        return FreeCAD.Placement(V(s["Dx"],s["Dy"],0)-R.multVec(V(D0[0],D0[1],0)),R)
    return FreeCAD.Placement()
def relieve(target,obstacle,margin=1.2):
    tgt=doc.getObject(target); obs=doc.getObject(obstacle)
    base=tgt.Shape           # placement is identity, so this is local geometry
    acc=None
    for i in range(-2,107,3):
        t=float(min(i,105))
        Tt=xform(target,t); To=xform(obstacle,t)
        rel=Tt.inverse().multiply(To)
        o=obs.Shape.copy(); o.Placement=rel
        if not base.BoundBox.intersect(o.BoundBox): continue
        c=base.common(o)
        if c.isNull() or c.Volume<1: continue
        acc=c if acc is None else acc.fuse(c)
    if acc is None:
        print("  %-26s vs %-26s already clear"%(target,obstacle)); return
    bb=acc.BoundBox
    cut=Part.makeBox(bb.XLength+2*margin,bb.YLength+2*margin,bb.ZLength+2*margin,
                     V(bb.XMin-margin,bb.YMin-margin,bb.ZMin-margin))
    new=base.cut(cut)
    if len(new.Solids)!=1 or not new.isClosed():
        print("  %-26s relief would break the part (%d solids) - SKIPPED"%(target,len(new.Solids))); return
    print("  %-26s vs %-26s relieved %.3f cm3 (%.1f -> %.1f cm3)"
          %(target,obstacle,acc.Volume/1000,base.Volume/1000,new.Volume/1000))
    tgt.Shape=new
print("measured relief passes:")
relieve("P2b_RodClevisBlock","P4_Rod_8mm")
relieve("P3_Carriage","P4_Rod_8mm")
relieve("P2b_RodClevisBlock","A2_BallScrew_SFU1620")
doc.recompute(); doc.save()
