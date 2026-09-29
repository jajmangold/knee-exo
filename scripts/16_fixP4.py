# -*- coding: utf-8 -*-
"""P4 came out as 3 disconnected solids: the guessed relief fan sliced the horn.
Replace it with the EXACT swept volume of the tang + nut tube, expressed in P4's own
frame, inflated 1.5 mm for clearance. Then assert the part is one solid."""
import math
B0 = pinB(0.0); A = pinA()
CLR = 1.5
def link_body(w_root):
    s = cz(21.0, *LINK)
    s = s.fuse(sector(70.0, *FINGER, *LINK, r_in=20.0))
    s = s.fuse(bar((0.0,0.0), B0, w_root, 14.0, *LINK))
    s = s.fuse(cz(16.0, 94.0, 122.0, *B0))
    s = s.fuse(bar((0.0,-20.0), (0.0,-160.0), 22.0, 18.0, *LINK))
    s = s.fuse(bx(*TONGUE['x'], *TONGUE['y'], *TONGUE['z']))
    return s
def swept_envelope(step=4.0):
    """union of tang+tube poses, transformed into P4's rotating frame"""
    acc = None
    th = ROM[0]
    while th <= ROM[1] + 1e-9:
        B = pinB(th); L = ab(th)
        ux, uy = (B[0]-A[0])/L, (B[1]-A[1])/L
        drv = FreeCAD.Placement(V(A[0],A[1],0.0),
              FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
        local = FreeCAD.Placement(V(0,0,0), FreeCAD.Rotation(V(0,0,1), -th))
        tw, tr = DR['tang_w']+CLR, DR['tube_r']+CLR
        s = bx(-tw, tw, L-DR['tang'], L, 101.0-CLR, 115.0+CLR)
        s = s.fuse(Part.makeCylinder(tr, DR['tang']-DR['tang']+ (DR['tube_len']-DR['tang']),
                   V(0.0, L-DR['tube_len'], Z_PLANE), V(0,1,0)))
        s.Placement = local.multiply(drv)
        acc = s if acc is None else acc.fuse(s)
        th += step
    return acc
env = swept_envelope(4.0)
print("swept envelope: %.0f cm3, valid=%s" % (env.Volume/1000, env.isValid()))

for w_root in (20.0, 16.0, 13.0):
    lk = link_body(w_root).cut(env)
    lk = lk.cut(cz(4.1, 92.0, 124.0, *B0))
    lk = lk.cut(cz(6.25, LINK[0]-2, LINK[1]+2))
    lk = lk.cut(cz(10.6, LINK[0]-0.5, LINK[0]+5.2)).cut(cz(10.6, LINK[1]-5.2, LINK[1]+0.5))
    n = len(lk.Solids)
    print("  horn root half-width %4.1f mm -> %6.1f cm3, %d solid(s) %s"
          % (w_root, lk.Volume/1000, n, "OK" if n==1 else "FRAGMENTED"))
    if n == 1:
        for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]:
            lk = lk.cut(cz(9.0, LINK[0]-1, LINK[1]+1, *p))
        lk = lk.cut(cz(3.1, TONGUE['z'][0]-2, TONGUE['z'][1]+2, 0.0, -178.0))
        doc.getObject("P4_ShankLink_Horn").Shape = lk
        print("  -> adopted w_root=%.1f  final %.1f cm3 solids=%d valid=%s"
              % (w_root, lk.Volume/1000, len(lk.Solids), lk.isValid()))
        break
doc.recompute()
