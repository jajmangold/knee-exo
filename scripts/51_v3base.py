# -*- coding: utf-8 -*-
"""KneeExo v3 - COAXIAL INLINE DRIVE. LA=350, ALPHA=105, beta0=-30.
Motor sits ON the screw axis at Z=108 -> max lateral extent ~140 mm (was 184)."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
DOC="KneeExo_v3"
for d in ("KneeExo_v2",): 
    if d in FreeCAD.listDocuments(): FreeCAD.closeDocument(d)
if DOC in FreeCAD.listDocuments(): FreeCAD.closeDocument(DOC)
doc=FreeCAD.newDocument(DOC); FreeCAD.setActiveDocument(DOC)
g=globals()
LA, R_CRANK, PHI0, ALPHA = 350.0, 60.0, 135.0, 105.0
ROM=(-2.0,105.0)
FORK_IN,GAP,LINK,FORK_OUT=(88.0,98.0),(98.0,118.0),(100.0,116.0),(118.0,128.0)
Z_PLANE=108.0
R_TH,R_SH,PAD,SHELL=78.0,58.0,6.0,4.0
Y_THC,Y_SHC=(170.0,290.0),(-278.0,-158.0)
R_HUB,R_PLATE,PLATE_SEC=24.0,76.0,(85.0,250.0)
R_PIN,D_PIN=60.0,12.0
FLEX_HOLES=[(240,105),(230,95),(220,85),(210,75),(200,65),(190,55)]
EXT_HOLES=[(101.0,0),(111.0,10),(121.0,20)]
FINGER=(109.0,129.0)
UPR_B, UPR_W = 105.0, 24.0                  # upright raked along bearing 105
TONGUE=dict(x=(-13.0,13.0),y=(-197.0,-150.0),z=(102.0,114.0))
EYE,MOTL,CPL,BLKL=14.0,74.0,12.0,22.0
BLK_END=EYE+MOTL+CPL+BLKL
NUT,TANG,T_TUBE=40.0,25.0,170.0
def rad(d): return math.radians(d)
def pol(r,b): return (r*math.cos(rad(b)), r*math.sin(rad(b)))
def pinA(): return pol(LA,ALPHA)
def pinB(t): return pol(R_CRANK,ALPHA-PHI0+t)
def ab(t): return math.sqrt(LA*LA+R_CRANK*R_CRANK-2*LA*R_CRANK*math.cos(rad(PHI0-t)))
def arm(t): return LA*R_CRANK*math.sin(rad(PHI0-t))/ab(t)
L_RET,L_EXT=ab(ROM[1]),ab(ROM[0]); STROKE=L_EXT-L_RET
THREAD=(L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0)
A=pinA()
assert THREAD[0]>=BLK_END and THREAD[1]<=L_RET-TANG, "schedule"
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
for k in ("doc","pol","pinA","pinB","ab","arm","bx","cz","sector","sector_at","bar","arc_shell","add","rad",
          "A","L_RET","L_EXT","STROKE","THREAD","BLK_END","NUT","TANG","T_TUBE","EYE","MOTL","CPL","BLKL",
          "LA","R_CRANK","PHI0","ALPHA","ROM","FORK_IN","GAP","LINK","FORK_OUT","Z_PLANE","R_TH","R_SH",
          "PAD","SHELL","Y_THC","Y_SHC","R_HUB","R_PLATE","PLATE_SEC","R_PIN","D_PIN","FLEX_HOLES",
          "EXT_HOLES","FINGER","UPR_B","UPR_W","TONGUE"): g[k]=locals()[k]
for n in ("A_Thigh","B_Shank","C_Drive","D_Reference"):
    g["G_"+n.split('_')[1][:2].upper()] = doc.addObject("App::DocumentObjectGroup",n)
G_TH,G_SH,G_DR,G_RF = doc.getObject("A_Thigh"),doc.getObject("B_Shank"),doc.getObject("C_Drive"),doc.getObject("D_Reference")
for k,v in (("G_TH",G_TH),("G_SH",G_SH),("G_DR",G_DR),("G_RF",G_RF)): g[k]=v
print("v3: pinA=(%.1f,%.1f) beta0=%.0f  pin-pin %.1f..%.1f stroke %.1f arm@60=%.1f"
      %(*A, ALPHA-PHI0, L_RET, L_EXT, STROKE, arm(60.0)))
print("    thread %.1f..%.1f  BLK_END %.0f  tang start %.1f  margin %.1f"
      %(*THREAD, BLK_END, L_RET-TANG, L_RET-TANG-THREAD[1]))
