# -*- coding: utf-8 -*-
"""Rod pivot 25 -> 32 mm posterior so the 608 housing clears the shank 2020's corner."""
import math
D0=(32.0,-67.5); globals()['D0']=D0
LROD=math.hypot(XE-D0[0], 85.0-D0[1]); globals()['LROD']=LROD
def carr(t):
    D=rot2(D0,t); dd=LROD*LROD-(XE-D[0])**2
    assert dd>0; return D[1]+math.sqrt(dd)
def armv(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s); L=math.hypot(C[0]-D[0],C[1]-D[1])
    return abs(D[0]*(C[1]-D[1])/L - D[1]*(C[0]-D[0])/L)
globals().update(carr=carr,armv=armv)
def Rth(y): return 62.0+(85.0-62.0)*max(0.0,min(y,300.0))/300.0
pen=-999.
for t in (85.,90.,95.,100.,105.):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    for i in range(61):
        f=i/60.; x=D[0]+(C[0]-D[0])*f; y=D[1]+(C[1]-D[1])*f
        if y>=60.: pen=max(pen,x-Rth(y))
print("|D|=%.1f mm  rod %.1f  travel %.1f  seat %+.1f mm -> %s"
      %(math.hypot(*D0),LROD,carr(105.)-carr(-2.),pen,"CLEAR" if pen<=0 else "FOULS"))
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
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L; nx,ny=-uy,ux
    r = cz(14.0,*ROD_Z,*D).fuse(cz(14.0,*ROD_Z,*C))
    p0=(D[0]+ux*INSET,D[1]+uy*INSET); p1=(C[0]-ux*INSET,C[1]-uy*INSET)
    pts=[(p0[0]+nx*10,p0[1]+ny*10),(p1[0]+nx*10,p1[1]+ny*10),
         (p1[0]-nx*10,p1[1]-ny*10),(p0[0]-nx*10,p0[1]-ny*10)]
    w=Part.makePolygon([V(x,y,BAR_Z[0]) for x,y in pts]+[V(pts[0][0],pts[0][1],BAR_Z[0])])
    r = r.fuse(Part.Face(w).extrude(V(0,0,BAR_Z[1]-BAR_Z[0])))
    return r.cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*D)).cut(cz(4.1,ROD_Z[0]-2,ROD_Z[1]+2,*C))
cb = bx(10.0,22.0,D0[1]-30.0,D0[1]+30.0,SH20_Z[0],EAR_Z[0][1])
cb = cb.fuse(bar((18.0,D0[1]),D0,17.0,17.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(15.5,*ROD_Z,*D0)).cut(sector_at(D0,52.0,b0,b1,*ROD_Z,r_in=15.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-20.,20.): cb=cb.cut(Part.makeCylinder(2.6,44.,V(-4.,D0[1]+dy,131.),V(1,0,0)))
assert len(cb.Solids)==1 and cb.isClosed(),"P2b %d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-36.,s+36.,*CAR_Z).fuse(cz(17.,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c=c.cut(cz(15.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=15.5))
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
pose(0.0); doc.recompute(); doc.save()
KT=8.27/190.; FA=2*math.pi*.9*KT/.020
print("%5s %8s %9s %7s"%("flex","arm mm","F@25N.m","amps"))
for t in (0,30,60,90,105):
    a=armv(float(t)); print("%5d %8.1f %8.0f N %6.1f"%(t,a,25000/a,25000/a/FA))
