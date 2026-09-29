# -*- coding: utf-8 -*-
import os, Mesh, MeshPart, math
OUT="C:/Users/Josh/KneeExo_v6_STL"; os.makedirs(OUT,exist_ok=True)
pose(0.0); doc.recompute()
# split the rod housing out as its own printed part
D=rot2(D0,0.0)
hsg = cz(14.0,*ROD_Z,*D).cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*D))
hsg = hsg.cut(cz(11.1,ROD_Z[0]+1.0,ROD_Z[0]+8.0,*D))        # 608 seat (22 OD)
hsg = hsg.cut(cz(11.1,ROD_Z[1]-8.0,ROD_Z[1]-1.0,*D))
hsg = hsg.fuse(bx(D[0]-10.,D[0]+10.,D[1]+8.,D[1]+30.,ROD_Z[0]-2,ROD_Z[1]+2))
hsg = hsg.cut(bx(D[0]-10.2,D[0]+10.2,D[1]+11.,D[1]+31.,ROD_Z[0],ROD_Z[1]))   # 2020 socket
add("P8_RodEndHousing_PETG",hsg,(0.25,0.60,0.35),G_S)
SPEC={"P1_KneeYoke":"PA6-CF   - bolts to the 20x60 rail",
      "P5_ThighCuff":"PA6-CF   - 6 mm foam liner",
      "P6_ShankSocket":"PA6-CF   - the shank 2020 slides in it (self-alignment)",
      "P7_ShankCuff":"PA6-CF   - 6 mm foam liner",
      "P8_RodEndHousing_PETG":"PETG-CF  - x2, holds 2x 608, sockets over the rod 2020",
      "P2a_KneeHingePlate":"10 mm 6061 flat profile - waterjet (or a stock ROM hinge)",
      "P2b_RodClevisBlock":"6061 block - THROUGH-BOLTED to the shank 2020"}
for n,s in SPEC.items():
    o=doc.getObject(n); sh=o.Shape; bb=sh.BoundBox
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=sh,LinearDeflection=0.15,AngularDeflection=0.6,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("%-24s %6.1f cm3 %3.0fx%3.0fx%3.0f  %s"%(n,sh.Volume/1000,bb.XLength,bb.YLength,bb.ZLength,s))
print()
print("EXTRUSION CUT LIST")
print("  20x60 V-slot  %3.0f mm   thigh rail"%(EXT_Y[1]-EXT_Y[0]))
print("  2020 V-slot   %3.0f mm   shank member"%(SH20_Y[1]-SH20_Y[0]))
print("  2020 V-slot   %3.0f mm   actuation rod (between housings)"%(152.7-2*INSET))
doc.recompute(); doc.saveAs(r"C:\Users\Josh\KneeExo_v6.FCStd")
print("saved",doc.FileName)
