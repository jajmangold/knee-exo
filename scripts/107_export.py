# -*- coding: utf-8 -*-
import os, Mesh, MeshPart, FreeCAD
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
OUT="C:/Users/Josh/KneeExo_anim"
CH=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","HW_JointBolts"]
for n in CH:
    o=doc.getObject(n)
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.25,AngularDeflection=0.8,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("  %-24s %6.1f cm3 -> %s.stl"%(n,o.Shape.Volume/1000,n))
# also refresh the STL dir used for printing
OUT2="C:/Users/Josh/KneeExo_v6_STL"
for n in ("P2a_KneeHingePlate","P2b_RodClevisBlock"):
    o=doc.getObject(n)
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.15,AngularDeflection=0.6,Relative=False)
    Mesh.export([m],OUT2+"/"+n+".stl"); doc.removeObject(m.Name)
print("exported")
