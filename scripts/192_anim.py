# -*- coding: utf-8 -*-
"""Differential animation. The two carriages move in OPPOSITE senses (LH/RH screws on one
shaft) and BOTH belt runs are rebuilt per frame, since neither has a constant length now."""
import math, json, FreeCAD, FreeCADGui, Part
from FreeCAD import Vector as V
from PySide import QtCore
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_diff.json"))
S=K["samples"]; C0=K["C0"]; C1=K["C1"]; R=K["R"]; BZ=tuple(K["belt_z"])
TMIN=S[0]["theta"]; TMAX=S[-1]["theta"]
BIN,BOUT=R-1.372+0.05,R+4.2
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff",
       "REF_Shank","HW_JointBolts"]
CA=["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
CB=["P3b_CarriageB","A2d_BallNut_LH","P10c_Slider_Delrin","P10d_Slider_Delrin"]
STAT=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
      "A2_BallScrew_SFU1620","A2c_BallScrew_LH","A3_Motor_6374","A7_DriveBox",
      "HW_PinB_10","A5_Belt_HTD8M"]
O=lambda n: doc.getObject(n)
for n in SHANK+CA+CB+STAT+["A5b_Belt_DriveRun","A5c_Belt_TakeRun"]:
    o=O(n)
    if o: o.ViewObject.Visibility=True
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency=82
DRV=O("A5b_Belt_DriveRun"); TAK=O("A5c_Belt_TakeRun")
def setpose(t):
    t=max(TMIN,min(TMAX,t)); th=math.radians(t)
    r=FreeCAD.Rotation(V(0,0,1),t); cA=C0-R*th; cB=C1+R*th
    for n in SHANK:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CA:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0.,cA-C0,0.),FreeCAD.Rotation())
    for n in CB:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0.,cB-C1,0.),FreeCAD.Rotation())
    DRV.Shape=Part.makeBox(BOUT-BIN,cA-24.,BZ[1]-BZ[0],V(-BOUT,0.,BZ[0]))
    TAK.Shape=Part.makeBox(BOUT-BIN,cB-24.,BZ[1]-BZ[0],V(BIN,0.,BZ[0]))
g['setpose']=setpose
old=g.get("_kx_timer")
if old is not None:
    try: old.stop()
    except Exception: pass
STEPS=120
def smooth(a,b,u):
    u=max(0.,min(1.,u)); return a+(b-a)*(u*u*(3-2*u))
def theta_at(i):
    u=(i%STEPS)/float(STEPS)
    if u<0.45: return smooth(0.,TMAX,u/0.45)
    if u<0.90: return smooth(TMAX,TMIN,(u-0.45)/0.45)
    return smooth(TMIN,0.,(u-0.90)/0.10)
class Runner(QtCore.QObject):
    def __init__(self): super(Runner,self).__init__(); self.i=0
    def tick(self):
        try:
            setpose(theta_at(self.i)); self.i+=1; FreeCADGui.updateGui()
        except Exception as e: FreeCAD.Console.PrintError("anim: %s\n"%e)
run=Runner(); t=QtCore.QTimer(); t.timeout.connect(run.tick); t.setInterval(45)
g['_kx_timer']=t; g['_kx_runner']=run
v=FreeCADGui.activeDocument().activeView(); v.viewTop()
FreeCADGui.SendMsgToActiveView("ViewFit")
t.start()
print("animating %d..%d deg"%(TMIN,TMAX))
for th in (0.,52.,104.):
    setpose(th)
    a=DRV.Shape.BoundBox.YMax; b=TAK.Shape.BoundBox.YMax
    print("  theta %5.1f: carriage A Y %7.2f (run %6.2f), carriage B Y %7.2f (run %6.2f), sum %7.2f"%(
        th,C0-R*math.radians(th),a,C1+R*math.radians(th),b,a+b))
setpose(0.)
print("A and B move in OPPOSITE senses; run A + run B is constant -> no spring needed")
