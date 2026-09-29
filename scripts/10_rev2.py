# -*- coding: utf-8 -*-
"""REV C: nut tube necks to a flat tang before pin B; screw support block + belt cover
moved clear of the pin-A clevis."""
import math
DR = dict(eye_r=11.0, neck=(8.0,20.0), neck_r=9.0, blk=(20.0,48.0), blk_r=20.0,
          cover=(22.0,48.0), screw=(48.0,200.0), screw_r=10.0,
          tube_len=150.0, tube_r=17.0, tang=34.0, tang_w=11.0,
          mot=(20.0,94.0), mot_r=31.5, mot_off=-62.0)
def build_drive(th):
    B = pinB(th); L = ab(th)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    plc = FreeCAD.Placement(V(A[0],A[1],0.0),
          FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
    def cyl(r,y0,y1,x=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,Z_PLANE),V(0,1,0))
    d = cz(DR['eye_r'], 101.0, 115.0)                        # rear eye lug (in the clevis)
    d = d.fuse(cyl(DR['neck_r'], *DR['neck']))               # eye shank
    d = d.fuse(cyl(DR['blk_r'], *DR['blk']))                 # screw support bearing block
    d = d.fuse(bx(-88.0, 20.0, *DR['cover'], 85.0, 131.0))   # 1:1 belt cover
    d = d.fuse(cyl(DR['screw_r'], *DR['screw']))             # SFU2020, 152 mm thread
    d = d.fuse(cyl(DR['tube_r'], L-DR['tube_len'], L-DR['tang']))          # nut tube
    d = d.fuse(bx(-DR['tang_w'], DR['tang_w'], L-DR['tang'], L, 101.0, 115.0))  # flat tang
    d = d.fuse(cz(DR['eye_r'], 101.0, 115.0, 0.0, L))        # pin-B clevis lug
    m = cyl(DR['mot_r'], *DR['mot'], x=DR['mot_off'])
    d.Placement = plc; m.Placement = plc
    return d, m, L
globals()['build_drive'] = build_drive
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1), t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d; P8.Shape = m
    doc.recompute()
globals()['pose'] = pose

O = lambda n: doc.getObject(n)
T=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
S=["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
D=["P7_Actuator_ENVELOPE","P8_Motor_6374"]; LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
def wp(la,lb):
    w,nm=0.0,"-"
    for x in la:
        for y in lb:
            v=vol(O(x).Shape,O(y).Shape)
            if v>w: w,nm=v,"%s/%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
print("th    | shank^thigh | drive^thigh | drive^shank | struct^limb | screw-nut on thread?")
print("------+-------------+-------------+-------------+-------------+---------------------")
acc={}
for th in [-2,0,5,15,30,45,60,75,90,100,105]:
    pose(float(th)); L=ab(float(th))
    a,_=wp(S,T+PINS); b,bn=wp(D,T); c,cn=wp(D,S); e,_=wp(T+S+D,LIMB)
    nut0 = L-DR['tube_len']; nut1 = nut0+50.0
    ok = "OK" if (nut0>=DR['screw'][0] and nut1<=DR['screw'][1]) else "OFF-THREAD"
    print("%5.0f | %6.2f      | %5.2f %-6s| %5.2f %-6s| %6.2f      | nut %5.1f-%5.1f %s"
          %(th,a,b,bn,c,cn,e,nut0,nut1,ok))
    for k,v in (("shank^thigh",a),("drive^thigh",b),("drive^shank",c),("struct^limb",e)): acc[k]=max(acc.get(k,0),v)
print("\nWORST OVER ROM (cm3):", {k:round(v,3) for k,v in acc.items()})
pose(0.0)
