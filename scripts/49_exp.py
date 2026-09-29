# -*- coding: utf-8 -*-
import os, Mesh, MeshPart
OUT = "C:/Users/Josh/KneeExo_STL"
os.makedirs(OUT, exist_ok=True)
for n in ("P2_ThighUpright_Upper", "P4_ShankLink_Horn"):
    o = doc.getObject(n)
    m = doc.addObject("Mesh::Feature", "m_tmp")
    m.Mesh = MeshPart.meshFromShape(Shape=o.Shape, LinearDeflection=0.15,
                                    AngularDeflection=0.6, Relative=False)
    Mesh.export([m], OUT + "/" + n + ".stl")
    doc.removeObject(m.Name)
    print("exported", n)
