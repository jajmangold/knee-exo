# -*- coding: utf-8 -*-
"""Trim the pin-A gusset clear of the coaxial motor (X<=-6) and widen the tang slot."""
import math
A=pinA(); B0=pinB(0.0)
EYE_Z=(113.0,127.0); Ya,Yb=336.0,368.0
CUFF_TH=[(-42.0,195.0),(-14.0,195.0),(-42.0,265.0),(-14.0,265.0)]
up = bx(CAV_X[0]+0.4,CAV_X[1]-0.4,*Y_TONGUE,CAV_Z[0]+0.4,CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X,Y_TONGUE[1]-6,Y_TOP,*BOX_Z)).cut(bx(*CAV_X,Y_TONGUE[1]+2,Y_TOP+2,*CAV_Z))
up = up.fuse(bx(BOX_X[0]+4,BOX_X[1]-4,190.0,270.0,100.0,112.0))
up = up.fuse(bx(-10.0,46.0,Ya,Yb,*BOX_Z))
up = up.fuse(bar((-32.0,A[1]-96.0),(A[0],A[1]),14.0,9.0,*BOX_Z)
             .common(bx(-60.0,-6.0,A[1]-104.0,A[1]+4.0,*BOX_Z)))     # gusset clear of motor
up = up.cut(bx(-14.0,50.0,330.0,Yb+2,*EYE_Z))
up = up.cut(cz(5.15,98.0,142.0,*A))
for y0 in (80.0,130.0): up=up.cut(bx(-30.75,-25.25,y0,y0+30.0,BOX_Z[0]-2,BOX_Z[1]+2))
for x,y in CUFF_TH: up=up.cut(cz(3.2,99.0,111.0,x,y))
assert len(up.Solids)==1 and up.isValid() and up.isClosed(),"P2 %d"%len(up.Solids)
doc.getObject("P2_ThighUpright_Upper").Shape=up
# P4: widen the tang slot
SLOT_Z,CHEEK_Z,R_CHEEK=(111.4,128.6),(106.0,134.0),(22.0,80.0)
ann_cheek=cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot =cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk=cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk=lk.fuse(cz(16.0,*CHEEK_Z,*B0))
lk=lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk=lk.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
slot=cz(26.0,*SLOT_Z,*B0).fuse(sector_at(B0,56.0,-50.0,130.0,*SLOT_Z,r_in=26.0))
lk=lk.cut(slot.common(ann_slot)).cut(cz(13.5,*SLOT_Z,*B0))
lk=lk.cut(cz(5.15,104.0,138.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk=lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk=lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk=lk.cut(cz(3.1,TONG['z'][0]-2,TONG['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid() and lk.isClosed(),"P4 %d"%len(lk.Solids)
doc.getObject("P4_ShankLink_Horn").Shape=lk
pose(0.0); doc.recompute(); doc.save()
print("P2 %.1f  P4 %.1f cm3 single closed solids"%(up.Volume/1000,lk.Volume/1000))
