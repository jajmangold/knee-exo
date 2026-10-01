# -*- coding: utf-8 -*-
"""Belt moved DOWN beside the rail instead of lifted above it. Requires a rail narrower
than the belt runs: back to a 20x60 (half-width 30) from the C-Beam (half-width 40).
Each carriage now gets an L-GIB -- a tongue in the outboard slot plus one in the side
slot -- which constrains more than two parallel tongues did.
Screws come down to Z=98 as well, so nothing needs lifting."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
TEETH=29; PITCH=8.0; R=TEETH*PITCH/(2*math.pi)
BIN,BOUT=R-1.372,R+4.2; BZ=(96.,126.)
RX=(-30.,30.); RZ=(88.,108.); RY=(58.,284.7)
OUT_SLOT=(-20.,0.,20.); SIDE_Z=(95.,101.)
SCR_X=(-58.,58.); SCR_Z=106.0; SCR_R=7.9; SCR_Y=(110.,290.)  # raised so the nuts clear the thigh cuff (Z<=88)
NUT_R=14.0; NUT_OFF=(36.,78.); C0,C1=152.0,138.0
MOT_Y=(314.,388.); MOT_R=31.5; DRV_Y=(290.,314.); MOT_Z=118.0
S=[{"theta":float(i),"carrA":C0-R*math.radians(float(i)),
    "carrB":C1+R*math.radians(float(i))} for i in range(-2,105)]
K={"drive":"belt_diff_lowbelt","pulley_teeth":TEETH,"pulley_pitch":PITCH,"R":R,
   "C0":C0,"C1":C1,"belt_z":list(BZ),"belt_x":[BIN,BOUT],
   "screw":{"xA":SCR_X[0],"xB":SCR_X[1],"z":SCR_Z},"samples":S}
json.dump(K,open(r"C:/Users/Josh/KneeExo_anim/kin_low.json","w"))
a=[s["carrA"] for s in S]; b=[s["carrB"] for s in S]
print("%dT -> R %.3f, travel %.2f mm, belt tension %.0f N"%(TEETH,R,max(a)-min(a),28200/R))
print("  belt runs at X +/-%.2f..%.2f, Z %.0f..%.0f (rail is |X|<=30, Z 88..108)"%(BIN,BOUT,*BZ))
print("  carriage A body Y %.1f..%.1f ; B body Y %.1f..%.1f ; rail %.1f..%.1f"%(
    min(a)-24,max(a)+78,min(b)-24,max(b)+78,*RY))
print("  runA+runB = %.2f / %.2f  (constant)"%(
    (a[2]-24)+(b[2]-24),(a[-1]-24)+(b[-1]-24)))
# ---- 20x60 rail ----
r=bx(RX[0],RX[1],*RY,*RZ)
for cx in OUT_SLOT:
    r=r.cut(bx(cx-3.,cx+3.,RY[0]-1,RY[1]+1,RZ[1]-4.,RZ[1]+1))     # outboard slots
    r=r.cut(bx(cx-3.,cx+3.,RY[0]-1,RY[1]+1,RZ[0]-1,RZ[0]+4.))     # inboard slots (yoke)
    r=r.cut(cy(4.0,RY[0]-1,RY[1]+1,cx,(RZ[0]+RZ[1])/2))
r=r.cut(bx(RX[0]-1,RX[0]+4.,RY[0]-1,RY[1]+1,*SIDE_Z))             # side slots
r=r.cut(bx(RX[1]-4.,RX[1]+1,RY[0]-1,RY[1]+1,*SIDE_Z))
assert len(r.Solids)==1 and r.isValid(),"A1 solids=%d"%len(r.Solids)
o=doc.getObject("A1_Extrusion_20x60_VSlot"); o.Shape=r; o.Label="A1_Extrusion_20x60_VSlot"
print("A1 rail 20x60  X %.0f..%.0f Z %.0f..%.0f  (~1.55 kg/m -> %.0f g)"%(
    RX[0],RX[1],RZ[0],RZ[1],1.55*(RY[1]-RY[0])))
# ---- screws / nuts / motor / drive box, all at Z=98 ----
for nm,sx in (("A2_BallScrew_SFU1620",SCR_X[0]),("A2c_BallScrew_LH",SCR_X[1])):
    doc.getObject(nm).Shape=cy(SCR_R,SCR_Y[0],SCR_Y[1],sx,SCR_Z)
for nm,sx,C in (("A2b_BallNut_SFU1620",SCR_X[0],C0),("A2d_BallNut_LH",SCR_X[1],C1)):
    n=cy(NUT_R,C+NUT_OFF[0],C+NUT_OFF[1],sx,SCR_Z)
    n=n.cut(cy(8.5,C+NUT_OFF[0]-1,C+NUT_OFF[1]+1,sx,SCR_Z))
    for k in range(4):
        aa=math.radians(45+90*k)
        n=n.cut(cz(2.1,SCR_Z+NUT_R-3.,SCR_Z+NUT_R+1.,sx+9.*math.cos(aa),C+NUT_OFF[0]+6.+k*10.))
    n=n.removeSplitter()
    assert len(n.Solids)==1 and n.isClosed(),nm
    doc.getObject(nm).Shape=n
print("screws X %+.0f / %+.0f at Z %.0f ; nuts Z %.0f..%.0f (clear of the belt at |X|<%.1f)"%(
    SCR_X[0],SCR_X[1],SCR_Z,SCR_Z-NUT_R,SCR_Z+NUT_R,BOUT))
print("  nut inner edge |X| %.0f vs belt outer %.1f -> %.1f mm gap"%(
    abs(SCR_X[0])-NUT_R,BOUT,abs(SCR_X[0])-NUT_R-BOUT))
doc.getObject("A3_Motor_6374").Shape=cy(MOT_R,MOT_Y[0],MOT_Y[1],SCR_X[0],MOT_Z)
doc.getObject("A7_DriveBox").Shape=bx(-74.,74.,DRV_Y[0],DRV_Y[1],96.,130.)
print("A3 motor at X %+.0f Z %.0f ; %.1f mm from the limb axis"%(
    SCR_X[0],MOT_Z,math.hypot(SCR_X[0],MOT_Z)-MOT_R))
doc.recompute(); doc.save()
