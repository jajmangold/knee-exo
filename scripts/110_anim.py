# -*- coding: utf-8 -*-
"""Live animation in the FreeCAD viewport, driven by a QTimer so it keeps running
in FreeCAD's event loop (the RPC call returns immediately)."""
import math, json, FreeCAD, FreeCADGui
from FreeCAD import Vector as V
from PySide import QtCore
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
FreeCAD.setActiveDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t):
    t=max(-2.0,min(105.0,t)); return min(S,key=lambda q:abs(q["theta"]-t))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts"]
ALL=SHANK+["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620",
           "A3_Motor_6374","P3_Carriage","P4_Rod_8mm","REF_Thigh","REF_Knee"]
O=lambda n: doc.getObject(n)
for n in ALL:
    o=O(n)
    if o: o.ViewObject.Visibility=True
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency=82
def setpose(t):
    s=sm(t); r=FreeCAD.Rotation(V(0,0,1),t)
    for n in SHANK:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    c=O("P3_Carriage")
    if c: c.Placement=FreeCAD.Placement(V(0.0,s["carr"]-CARR0,0.0),FreeCAD.Rotation())
    rd=O("P4_Rod_8mm")
    if rd:
        R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
        rd.Placement=FreeCAD.Placement(V(s["Dx"],s["Dy"],0.0)-R.multVec(V(D0[0],D0[1],0.0)),R)
g['setpose']=setpose
# stop a previous run if one is live
old=g.get("_kx_timer")
if old is not None:
    try: old.stop()
    except Exception: pass
STEPS=110
def smooth(a,b,u):
    u=max(0.0,min(1.0,u)); return a+(b-a)*(u*u*(3-2*u))
def theta_at(i):
    u=(i%STEPS)/float(STEPS)
    if u<0.45:  return smooth(0.0,105.0,u/0.45)
    if u<0.90:  return smooth(105.0,-2.0,(u-0.45)/0.45)
    return smooth(-2.0,0.0,(u-0.90)/0.10)
class Runner(QtCore.QObject):
    def __init__(self):
        super(Runner,self).__init__(); self.i=0
    def tick(self):
        try:
            setpose(theta_at(self.i)); self.i+=1
            FreeCADGui.updateGui()
        except Exception as e:
            FreeCAD.Console.PrintError("anim: %s\n"%e)
run=Runner()
t=QtCore.QTimer(); t.timeout.connect(run.tick); t.setInterval(40)
g['_kx_timer']=t; g['_kx_runner']=run
v=FreeCADGui.activeDocument().activeView()
v.viewTop(); FreeCADGui.SendMsgToActiveView("ViewFit")
t.start()
print("animating: theta 0 -> 105 -> -2 -> 0, %d steps @40 ms (%.1f s/cycle)"%(STEPS,STEPS*0.04))
print("sagittal (Top) view; drag to orbit freely while it runs")
