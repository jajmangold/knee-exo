# -*- coding: utf-8 -*-
"""v3 knee parts: P1 fork + raked lower upright, P4 shank link with crank at bearing -30."""
import math
B0 = pinB(0.0)
SLOT_Z,CHEEK_Z,R_CHEEK=(99.6,116.4),(94.0,122.0),(24.0,80.0)
UA = pol(190.0, UPR_B)          # lower upright runs from the knee out to r=190
# ---------- P1 ----------
def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low = fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
low = low.fuse(bar((0.0,0.0), UA, UPR_W, UPR_W, 88.0, 128.0))     # raked upright
low = low.cut(cz(80.0, *GAP))                                     # keep the joint gap open
low = low.cut(bar(pol(153.0,UPR_B), pol(196.0,UPR_B), 25.0, 25.0, 108.0, 130.0))  # lap for P2
low = low.cut(cz(6.15, FORK_IN[0]-2, FORK_OUT[1]+2))
for b,_ in FLEX_HOLES+EXT_HOLES:
    low = low.cut(cz(D_PIN/2+0.1, FORK_IN[0]-2, FORK_OUT[1]+2, *pol(R_PIN,b)))
for z0,z1 in (FORK_IN,FORK_OUT):
    for b in (140,175,210,240): low = low.cut(cz(10.0,z0-1,z1+1,*pol(52.0,b)))
for r in (120.0, 145.0):                                          # lightening in the shaft
    low = low.cut(cz(11.0, 86.0, 130.0, *pol(r,UPR_B)))
for r in (165.0, 185.0):                                          # lap bolts
    low = low.cut(cz(2.75, 86.0, 130.0, *pol(r,UPR_B)))
assert len(low.Solids)==1 and low.isValid() and low.isClosed(), "P1 %d solids"%len(low.Solids)
add("P1_ThighUpright_Lower", low, (0.20,0.42,0.75), G_TH)

# ---------- P4 ----------
ann_cheek = cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot  = cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk = cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk = lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk = lk.fuse(cz(16.0,*CHEEK_Z,*B0))
lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
lk = lk.fuse(bx(*TONGUE['x'],*TONGUE['y'],*TONGUE['z']))
slot = cz(24.0,*SLOT_Z,*B0).fuse(sector_at(B0,52.0,-5.0,125.0,*SLOT_Z,r_in=24.0))
lk = lk.cut(slot.common(ann_slot)).cut(cz(13.0,*SLOT_Z,*B0))
lk = lk.cut(cz(5.15,92.0,126.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk = lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk=lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk = lk.cut(cz(3.1,TONGUE['z'][0]-2,TONGUE['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid() and lk.isClosed(), "P4 %d solids"%len(lk.Solids)
add("P4_ShankLink_Horn", lk, (0.75,0.20,0.22), G_SH)
# hardware
pf,pe = pol(R_PIN,FLEX_HOLES[0][0]), pol(R_PIN,EXT_HOLES[0][0])
add("HW_ROMpin_flexion_105deg", cz(6.0,84.0,132.0,*pf), (0.55,0.55,0.58), G_TH)
add("HW_ROMpin_extension_0deg", cz(6.0,84.0,132.0,*pe), (0.55,0.55,0.58), G_TH)
add("HW_PinB_10", cz(5.0,92.0,126.0,*B0), (0.85,0.75,0.20), G_SH)
doc.recompute()
print("P1 %.1f cm3  P4 %.1f cm3  both single closed solids"%(low.Volume/1000, lk.Volume/1000))
print("crank pin B0 = (%.1f, %.1f) bearing %.0f" % (*B0, -30.0))
