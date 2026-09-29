# -*- coding: utf-8 -*-
"""KneeExo v4 - GANTRY. 20x60 V-slot along the lateral thigh, carriage on V-wheels,
8 mm rod from carriage to a pivot 120 mm below the knee on an ALUMINIUM shank bracket.
Knee = single-axis hinge; instant-centre migration handled by the telescoping shank joint."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
DOC="KneeExo_v4"
for d in ("KneeExo_v2","KneeExo_v3"):
    if d in FreeCAD.listDocuments(): FreeCAD.closeDocument(d)
if DOC in FreeCAD.listDocuments(): FreeCAD.closeDocument(DOC)
doc=FreeCAD.newDocument(DOC); FreeCAD.setActiveDocument(DOC)
g=globals()
XE, D0, LROD = 40.0, (30.0,-120.0), 165.3
ROM=(-2.0,105.0)
EXT_X, EXT_Z, EXT_Y = (10.0,70.0), (88.0,108.0), (15.0,356.0)
CAR_Z=(108.0,122.0); ROD_Z=(109.0,121.0); EAR_Z=((103.0,109.0),(121.0,127.0))
SCREW_Z, SCREW_R = 120.0, 8.0
FORK_Z=((86.0,98.0),(114.0,126.0)); SBR_Z=(100.0,112.0)
R_TH,R_SH,PAD,SHELL=78.0,58.0,6.0,4.0
Y_THC,Y_SHC=(170.0,290.0),(-278.0,-158.0)
TONG=dict(x=(-13.0,13.0),y=(-197.0,-150.0),z=(102.0,114.0))
def rad(d): return math.radians(d)
def rot2(p,t):
    c,s=math.cos(rad(t)),math.sin(rad(t)); return (p[0]*c-p[1]*s, p[0]*s+p[1]*c)
def carr(t):
    D=rot2(D0,t); dd=LROD*LROD-(XE-D[0])**2
    assert dd>0, "rod cannot reach at %.0f deg"%t
    return D[1]+math.sqrt(dd)
def armv(t):
    D=rot2(D0,t); s=carr(t); C=(XE,s)
    L=math.hypot(C[0]-D[0],C[1]-D[1]); ux,uy=(C[0]-D[0])/L,(C[1]-D[1])/L
    return abs(D[0]*uy-D[1]*ux)
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
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
def add(n,s,rgb,grp=None,tr=0):
    o=doc.addObject("Part::Feature",n); o.Shape=s; o.ViewObject.ShapeColor=rgb
    o.ViewObject.Transparency=tr
    if grp is not None: grp.addObject(o)
    return o
for k in ("doc","rot2","carr","armv","bx","cz","cy","bar","arc_shell","add","rad","XE","D0","LROD",
          "ROM","EXT_X","EXT_Z","EXT_Y","CAR_Z","ROD_Z","EAR_Z","SCREW_Z","SCREW_R","FORK_Z","SBR_Z",
          "R_TH","R_SH","PAD","SHELL","Y_THC","Y_SHC","TONG"): g[k]=locals()[k]
G_T=doc.addObject("App::DocumentObjectGroup","A_ThighRail"); g['G_T']=G_T
G_S=doc.addObject("App::DocumentObjectGroup","B_Shank");     g['G_S']=G_S
G_D=doc.addObject("App::DocumentObjectGroup","C_Drive");     g['G_D']=G_D
G_R=doc.addObject("App::DocumentObjectGroup","D_Reference"); g['G_R']=G_R

# ---------- A1 extrusion (off-the-shelf 20x60 V-slot) ----------
ext=bx(*EXT_X,*EXT_Y,*EXT_Z)
for xo in (20.0,40.0,60.0):                                   # slot mouths, both faces
    ext=ext.cut(bx(EXT_X[0]+xo-3.0,EXT_X[0]+xo+3.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[0]-1,EXT_Z[0]+4.0))
    ext=ext.cut(bx(EXT_X[0]+xo-3.0,EXT_X[0]+xo+3.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_Z[1]-4.0,EXT_Z[1]+1))
ext=ext.cut(cy(7.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_X[0]+15.0,98.0))
ext=ext.cut(cy(7.0,EXT_Y[0]-1,EXT_Y[1]+1,EXT_X[0]+45.0,98.0))
add("A1_Extrusion_20x60_VSlot",ext,(0.62,0.64,0.66),G_T)
# ---------- reference limb ----------
add("REF_Thigh",Part.makeCone(62.0,85.0,285.0,V(0,15,0),V(0,1,0)),(0.85,0.75,0.70),G_R,80)
add("REF_Knee",Part.makeSphere(52.0,V(0,0,0)),(0.85,0.75,0.70),G_R,80)
add("REF_Shank",Part.makeCone(60.0,38.0,360.0,V(0,-20,0),V(0,-1,0)),(0.85,0.75,0.70),G_S,80)
doc.recompute()
print("v4 base. carriage %.1f..%.1f (travel %.1f)  arm %.1f..%.1f"
      %(carr(ROM[0]),carr(ROM[1]),carr(ROM[1])-carr(ROM[0]),armv(0.0),armv(105.0)))
