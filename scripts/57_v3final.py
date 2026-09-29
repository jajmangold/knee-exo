# -*- coding: utf-8 -*-
"""Cheek band inner radius back to 25 (just clear of the fork hub disc r=24)."""
import math
B0=pinB(0.0)
SLOT_Z,CHEEK_Z,R_CHEEK=(111.4,128.6),(106.0,134.0),(25.0,80.0)
ann_cheek=cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot =cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk=cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk=lk.fuse(cz(16.0,*CHEEK_Z,*B0))
lk=lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk=lk.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
slot=cz(26.0,*SLOT_Z,*B0).fuse(sector_at(B0,58.0,-52.0,132.0,*SLOT_Z,r_in=26.0))
lk=lk.cut(slot.common(ann_slot)).cut(cz(13.5,*SLOT_Z,*B0))
lk=lk.cut(cz(5.15,104.0,138.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk=lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk=lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk=lk.cut(cz(3.1,TONG['z'][0]-2,TONG['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid() and lk.isClosed(),"P4 %d"%len(lk.Solids)
doc.getObject("P4_ShankLink_Horn").Shape=lk
pose(0.0); doc.recompute(); doc.save()
O=lambda n: doc.getObject(n)
def vol(a,b):
    try:
        if a.isNull() or b.isNull() or not a.BoundBox.intersect(b.BoundBox): return 0.0
        c=a.common(b); return 0.0 if c.isNull() else c.Volume/1000.0
    except Exception: return 0.0
PRN=["P1_ThighUpright_Lower","P2_ThighUpright_Upper","P3_ThighCuff",
     "P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff"]
THI=PRN[:3]; SHA=PRN[3:]
PINS=["HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"]; DRV=["P7_Drive_Coaxial","P8_Motor_6374"]
w=0.0; off={}
for th in [float(x) for x in range(-2,106,3)]+[105.0]:
    pose(th)
    for la,lb,tag in ((SHA,THI+PINS,"shank^thigh"),(DRV,THI,"drive^thigh"),(DRV,SHA,"drive^shank")):
        for x in la:
            for y in lb:
                v=vol(O(x).Shape,O(y).Shape); w=max(w,v)
                if v>=0.05: off[tag]=round(max(off.get(tag,0),v),3)
print("P4 %.1f cm3"%(lk.Volume/1000))
print("worst structural interference over full ROM: %.4f cm3"%w)
print("offenders:",off if off else "NONE - full ROM clear")
KT=8.27/190.0; FA=2*math.pi*0.90*KT/0.020
print("\n%5s %8s %10s %10s"%("flex","arm mm","tau@40A","tau@80A"))
for t in (0,30,45,60,75,90,105):
    a_=arm(float(t)); print("%5d %8.1f %9.1f %9.1f"%(t,a_,FA*40*a_/1000,FA*80*a_/1000))
pose(0.0); doc.recompute(); doc.save()
