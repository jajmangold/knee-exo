# -*- coding: utf-8 -*-
"""Export every part at pose(0) in GLOBAL coords for the Blender animation,
plus a JSON of the kinematics so Blender can drive the motion."""
import os, json, math, Mesh, MeshPart
OUT=r"C:/Users/Josh/KneeExo_anim"; os.makedirs(OUT,exist_ok=True)
pose(0.0); doc.recompute()
PARTS=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620",
       "A3_Motor_6374","P3_Carriage","P4_Rod_8mm","P2a_KneeHingePlate","P2b_RodClevisBlock",
       "A4_Shank2020_VSlot","P6_ShankSocket","P7_ShankCuff","REF_Thigh","REF_Knee","REF_Shank"]
for n in PARTS:
    o=doc.getObject(n)
    if o is None: print("MISSING",n); continue
    m=doc.addObject("Mesh::Feature","m_tmp")
    m.Mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=0.25,AngularDeflection=0.8,Relative=False)
    Mesh.export([m],OUT+"/"+n+".stl"); doc.removeObject(m.Name)
print("exported %d parts"%len(PARTS))
# kinematics table for Blender
K=[]
for i in range(0,107):
    t=float(i)-2.0
    if t>105.0: break
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    phi=math.degrees(math.atan2(C[1]-D[1],C[0]-D[0]))
    K.append(dict(theta=t, carr=s, Dx=D[0], Dy=D[1], Cx=C[0], Cy=C[1], phi=phi, arm=armv(t)))
meta=dict(knee_axis=[0.0,0.0], XE=XE, D0=list(D0), rod_len=LROD,
          carr0=carr(0.0), phi0=K[2]["phi"], rom=[-2.0,105.0],
          rod_z=list(ROD_Z), samples=K)
open(OUT+"/kinematics.json","w").write(json.dumps(meta))
print("carriage %.1f..%.1f | rod angle %.1f..%.1f deg | arm %.1f..%.1f mm"
      %(carr(-2.),carr(105.),K[0]["phi"],K[-1]["phi"],armv(0.),armv(90.)))
print("wrote kinematics.json (%d samples)"%len(K))
