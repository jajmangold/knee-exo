# -*- coding: utf-8 -*-
"""KneeExo v2 - ANTERIOR layout. Drive lies on top of the front of the thigh so the
posterior thigh is clear for sitting.  X=posterior+  Y=proximal+  Z=lateral+ from midline.
alpha=110 (upright raked 20 deg anterior of vertical), beta0=135 (crank anterior-proximal),
actuator in TENSION to extend."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
DOC = "KneeExo_v2"
if DOC in FreeCAD.listDocuments(): FreeCAD.closeDocument(DOC)
doc = FreeCAD.newDocument(DOC)
g = globals()
P = dict(
  LA=300.0, R_CRANK=60.0, ALPHA=110.0, DELTA=25.0, ROM=(-2.0,105.0),   # DELTA = beta0-alpha
  R_TH=78.0, R_SH=58.0, PAD=6.0, SHELL=4.0, Y_THC=(170.0,290.0), Y_SHC=(-278.0,-158.0),
  FORK_IN=(88.0,98.0), GAP=(98.0,118.0), LINK=(100.0,116.0), FORK_OUT=(118.0,128.0),
  Z_PLANE=108.0, BUNGEE_PL=143.0, BUNGEE_Z=(136.0,150.0),
  UPR_Z=(88.0,128.0), UPR_W=24.0, R_HUB=24.0, R_PLATE=76.0, PLATE_SEC=(50.0,128.0),
  LAP=(140.0,175.0), BUMP_SEC=(103.0,119.5), BUMP_R=(40.0,70.0),
  TONGUE=dict(x=(-13.0,13.0), y=(-197.0,-150.0), z=(102.0,114.0)),
)
g.update(P)
BETA0 = ALPHA + DELTA; g['BETA0']=BETA0
def rad(d): return math.radians(d)
def pol(r,b): return (r*math.cos(rad(b)), r*math.sin(rad(b)))
def pinA(): return pol(LA, ALPHA)
def pinB(t): return pol(R_CRANK, BETA0+t)
def ab(t): return math.sqrt(LA*LA+R_CRANK*R_CRANK-2*LA*R_CRANK*math.cos(rad(DELTA+t)))
def arm(t): return LA*R_CRANK*math.sin(rad(DELTA+t))/ab(t)
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def sector(r_out,b0,b1,z0,z1,r_in=0.0):
    s=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(b1-b0)%360 or 360)
    s.rotate(V(0,0,0),V(0,0,1),b0)
    return s.cut(cz(r_in,z0-1,z1+1)) if r_in>0 else s
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s=sector(r_out,b0,b1,z0,z1,r_in); s.translate(V(c[0],c[1],0.0)); return s
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
def arc_shell(ri,ro,y0,y1,b0=250.0,sw=170.0):
    s=Part.makeCylinder(ro,y1-y0,V(0,0,0),V(0,0,1),sw)
    s=s.cut(Part.makeCylinder(ri,y1-y0+2,V(0,0,-1),V(0,0,1)))
    s.rotate(V(0,0,0),V(0,0,1),b0); s.rotate(V(0,0,0),V(1,0,0),-90); s.translate(V(0,y0,0))
    return s
def add(name,shape,rgb,grp=None):
    o=doc.addObject("Part::Feature",name); o.Shape=shape; o.ViewObject.ShapeColor=rgb
    if grp is not None: grp.addObject(o)
    return o
for k in ("doc","pol","pinA","pinB","ab","arm","bx","cz","sector","sector_at","bar","arc_shell","add","rad"):
    g[k]=locals()[k]
G_TH=doc.addObject("App::DocumentObjectGroup","A_Thigh"); g['G_TH']=G_TH
G_SH=doc.addObject("App::DocumentObjectGroup","B_Shank"); g['G_SH']=G_SH
G_AC=doc.addObject("App::DocumentObjectGroup","C_Drive"); g['G_AC']=G_AC
G_RF=doc.addObject("App::DocumentObjectGroup","D_Reference"); g['G_RF']=G_RF

# ---- carried over unchanged from v1: cuffs + telescoping slide housing ----
SOCK=dict(x=(-22.0,22.0), y=(-215.0,-145.0), z=(97.0,119.0)); g['SOCK']=SOCK
hs=bx(*SOCK['x'],*SOCK['y'],*SOCK['z'])
hs=hs.cut(bx(TONGUE['x'][0]-0.4,TONGUE['x'][1]+0.4,-216.0,-157.0,TONGUE['z'][0]-0.4,TONGUE['z'][1]+0.4))
hs=hs.cut(bx(-3.0,3.0,-190.0,-165.0,116.0,121.0))
hs=hs.fuse(bx(-30.0,30.0,-273.0,-163.0,68.0,78.0)).fuse(bx(-8.0,8.0,-262.0,-174.0,76.0,99.0))
for xa,xb in ((14.0,22.0),(-22.0,-14.0)): hs=hs.fuse(bx(xa,xb,-258.0,-178.0,70.0,99.0))
CUFF_SH=[(-22.0,-190.0),(22.0,-190.0),(-22.0,-246.0),(22.0,-246.0)]; g['CUFF_SH']=CUFF_SH
for x,y in CUFF_SH: hs=hs.cut(cz(3.2,67.0,79.0,x,y))
add("P5_ShankSlideHousing",hs,(0.85,0.35,0.15),G_SH)
def cuff(ri,ro,yspan,pts,padz):
    c=arc_shell(ri,ro,*yspan).fuse(bx(-30.0,30.0,yspan[0]+5,yspan[1]-5,padz[0],padz[1]))
    for x,y in pts: c=c.cut(cz(2.75,padz[0]-2,padz[1]+2,x,y))
    for b in (256.0,64.0):
        for y in (yspan[0]+22,yspan[1]-22):
            sl=bx(-2.6,2.6,y-20.0,y+20.0,ri-6.0,ro+6.0)
            sl.rotate(V(0,0,0),V(0,1,0),-(b-270.0)); c=c.cut(sl)
    return c
add("P6_ShankCuff",cuff(R_SH+PAD,R_SH+PAD+SHELL,Y_SHC,CUFF_SH,(56.0,68.0)),(0.95,0.62,0.10),G_SH)
th=Part.makeCone(62.0,85.0,285.0,V(0,15,0),V(0,1,0))
kn=Part.makeSphere(52.0,V(0,0,0))
sh=Part.makeCone(60.0,38.0,360.0,V(0,-20,0),V(0,-1,0))
for n,s,grp in (("REF_Thigh",th,G_RF),("REF_Knee",kn,G_RF),("REF_Shank",sh,G_SH)):
    o=add(n,s,(0.85,0.75,0.70),grp); o.ViewObject.Transparency=80
doc.recompute()
print("v2 base: pinA=(%.1f,%.1f) pinB0=(%.1f,%.1f)" % (*pinA(), *pinB(0.0)))
print("stroke %.1f mm, arm %.1f@65deg, tension-to-extend" % (ab(105.0)-ab(-2.0), arm(65.0)))
