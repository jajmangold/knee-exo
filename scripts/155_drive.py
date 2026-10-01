# -*- coding: utf-8 -*-
"""Screw back coaxial with the rod pivot at X=40, raised to Z=122 so a FLANGELESS nut
body clears the rail. Nut offset proximally along the carriage so the rod ear only has
to clear the screw. Rail shortened again (carriage now reaches further proximally, so
its distal limit moves up). Yoke pad back to the full 60 mm face -- no wheels to dodge."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
RAIL_X=(10.0,70.0); RAIL_Y=(58.0,284.7); RAIL_Z=(88.0,108.0)
SCR_X,SCR_Z,SCR_R=40.0,122.0,7.9; SCR_Y=(110.0,284.7)
NUT_R=14.0; NUT_OFF=(36.0,78.0)                  # nut spans carr+36 .. carr+78
MOT_Y=(288.7,362.7); MOT_R=31.5
YOKE_Z=(76.0,88.0)
# ---- A1 rail ----
EX,EY,EZ=RAIL_X,RAIL_Y,RAIL_Z
ext=bx(*EX,*EY,*EZ)
for cx in (EX[0]+10.,EX[0]+30.,EX[0]+50.):
    ext=ext.cut(bx(cx-3.,cx+3.,EY[0]-1,EY[1]+1,EZ[0]-1,EZ[0]+4.))
    ext=ext.cut(bx(cx-3.,cx+3.,EY[0]-1,EY[1]+1,EZ[1]-4.,EZ[1]+1))
    ext=ext.cut(cy(4.,EY[0]-1,EY[1]+1,cx,(EZ[0]+EZ[1])/2))
zc=(EZ[0]+EZ[1])/2
ext=ext.cut(bx(EX[0]-1,EX[0]+4.,EY[0]-1,EY[1]+1,zc-3.,zc+3.))
ext=ext.cut(bx(EX[1]-4.,EX[1]+1,EY[0]-1,EY[1]+1,zc-3.,zc+3.))
assert len(ext.Solids)==1 and ext.isValid(),"A1"
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=ext
print("A1 rail  Y %.1f..%.1f = %.1f mm (orig 274.7, saved %.1f)  %.1f cm3"%(
    EY[0],EY[1],EY[1]-EY[0],274.7-(EY[1]-EY[0]),ext.Volume/1000))
# ---- A2 screw, coaxial with the rod pivot ----
doc.getObject("A2_BallScrew_SFU1620").Shape=cy(SCR_R,SCR_Y[0],SCR_Y[1],SCR_X,SCR_Z)
print("A2 screw X %.1f Z %.1f  Y %.1f..%.1f  (coaxial with the rod pivot at X=40)"%(
    SCR_X,SCR_Z,SCR_Y[0],SCR_Y[1]))
# ---- A2b flangeless nut body ----
n=cy(NUT_R,s0+NUT_OFF[0],s0+NUT_OFF[1],SCR_X,SCR_Z)
n=n.cut(cy(8.5,s0+NUT_OFF[0]-1,s0+NUT_OFF[1]+1,SCR_X,SCR_Z))
for k in range(4):                                # 4 clamp screws, tangential
    a=math.radians(45+90*k)
    n=n.cut(cz(2.1,SCR_Z+NUT_R-3.,SCR_Z+NUT_R+1.,SCR_X+9.*math.cos(a),s0+NUT_OFF[0]+6.+k*10.))
n=n.removeSplitter()
assert len(n.Solids)==1 and n.isClosed(),"A2b"
doc.getObject("A2b_BallNut_SFU1620").Shape=n
b=n.BoundBox
print("A2b nut  FLANGELESS body r=%.0f  X %.1f..%.1f  Z %.1f..%.1f  (rail top is 108)"%(
    NUT_R,b.XMin,b.XMax,b.ZMin,b.ZMax))
print("  nut Y %.1f..%.1f at zero pose = carr+%.0f..carr+%.0f, rod ear is carr-17..carr+17"%(
    b.YMin,b.YMax,NUT_OFF[0],NUT_OFF[1]))
# ---- A3 motor, coaxial ----
doc.getObject("A3_Motor_6374").Shape=cy(MOT_R,MOT_Y[0],MOT_Y[1],SCR_X,SCR_Z)
print("A3 motor X %.1f Z %.1f; closest approach to the limb axis %.1f mm (thigh max 84.4)"%(
    SCR_X,SCR_Z,math.hypot(SCR_X,SCR_Z)-MOT_R))
# ---- P1 yoke: pad back to the FULL 60 mm face ----
yk=cz(40.0,*YOKE_Z).fuse(bar((0.,0.),(40.,72.),34.,30.,*YOKE_Z))
yk=yk.fuse(bx(RAIL_X[0],RAIL_X[1],RAIL_Y[0],124.0,*YOKE_Z)).removeSplitter()
yk=yk.cut(cz(5.15,YOKE_Z[0]-2,YOKE_Z[1]+2))
for x in (20.,40.,60.):
    for y in (70.,112.): yk=yk.cut(cz(2.6,YOKE_Z[0]-1,YOKE_Z[1]+1,x,y))
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
b=yk.BoundBox
print("P1 yoke  X %.1f..%.1f (pad %.0f..%.0f, FULL face -- was trimmed to 16..64 for wheels)"%(
    b.XMin,b.XMax,RAIL_X[0],RAIL_X[1]))
doc.recompute(); doc.save()
