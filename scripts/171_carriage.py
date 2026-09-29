# -*- coding: utf-8 -*-
"""P3 carriage on DELRIN SLIDERS in the rail's two outboard-face slots (X=20 and X=60;
X=40 is skipped because the rod pivot bolt lands there). Nothing outside X 10..70 and
nothing below Z 104.2, so the carriage never meets the yoke on the inboard face.

Note the rod pivot bolt CANNOT pass down through Z=122 -- the screw runs along Y there,
coaxial in X. It stops on the 7.4 mm cheek that bridges over the screw channel."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def sector_at(c,r_out,a0,a1,z0,z1,r_in=0.0):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    if r_in>0: q=q.cut(cz(r_in,z0-1,z1+1))
    q.translate(V(c[0],c[1],0.0)); return q
def unwrap(v):
    o=[v[0]]
    for x in v[1:]:
        p=o[-1]
        while x-p>180: x-=360
        while p-x>180: x+=360
        o.append(x)
    return o
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
def rot2(p,t):
    c,s=math.cos(math.radians(t)),math.sin(math.radians(t)); return (p[0]*c-p[1]*s,p[0]*s+p[1]*c)
s0=sm(0.0)["carr"]
ts=[-2.,0.,10.,20.,30.,45.,60.,75.,90.,104.]
cs=unwrap([math.degrees(math.atan2(rot2(D0,q)[1]-sm(q)["carr"],rot2(D0,q)[0]-XE)) for q in ts])
c0,c1=min(cs)-5.,max(cs)+5.
Y0,Y1=s0-24.,s0+78.                     # 102 mm grip
ZM=148.0; SLOT_Z=(138.0,155.0); POCK=13.; BAR_R=7.6; R_OUT=40.; U_LO,U_HI=6.,33.
TAN=18.0/152.71                      # rod descends toward the shank pivot at Z=130
EAR=(108.,163.4); BASE=(108.,120.)
SCR_X,SCR_Z=40.,122.; CHAN_R=9.0; NUT_R=14.0
SLID_X=(20.,60.); SLID_W=3.0; SLID_TOP=114.0
NUT_Y=(s0+34.,s0+80.)
def relief(c,a0,a1):
    s=cz(POCK,SLOT_Z[0],SLOT_Z[1],*c).fuse(sector_at(c,R_OUT,a0,a1,*SLOT_Z))
    m=math.sqrt(1.0+TAN*TAN)
    for a in (a0,a1):
        ca,sa=math.cos(math.radians(a)),math.sin(math.radians(a))
        d=(ca/m,sa/m,-TAN/m)          # TILTED: descends toward the shank
        s=s.fuse(Part.makeCylinder(BAR_R,U_HI-U_LO,
            V(c[0]+d[0]*U_LO,c[1]+d[1]*U_LO,ZM+d[2]*U_LO),V(*d)))
    return s.removeSplitter()
ca=bx(10.,70.,Y0,Y1,*BASE)
ca=ca.fuse(bx(22.,58.,NUT_Y[0],NUT_Y[1],108.,142.))          # nut clamp
ca=ca.fuse(cz(17.,*EAR,XE,s0)).removeSplitter()              # rod ear
ca=ca.cut(cy(CHAN_R,Y0-1,Y1+1,SCR_X,SCR_Z))                  # screw channel
ca=ca.cut(cy(NUT_R+0.2,NUT_Y[0]-1,NUT_Y[1]+1,SCR_X,SCR_Z))   # nut seat
for cx in SLID_X:                                            # Delrin slider pockets
    ca=ca.cut(bx(cx-SLID_W,cx+SLID_W,Y0-1,Y1+1,BASE[0],SLID_TOP))
for k in range(4):                                           # nut clamp screws
    ca=ca.cut(cz(2.1,138.,143.,SCR_X-9.+6.*k,NUT_Y[0]+8.+k*9.))
ca=ca.cut(relief((XE,s0),c0,c1))
ca=ca.cut(cz(4.1,131.5,170.,XE,s0))                          # rod bolt: stops above the screw
assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"P3 solids=%d"%len(ca.Solids)
doc.getObject("P3_Carriage").Shape=ca
b=ca.BoundBox
print("P3 carriage X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000))
print("  grip %.0f mm; rod ear Z %.0f..%.0f; slot %.1f..%.1f"%(Y1-Y0,EAR[0],EAR[1],*SLOT_Z))
print("  cheek over the screw channel: %.1f mm (channel top %.1f)"%(SLOT_Z[0]-(SCR_Z+CHAN_R),SCR_Z+CHAN_R))
print("  rod-end P9b spans Z 138.1..154.2 -> slot %.1f..%.1f clears it"%SLOT_Z)
# ---- the two Delrin sliders ----
made=[]
for i,cx in enumerate(SLID_X):
    s=bx(cx-2.8,cx+2.8,Y0,Y1,104.2,SLID_TOP)
    for y in (Y0+15.,(Y0+Y1)/2,Y1-15.):                      # retaining screws up into the carriage
        s=s.cut(cz(1.7,110.,SLID_TOP+1,cx,y))
    assert len(s.Solids)==1 and s.isClosed(),"slider %d"%i
    nm="P10%s_Slider_Delrin"%("ab"[i])
    o=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
    o.Shape=s; o.Label=nm; o.ViewObject.Visibility=True; made.append(o)
    print("  %-22s X %.1f..%.1f  Z 104.2..%.1f  L %.0f mm  vol %.2f cm3"%(
        nm,cx-2.8,cx+2.8,SLID_TOP,Y1-Y0,s.Volume/1000))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive": gg.addObjects(made)
print("  tongues reach Z 104.2..108 into the rail slots (4 mm deep, 5.6 wide in a 6.0 pocket)")
doc.recompute(); doc.save()
