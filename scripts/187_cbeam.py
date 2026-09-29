# -*- coding: utf-8 -*-
"""C-Beam rail + twin LH/RH lead screws + differential kinematics.

Rail: 80 (X) x 40 (Z), X -40..+40, Z 88..128, channel opening INBOARD so the void sits
over the thigh where it bulges. The outboard face (Z=128) is a full 80 mm wide with FOUR
slot positions (X -30/-10/+10/+30), which is the real win: two sliders per carriage.

Kinematics: carr_A = C0 - R*theta, carr_B = C1 + R*theta.  Ya + Yb = const exactly, which
is what equal-pitch LH/RH screws on one shaft produce. No spring.
NOTE: verify the slot/bore detail against your actual C-Beam before cutting metal."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
TEETH=28; PITCH=8.0; R=TEETH*PITCH/(2*math.pi)
RY=(58.0,284.7); WEB_Z=(108.,128.); WING_Z=(88.,108.); RX=(-40.,40.)
SLOT_OUT=(-30.,-10.,10.,30.); WING_X=((-40.,-20.),(20.,40.))
SCR_X=(-18.,18.); SCR_Z=152.0; SCR_R=7.9; SCR_Y=(104.,288.)   # raised so the nuts clear the sliders
MOT_Z=130.0                                              # motor NOT coaxial: keeps lateral at 122
NUT_R=14.0; NUT_OFF=(36.,78.)
C0,C1=150.0,140.0
MOT_Y=(312.,386.); MOT_R=31.5; DRV_Y=(288.,312.)
# ---- kinematics ----
S=[{"theta":float(i),"carrA":C0-R*math.radians(float(i)),
    "carrB":C1+R*math.radians(float(i))} for i in range(-2,105)]
K={"drive":"belt_capstan_differential","pulley_teeth":TEETH,"pulley_pitch":PITCH,"R":R,
   "C0":C0,"C1":C1,"belt_width":30.0,"drive_x":-R,"take_x":R,
   "screw":{"xA":SCR_X[0],"xB":SCR_X[1],"z":SCR_Z},"belt_z":[136.,166.],"samples":S}
json.dump(K,open(r"C:/Users/Josh/KneeExo_anim/kin_diff.json","w"))
a=[s["carrA"] for s in S]; b=[s["carrB"] for s in S]
print("R=%.3f  travel %.2f mm each, opposite senses"%(R,max(a)-min(a)))
print("  carriage A Y %.1f..%.1f  (body %.1f..%.1f)"%(min(a),max(a),min(a)-24,max(a)+78))
print("  carriage B Y %.1f..%.1f  (body %.1f..%.1f)   rail %.1f..%.1f"%(
    min(b),max(b),min(b)-24,max(b)+78,*RY))
print("  Ya+Yb = %.2f at theta=0, %.2f at theta=104  (must be equal)"%(
    (S[2]["carrA"]-24)+(S[2]["carrB"]-24),(S[-1]["carrA"]-24)+(S[-1]["carrB"]-24)))
# ---- C-Beam profile ----
r=bx(RX[0],RX[1],*RY,*WEB_Z)
for wx in WING_X: r=r.fuse(bx(wx[0],wx[1],*RY,*WING_Z))
r=r.removeSplitter()
for cx in SLOT_OUT:                                   # outboard face slots
    r=r.cut(bx(cx-3.,cx+3.,RY[0]-1,RY[1]+1,WEB_Z[1]-4.,WEB_Z[1]+1))
for cx in (-30.,30.):                                 # wing inboard slots (yoke mounts here)
    r=r.cut(bx(cx-3.,cx+3.,RY[0]-1,RY[1]+1,WING_Z[0]-1,WING_Z[0]+4.))
for x0,x1 in ((-24.,-20.),(20.,24.)):                 # channel inner slots (cut into the wings)
    r=r.cut(bx(x0,x1,RY[0]-1,RY[1]+1,95.,101.))
zc=(WEB_Z[0]+WEB_Z[1])/2
r=r.cut(bx(RX[0]-1,RX[0]+4.,RY[0]-1,RY[1]+1,zc-3.,zc+3.))   # end-face slots
r=r.cut(bx(RX[1]-4.,RX[1]+1,RY[0]-1,RY[1]+1,zc-3.,zc+3.))
for cx in (-30.,-10.,10.,30.): r=r.cut(cy(4.0,RY[0]-1,RY[1]+1,cx,zc))
for cx in (-30.,30.):          r=r.cut(cy(4.0,RY[0]-1,RY[1]+1,cx,98.))
assert len(r.Solids)==1 and r.isValid(),"A1 solids=%d"%len(r.Solids)
doc.getObject("A1_Extrusion_20x60_VSlot").Shape=r
doc.getObject("A1_Extrusion_20x60_VSlot").Label="A1_CBeam_80x40"
L=(RY[1]-RY[0])/1000.
print("A1 C-Beam X %.0f..%.0f  Z %.0f..%.0f  length %.1f mm"%(
    RX[0],RX[1],WING_Z[0],WEB_Z[1],RY[1]-RY[0]))
print("   MODEL PROFILE IS SIMPLIFIED (outline + slots + bores, no internal cavities),")
print("   so its volume overstates mass. Use the published figure for weight:")
print("   C-Beam ~2.30 kg/m -> %.0f g for this %.0f mm piece"%(2.30*L*1000,RY[1]-RY[0]))
print("   (the 20x60 it replaces was ~1.55 kg/m -> %.0f g, so +%.0f g)"%(
    1.55*L*1000,(2.30-1.55)*L*1000))
# ---- twin screws ----
for i,(nm,sx) in enumerate((("A2_BallScrew_SFU1620",SCR_X[0]),("A2c_BallScrew_LH",SCR_X[1]))):
    s=cy(SCR_R,SCR_Y[0],SCR_Y[1],sx,SCR_Z)
    o=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
    o.Shape=s; o.Label=nm+("" if i==0 else "_LeftHand"); o.ViewObject.Visibility=True
    print("  %-24s X %+6.1f Z %.0f  Y %.0f..%.0f"%(nm,sx,SCR_Z,*SCR_Y))
# ---- twin nuts ----
for i,(nm,sx,C) in enumerate((("A2b_BallNut_SFU1620",SCR_X[0],C0),("A2d_BallNut_LH",SCR_X[1],C1))):
    n=cy(NUT_R,C+NUT_OFF[0],C+NUT_OFF[1],sx,SCR_Z)
    n=n.cut(cy(8.5,C+NUT_OFF[0]-1,C+NUT_OFF[1]+1,sx,SCR_Z))
    for k in range(4):
        aa=math.radians(45+90*k)
        n=n.cut(cz(2.1,SCR_Z+NUT_R-3.,SCR_Z+NUT_R+1.,sx+9.*math.cos(aa),C+NUT_OFF[0]+6.+k*10.))
    n=n.removeSplitter()
    assert len(n.Solids)==1 and n.isClosed(),nm
    o=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
    o.Shape=n; o.Label=nm; o.ViewObject.Visibility=True
    bb=n.BoundBox
    print("  %-24s X %.1f..%.1f (belt run at X %+.2f -> gap %.2f mm)"%(
        nm,bb.XMin,bb.XMax,-R if i==0 else R,abs(abs(-R-4.2 if i==0 else R+4.2))-abs(bb.XMin if i==0 else bb.XMax)))
# ---- drive box linking the two screws + motor ----
d=bx(-34.,34.,DRV_Y[0],DRV_Y[1],120.,170.)
o=doc.getObject("A7_DriveBox") or doc.addObject("Part::Feature","A7_DriveBox")
o.Shape=d; o.Label="A7_DriveBox_TwinScrew"; o.ViewObject.Visibility=True
doc.getObject("A3_Motor_6374").Shape=cy(MOT_R,MOT_Y[0],MOT_Y[1],SCR_X[0],MOT_Z)
print("A7 drive box Y %.0f..%.0f (one belt pair couples both screws to the motor)"%DRV_Y)
print("A3 motor at Z=%.0f (offset in the drive box, not coaxial);"%MOT_Z+"  %.1f mm from the limb axis (thigh max 84.4)"%(
    math.hypot(SCR_X[0],MOT_Z)-MOT_R))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([doc.getObject(n) for n in
            ("A2c_BallScrew_LH","A2d_BallNut_LH","A7_DriveBox")])
doc.recompute(); doc.save()
