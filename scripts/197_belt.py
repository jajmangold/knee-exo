# -*- coding: utf-8 -*-
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
R=K["R"]; C0=K["C0"]; C1=K["C1"]; BIN,BOUT=K["belt_x"]; BZ=tuple(K["belt_z"]); S=K["samples"]
BI=BIN+0.05
w=Part.makeCylinder(BOUT,BZ[1]-BZ[0],V(0,0,BZ[0]),V(0,0,1),180.0)
w.rotate(V(0,0,0),V(0,0,1),180.0)
w=w.cut(cz(BI,BZ[0]-1,BZ[1]+1)).removeSplitter()
assert len(w.Solids)==1 and w.isValid(),"wrap"
doc.getObject("A5_Belt_HTD8M").Shape=w
doc.getObject("A5_Belt_HTD8M").Label="A5_Belt_Wrap180_29T"
for nm,g,C in (("A5b_Belt_DriveRun",-1.,C0),("A5c_Belt_TakeRun",1.,C1)):
    x0,x1=sorted((g*BI,g*BOUT))
    doc.getObject(nm).Shape=bx(x0,x1,0.,C-24.,*BZ)
a=[s["carrA"]-24 for s in S]; b=[s["carrB"]-24 for s in S]
print("belt Z %.0f..%.0f at X +/-%.2f..%.2f ; wrap 180 deg (14.5 of 29 teeth)"%(
    BZ[0],BZ[1],BI,BOUT))
print("  run A %.1f..%.1f, run B %.1f..%.1f, sum %.2f constant"%(
    min(a),max(a),min(b),max(b),a[0]+b[0]))
print("  tension %.0f N (was 791 at 28T); HTD-8M 30 mm SF %.2f at %.0f N tight side"%(
    28200/R,1350/(28200/R+150),28200/R+150))
doc.recompute(); doc.save()
