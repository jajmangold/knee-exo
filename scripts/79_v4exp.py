# -*- coding: utf-8 -*-
import os, Mesh, MeshPart, math
OUT="C:/Users/Josh/KneeExo_v4_STL"; os.makedirs(OUT,exist_ok=True)
pose(0.0); doc.recompute()
SPEC={"P1_KneeYoke":"PA6-CF, flat on a Z face; bolts to the rail's T-slots",
      "P5_ThighCuff":"PA6-CF, on end; 6 mm foam liner inside",
      "P6_ShankSlideHousing":"PA6-CF, socket axis vertical",
      "P7_ShankCuff":"PA6-CF, on end",
      "P2_ShankBracket_ALU":"*** 10 mm 6061 PLATE - waterjet/mill, NOT printed ***"}
for n,s in SPEC.items():
    o=doc.getObject(n); sh=o.Shape; bb=sh.BoundBox
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=0.15,AngularDeflection=0.6,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("%-24s %6.1f cm3 %3.0fx%3.0fx%3.0f  %s"%(n,sh.Volume/1000,bb.XLength,bb.YLength,bb.ZLength,s))
print()
KT=8.27/190.; FA=2*math.pi*.9*KT/.020
print("%5s %8s %9s %7s %9s"%("flex","arm mm","F@25N.m","amps","tau@40A"))
for t in (0,30,60,90,105):
    a=armv(float(t)); print("%5d %8.1f %8.0f N %6.1f %8.1f N.m"%(t,a,25000/a,25000/a/FA,FA*40*a/1000))
n60=(armv(60.)/1000)/.020*2*math.pi
print("swing inertia +%.0f%% | rail 20x60 V-slot %.0f mm (~%.0f g) | screw %.0f mm | travel %.0f mm"
      %(2.5e-4*n60*n60/.29*100, EXT_Y[1]-EXT_Y[0], (EXT_Y[1]-EXT_Y[0])/1000*1450,
        SCR_Y[1]-SCR_Y[0], carr(105.)-carr(-2.)))
