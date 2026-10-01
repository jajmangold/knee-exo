import math, json, FreeCAD
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
S=K["samples"]; C0=K["C0"]
CARR=["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
for th in (0.,3.,10.):
    s=min(S,key=lambda q:abs(q["theta"]-th))
    for n in CARR: doc.getObject(n).Placement=FreeCAD.Placement(V(0,s["carr"]-C0,0),FreeCAD.Rotation())
    a=doc.getObject("P3_Carriage").Shape; b=doc.getObject("A2_BallScrew_SFU1620").Shape
    c=a.common(b)
    if c.isNull() or c.Volume<1e-6: print("th=%5.1f  0"%th); continue
    bb=c.BoundBox
    print("th=%5.1f vol %.3f  X %7.2f..%7.2f Y %7.2f..%7.2f Z %7.2f..%7.2f"%(
        th,c.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
print()
print("screw: X -21.9..-6.1, Z 114.1..129.9, Y 104.0..284.7")
print("nut seat cut spans local Y %.1f..%.1f ; clamp box spans %.1f..%.1f"%(
    C0+35.,C0+79.,C0+30.,C0+84.))
print("carriage local Y %.1f..%.1f"%(C0-24.,C0+78.))
