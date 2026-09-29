# -*- coding: utf-8 -*-
"""Rod clevis: ears must overlap the bracket in Z, and the eye pocket needs a swept
opening (rod sweeps 77 deg relative to the bracket, 28 deg relative to the carriage)."""
import math
EXT_Z=(88.0,108.0); CAR_Z=(108.0,122.0); SCREW_Z=115.0; SCREW_R=8.0
ROD_Z=(122.0,132.0); EAR_Z=((112.0,122.0),(132.0,142.0))
FORK_Z=((108.0,120.0),(134.0,146.0)); SBR_Z=(122.0,132.0)
TONG=dict(x=(-13.0,13.0),y=(-200.0,-153.0),z=(122.0,132.0))
Y_THC=(150.0,260.0)
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(b1-b0)%360 or 360)
    s.rotate(V(0,0,0),V(0,0,1),b0)
    if r_in>0: s=s.cut(cz(r_in,z0-1,z1+1))
    s.translate(V(c[0],c[1],0.0)); return s
g=globals(); g.update(EXT_Z=EXT_Z,CAR_Z=CAR_Z,SCREW_Z=SCREW_Z,SCREW_R=SCREW_R,ROD_Z=ROD_Z,
    EAR_Z=EAR_Z,FORK_Z=FORK_Z,SBR_Z=SBR_Z,TONG=TONG,Y_THC=Y_THC,sector_at=sector_at)
# rod bearings relative to each body, over the ROM
def rodbear(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    gb=math.degrees(math.atan2(C[1]-D[1],C[0]-D[0]))
    return (gb-t)%360, (math.degrees(math.atan2(D[1]-s,D[0]-XE)))%360
bs=[rodbear(x) for x in (ROM[0],0,30,60,90,105)]
print("rod bearing in BRACKET frame %.0f..%.0f ; in CARRIAGE frame %.0f..%.0f"
      %(min(b[0] for b in bs),max(b[0] for b in bs),min(b[1] for b in bs),max(b[1] for b in bs)))
# ---------- P2 shank bracket ----------
sb = bar((0.0,0.0),D0,26.0,20.0,*SBR_Z).fuse(bar(D0,(0.0,-205.0),20.0,18.0,*SBR_Z))
sb = sb.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
sb = sb.fuse(cz(20.0,EAR_Z[0][0],EAR_Z[1][1],*D0))                  # clevis boss spans the ears
sb = sb.cut(cz(13.0,*ROD_Z,*D0))                                    # eye pocket
sb = sb.cut(sector_at(D0,60.0,-2.0,98.0,*ROD_Z,r_in=13.0))          # swept opening (77 deg + margin)
sb = sb.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,*D0))
sb = sb.cut(cz(6.25,SBR_Z[0]-2,SBR_Z[1]+2))
sb = sb.cut(cz(10.6,SBR_Z[0]-0.5,SBR_Z[0]+4.2)).cut(cz(10.6,SBR_Z[1]-4.2,SBR_Z[1]+0.5))
for p in ((14.0,-52.0),(0.0,-160.0),(0.0,-185.0)): sb=sb.cut(cz(8.0,SBR_Z[0]-1,SBR_Z[1]+1,*p))
assert len(sb.Solids)==1 and sb.isValid() and sb.isClosed(),"P2 %d solids"%len(sb.Solids)
o=doc.getObject("P2_ShankBracket_ALU")
if o is None: o=add("P2_ShankBracket_ALU",sb,(0.70,0.72,0.75),G_S)
else: o.Shape=sb
# ---------- carriage + rod ----------
def build_carriage(t):
    s=carr(t)
    c = bx(EXT_X[0]-6.0,EXT_X[1]+6.0,s-38.0,s+38.0,*CAR_Z)
    c = c.fuse(cz(20.0,EAR_Z[0][0],EAR_Z[1][1],XE,s))
    c = c.cut(cz(13.0,*ROD_Z,XE,s))
    c = c.cut(sector_at((XE,s),60.0,250.0,310.0,*ROD_Z,r_in=13.0))
    c = c.cut(cz(4.1,EAR_Z[0][0]-2,EAR_Z[1][1]+2,XE,s))
    c = c.cut(cz(SCREW_R+1.5,CAR_Z[0]-1,CAR_Z[1]+1,XE,s))
    return c
def build_rod(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    zc=(ROD_Z[0]+ROD_Z[1])/2
    r=Part.makeCylinder(4.0,L,V(D[0],D[1],zc),V(ux,uy,0.0))
    return r.fuse(cz(11.0,ROD_Z[0]+0.5,ROD_Z[1]-0.5,*D)).fuse(cz(11.0,ROD_Z[0]+0.5,ROD_Z[1]-0.5,*C))
g.update(build_carriage=build_carriage,build_rod=build_rod)
for n,f in (("P3_Carriage",build_carriage),("P4_Rod_8mm",build_rod)):
    o=doc.getObject(n)
    if o is None: add(n,f(0.0),(0.30,0.32,0.36) if "Carr" in n else (0.85,0.85,0.88),G_D)
    else: o.Shape=f(0.0)
for n,f,col in (("A2_BallScrew_SFU1620",lambda t: cy(SCREW_R,20.0,300.0,XE,SCREW_Z),(0.55,0.57,0.60)),
                ("A3_Motor_6374",lambda t: cy(31.5,302.0,376.0,XE,SCREW_Z),(0.15,0.15,0.18))):
    o=doc.getObject(n)
    if o is None: add(n,f(0.0),col,G_D)
    else: o.Shape=f(0.0)
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    doc.getObject("P3_Carriage").Shape=build_carriage(t)
    doc.getObject("P4_Rod_8mm").Shape=build_rod(t)
    doc.recompute()
g['pose']=pose
pose(0.0); doc.recompute()
print("P2 %.1f cm3 single closed solid"%(sb.Volume/1000))
