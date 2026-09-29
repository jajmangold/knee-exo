# -*- coding: utf-8 -*-
"""P4 REV G - crank horn becomes a FORK over its outer span.
The tang swings inside a 16.4 mm slot; the two 5.8 mm cheeks (Z 94-99.8 / 116.2-122)
carry the bending around it, so nothing is severed. Cheeks exist only outside r=34
from the knee axis, which keeps them clear of the fork plates' hub discs."""
import math
B0 = pinB(0.0)
SLOT_Z  = (99.8, 116.2)
CHEEK_Z = (94.0, 122.0)
R_CHEEK = (34.0, 80.0)          # radial band (from knee axis) where the horn is forked

ann_cheek = cz(R_CHEEK[1], *CHEEK_Z).cut(cz(R_CHEEK[0], CHEEK_Z[0]-1, CHEEK_Z[1]+1))
ann_slot  = cz(R_CHEEK[1], *SLOT_Z ).cut(cz(R_CHEEK[0], SLOT_Z[0]-1,  SLOT_Z[1]+1))

lk = cz(R_SHUB, *LINK)                                          # hub (bearings)
lk = lk.fuse(sector(70.0, *FINGER, *LINK, r_in=20.0))           # ROM stop finger
lk = lk.fuse(bar((0.0,0.0), B0, 18.0, 12.0, *LINK))             # horn, thin core
lk = lk.fuse(bar((0.0,0.0), B0, 18.0, 12.0, *CHEEK_Z).common(ann_cheek))   # horn cheeks
lk = lk.fuse(cz(16.0, *CHEEK_Z, *B0))                           # pin-B tip boss
lk = lk.fuse(bar((0.0,-20.0), (0.0,-160.0), 22.0, 18.0, *LINK)) # shank strut
lk = lk.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))      # telescoping tongue
# tang swing slot, confined to the forked band
slot = cz(22.0, *SLOT_Z, *B0).fuse(sector_at(B0, 44.0, -40.0, 120.0, *SLOT_Z, r_in=22.0))
lk = lk.cut(slot.common(ann_slot))
lk = lk.cut(cz(12.5, *SLOT_Z, *B0))                             # rod-eye clearance at pin B
lk = lk.cut(cz(4.1, CHEEK_Z[0]-2, CHEEK_Z[1]+2, *B0))           # pin B bore
lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))                     # pivot
lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]:
    lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
n = len(lk.Solids)
print("P4 REV G: %.1f cm3  solids=%d  valid=%s" % (lk.Volume/1000, n, lk.isValid()))
assert n == 1 and lk.isValid(), "STILL FRAGMENTED (%d solids)" % n
doc.getObject("P4_ShankLink_Horn").Shape = lk
# cheek bending check at the fork/solid transition
t_cheek = 2*(SLOT_Z[0]-CHEEK_Z[0]); wid = 2*14.0
Zsec = t_cheek*wid*wid/6.0
M = 600.0*math.sin(math.radians(35.0))*40.0
print("fork cheeks: 2 x %.1f mm thick, %.0f mm wide -> sigma %.1f MPa (SF %.1f vs 35 MPa fatigue)"
      % (t_cheek/2, wid, M/Zsec, 35.0/(M/Zsec)))
doc.recompute(); doc.save()
print("saved")
