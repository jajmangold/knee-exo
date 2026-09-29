import math, json, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
S=K["samples"]; C0=K["C0"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate"]
def pose(s):
    r=FreeCAD.Rotation(V(0,0,1),s["theta"])
    for n in SHANK: doc.getObject(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
for tgt in SHANK:
    print("=== %s ^ A5_Belt_HTD8M ==="%tgt)
    for th in (80.,92.,104.):
        s=min(S,key=lambda q:abs(q["theta"]-th)); pose(s)
        a=doc.getObject(tgt).Shape; b=doc.getObject("A5_Belt_HTD8M").Shape
        if not a.BoundBox.intersect(b.BoundBox): print("  th=%5.1f no bbox"%th); continue
        c=a.common(b)
        if c.isNull() or c.Volume<1e-6: print("  th=%5.1f 0"%th); continue
        bb=c.BoundBox
        print("  th=%5.1f vol %.3f cm3  X %7.2f..%7.2f Y %7.2f..%7.2f Z %7.2f..%7.2f"%(
            th,c.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
pose(S[2])
