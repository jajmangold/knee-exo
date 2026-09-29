# -*- coding: utf-8 -*-
"""v3 upper upright, cuffs, slide housing, and the COAXIAL INLINE drive."""
import math
A=pinA(); B0=pinB(0.0)
EYE_Z=(113.0,127.0)
Ya,Yb = 336.0, 368.0
CUFF_TH=[(-42.0,195.0),(-14.0,195.0),(-42.0,265.0),(-14.0,265.0)]
# ---------- P2 ----------
up = bx(CAV_X[0]+0.4,CAV_X[1]-0.4,*Y_TONGUE,CAV_Z[0]+0.4,CAV_Z[1]-0.4)
up = up.fuse(bx(*BOX_X,Y_TONGUE[1]-6,Y_TOP,*BOX_Z)).cut(bx(*CAV_X,Y_TONGUE[1]+2,Y_TOP+2,*CAV_Z))
up = up.fuse(bx(BOX_X[0]+4,BOX_X[1]-4,190.0,270.0,100.0,112.0))        # cuff-mount boss
up = up.fuse(bx(-10.0,46.0,Ya,Yb,*BOX_Z))                              # pin-A clevis boss
up = up.fuse(bar((-32.0,A[1]-96.0),(A[0],A[1]),14.0,9.0,*BOX_Z).common(bx(-60.0,4.0,A[1]-104.0,A[1]+4.0,*BOX_Z)))
up = up.cut(bx(-14.0,50.0,330.0,Yb+2,*EYE_Z))                          # eye slot, opens distally
up = up.cut(cz(5.15,98.0,142.0,*A))                                    # 10 mm pin A
for y0 in (80.0,130.0): up=up.cut(bx(-30.75,-25.25,y0,y0+30.0,BOX_Z[0]-2,BOX_Z[1]+2))
for x,y in CUFF_TH: up=up.cut(cz(3.2,99.0,111.0,x,y))
assert len(up.Solids)==1 and up.isValid() and up.isClosed(),"P2 %d"%len(up.Solids)
add("P2_ThighUpright_Upper",up,(0.25,0.50,0.85),G_TH)
# ---------- P3 / P5 / P6 ----------
ri,ro = R_TH+PAD, R_TH+PAD+SHELL
cuff = arc_shell(ri,ro,*Y_THC).fuse(bx(BOX_X[0]+4,BOX_X[1]-4,Y_THC[0]+5,Y_THC[1]-5,76.0,100.0))
for x,y in CUFF_TH: cuff=cuff.cut(cz(2.75,74.0,102.0,x,y))
for b in (256.0,64.0):
    for y in (Y_THC[0]+22,Y_THC[1]-22):
        sl=bx(-2.6,2.6,y-20.0,y+20.0,ri-6.0,ro+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); cuff=cuff.cut(sl)
assert len(cuff.Solids)==1
add("P3_ThighCuff",cuff,(0.95,0.62,0.10),G_TH)
SOCK=dict(x=(-22.0,22.0),y=(-215.0,-145.0),z=(109.0,131.0))
hs=bx(*SOCK['x'],*SOCK['y'],*SOCK['z'])
hs=hs.cut(bx(TONG['x'][0]-0.4,TONG['x'][1]+0.4,-216.0,-157.0,TONG['z'][0]-0.4,TONG['z'][1]+0.4))
hs=hs.cut(bx(-3.0,3.0,-190.0,-165.0,128.0,133.0))
hs=hs.fuse(bx(-30.0,30.0,-273.0,-163.0,68.0,78.0)).fuse(bx(-8.0,8.0,-262.0,-174.0,76.0,111.0))
for xa,xb in ((14.0,22.0),(-22.0,-14.0)): hs=hs.fuse(bx(xa,xb,-258.0,-178.0,70.0,111.0))
CUFF_SH=[(-22.0,-190.0),(22.0,-190.0),(-22.0,-246.0),(22.0,-246.0)]
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.0,79.0,x,y))
assert len(hs.Solids)==1
add("P5_ShankSlideHousing",hs,(0.85,0.35,0.15),G_SH)
sc=arc_shell(R_SH+PAD,R_SH+PAD+SHELL,*Y_SHC).fuse(bx(-30.0,30.0,Y_SHC[0]+5,Y_SHC[1]-5,56.0,68.0))
for x,y in CUFF_SH: sc=sc.cut(cz(2.75,54.0,70.0,x,y))
for b in (256.0,64.0):
    for y in (Y_SHC[0]+22,Y_SHC[1]-22):
        sl=bx(-2.6,2.6,y-20.0,y+20.0,R_SH+PAD-6.0,R_SH+PAD+SHELL+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); sc=sc.cut(sl)
add("P6_ShankCuff",sc,(0.95,0.62,0.10),G_SH)
th=Part.makeCone(62.0,85.0,285.0,V(0,15,0),V(0,1,0)); kn=Part.makeSphere(52.0,V(0,0,0))
sh=Part.makeCone(60.0,38.0,360.0,V(0,-20,0),V(0,-1,0))
for n,s,grp in (("REF_Thigh",th,G_RF),("REF_Knee",kn,G_RF),("REF_Shank",sh,G_SH)):
    o=add(n,s,(0.85,0.75,0.70),grp); o.ViewObject.Transparency=80
# ---------- COAXIAL INLINE DRIVE ----------
def _plc(t):
    B=pinB(t); L=ab(t); ux,uy=(B[0]-A[0])/L,(B[1]-A[1])/L
    return FreeCAD.Placement(V(A[0],A[1],0.0),FreeCAD.Rotation(V(0,0,1),math.degrees(math.atan2(-ux,uy)))),L
def build_drive(t):
    plc,L=_plc(t); p=L-T_TUBE
    def cyl(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,Z_PLANE),V(0,1,0))
    d = cz(11.0,*EYE_Z)                                  # rear eye lug (in the clevis)
    d = d.fuse(cyl(14.0, EYE, EYE+MOTL+CPL+BLKL))        # motor->coupling->block shell
    d = d.fuse(cyl(10.0,*THREAD))                        # SFU2020
    d = d.fuse(cyl(23.0,p,p+NUT+10.0))                   # ball-nut housing
    d = d.fuse(cyl(13.0,p+NUT+10.0,L-TANG))              # output tube
    d = d.fuse(bx(-8.0,8.0,L-TANG,L,*EYE_Z))             # flat tang
    d = d.fuse(cz(11.0,*EYE_Z,0.0,L))                    # pin-B lug
    m = cyl(31.5, EYE, EYE+MOTL)                         # 6374 ON AXIS
    d.Placement=plc; m.Placement=plc
    return d,m,L
dv,mo,_=build_drive(0.0)
add("P7_Drive_Coaxial",dv,(0.30,0.32,0.36),G_DR)
add("P8_Motor_6374",mo,(0.15,0.15,0.18),G_DR)
SHANK_OBJS=[doc.getObject(n) for n in ("P4_ShankLink_Horn","P5_ShankSlideHousing","P6_ShankCuff",
            "REF_Shank","HW_PinB_10") if doc.getObject(n)]
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_=build_drive(t)
    doc.getObject("P7_Drive_Coaxial").Shape=d
    doc.getObject("P8_Motor_6374").Shape=m
    doc.recompute()
globals().update(build_drive=build_drive,pose=pose,SHANK_OBJS=SHANK_OBJS,_plc=_plc,EYE_Z=EYE_Z)
pose(0.0); doc.recompute()
print("v3 built. P2 %.1f P3 %.1f P5 %.1f P6 %.1f cm3"%(up.Volume/1000,cuff.Volume/1000,hs.Volume/1000,sc.Volume/1000))
