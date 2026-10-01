import math, json, FreeCAD
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration under freecadcmd, where no document is
    open yet -- which is why these older build scripts could not be re-run without the GUI.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]
for th in (-2.,0.,4.):
    s=min(S,key=lambda q:abs(q["theta"]-th))
    doc.getObject("P2a_KneeHingePlate").Placement=FreeCAD.Placement(
        V(0,0,0),FreeCAD.Rotation(V(0,0,1),s["theta"]),V(0,0,0))
    for other in ("P20_KneeShroud","P1_KneeYoke"):
        c=doc.getObject("P2a_KneeHingePlate").Shape.common(doc.getObject(other).Shape)
        if c.isNull() or c.Volume<1e-6: print("th=%5.1f  %-16s 0"%(th,other)); continue
        b=c.BoundBox
        r0=min(math.hypot(v.X,v.Y) for v in c.Vertexes); r1=max(math.hypot(v.X,v.Y) for v in c.Vertexes)
        angs=[math.degrees(math.atan2(v.Y,v.X))%360 for v in c.Vertexes]
        print("th=%5.1f  %-16s %.3f cm3  Z %.1f..%.1f  r %.1f..%.1f  ang %.0f..%.0f"%(
            th,other,c.Volume/1000,b.ZMin,b.ZMax,r0,r1,min(angs),max(angs)))
doc.getObject("P2a_KneeHingePlate").Placement=FreeCAD.Placement()
