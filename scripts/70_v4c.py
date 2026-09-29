# -*- coding: utf-8 -*-
"""Unwrap the rod bearings (they cross 0/360) before cutting the clevis slot."""
import math
def unwrap(vals):
    out=[vals[0]]
    for v in vals[1:]:
        p=out[-1]
        while v-p>180: v-=360
        while p-v>180: v+=360
        out.append(v)
    return out
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
raw=[math.degrees(math.atan2(carr(t)-rot2(D0,t)[1], XE-rot2(D0,t)[0]))-t for t in ts]
bs=unwrap(raw)
b0,b1=min(bs)-15.0,max(bs)+15.0
print("rod bearing in bracket frame: %.0f -> %.0f deg (sweep %.0f); slot %.0f..%.0f"
      %(bs[0],bs[-1],abs(bs[-1]-bs[0]),b0,b1))
raw2=[math.degrees(math.atan2(rot2(D0,t)[1]-carr(t), rot2(D0,t)[0]-XE)) for t in ts]
cs=unwrap(raw2); c0,c1=min(cs)-12.0,max(cs)+12.0
print("rod bearing in carriage frame: %.0f -> %.0f (sweep %.0f); slot %.0f..%.0f"
      %(cs[0],cs[-1],abs(cs[-1]-cs[0]),c0,c1))
# ---- P2 with a correct slot ----
sb = bar((0.0,0.0),D0,24.0,19.0,*SBR_Z).fuse(bar(D0,(0.0,-205.0),19.0,18.0,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
sb = sb.fuse(cz(19.0,EAR_Z[0][0],EAR_Z[1][1],*D0))
sb = sb.cut(cz(13.0,*ROD_Z,*D0))
sb = sb.cut(sector_at(D0,58.0,b0,b1,*ROD_Z,r_in=13.0))
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
sb = sb.cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-0.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+0.5))
for p in ((0.0,-120.0),(0.0,-160.0),(0.0,-185.0)): sb=sb.cut(cz(8.0,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d"%len(sb.Solids)
doc.getObject("P2_ShankBracket_ALU").Shape=sb
# ---- carriage with a correct slot ----
def build_carriage(t):
    s=carr(t)
    c = bx(EXT_X[0]-6.0,EXT_X[1]+6.0,s-36.0,s+36.0,*CAR_Z)
    c = c.fuse(cz(19.0,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c = c.cut(cz(13.0,*ROD_Z,XE,s))
    c = c.cut(sector_at((XE,s),58.0,c0,c1,*ROD_Z,r_in=13.0))
    c = c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s))
    c = c.cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
globals()['build_carriage']=build_carriage
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals()['pose']=pose
pose(0.0); doc.recompute(); doc.save()
print("P2 %.1f cm3 single closed solid"%(sb.Volume/1000))
