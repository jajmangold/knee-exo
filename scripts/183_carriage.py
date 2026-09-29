# -*- coding: utf-8 -*-
"""Carriage: top plate on the rail (Delrin sliders at X=20/60) + an ANTERIOR ARM
carrying both the ball nut (X=-14) and the belt anchor (X=-35.65). A groove at
X 33..41 lets the posterior SPRING run pass over the plate."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
R=K["R"]; C0=K["C0"]; SCR_X=K["screw"]["x"]; SCR_Z=K["screw"]["z"]
Y0,Y1=C0-24.,C0+78.
PLATE=(108.,120.); SLID_X=(20.,60.); SLID_W=3.0; SLID_TOP=114.0
BIN,BOUT=R-1.4,R+4.2                      # belt body radii
GRV=(33.,41.)                             # spring-run corridor
ANC_Z=(108.,154.); BELT_Z=(116.,146.); NUT_R=14.0; NUT_Y=(C0+36.,C0+78.)
ca=bx(10.,70.,Y0,Y1,*PLATE)                                 # plate on the rail
ca=ca.fuse(bx(-42.,10.,Y0,Y0+56.,*PLATE))                   # anterior arm
ca=ca.fuse(bx(-30.,2.,NUT_Y[0]-6.,NUT_Y[1]+6.,108.,138.))   # nut clamp
ca=ca.fuse(bx(-30.,2.,Y0+40.,NUT_Y[0]-6.,108.,120.))        # arm out to the nut clamp
ca=ca.fuse(bx(-43.,-31.,Y0,Y0+34.,*ANC_Z)).removeSplitter() # belt anchor boss
ca=ca.cut(cy(9.0,Y0-1,NUT_Y[1]+8.,SCR_X,SCR_Z))             # screw channel, past the clamp box
ca=ca.cut(cy(NUT_R+0.2,NUT_Y[0]-1,NUT_Y[1]+1,SCR_X,SCR_Z))  # nut seat
for cxx in SLID_X: ca=ca.cut(bx(cxx-SLID_W,cxx+SLID_W,Y0-1,Y1+1,PLATE[0],SLID_TOP))
ca=ca.cut(bx(GRV[0],GRV[1],Y0-1,Y1+1,SLID_TOP,PLATE[1]+1))  # spring-run groove
ca=ca.cut(bx(-BOUT,-BIN,Y0+5.,Y0+12.,*BELT_Z))              # belt clamp slot
for k in range(3): ca=ca.cut(cz(2.1,ANC_Z[1]-13.,ANC_Z[1]+1,-37.,Y0+18.+k*7.))
for k in range(4): ca=ca.cut(cz(2.1,134.,139.,SCR_X-9.+6.*k,NUT_Y[0]+4.+k*9.))
assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"P3 solids=%d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
b=ca.BoundBox
print("P3 carriage X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000))
print("  belt anchor X -43..-31 (slot %.1f..%.1f), nut at X %.1f, grip %.0f mm"%(
    -BOUT,-BIN,SCR_X,Y1-Y0))
print("  spring groove X %.0f..%.0f above Z %.0f -> posterior run clears the plate"%(
    GRV[0],GRV[1],SLID_TOP))
for i,cxx in enumerate(SLID_X):
    s=bx(cxx-2.8,cxx+2.8,Y0,Y1,104.2,SLID_TOP)
    for y in (Y0+15.,(Y0+Y1)/2,Y1-15.): s=s.cut(cz(1.7,110.,SLID_TOP+1,cxx,y))
    assert len(s.Solids)==1 and s.isClosed()
    doc.getObject("P10%s_Slider_Delrin"%("ab"[i])).Shape=s
print("  Delrin sliders Y %.1f..%.1f at X 20 / 60"%(Y0,Y1))
doc.recompute(); doc.save()
