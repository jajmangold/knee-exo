# -*- coding: utf-8 -*-
"""Final clearance: widen the tang slot, pull the fork plate sector back to 88 deg."""
import math
A = pinA(); B0 = pinB(0.0)
R_HUB, PLATE_SEC = 24.0, (88.0, 252.0)
SLOT_Z, CHEEK_Z, R_CHEEK = (99.6,116.4), (94.0,122.0), (24.0, 80.0)
GAS_Z = (143.0,157.0)
FLEX_HOLES=[(238,105),(228,95),(218,85),(208,75),(198,65),(188,55)]
EXT_HOLES=[(99.6,0),(109.6,10),(119.6,20)]
Y_TWIN, Y_CLOSED = (25.0,84.0), 75.0

def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
for z0,z1 in (FORK_IN,FORK_OUT): low = low.fuse(bx(*BOX_X,*Y_TWIN,z0,z1))
low = low.fuse(bx(*BOX_X,Y_CLOSED,170.0,*BOX_Z)).cut(bx(*CAV_X,Y_CLOSED+4,172.0,*CAV_Z))
for z0,z1 in (FORK_IN,FORK_OUT):
    for b in (100,135,170,205,235): low = low.cut(cz(11.0,z0-1,z1+1,*pol(54.0,b)))
low = low.cut(cz(6.15,FORK_IN[0]-2,FORK_OUT[1]+2))
for b,_ in FLEX_HOLES+EXT_HOLES: low = low.cut(cz(D_PIN/2+0.1,FORK_IN[0]-2,FORK_OUT[1]+2,*pol(R_PIN,b)))
for y in (110.0,150.0): low = low.cut(cz(2.75,BOX_Z[0]-2,BOX_Z[1]+2,-26.0,y))
assert len(low.Solids)==1 and low.isValid()
doc.getObject("P1_ThighUpright_Lower").Shape = low

ann_cheek = cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot  = cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk = cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk = lk.fuse(cz(16.0,*CHEEK_Z,*B0)).fuse(cz(16.0,122.0,164.0,*B0))
lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk = lk.fuse(bx(*TONGUE['x'],*TONGUE['y'],*TONGUE['z']))
slot = cz(24.0,*SLOT_Z,*B0).fuse(sector_at(B0,52.0,-46.0,126.0,*SLOT_Z,r_in=24.0))
lk = lk.cut(slot.common(ann_slot)).cut(cz(13.0,*SLOT_Z,*B0))
lk = lk.cut(cz(13.0,*GAS_Z,*B0)).cut(sector_at(B0,52.0,-46.0,126.0,*GAS_Z,r_in=13.0))
lk = lk.cut(cz(5.15,92.0,168.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk = lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk = lk.cut(cz(3.1,TONGUE['z'][0]-2,TONGUE['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid()
doc.getObject("P4_ShankLink_Horn").Shape = lk
print("P1 %.1f  P4 %.1f cm3 single solids" % (low.Volume/1000, lk.Volume/1000))
pose(0.0); doc.recompute(); doc.save()
