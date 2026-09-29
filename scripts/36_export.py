# -*- coding: utf-8 -*-
import os, Mesh, MeshPart
OUT = r"C:\Users\Josh\KneeExo_STL"
os.makedirs(OUT, exist_ok=True)
PRINTED = ["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
           "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
pose(0.0); doc.recompute()
print("%-26s %8s %8s  %s" % ("part","cm3","grams","bbox (mm)  print orientation"))
ORI = {"P1_ThighUpright_Lower":"flat on the Z face - layers in the sagittal plane (bending load in-plane)",
       "P2_ThighUpright_Upper":"flat on the Z face - same reason; clevis needs support",
       "P3_ThighCuff":"on its end, axis vertical - hoop layers",
       "P4_ShankLink_Horn":"flat on the Z face - CRITICAL, layers must be in-plane",
       "P5_ShankSlideHousing":"socket axis vertical",
       "P6_ShankCuff":"on its end, axis vertical"}
tot = 0.0
for n in PRINTED:
    o = doc.getObject(n); s = o.Shape; tot += s.Volume
    m = doc.addObject("Mesh::Feature", "m_"+n)
    m.Mesh = MeshPart.meshFromShape(Shape=s, LinearDeflection=0.05, AngularDeflection=0.25, Relative=False)
    p = os.path.join(OUT, n + ".stl")
    Mesh.export([m], p)
    doc.removeObject(m.Name)
    bb = s.BoundBox
    print("%-26s %8.1f %8.0f  %3.0fx%3.0fx%3.0f  %s"
          % (n, s.Volume/1000, s.Volume/1000*1.19*0.78, bb.XLength, bb.YLength, bb.ZLength, ORI[n]))
print("\ntotal %.0f cm3 -> %.0f g in PA6-CF" % (tot/1000, tot/1000*1.19*0.78))
print("exported to", OUT)
doc.recompute(); doc.save()
print("model:", doc.FileName)
