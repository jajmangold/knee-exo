# -*- coding: utf-8 -*-
"""v5b restack: 2020 INBOARD at Z 108-128 (the yoke's disc only reaches r=40, so the 2020
can start at Y=-45). Hinge plate laps the 2020's ANTERIOR face, rod clevis its POSTERIOR
face - opposite sides, no clash. Motor becomes the width driver again."""
import math
SH20_Z=(108.0,128.0); SH20_X=(-10.0,10.0); SH20_Y=(-255.0,-45.0)
HINGE_Z=(122.0,134.0); ROD_Z=(118.0,128.0); EAR_Z=((108.0,118.0),(128.0,138.0))
globals().update(SH20_Z=SH20_Z,SH20_X=SH20_X,SH20_Y=SH20_Y,HINGE_Z=HINGE_Z,ROD_Z=ROD_Z,EAR_Z=EAR_Z)
# ---- 2020 ----
s20=bx(*SH20_X,*SH20_Y,*SH20_Z)
s20=s20.cut(bx(-3.,3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4.))
s20=s20.cut(bx(-3.,3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4.,SH20_Z[1]+1))
s20=s20.cut(bx(SH20_X[0]-1,SH20_X[0]+4.,SH20_Y[0]-1,SH20_Y[1]+1,115.,121.))
s20=s20.cut(bx(SH20_X[1]-4.,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,115.,121.))
s20=s20.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.0,118.0))
doc.getObject("A4_Shank2020_VSlot").Shape=s20
# ---- P2a hinge plate: pivot at O, laps the 2020's ANTERIOR face ----
hp = cz(32.0,*HINGE_Z).fuse(bar((0.0,-10.0),(-18.0,-120.0),22.0,15.0,*HINGE_Z))
hp = hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp = hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-60.,-85.,-110.):
    hp = hp.cut(Part.makeCylinder(2.6,40.,V(-30.,y,128.),V(1,0,0)))     # bolts into the 2020
assert len(hp.Solids)==1 and hp.isValid() and hp.isClosed(),"P2a %d"%len(hp.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=hp
# ---- P2b rod clevis: POSTERIOR face of the 2020 ----
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
b0,b1=min(bs)-15.,max(bs)+15.; c0,c1=min(cs)-12.,max(cs)+12.
cb = bx(10.0,20.0,D0[1]-28.0,D0[1]+28.0,SH20_Z[0]-2.0,SH20_Z[1]+2.0)
cb = cb.fuse(bar((16.0,D0[1]),D0,15.0,15.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,46.0,b0,b1,*ROD_Z,r_in=11.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-18.,18.):
    cb = cb.cut(Part.makeCylinder(2.6,40.,V(-4.,D0[1]+dy,118.),V(1,0,0)))   # M5 through-bolts
assert len(cb.Solids)==1 and cb.isValid() and cb.isClosed(),"P2b %d"%len(cb.Solids)
doc.getObject("P2b_RodClevisBlock").Shape=cb
# ---- P6 socket (8 mm walls) ----
hs = bx(-20.0,20.0,-318.0,-248.0,SH20_Z[0]-9.0,SH20_Z[1]+9.0)
hs = hs.cut(bx(SH20_X[0]-0.3,SH20_X[1]+0.3,-319.0,-262.0,SH20_Z[0]-0.3,SH20_Z[1]+0.3))
hs = hs.fuse(bx(-30.0,30.0,-318.0,-208.0,68.0,78.0))
hs = hs.fuse(bx(-8.0,8.0,-314.0,-218.0,76.0,SH20_Z[0]-6.0))
for xa,xb in ((14.,22.),(-22.,-14.)): hs=hs.fuse(bx(xa,xb,-310.,-222.,70.,SH20_Z[0]-6.0))
hs = hs.cut(bx(-3.,3.,-292.,-270.,SH20_Z[1]+3.,SH20_Z[1]+11.))
CUFF_SH=[(-22.,-233.),(22.,-233.),(-22.,-293.),(22.,-293.)]
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.,79.,x,y))
assert len(hs.Solids)==1 and hs.isValid() and hs.isClosed(),"P6 %d"%len(hs.Solids)
doc.getObject("P6_ShankSocket").Shape=hs
Y_SHC2=(-328.0,-208.0)
sc=arc_shell(R_SH+PAD,R_SH+PAD+SHELL,*Y_SHC2).fuse(bx(-30.,30.,Y_SHC2[0]+5,Y_SHC2[1]-5,56.,68.))
for x,y in CUFF_SH: sc=sc.cut(cz(2.75,54.,70.,x,y))
for b in (256.,64.):
    for y in (Y_SHC2[0]+22,Y_SHC2[1]-22):
        sl=bx(-2.6,2.6,y-20.,y+20.,R_SH+PAD-6.,R_SH+PAD+SHELL+6.)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.)); sc=sc.cut(sl)
doc.getObject("P7_ShankCuff").Shape=sc
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-34.,s+34.,*CAR_Z).fuse(cz(16.,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c=c.cut(cz(11.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=11.5))
    c=c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    zc=(ROD_Z[0]+ROD_Z[1])/2
    return Part.makeCylinder(4.,L,V(D[0],D[1],zc),V(ux,uy,0.)).fuse(
           cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*D)).fuse(cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*C))
globals().update(build_carriage=build_carriage,build_rod=build_rod)
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals()['pose']=pose
pose(0.0); doc.recompute(); doc.save()
print("rebuilt. 2020 Z %s, hinge %s, rod eye %s"%(SH20_Z,HINGE_Z,ROD_Z))
