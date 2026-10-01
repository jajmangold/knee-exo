# -*- coding: utf-8 -*-
"""Corrected drive side. Belt drive run moves ANTERIOR (X=-R) so the screw powers
EXTENSION, both runs become parallel to the rail (exact linear pose law, zero side
load), and the screw/nut/motor move to X=-14 so the nut sits beside the belt on the
carriage's anterior arm -- yaw couple 59.8 -> 17.1 N.m."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
TEETH=28; PITCH=8.0; R=TEETH*PITCH/(2*math.pi)
C0=150.0; SCR_X,SCR_Z,SCR_R=-14.0,122.0,7.9; SCR_Y=(104.0,284.7)
NUT_R=14.0; NUT_OFF=(36.,78.); MOT_Y=(288.7,362.7); MOT_R=31.5
S=[{"theta":float(i),"carr":C0-R*math.radians(float(i))} for i in range(-2,105)]
K={"drive":"belt_capstan_parallel","pulley_teeth":TEETH,"pulley_pitch":PITCH,"R":R,
   "C0":C0,"belt_width":30.0,"drive_x":-R,"spring_x":R,
   "screw":{"x":SCR_X,"z":SCR_Z},"samples":S}
json.dump(K,open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json","w"))
c=[s["carr"] for s in S]
print("pose law dY/dtheta = R = %.3f mm/rad EXACTLY (runs parallel -> alpha=0)"%R)
print("carriage Y %.1f..%.1f, travel %.2f mm"%(min(c),max(c),max(c)-min(c)))
print("carriage body Y %.1f..%.1f  (rail 58.0..284.7)"%(min(c)-24,max(c)+78))
print("nut          Y %.1f..%.1f  (screw %.1f..%.1f)"%(
    min(c)+NUT_OFF[0],max(c)+NUT_OFF[1],SCR_Y[0],SCR_Y[1]))
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCR_R,SCR_Y[0],SCR_Y[1],SCR_X,SCR_Z)
n=cy(NUT_R,C0+NUT_OFF[0],C0+NUT_OFF[1],SCR_X,SCR_Z)
n=n.cut(cy(8.5,C0+NUT_OFF[0]-1,C0+NUT_OFF[1]+1,SCR_X,SCR_Z))
for k in range(4):
    a=math.radians(45+90*k)
    n=n.cut(cz(2.1,SCR_Z+NUT_R-3.,SCR_Z+NUT_R+1.,SCR_X+9.*math.cos(a),C0+NUT_OFF[0]+6.+k*10.))
n=n.removeSplitter()
assert len(n.Solids)==1 and n.isClosed(),"A2b"
doc.getObject("A2b_BallNut_SFU1620").Shape=n
doc.getObject("A3_Motor_6374").Shape=cy(MOT_R,MOT_Y[0],MOT_Y[1],SCR_X,SCR_Z)
b=n.BoundBox
print("A2 screw X %.1f Z %.1f (was X 40); A2b nut X %.1f..%.1f  belt sits at X %.1f..%.1f"%(
    SCR_X,SCR_Z,b.XMin,b.XMax,-(R+4.2),-(R-1.4)))
print("A3 motor closest approach to the limb axis: %.1f mm (thigh max 84.4)"%(
    math.hypot(SCR_X,SCR_Z)-MOT_R))
doc.recompute(); doc.save()
