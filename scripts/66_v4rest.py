# -*- coding: utf-8 -*-
"""Build the parts script 64 never reached, then wire up pose()."""
import math
print("existing:",[o.Name for o in doc.Objects if o.Name.startswith(("P","A"))])
def ensure(n,shape,col,grp,tr=0):
    o=doc.getObject(n)
    if o is None: return add(n,shape,col,grp,tr)
    o.Shape=shape; return o
# thigh cuff (pad now reaches the rail face at Z=88)
CUFF_TH=[(20.0,Y_THC[0]+22),(60.0,Y_THC[0]+22),(20.0,Y_THC[1]-22),(60.0,Y_THC[1]-22)]
tc=arc_shell(R_TH+PAD,R_TH+PAD+SHELL,*Y_THC)
tc=tc.fuse(bx(EXT_X[0],EXT_X[1],Y_THC[0]+5,Y_THC[1]-5,76.0,EXT_Z[0]))
for x,y in CUFF_TH: tc=tc.cut(cz(2.6,74.0,EXT_Z[0]+1,x,y))
for b in (256.0,64.0):
    for y in (Y_THC[0]+18,Y_THC[1]-18):
        sl=bx(-2.6,2.6,y-18.0,y+18.0,R_TH+PAD-6.0,R_TH+PAD+SHELL+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); tc=tc.cut(sl)
assert len(tc.Solids)==1 and tc.isClosed(),"P5 %d"%len(tc.Solids)
ensure("P5_ThighCuff",tc,(0.95,0.62,0.10),G_T)
# shank slide housing
SOCK=dict(x=(-22.0,22.0),y=(-218.0,-148.0),z=(117.0,137.0))
hs=bx(*SOCK['x'],*SOCK['y'],*SOCK['z'])
hs=hs.cut(bx(TONG['x'][0]-0.4,TONG['x'][1]+0.4,-219.0,-160.0,TONG['z'][0]-0.4,TONG['z'][1]+0.4))
hs=hs.cut(bx(-3.0,3.0,-193.0,-168.0,134.0,139.0))
hs=hs.fuse(bx(-30.0,30.0,-273.0,-163.0,68.0,78.0)).fuse(bx(-8.0,8.0,-262.0,-174.0,76.0,119.0))
for xa,xb in ((14.0,22.0),(-22.0,-14.0)): hs=hs.fuse(bx(xa,xb,-258.0,-178.0,70.0,119.0))
CUFF_SH=[(-22.0,-190.0),(22.0,-190.0),(-22.0,-246.0),(22.0,-246.0)]
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.0,79.0,x,y))
assert len(hs.Solids)==1 and hs.isClosed(),"P6 %d"%len(hs.Solids)
ensure("P6_ShankSlideHousing",hs,(0.85,0.35,0.15),G_S)
# shank cuff
sc=arc_shell(R_SH+PAD,R_SH+PAD+SHELL,*Y_SHC).fuse(bx(-30.0,30.0,Y_SHC[0]+5,Y_SHC[1]-5,56.0,68.0))
for x,y in CUFF_SH: sc=sc.cut(cz(2.75,54.0,70.0,x,y))
for b in (256.0,64.0):
    for y in (Y_SHC[0]+22,Y_SHC[1]-22):
        sl=bx(-2.6,2.6,y-20.0,y+20.0,R_SH+PAD-6.0,R_SH+PAD+SHELL+6.0)
        sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); sc=sc.cut(sl)
assert len(sc.Solids)==1 and sc.isClosed()
ensure("P7_ShankCuff",sc,(0.95,0.62,0.10),G_S)
SHANK=[doc.getObject(n) for n in ("P2_ShankBracket_ALU","P6_ShankSlideHousing",
        "P7_ShankCuff","REF_Shank") if doc.getObject(n)]
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
globals().update(SHANK=SHANK,pose=pose)
pose(0.0); doc.recompute(); doc.saveAs(r"C:\Users\Josh\KneeExo_v4.FCStd")
PRN=["P1_KneeYoke","P5_ThighCuff","P6_ShankSlideHousing","P7_ShankCuff"]
ALU=["P2_ShankBracket_ALU"]
tot=0.0
print()
for n in PRN:
    s=doc.getObject(n).Shape; tot+=s.Volume
    print("  printed %-24s %6.1f cm3 solids=%d closed=%s"%(n,s.Volume/1000,len(s.Solids),s.isClosed()))
for n in ALU:
    s=doc.getObject(n).Shape
    print("  ALU     %-24s %6.1f cm3 = %.0f g in 6061"%(n,s.Volume/1000,s.Volume/1000*2.70))
print("  printed total %.0f cm3 -> %.0f g PA6-CF"%(tot/1000,tot/1000*1.19*0.78))
print("saved",doc.FileName)
