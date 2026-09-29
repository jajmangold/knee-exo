# -*- coding: utf-8 -*-
"""Restore the v1 (final) parameter context - the v2 base script had overwritten
LA/ALPHA/ab()/pinB() globally."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
if "KneeExo_v2" in FreeCAD.listDocuments(): FreeCAD.closeDocument("KneeExo_v2")
doc = FreeCAD.getDocument("KneeExo_v1")
FreeCAD.setActiveDocument("KneeExo_v1")
g = globals()
LA, R_CRANK, PHI0, ALPHA = 300.0, 60.0, 135.0, 85.0
ROM = (-2.0, 105.0)
Z_PLANE, LINK = 108.0, (100.0, 116.0)
GAS_PL, GAS_Z = 150.0, (143.0, 157.0)
FORK_IN, GAP, FORK_OUT = (88.0,98.0), (98.0,118.0), (118.0,128.0)
BOX_X, BOX_Z, CAV_X, CAV_Z = (-50.0,-2.0), (88.0,128.0), (-45.0,-7.0), (93.0,123.0)
R_TH, R_SH, PAD, SHELL = 78.0, 58.0, 6.0, 4.0
NUT, TANG, T_TUBE, BLK = 50.0, 35.0, 190.0, (20.0, 56.0)
def rad(d): return math.radians(d)
def pol(r,b): return (r*math.cos(rad(b)), r*math.sin(rad(b)))
def pinA(): return pol(LA, ALPHA)
def pinB(t): return pol(R_CRANK, ALPHA-PHI0+t)
def ab(t): return math.sqrt(LA*LA+R_CRANK*R_CRANK-2*LA*R_CRANK*math.cos(rad(PHI0-t)))
def arm(t): return LA*R_CRANK*math.sin(rad(PHI0-t))/ab(t)
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
L_RET, L_EXT = ab(ROM[1]), ab(ROM[0]); STROKE = L_EXT-L_RET
THREAD = (L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0)
A = pinA()
SHANK_OBJS = [doc.getObject(n) for n in ("P4_ShankLink_Horn","P5_ShankSlideHousing",
              "P6_ShankCuff","REF_Shank","HW_PinB_M8x36_quickpull") if doc.getObject(n)]
def _plc(th):
    B=pinB(th); L=ab(th); ux,uy=(B[0]-A[0])/L,(B[1]-A[1])/L
    return FreeCAD.Placement(V(A[0],A[1],0.0),
           FreeCAD.Rotation(V(0,0,1),math.degrees(math.atan2(-ux,uy)))), L
def build_gas(th):
    plc,L=_plc(th)
    def gc(r,y0,y1): return Part.makeCylinder(r,y1-y0,V(0.0,y0,GAS_PL),V(0,1,0))
    s = cz(11.0,*GAS_Z).fuse(gc(6.5,8.0,28.0)).fuse(gc(14.0,28.0,28.0+STROKE+50.0))
    s = s.fuse(gc(4.5,28.0+STROKE+50.0,L-14.0)).fuse(cz(11.0,*GAS_Z,0.0,L))
    s.Placement=plc; return s
for k in ("doc","pol","pinA","pinB","ab","arm","bx","cz","rad","A","_plc","build_gas",
          "SHANK_OBJS","THREAD","L_RET","L_EXT","STROKE","LA","R_CRANK","PHI0","ALPHA","ROM",
          "Z_PLANE","LINK","GAS_PL","GAS_Z","NUT","TANG","T_TUBE","BLK","R_TH"):
    g[k]=locals()[k]
print("v1 context: pinA=(%.1f,%.1f) pinB0=(%.1f,%.1f) stroke=%.1f arm@60=%.1f"
      % (*A, *pinB(0.0), STROKE, arm(60.0)))
print("v1 max X on the A-B line = %.1f (seat line is +78)" % max([A[0]]+[pinB(t)[0] for t in (-2,0,30,60,90,105)]))
