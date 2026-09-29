# -*- coding: utf-8 -*-
"""(1) pin-A gusset trimmed to X<=4, anterior of the screw block + belt cover
   (2) horn fork cheeks extended inward 34->26 mm so the slot covers where the tube/tang
       actually pass; fork-plate hub disc 32->24 mm so those cheeks stay clear of it."""
import math
A = pinA(); B0 = pinB(0.0)
R_HUB = 24.0; globals()['R_HUB'] = R_HUB
PLATE_SEC = (84.0, 252.0)
SLOT_Z, CHEEK_Z, R_CHEEK = (99.8,116.2), (94.0,122.0), (26.0, 80.0)
GAS_PL, GAS_Z = 150.0, (143.0,157.0)
CLEV_Z, CLEV2_Z = ((94.0,101.0),(115.0,122.0)), ((136.0,143.0),(157.0,164.0))
CUFF_TH_PTS = [(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
Ya, Yb = A[1]-18.0, A[1]+19.0; Y_TOP = 340.0
Y_TWIN, Y_CLOSED = (25.0,84.0), 75.0
FLEX_HOLES=[(238,105),(228,95),(218,85),(208,75),(198,65),(188,55)]
EXT_HOLES=[(99.6,0),(109.6,10),(119.6,20)]

# ---- P1: hub disc 24 ----
def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
for z0,z1 in (FORK_IN,FORK_OUT): low = low.fuse(bx(*BOX_X,*Y_TWIN,z0,z1))
low = low.fuse(bx(*BOX_X,Y_CLOSED,170.0,*BOX_Z)).cut(bx(*CAV_X,Y_CLOSED+4,172.0,*CAV_Z))
for z0,z1 in (FORK_IN,FORK_OUT):
    for b in (95,130,165,200,235): low = low.cut(cz(11.0,z0-1,z1+1,*pol(54.0,b)))
low = low.cut(cz(6.15,FORK_IN[0]-2,FORK_OUT[1]+2))
for b,_ in FLEX_HOLES+EXT_HOLES: low = low.cut(cz(D_PIN/2+0.1,FORK_IN[0]-2,FORK_OUT[1]+2,*pol(R_PIN,b)))
for y in (110.0,150.0): low = low.cut(cz(2.75,BOX_Z[0]-2,BOX_Z[1]+2,-26.0,y))
assert len(low.Solids)==1 and low.isValid(), "P1 %d"%len(low.Solids)
doc.getObject("P1_ThighUpright_Lower").Shape = low

# ---- P4: cheeks inward to 26 ----
ann_cheek = cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot  = cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk = cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk = lk.fuse(cz(16.0,*CHEEK_Z,*B0)).fuse(cz(16.0,122.0,164.0,*B0))
lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk = lk.fuse(bx(*TONGUE['x'],*TONGUE['y'],*TONGUE['z']))
slot = cz(22.0,*SLOT_Z,*B0).fuse(sector_at(B0,46.0,-40.0,120.0,*SLOT_Z,r_in=22.0))
lk = lk.cut(slot.common(ann_slot)).cut(cz(12.5,*SLOT_Z,*B0))
lk = lk.cut(cz(12.5,*GAS_Z,*B0)).cut(sector_at(B0,46.0,-40.0,120.0,*GAS_Z,r_in=12.5))
lk = lk.cut(cz(5.15,92.0,168.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk = lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk = lk.cut(cz(3.1,TONGUE['z'][0]-2,TONGUE['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid(), "P4 %d"%len(lk.Solids)
doc.getObject("P4_ShankLink_Horn").Shape = lk

# ---- P2: gusset trimmed anterior of X=4 ----
up = bx(CAV_X[0]+0.4,CAV_X[1]-0.4,*Y_TONGUE,CAV_Z[0]+0.4,CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X,Y_TONGUE[1]-6,Y_TOP,*BOX_Z)).cut(bx(*CAV_X,Y_TONGUE[1]+2,Y_TOP+2,*CAV_Z))
up = up.fuse(bx(BOX_X[0]+4,BOX_X[1]-4,190.0,270.0,88.0,100.0))
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1))
    gus = bar((-30.0,A[1]-84.0),(A[0],A[1]),12.0,8.0,z0,z1)
    up = up.fuse(gus.common(bx(-60.0,4.0,A[1]-92.0,A[1]+4.0,z0,z1)))
up = up.fuse(bx(-14.0,6.0,Ya,Yb,122.0,164.0))
for z0,z1 in CLEV2_Z: up = up.fuse(bx(-10.0,36.0,Ya,Yb,z0,z1))
up = up.cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*LINK)).cut(bx(-14.0,40.0,Ya-4.0,A[1]+7.0,*GAS_Z))
up = up.cut(cz(5.15,92.0,168.0,*A))
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25,y0,y0+30.0,BOX_Z[0]-2,BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2,87.0,99.0,x,y))
assert len(up.Solids)==1 and up.isValid(), "P2 %d"%len(up.Solids)
doc.getObject("P2_ThighUpright_Upper").Shape = up
print("P1 %.1f  P2 %.1f  P4 %.1f cm3, all single solids"
      % (low.Volume/1000, up.Volume/1000, lk.Volume/1000))
pose(0.0); doc.recompute(); doc.save(); print("saved")
