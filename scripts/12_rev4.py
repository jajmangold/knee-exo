# -*- coding: utf-8 -*-
"""REV E: eye shank 15 mm (fits the 16 mm clevis), belt cover clear of the clevis,
pin-B relief = circular pocket r34 + 140 deg fan so the tang's corners never bind."""
import math
B0 = pinB(0.0)
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s = sector(r_out,b0,b1,z0,z1,r_in); s.translate(V(c[0],c[1],0.0)); return s

lk = cz(21.0, *LINK)
lk = lk.fuse(sector(70.0, *FINGER, *LINK, r_in=20.0))
lk = lk.fuse(bar((0.0,0.0), B0, 20.0, 14.0, *LINK))
lk = lk.fuse(cz(16.0, 94.0, 122.0, *B0))
lk = lk.fuse(bar((0.0,-20.0), (0.0,-160.0), 22.0, 18.0, *LINK))
lk = lk.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))
lk = lk.cut(cz(34.0, 100.4, 115.6, *B0))                              # circular relief
lk = lk.cut(sector_at(B0, 80.0, -30.0, 110.0, 100.4, 115.6, r_in=34.0))  # tang fan
lk = lk.cut(cz(4.1, 92.0, 124.0, *B0))
lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))
lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
doc.getObject("P4_ShankLink_Horn").Shape = lk

DR.update(neck_r=7.5, cover=(26.0,50.0), blk=(24.0,50.0), screw=(50.0,200.0))
def build_drive(th):
    B = pinB(th); L = ab(th)
    ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
    plc = FreeCAD.Placement(V(A[0],A[1],0.0),
          FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
    def cyl(r,y0,y1,x=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,Z_PLANE),V(0,1,0))
    d = cz(DR['eye_r'], 101.0, 115.0)
    d = d.fuse(cyl(DR['neck_r'], 8.0, 26.0)).fuse(cyl(DR['blk_r'], *DR['blk']))
    d = d.fuse(bx(-88.0, 20.0, *DR['cover'], 85.0, 131.0))
    d = d.fuse(cyl(DR['screw_r'], *DR['screw']))
    d = d.fuse(cyl(DR['tube_r'], L-DR['tube_len'], L-DR['tang']))
    d = d.fuse(bx(-DR['tang_w'], DR['tang_w'], L-DR['tang'], L, 101.0, 115.0))
    d = d.fuse(cz(DR['eye_r'], 101.0, 115.0, 0.0, L))
    m = cyl(DR['mot_r'], *DR['mot'], x=DR['mot_off'])
    d.Placement = plc; m.Placement = plc
    return d, m, L
globals()['build_drive'] = build_drive
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1), t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0), r, V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d; P8.Shape = m; doc.recompute()
globals()['pose'] = pose

O = lambda n: doc.getObject(n)
T=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff"]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]
S=["P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
D=["P7_Actuator_ENVELOPE","P8_Motor_6374"]
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
            if v>w: w,nm=v,"%s^%s"%(x.split('_')[0],y.split('_')[0])
    return w,nm
acc={}; bad=0
print("  th | shank^thigh | drive^thigh | drive^shank | verdict")
for th in [-2,0,2,4,6,8,10,15,20,25,30,40,50,60,70,80,85,90,95,98,100,102,104,105]:
    pose(float(th))
    a,_=wp(S,T+PINS); b,bn=wp(D,T); c,cn=wp(D,S)
    m = max(a,b,c); v = "clear" if m < 0.05 else ("TOUCH %.2f"%m)
    if m >= 0.05: bad += 1
    print("%5.0f | %6.3f      | %6.3f      | %6.3f      | %s"%(th,a,b,c,v))
    for k,x in (("shank^thigh",a),("drive^thigh",b),("drive^shank",c)): acc[k]=max(acc.get(k,0),x)
print("\nWORST (cm3):", {k:round(v,4) for k,v in acc.items()}, " poses over 0.05 cm3:", bad)
o=doc.getObject("P4_ShankLink_Horn")
print("P4 %.1f cm3 valid=%s solids=%d"%(o.Shape.Volume/1000,o.Shape.isValid(),len(o.Shape.Solids)))
pose(0.0); doc.recompute()
