# -*- coding: utf-8 -*-
import math
A = pinA(); O = lambda n: doc.getObject(n)
L_RET,L_EXT = ab(ROM[1]),ab(ROM[0]); STROKE=L_EXT-L_RET
NUT,TANG,T_TUBE = 50.0,35.0,190.0
THREAD=(L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0); BLK=(20.0,56.0)
for th,target in ((0.0,"P2_ThighUpright_Upper"),(105.0,"P4_ShankLink_Horn"),(-2.0,"P4_ShankLink_Horn")):
    pose(th)
    B=pinB(th); L=ab(th); ux,uy=(B[0]-A[0])/L,(B[1]-A[1])/L
    plc=FreeCAD.Placement(V(A[0],A[1],0.0),FreeCAD.Rotation(V(0,0,1),math.degrees(math.atan2(-ux,uy))))
    p=L-T_TUBE
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    comps={"rear_eye":cz(11.0,101.0,115.0),"neck":cyl(7.5,8.0,BLK[0]+2.0),"block":cyl(20.0,*BLK),
           "belt_cover":bx(-88.0,20.0,BLK[0]+6.0,BLK[1],94.0,122.0),"screw":cyl(10.0,*THREAD),
           "nut_house":cyl(23.0,p,p+55.0),"tube":cyl(13.0,p+55.0,L-TANG),
           "tang":bx(-8.0,8.0,L-TANG,L,101.0,115.0),"pinB_lug":cz(11.0,101.0,115.0,0.0,L)}
    t=O(target).Shape
    for k,s in comps.items():
        s.Placement=plc
        if not s.BoundBox.intersect(t.BoundBox): continue
        c=s.common(t)
        if c.isNull() or c.Volume<30: continue
        bb=c.BoundBox
        print("th=%+5.0f %-11s ^ %-10s %6.3f cm3  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]"
              %(th,k,target.split('_')[1],c.Volume/1000,bb.XMin,bb.XMax,bb.YMin,bb.YMax,bb.ZMin,bb.ZMax))
pose(0.0)
