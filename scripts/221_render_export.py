# -*- coding: utf-8 -*-
"""Export the whole assembly, posed, with a material tag in each filename so the Blender
script can assign shaders without a lookup table. Placements are baked in (Shape already
carries them), which is what we want for a still."""
import os, math, json, FreeCAD, Part, Mesh, MeshPart
from FreeCAD import Vector as V
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
g["_kx_timer"]=None
# One-screw kinematics (391_onescrew_build.py): one clamp, Y = A0 - R*theta. kin_low.json
# is the TWO-screw file and its C0/C1 no longer mean anything here.
R = 29 * 8.0 / (2 * math.pi)
A0 = 161.0
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff",
       "P24_FairingShank","HW_JointBolts"]
# posed with the shank but never exported: the renders leave the reference limb out.
# vlow.py has always posed REF_Shank; this script used not to, which was invisible while
# the limb was hidden and wrong the moment it was shown.
POSED_REF=["REF_Shank"]
# One moving group, not two. The belt is a closed loop whose strands and wraps are all
# STATIC -- only the clamp slides along the -X strand -- so nothing is rebuilt per pose.
GANTRY=["P3_Carriage","A2b_BallNut_SFU1620",
        "P10a_VWheel","P10b_VWheel","P10c_VWheel","P10d_VWheel"]
STAT=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620",
      "A3_Motor_6374","A6_Idler29T","A7_DriveBox","A7b_LinkBelt","HW_PinB_10",
      "A5_Belt_HTD8M","A5b_Belt_DriveRun","A5c_Belt_TakeRun","A5d_Belt_WrapIdler",
      "P20_KneeShroud","P21_ShellAnterior","P22_DriveCap","P25_MotorNacelle","P23a_FairingMount","P23b_FairingMount","P23c_FairingMount"]
MAT={}
for n in ("A1_Extrusion_20x60_VSlot","A4_Shank2020_VSlot"): MAT[n]="ALU"
for n in ("P1_KneeYoke","P2a_KneeHingePlate","P5_ThighCuff","A6_Idler29T",
          "P6_ShankSocket","P7_ShankCuff"): MAT[n]="PETG"
for n in ("P20_KneeShroud","P21_ShellAnterior","P22_DriveCap","P25_MotorNacelle","P24_FairingShank","P23a_FairingMount","P23b_FairingMount",
          "P23c_FairingMount"): MAT[n]="FAIR"
for n in ("A2_BallScrew_SFU1620","HW_PinB_10","HW_JointBolts"): MAT[n]="STEEL"
MAT["A2b_BallNut_SFU1620"]="NUT"
for n in ("A5_Belt_HTD8M","A5b_Belt_DriveRun","A5c_Belt_TakeRun",
          "A5d_Belt_WrapIdler","A7b_LinkBelt"): MAT[n]="BELT"
for n in ("P10a_VWheel","P10b_VWheel","P10c_VWheel","P10d_VWheel"): MAT[n]="DELRIN"
MAT["A3_Motor_6374"]="MOTOR"
# ALUM, not ALU: ALU is the extrusion's black anodising. These are machined 6061 and
# should read as bought metal, not as more extrusion.
MAT["A7_DriveBox"]="ALUM"
MAT["P3_Carriage"]="ALUM"
O=lambda n: doc.getObject(n)
def pose(th):
    r=FreeCAD.Rotation(V(0,0,1),th)
    dy=(A0-R*math.radians(th))-A0
    for n in SHANK+POSED_REF:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in GANTRY:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0.,dy,0.),FreeCAD.Rotation())
for th,tag in ((40.,"p40"),(0.,"p00")):
    OUT=r"C:/Users/Josh/KneeExo_render/"+tag
    if not os.path.isdir(OUT): os.makedirs(OUT)
    for f in os.listdir(OUT):
        if f.endswith(".stl"): os.remove(os.path.join(OUT,f))
    pose(th); doc.recompute()
    cnt=0; tri=0
    for n in SHANK+GANTRY+STAT:
        o=O(n)
        if not o: continue
        m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.04,
                                 AngularDeflection=0.20,Relative=False)
        Mesh.Mesh(m.Topology).write(os.path.join(OUT,"%s__%s.stl"%(MAT.get(n,"MISC"),n)))
        cnt+=1; tri+=m.CountFacets
    print("%s (theta=%.0f): %d parts, %d facets -> %s"%(tag,th,cnt,tri,OUT))
pose(0.)
print("done")
