# -*- coding: utf-8 -*-
"""Reopen the saved model and re-establish the parametric context (no geometry rebuild)."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
PATH = r"C:\Users\Josh\KneeExo_v1.FCStd"
doc = FreeCAD.openDocument(PATH) if "KneeExo_v1" not in FreeCAD.listDocuments() else FreeCAD.getDocument("KneeExo_v1")
g = globals()
P = dict(R_TH=78.0, R_SH=58.0, PAD=6.0, SHELL=4.0, Y_THC=(170.0,290.0), Y_SHC=(-278.0,-158.0),
    LA=250.0, R_CRANK=60.0, PHI0=135.0, ALPHA=85.0, ROM=(-2.0,105.0), F_ACT=600.0,
    FORK_IN=(88.0,98.0), GAP=(98.0,118.0), FORK_OUT=(118.0,128.0), LINK=(100.0,116.0),
    Z_PLANE=108.0, BOX_X=(-50.0,-2.0), BOX_Z=(88.0,128.0), CAV_X=(-45.0,-7.0), CAV_Z=(93.0,123.0),
    WALL=5.0, R_HUB=32.0, R_PLATE=76.0, PLATE_SEC=(74.0,252.0), R_PIN=60.0, D_PIN=12.0,
    Y_TONGUE=(70.0,178.0), CLEV_Z=((94.0,101.0),(115.0,122.0)),
    FINGER=(107.3,127.3), R_SHUB=21.0,
    TONGUE=dict(x=(-13.0,13.0), y=(-197.0,-150.0), z=(102.0,114.0)),
    DR=dict(eye_r=11.0, neck_r=7.5, blk=(24.0,50.0), blk_r=20.0, cover=(26.0,50.0),
            screw=(50.0,200.0), screw_r=10.0, tube_len=150.0, tube_r=17.0,
            tang=75.0, tang_w=8.0, mot=(20.0,94.0), mot_r=31.5, mot_off=-62.0))
g.update(P)
def rad(d): return math.radians(d)
def pol(r,b): return (r*math.cos(rad(b)), r*math.sin(rad(b)))
def pinA(): return pol(LA, ALPHA)
def pinB(t): return pol(R_CRANK, ALPHA-PHI0+t)
def ab(t): return math.sqrt(LA*LA+R_CRANK*R_CRANK-2*LA*R_CRANK*math.cos(rad(PHI0-t)))
def arm(t): return LA*R_CRANK*math.sin(rad(PHI0-t))/ab(t)
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def sector(r_out,b0,b1,z0,z1,r_in=0.0):
    s = Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(b1-b0)%360 or 360)
    s.rotate(V(0,0,0),V(0,0,1),b0)
    return s.cut(cz(r_in,z0-1,z1+1)) if r_in>0 else s
def sector_at(c,r_out,b0,b1,z0,z1,r_in=0.0):
    s = sector(r_out,b0,b1,z0,z1,r_in); s.translate(V(c[0],c[1],0.0)); return s
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy = p1[0]-p0[0], p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy = dx/L,dy/L; nx,ny = -uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    s=Part.Face(w).extrude(V(0,0,z1-z0))
    return s.fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
A = pinA()
def build_drive(th):
    B = pinB(th); L = ab(th)
    ux,uy = (B[0]-A[0])/L,(B[1]-A[1])/L
    plc = FreeCAD.Placement(V(A[0],A[1],0.0), FreeCAD.Rotation(V(0,0,1), math.degrees(math.atan2(-ux,uy))))
    def cyl(r,y0,y1,x=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,Z_PLANE),V(0,1,0))
    d = cz(DR['eye_r'],101.0,115.0)
    d = d.fuse(cyl(DR['neck_r'],8.0,26.0)).fuse(cyl(DR['blk_r'],*DR['blk']))
    d = d.fuse(bx(-88.0,20.0,*DR['cover'],94.0,122.0)).fuse(cyl(DR['screw_r'],*DR['screw']))
    d = d.fuse(cyl(DR['tube_r'], L-DR['tube_len'], L-DR['tang']))
    d = d.fuse(bx(-DR['tang_w'],DR['tang_w'],L-DR['tang'],L,101.0,115.0))
    d = d.fuse(cz(DR['eye_r'],101.0,115.0,0.0,L))
    m = cyl(DR['mot_r'],*DR['mot'],x=DR['mot_off'])
    d.Placement = plc; m.Placement = plc
    return d,m,L
SHANK_OBJS = [doc.getObject(n) for n in ("P4_ShankLink_Horn","P5_ShankSlideHousing",
              "P6_ShankCuff","REF_Shank","HW_PinB_M8x36_quickpull") if doc.getObject(n)]
def pose(t):
    r = FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement = FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_ = build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape = d
    if doc.getObject("P8_Motor_6374"): doc.getObject("P8_Motor_6374").Shape = m
    doc.recompute()
for k in ("doc","pinA","pinB","ab","arm","bx","cz","sector","sector_at","bar","A",
          "build_drive","pose","SHANK_OBJS","pol","rad"): g[k]=locals()[k]
print("context restored;", len(doc.Objects), "objects")
o=doc.getObject("P4_ShankLink_Horn"); print("P4 currently: %.1f cm3 solids=%d"%(o.Shape.Volume/1000,len(o.Shape.Solids)))
