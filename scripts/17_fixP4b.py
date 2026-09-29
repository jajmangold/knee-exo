# -*- coding: utf-8 -*-
"""Cheap, exact-enough fix: constant-width horn + bounded relief. Assert ONE solid."""
import math
B0 = pinB(0.0)
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s = sector(r_out,b0,b1,z0,z1,r_in); s.translate(V(c[0],c[1],0.0)); return s
PK = (99.8, 116.2)
best = None
for w_root, fr, b1 in [(20.0,72.0,106.0),(16.0,72.0,108.0),(14.0,78.0,108.0),(14.0,72.0,104.0)]:
    lk = cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
    lk = lk.fuse(bar((0.0,0.0), B0, w_root, 14.0, *LINK)).fuse(cz(16.0, 94.0, 122.0, *B0))
    lk = lk.fuse(bar((0.0,-20.0),(0.0,-160.0), 22.0, 18.0, *LINK))
    lk = lk.fuse(bx(*TONGUE['x'],*TONGUE['y'],*TONGUE['z']))
    lk = lk.cut(cz(40.0, *PK, *B0)).cut(sector_at(B0, fr, -40.0, b1, *PK, r_in=40.0))
    lk = lk.cut(cz(4.1, 92.0, 124.0, *B0)).cut(cz(6.25, LINK[0]-2, LINK[1]+2))
    lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
    n = len(lk.Solids)
    # section modulus of the horn root, bending in-plane
    Zsec = (LINK[1]-LINK[0])*(2*w_root)**2/6.0
    print("w_root %4.1f fan r%.0f b1=%.0f -> %6.1f cm3  %d solid(s)  horn sigma=%5.1f MPa (SF %.1f on 35)"
          % (w_root, fr, b1, lk.Volume/1000, n, 36000.0/Zsec, 35.0/(36000.0/Zsec)))
    if n == 1 and best is None: best = (lk, w_root, fr, b1)
if best is None:
    print("ALL FRAGMENTED - horn needs reshaping"); raise SystemExit
lk, w_root, fr, b1 = best
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
assert len(lk.Solids) == 1 and lk.isValid(), "P4 not a single valid solid"
doc.getObject("P4_ShankLink_Horn").Shape = lk
doc.recompute()
print("\nADOPTED w_root=%.1f fan r%.0f bearings -40..%.0f" % (w_root, fr, b1))
print("P4 final: %.1f cm3  solids=%d  valid=%s" % (lk.Volume/1000, len(lk.Solids), lk.isValid()))
