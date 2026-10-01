# -*- coding: utf-8 -*-
"""Carriage: rod ear gone, belt anchor in. The anchor sits at X 52..68 -- offset
posteriorly from the screw (X 31..49) because the belt has to reach Z 110..140 and
would otherwise run straight through the screw channel."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
S=K["samples"]; XE=K["XE"]; C0=K["C0"]
s0=C0
Y0,Y1=s0-24.,s0+78.
BASE=(108.,120.); SCR_X,SCR_Z=40.,122.; CHAN_R=9.0; NUT_R=14.0
SLID_X=(20.,60.); SLID_W=3.0; SLID_TOP=114.0
NUT_Y=(s0+34.,s0+80.)
ANC_X=(52.,68.); ANC_Z=(108.,154.); BELT_Z=(116.,146.)
ca=bx(10.,70.,Y0,Y1,*BASE)
ca=ca.fuse(bx(22.,58.,NUT_Y[0],NUT_Y[1],108.,142.))            # ball-nut clamp
ca=ca.fuse(bx(ANC_X[0],ANC_X[1],Y0,Y0+34.,*ANC_Z)).removeSplitter()   # belt anchor boss
ca=ca.cut(cy(CHAN_R,Y0-1,Y1+1,SCR_X,SCR_Z))                    # screw channel
ca=ca.cut(cy(NUT_R+0.2,NUT_Y[0]-1,NUT_Y[1]+1,SCR_X,SCR_Z))     # nut seat
for cxx in SLID_X: ca=ca.cut(bx(cxx-SLID_W,cxx+SLID_W,Y0-1,Y1+1,BASE[0],SLID_TOP))
for k in range(4):
    ca=ca.cut(cz(2.1,138.,143.,SCR_X-9.+6.*k,NUT_Y[0]+8.+k*9.))
ca=ca.cut(bx(ANC_X[0]-1,ANC_X[1]+1,Y0+6.,Y0+12.,BELT_Z[0],BELT_Z[1]))  # belt slot
for k in range(3):                                             # belt clamp screws
    ca=ca.cut(cz(2.1,ANC_Z[1]-12.,ANC_Z[1]+1,60.,Y0+18.+k*7.))
assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"P3 solids=%d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
b=ca.BoundBox
print("P3 carriage X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3 (was 91.6)"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000))
print("  belt anchor X %.0f..%.0f, slot at Z %.0f..%.0f; screw channel is X 31..49 -> clear"%(
    ANC_X[0],ANC_X[1],BELT_Z[0],BELT_Z[1]))
# sliders follow the new carriage span
for i,cxx in enumerate(SLID_X):
    s=bx(cxx-2.8,cxx+2.8,Y0,Y1,104.2,SLID_TOP)
    for y in (Y0+15.,(Y0+Y1)/2,Y1-15.): s=s.cut(cz(1.7,110.,SLID_TOP+1,cxx,y))
    assert len(s.Solids)==1 and s.isClosed()
    doc.getObject("P10%s_Slider_Delrin"%("ab"[i])).Shape=s
print("  Delrin sliders re-spanned to Y %.1f..%.1f"%(Y0,Y1))
doc.recompute(); doc.save()
