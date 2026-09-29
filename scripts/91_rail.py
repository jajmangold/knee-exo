# -*- coding: utf-8 -*-
"""Rail read as four thin rods: 14 mm bores + a slot straddling the x=70 edge left
almost no web. Rebuild as a proper 20x60 V-slot: 8 mm bores centred in each 20 mm cell,
slots on all four faces."""
import FreeCAD, Part, os
from FreeCAD import Vector as V
doc = FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
A1=doc.getObject("A1_Extrusion_20x60_VSlot"); bb=A1.Shape.BoundBox
EX=(bb.XMin,bb.XMax); EY=(bb.YMin,bb.YMax); EZ=(bb.ZMin,bb.ZMax)
print("rail bbox X%s Y%s Z%s"%(EX,EY,EZ))
ext=bx(*EX,*EY,*EZ)
CELL=[EX[0]+10.0, EX[0]+30.0, EX[0]+50.0]          # centres of the three 20 mm cells
for cx in CELL:
    ext=ext.cut(bx(cx-3.0,cx+3.0,EY[0]-1,EY[1]+1,EZ[0]-1,EZ[0]+4.0))   # inboard face slot
    ext=ext.cut(bx(cx-3.0,cx+3.0,EY[0]-1,EY[1]+1,EZ[1]-4.0,EZ[1]+1))   # outboard face slot
    ext=ext.cut(cy(4.0,EY[0]-1,EY[1]+1,cx,(EZ[0]+EZ[1])/2))            # 8 mm bore
zc=(EZ[0]+EZ[1])/2
ext=ext.cut(bx(EX[0]-1,EX[0]+4.0,EY[0]-1,EY[1]+1,zc-3.0,zc+3.0))       # end-face slots
ext=ext.cut(bx(EX[1]-4.0,EX[1]+1,EY[0]-1,EY[1]+1,zc-3.0,zc+3.0))
assert len(ext.Solids)==1 and ext.isValid(), "rail %d solids"%len(ext.Solids)
A1.Shape=ext
print("rail rebuilt: %.1f cm3 (was %.1f), solids=%d"%(ext.Volume/1000, 0, len(ext.Solids)))
# shank 2020 already has an 8.4 mm bore - just confirm
A4=doc.getObject("A4_Shank2020_VSlot")
print("shank 2020: %.1f cm3 solids=%d"%(A4.Shape.Volume/1000,len(A4.Shape.Solids)))
doc.recompute()
import Mesh, MeshPart
OUT="C:/Users/Josh/KneeExo_anim"
for n in ("A1_Extrusion_20x60_VSlot","A4_Shank2020_VSlot"):
    o=doc.getObject(n)
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.25,AngularDeflection=0.8,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
    print("re-exported",n)
doc.save()
