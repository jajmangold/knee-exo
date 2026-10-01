# -*- coding: utf-8 -*-
"""Re-export the printed parts. Timer stopped and placements zeroed first so each part
exports in its own build frame rather than whatever animation pose was live."""
import os, FreeCAD, Mesh, MeshPart
g=globals()
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
t=g.get("_kx_timer")
if t is not None:
    try: t.stop(); print("timer stopped")
    except Exception as e: print("stop failed %s"%e)
ident=FreeCAD.Placement()
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=ident
doc.recompute()
OUT=r"C:/Users/Josh/KneeExo_v6_STL"
if not os.path.isdir(OUT): os.makedirs(OUT)
PRINTED=["P1_KneeYoke","P2a_KneeHingePlate","P2b_RodClevisBlock","P3_Carriage",
         "P5_ThighCuff","P6_ShankSocket","P7_ShankCuff"]
for n in PRINTED:
    o=doc.getObject(n)
    if not o: print("  %-24s MISSING"%n); continue
    assert len(o.Shape.Solids)==1 and o.Shape.isClosed(), n
    m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.08,AngularDeflection=0.35,Relative=False)
    p=os.path.join(OUT,n+".stl"); Mesh.Mesh(m.Topology).write(p)
    print("  %-24s %6.1f cm3  %6d facets"%(n,o.Shape.Volume/1000,m.CountFacets))
print("exported to %s"%OUT)
