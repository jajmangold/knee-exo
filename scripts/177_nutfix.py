# -*- coding: utf-8 -*-
"""The ball nut was still placed from the OLD kinematics (carriage zero at Y=85);
the belt drive puts it at Y=150. Rebuild it there."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
s0=K["C0"]; SCR_X,SCR_Z,NUT_R=40.,122.,14.0; NUT_OFF=(36.,78.)
n=cy(NUT_R,s0+NUT_OFF[0],s0+NUT_OFF[1],SCR_X,SCR_Z)
n=n.cut(cy(8.5,s0+NUT_OFF[0]-1,s0+NUT_OFF[1]+1,SCR_X,SCR_Z))
for k in range(4):
    a=math.radians(45+90*k)
    n=n.cut(cz(2.1,SCR_Z+NUT_R-3.,SCR_Z+NUT_R+1.,SCR_X+9.*math.cos(a),s0+NUT_OFF[0]+6.+k*10.))
n=n.removeSplitter()
assert len(n.Solids)==1 and n.isClosed(),"A2b"
doc.getObject("A2b_BallNut_SFU1620").Shape=n
b=n.BoundBox
print("A2b nut Y %.1f..%.1f (was 121..163 from the stale s0=85)"%(b.YMin,b.YMax))
c=[s["carr"] for s in K["samples"]]
print("  nut travel over the ROM: Y %.1f..%.1f; screw is 110.0..284.7"%(
    min(c)+NUT_OFF[0],max(c)+NUT_OFF[1]))
doc.recompute(); doc.save()
