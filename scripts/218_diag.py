import math, json, FreeCAD
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json")); S=K["samples"]
SH=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P24_FairingShank"]
def pose(th):
    r=FreeCAD.Rotation(V(0,0,1),th)
    for n in SH: doc.getObject(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
for a,b in (("A4_Shank2020_VSlot","P24_FairingShank"),
            ("P2a_KneeHingePlate","P21_ShellAnterior"),
            ("P2a_KneeHingePlate","P20_KneeShroud")):
    print("=== %s ^ %s ==="%(a,b))
    for th in (0.,52.,104.):
        pose(th)
        c=doc.getObject(a).Shape.common(doc.getObject(b).Shape)
        if c.isNull() or c.Volume<1e-6: print("  th %5.1f  0"%th); continue
        bb=c.BoundBox
        print("  th %5.1f  %.3f cm3  X %7.2f..%7.2f Y %8.2f..%8.2f Z %6.2f..%6.2f"%(
            th,c.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
pose(0.)
