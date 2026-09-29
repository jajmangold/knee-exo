import math, json, FreeCAD, FreeCADGui, Part
from FreeCAD import Vector as V
from PySide import QtCore
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]; C0=K["C0"]; C1=K["C1"]; R=K["R"]; BZ=tuple(K["belt_z"])
BIN,BOUT=K["belt_x"][0]+0.05,K["belt_x"][1]
TMIN,TMAX=S[0]["theta"],S[-1]["theta"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff",
       "P24_FairingShank","REF_Shank","HW_JointBolts"]
CA=["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
CB=["P3b_CarriageB","A2d_BallNut_LH","P10c_Slider_Delrin","P10d_Slider_Delrin",
    "P11_SprungAnchor","A8_TensionSpring","P13_HallTension"]
STAT=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
      "A2_BallScrew_SFU1620","A2c_BallScrew_LH","A3_Motor_6374","A7_DriveBox","HW_PinB_10",
      "A5_Belt_HTD8M","P20_KneeShroud","P21_ShellAnterior"]
O=lambda n: doc.getObject(n)
for n in SHANK+CA+CB+STAT+["A5b_Belt_DriveRun","A5c_Belt_TakeRun"]:
    o=O(n)
    if o: o.ViewObject.Visibility=True
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency=82
for n in ("P20_KneeShroud","P21_ShellAnterior","P24_FairingShank"):
    if O(n): O(n).ViewObject.Transparency=55      # see the mechanism through the fairing
DRV,TAK=O("A5b_Belt_DriveRun"),O("A5c_Belt_TakeRun")
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
def sm(a,b,u):
    u=max(0.,min(1.,u)); return a+(b-a)*(u*u*(3-2*u))
def th_at(i):
    u=(i%STEPS)/float(STEPS)
    if u<0.45: return sm(0.,TMAX,u/0.45)
    if u<0.90: return sm(TMAX,TMIN,(u-0.45)/0.45)
    return sm(TMIN,0.,(u-0.90)/0.10)
class Runner(QtCore.QObject):
    def __init__(self): super(Runner,self).__init__(); self.i=0
    def tick(self):
        try: setpose(th_at(self.i)); self.i+=1; FreeCADGui.updateGui()
        except Exception as e: FreeCAD.Console.PrintError("anim: %s\n"%e)
run=Runner(); t=QtCore.QTimer(); t.timeout.connect(run.tick); t.setInterval(50)
g['_kx_timer']=t; g['_kx_runner']=run
v=FreeCADGui.activeDocument().activeView(); v.viewTop()
FreeCADGui.SendMsgToActiveView("ViewFit"); t.start()
print("animating %d..%d deg; fairings at 55%% transparency so the drive is visible"%(TMIN,TMAX))
