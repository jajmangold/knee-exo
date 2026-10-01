# -*- coding: utf-8 -*-
import os, Mesh, MeshPart, FreeCAD
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
OUT="C:/Users/Josh/KneeExo_anim"
CH=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
    "P3_Carriage","A2_BallScrew_SFU1620","A3_Motor_6374"]
for n in CH:
    o=doc.getObject(n)
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.25,AngularDeflection=0.8,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("  %-26s %6.1f cm3"%(n,o.Shape.Volume/1000))
print("re-exported",len(CH))
