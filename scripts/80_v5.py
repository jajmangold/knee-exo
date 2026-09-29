# -*- coding: utf-8 -*-
"""v5: P2 (machined 10 mm plate) -> 2020 V-slot + knee hinge plate + through-bolted rod
clevis block. The 2020 doubles as the telescoping tongue, so P6 becomes a plain socket.
Z: rail 88-108 | yoke 108-120 | hinge plate 122-134 | 2020 134-154 | rod eye 137-147"""
import math
HINGE_Z=(122.0,134.0); SH20_Z=(134.0,154.0); SH20_X=(-10.0,10.0)
ROD_Z=(137.0,147.0); EAR_Z=((127.0,137.0),(147.0,157.0))
SH20_Y=(-235.0,-25.0)
globals().update(HINGE_Z=HINGE_Z,SH20_Z=SH20_Z,SH20_X=SH20_X,ROD_Z=ROD_Z,EAR_Z=EAR_Z,SH20_Y=SH20_Y)
for n in ("P2_ShankBracket_ALU","P6_ShankSlideHousing"):
    if doc.getObject(n): doc.removeObject(n)
# ---- A4 shank 2020 (off-the-shelf) ----
s20=bx(*SH20_X,*SH20_Y,*SH20_Z)
for zo in (10.0,):
    s20=s20.cut(bx(SH20_X[0]+zo-3.,SH20_X[0]+zo+3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]-1,SH20_Z[0]+4.))
    s20=s20.cut(bx(SH20_X[0]+zo-3.,SH20_X[0]+zo+3.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[1]-4.,SH20_Z[1]+1))
for zo in (10.0,):
    s20=s20.cut(bx(SH20_X[0]-1,SH20_X[0]+4.,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]+zo-3.,SH20_Z[0]+zo+3.))
    s20=s20.cut(bx(SH20_X[1]-4.,SH20_X[1]+1,SH20_Y[0]-1,SH20_Y[1]+1,SH20_Z[0]+zo-3.,SH20_Z[0]+zo+3.))
s20=s20.cut(cy(4.2,SH20_Y[0]-1,SH20_Y[1]+1,0.0,144.0))
add("A4_Shank2020_VSlot",s20,(0.62,0.64,0.66),G_S)
# ---- P2a knee hinge plate (laps the 2020's inboard face) ----
hp = cz(34.0,*HINGE_Z).fuse(bar((0.0,0.0),(0.0,-95.0),20.0,16.0,*HINGE_Z))
hp = hp.cut(cz(6.25,HINGE_Z[0]-2,HINGE_Z[1]+2))
hp = hp.cut(cz(10.6,HINGE_Z[0]-.5,HINGE_Z[0]+4.2)).cut(cz(10.6,HINGE_Z[1]-4.2,HINGE_Z[1]+.5))
for y in (-40.0,-60.0,-80.0): hp=hp.cut(cz(2.6,HINGE_Z[0]-1,HINGE_Z[1]+1,0.0,y))   # bolts into the 2020
assert len(hp.Solids)==1 and hp.isValid() and hp.isClosed(),"P2a %d"%len(hp.Solids)
add("P2a_KneeHingePlate",hp,(0.70,0.72,0.75),G_S)
# ---- P2b rod clevis block (through-bolted to the 2020's posterior face) ----
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
cb = bx(2.0,14.0,D0[1]-26.0,D0[1]+26.0,SH20_Z[0]-2.0,SH20_Z[1]+2.0)      # root on the 2020 face
cb = cb.fuse(bar((8.0,D0[1]),D0,14.0,15.0,EAR_Z[0][0],EAR_Z[1][1]))
cb = cb.cut(cz(11.5,*ROD_Z,*D0)).cut(sector_at(D0,46.0,b0,b1,*ROD_Z,r_in=11.5))
cb = cb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
for dy in (-18.0,18.0): cb=cb.cut(cy(2.6,-2.0,20.0,0.0,SH20_Z[0]+10.0+0.0))       # placeholder
cb = cb.cut(bx(-2.0,10.5,D0[1]-30.0,D0[1]+30.0,SH20_Z[0]-3.0,SH20_Z[1]+3.0))      # clear the 2020
for dy in (-16.0,16.0):
    cb = cb.cut(Part.makeCylinder(2.6,30.0,V(0.0,D0[1]+dy,144.0),V(1,0,0)))        # M5 through-bolts
assert len(cb.Solids)==1 and cb.isValid() and cb.isClosed(),"P2b %d"%len(cb.Solids)
add("P2b_RodClevisBlock",cb,(0.70,0.72,0.75),G_S)
# ---- P6 socket: the 2020 is now the tongue ----
hs = bx(-24.0,24.0,-300.0,-228.0,SH20_Z[0]-14.0,SH20_Z[1]+14.0)
hs = hs.cut(bx(SH20_X[0]-0.3,SH20_X[1]+0.3,-301.0,-243.0,SH20_Z[0]-0.3,SH20_Z[1]+0.3))
hs = hs.fuse(bx(-30.0,30.0,-300.0,-190.0,68.0,78.0))
hs = hs.fuse(bx(-8.0,8.0,-296.0,-200.0,76.0,SH20_Z[0]-4.0))
for xa,xb in ((14.0,22.0),(-22.0,-14.0)): hs=hs.fuse(bx(xa,xb,-292.0,-204.0,70.0,SH20_Z[0]-4.0))
hs = hs.cut(bx(-3.0,3.0,-274.0,-252.0,SH20_Z[1]+8.0,SH20_Z[1]+16.0))
CUFF_SH=[(-22.0,-215.0),(22.0,-215.0),(-22.0,-275.0),(22.0,-275.0)]
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.0,79.0,x,y))
assert len(hs.Solids)==1 and hs.isValid() and hs.isClosed(),"P6 %d"%len(hs.Solids)
add("P6_ShankSocket",hs,(0.85,0.35,0.15),G_S)
# shank cuff moves down to match
Y_SHC2=(-310.0,-190.0)
sc=arc_shell(R_SH+PAD,R_SH+PAD+SHELL,*Y_SHC2).fuse(bx(-30.0,30.0,Y_SHC2[0]+5,Y_SHC2[1]-5,56.0,68.0))
for x,y in CUFF_SH: sc=sc.cut(cz(2.75,54.0,70.0,x,y))
for b in (256.0,64.0):
    for y in (Y_SHC2[0]+22,Y_SHC2[1]-22):
        sl=bx(-2.6,2.6,y-20.0,y+20.0,R_SH+PAD-6.0,R_SH+PAD+SHELL+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); sc=sc.cut(sl)
doc.getObject("P7_ShankCuff").Shape=sc
# ---- carriage + rod at the new Z ----
def build_carriage(t):
    s=carr(t)
    c=bx(4.,76.,s-34.,s+34.,*CAR_Z).fuse(cz(16.,CAR_Z[1],EAR_Z[1][1],XE,s))
    c=c.cut(cz(11.5,*ROD_Z,XE,s)).cut(sector_at((XE,s),52.,c0,c1,*ROD_Z,r_in=11.5))
    c=c.cut(cz(4.1,CAR_Z[1]-2,EAR_Z[1][1]+2,XE,s)).cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    zc=(ROD_Z[0]+ROD_Z[1])/2
    return Part.makeCylinder(4.,L,V(D[0],D[1],zc),V(ux,uy,0.)).fuse(
           cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*D)).fuse(cz(10.,ROD_Z[0]+.5,ROD_Z[1]-.5,*C))
SHANK=[doc.getObject(n) for n in ("A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock",
        "P6_ShankSocket","P7_ShankCuff","REF_Shank") if doc.getObject(n)]
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals().update(build_carriage=build_carriage,build_rod=build_rod,SHANK=SHANK,pose=pose)
pose(0.0); doc.recompute(); doc.saveAs(r"C:\Users\Josh\KneeExo_v5.FCStd")
for n in ("P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket","P7_ShankCuff"):
    s=doc.getObject(n).Shape
    print("  %-24s %6.1f cm3 solids=%d closed=%s"%(n,s.Volume/1000,len(s.Solids),s.isClosed()))
print("saved",doc.FileName)
