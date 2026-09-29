# -*- coding: utf-8 -*-
"""P2 rebuilt clean. The outboard gas-spring clevis plates need a WEB tying them back to
the upright box (which only reaches Z 128), and the eye slots must stay open toward -Y
only, so the outer plate keeps a proximal bridge. Web is held anterior of X=6 to clear
the gas cylinder."""
import math
A = pinA()
CUFF_TH_PTS = [(-40.0,195.0),(-12.0,195.0),(-40.0,265.0),(-12.0,265.0)]
CLEV_Z  = ((94.0,101.0),(115.0,122.0))      # ballscrew eye gap 101-115
CLEV2_Z = ((129.0,136.0),(150.0,157.0))     # gas eye gap 136-150
GAS_Z   = (136.0,150.0)

up = bx(CAV_X[0]+0.4, CAV_X[1]-0.4, *Y_TONGUE, CAV_Z[0]+0.4, CAV_Z[1]-0.4)   # tongue
up = up.fuse(bx(*BOX_X, Y_TONGUE[1]-6, 300.0, *BOX_Z))                       # box
up = up.cut(bx(*CAV_X, Y_TONGUE[1]+2, 302.0, *CAV_Z))                        # hollow
up = up.fuse(bx(BOX_X[0]+4, BOX_X[1]-4, 190.0, 270.0, 88.0, 100.0))          # cuff boss
# ballscrew clevis (ties to the box through X -10..-2)
for z0,z1 in CLEV_Z:
    up = up.fuse(bx(-10.0, 36.0, 232.0, 268.0, z0, z1))
    up = up.fuse(bar((-30.0,205.0),(A[0],A[1]), 12.0, 8.0, z0, z1))
# outboard web + gas clevis
up = up.fuse(bx(-14.0, 6.0, 232.0, 268.0, 122.0, 157.0))
for z0,z1 in CLEV2_Z:
    up = up.fuse(bx(-10.0, 36.0, 232.0, 268.0, z0, z1))
# eye slots: open toward -Y, bridged at Y 256-268
up = up.cut(bx(-14.0, 40.0, 228.0, 256.0, *LINK))        # ballscrew eye 100-116
up = up.cut(bx(-14.0, 40.0, 228.0, 256.0, *GAS_Z))       # gas eye 136-150
up = up.cut(cz(5.15, 92.0, 160.0, *A))                   # 10 mm pin A
for y0 in (80.0,130.0): up = up.cut(bx(-28.75,-23.25, y0, y0+30.0, BOX_Z[0]-2, BOX_Z[1]+2))
for x,y in CUFF_TH_PTS: up = up.cut(cz(3.2, 87.0, 99.0, x, y))
n = len(up.Solids)
print("P2 REV H: %.1f cm3 solids=%d valid=%s" % (up.Volume/1000, n, up.isValid()))
assert n == 1 and up.isValid(), "P2 still in %d pieces" % n
doc.getObject("P2_ThighUpright_Upper").Shape = up
doc.recompute(); doc.save(); print("saved")
