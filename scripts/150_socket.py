# -*- coding: utf-8 -*-
"""P6 shank socket follows A4 to Z 94..114. Its calf base plate stays at Z 68..78
(where P7_ShankCuff mates it), so the riser between them shortens from 39 to 12 mm --
the socket gets stiffer as a side effect of the compaction."""
import FreeCAD, Part
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
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
SH20_X=(-10.0,10.0); SH20_Z=(94.0,114.0)
hs=bx(-20.,20.,-318.,-248.,SH20_Z[0]-9,SH20_Z[1]+9)
hs=hs.cut(bx(SH20_X[0]-0.3,SH20_X[1]+0.3,-319.,-246.,SH20_Z[0]-0.3,SH20_Z[1]+0.3))
hs=hs.fuse(bx(-30.,30.,-318.,-208.,68.,78.))
hs=hs.fuse(bx(-8.,8.,-314.,-218.,76.,SH20_Z[0]-6))
for xa,xb in ((14.,22.),(-22.,-14.)): hs=hs.fuse(bx(xa,xb,-310.,-222.,70.,SH20_Z[0]-6))
hs=hs.removeSplitter()
hs=hs.cut(bx(-3.,3.,-292.,-270.,SH20_Z[1]+3,SH20_Z[1]+11))
for x,y in [(-22.,-233.),(22.,-233.),(-22.,-293.),(22.,-293.)]: hs=hs.cut(cz(3.2,67.,79.,x,y))
assert len(hs.Solids)==1 and hs.isClosed() and hs.isValid(),"P6 solids=%d"%len(hs.Solids)
doc.getObject("P6_ShankSocket").Shape=hs
b=hs.BoundBox
print("P6 socket X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,hs.Volume/1000))
print("  bore %.1f..%.1f for the 2020 at %.0f..%.0f (0.3 sliding fit), engagement 52 mm"%(
    SH20_Z[0]-0.3,SH20_Z[1]+0.3,SH20_Z[0],SH20_Z[1]))
print("  riser Z 76..%.0f (was 76..115) -- %.0f mm shorter"%(SH20_Z[0]-6,115-(SH20_Z[0]-6)))
doc.recompute(); doc.save()
