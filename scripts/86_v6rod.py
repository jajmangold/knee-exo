# -*- coding: utf-8 -*-
"""v6: replace the 8 mm rod with 2020 + printed end housings carrying 2x 608 bearings.
16 mm eye (2x7 mm bearings) pushes the pin joints outboard: eye 128-144, ears 120-128/144-152."""
import math
ROD_Z=(128.0,144.0); EAR_Z=((120.0,128.0),(144.0,152.0)); BAR_Z=(126.0,146.0)
INSET=28.0                                   # pin centre to the 2020's end
globals().update(ROD_Z=ROD_Z,EAR_Z=EAR_Z,BAR_Z=BAR_Z,INSET=INSET)
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    nx,ny=-uy,ux
    r = cz(16.0,*ROD_Z,*D).fuse(cz(16.0,*ROD_Z,*C))            # 608 housings (22 OD + wall)
    p0=(D[0]+ux*INSET, D[1]+uy*INSET); p1=(C[0]-ux*INSET, C[1]-uy*INSET)
    pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),
         (p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
    w=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
    bar20=Part.Face(w).extrude(V(0,0,BAR_Z[1]-BAR_Z[0]))
    r = r.fuse(bar20)
    r = r.cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*D)).cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*C))
    return r
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
ts=[-2.,0.,15.,30.,45.,60.,75.,90.,105.]
bs=unwrap([math.degrees(math.atan2(carr(t)-rot2(D0,t)[1],XE-rot2(D0,t)[0]))-t for t in ts])
cs=unwrap([math.degrees(math.atan2(rot2(D0,t)[1]-carr(t),rot2(D0,t)[0]-XE)) for t in ts])
b0,b1=min(bs)-18.,max(bs)+18.; c0,c1=min(cs)-15.,max(cs)+15.
# clevis block with a 16 mm slot
cb = bx(10.0,20.0,D0[1]-30.0,D0[1]+30.0,SH20_Z[0],EAR_Z[0][1])
cb = cb.fuse(bar((16.0,D0[1]),D0,17.0,18.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(17.5,*ROD_Z,*D0)).cut(sector_at(D0,52.0,b0,b1,*ROD_Z,r_in=17.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-20.,20.): cb=cb.cut(Part.makeCylinder(2.6,40.,V(-4.,D0[1]+dy,131.),V(1,0,0)))
assert len(cb.Solids)==1 and cb.isClosed(),"P2b %d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-36.,s+36.,*CAR_Z).fuse(cz(19.,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c=c.cut(cz(17.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=17.5))
    c=c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
globals().update(build_rod=build_rod,build_carriage=build_carriage)
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals()['pose']=pose
doc.getObject("P4_Rod_8mm").Label="P4_Rod_2020_608"
pose(0.0); doc.recompute()
print("2020 rod: eye %s, bar %s, ears %s"%(ROD_Z,BAR_Z,EAR_Z))
print("2020 length between housings = %.0f mm"%(153.2-2*INSET))
