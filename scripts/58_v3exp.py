# -*- coding: utf-8 -*-
import os, Mesh, MeshPart
OUT="C:/Users/Josh/KneeExo_v3_STL"; os.makedirs(OUT,exist_ok=True)
pose(0.0); doc.recompute()
ORI={"P1_ThighUpright_Lower":"flat on a Z face; layers in the sagittal plane",
     "P2_ThighUpright_Upper":"flat on a Z face; 320 mm long - plate diagonally",
     "P3_ThighCuff":"on end, axis vertical",
     "P4_ShankLink_Horn":"flat on a Z face - CRITICAL, layers must be in-plane",
     "P5_ShankSlideHousing":"socket axis vertical",
     "P6_ShankCuff":"on end, axis vertical"}
tot=0.0
for n in ORI:
    o=doc.getObject(n); s=o.Shape; tot+=s.Volume; bb=s.BoundBox
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=0.15,AngularDeflection=0.6,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("%-26s %6.1f cm3 %6.0f g  %3.0fx%3.0fx%3.0f  %s"
          %(n,s.Volume/1000,s.Volume/1000*1.19*0.78,bb.XLength,bb.YLength,bb.ZLength,ORI[n]))
print("total %.0f cm3 -> %.0f g printed"%(tot/1000,tot/1000*1.19*0.78))
