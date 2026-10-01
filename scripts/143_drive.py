# -*- coding: utf-8 -*-
"""Rail shortened, ball screw moved ANTERIOR (out from under the rod pivot), and the
SFU1620 ball nut modelled for the first time. Screw Z stays 117 so the motor stays
coaxial; only X changes, which is all that was needed to free the rod plane."""
import FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
RAIL_X=(10.0,70.0); RAIL_Y=(46.0,284.7); RAIL_Z=(88.0,108.0)
SCR_X, SCR_Z, SCR_R = -18.0, 117.0, 7.9
SCR_Y=(57.9,282.7)
NUT_Y=(64.0,106.0); NUT_R=14.0; FLG_R=24.0; FLG_T=10.0; NUT_BORE=8.5
MOT_Y=(300.7,374.7); MOT_R=31.5
# ---- A1 rail, shortened ----
EX,EY,EZ=RAIL_X,RAIL_Y,RAIL_Z
ext=bx(*EX,*EY,*EZ)
for cx in (EX[0]+10.0,EX[0]+30.0,EX[0]+50.0):
    ext=ext.cut(bx(cx-3.0,cx+3.0,EY[0]-1,EY[1]+1,EZ[0]-1,EZ[0]+4.0))
    ext=ext.cut(bx(cx-3.0,cx+3.0,EY[0]-1,EY[1]+1,EZ[1]-4.0,EZ[1]+1))
    ext=ext.cut(cy(4.0,EY[0]-1,EY[1]+1,cx,(EZ[0]+EZ[1])/2))
zc=(EZ[0]+EZ[1])/2
ext=ext.cut(bx(EX[0]-1,EX[0]+4.0,EY[0]-1,EY[1]+1,zc-3.0,zc+3.0))
ext=ext.cut(bx(EX[1]-4.0,EX[1]+1,EY[0]-1,EY[1]+1,zc-3.0,zc+3.0))
assert len(ext.Solids)==1 and ext.isValid(),"A1"
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=ext
print("A1 rail  Y %.1f..%.1f (%.1f mm, was 274.7)  %.1f cm3"%(EY[0],EY[1],EY[1]-EY[0],ext.Volume/1000))
# ---- A2 ball screw, anterior ----
s=cy(SCR_R,SCR_Y[0],SCR_Y[1],SCR_X,SCR_Z)
doc.getObject("A2_BallScrew_SFU1620").Shape=s
print("A2 screw X %.1f Z %.1f (was X 40.0 Z 117.0) -- %.1f mm anterior of the rod pivot"%(
    SCR_X,SCR_Z,40.0-SCR_X))
# ---- A2b SFU1620 ball nut (NEW) ----
n=cy(NUT_R,NUT_Y[0],NUT_Y[1],SCR_X,SCR_Z)
n=n.fuse(cy(FLG_R,NUT_Y[0],NUT_Y[0]+FLG_T,SCR_X,SCR_Z))
n=n.cut(cy(NUT_BORE,NUT_Y[0]-1,NUT_Y[1]+1,SCR_X,SCR_Z))
import math
for k in range(4):
    a=math.radians(45+90*k)
    n=n.cut(cy(3.3,NUT_Y[0]-1,NUT_Y[0]+FLG_T+1,SCR_X+19.0*math.cos(a),SCR_Z+19.0*math.sin(a)))
n=n.removeSplitter()
assert len(n.Solids)==1 and n.isClosed() and n.isValid(),"A2b nut solids=%d"%len(n.Solids)
o=doc.getObject("A2b_BallNut_SFU1620") or doc.addObject("Part::Feature","A2b_BallNut_SFU1620")
o.Shape=n; o.Label="A2b_BallNut_SFU1620"; o.ViewObject.Visibility=True
b=n.BoundBox
print("A2b nut  X %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3  (flange dia %.0f)"%(
    b.XMin,b.XMax,b.ZMin,b.ZMax,n.Volume/1000,FLG_R*2))
# ---- A3 motor, coaxial with the screw, pushed clear of the thigh ----
m=cy(MOT_R,MOT_Y[0],MOT_Y[1],SCR_X,SCR_Z)
doc.getObject("A3_Motor_6374").Shape=m
d=math.hypot(SCR_X,SCR_Z)-MOT_R
print("A3 motor Y %.1f..%.1f (was 288.7..362.7); closest approach to limb axis %.1f mm"%(
    MOT_Y[0],MOT_Y[1],d))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive": gg.addObject(o)
doc.recompute(); doc.save()
