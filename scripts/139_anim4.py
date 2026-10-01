# -*- coding: utf-8 -*-
"""Live animation, placements only. Two fixes over 123_anim3.py:
  * the shank rotation comes from the SAMPLE's theta, so it can never disagree with the
    rod placement (that mismatch at t=105 was the phantom 0.04 cm3 clash)
  * travel is clamped to the sample range (-2 .. 104), and HW_PinC rides the carriage"""
import math, json, FreeCAD, FreeCADGui
from FreeCAD import Vector as V
from PySide import QtCore
g=globals()
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
TMIN=S[0]["theta"]; TMAX=S[-1]["theta"]
def sm(t): return min(S,key=lambda q:abs(q["theta"]-max(TMIN,min(TMAX,t))))
BASE=sm(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P2b_RodClevisBlock","P6_ShankSocket",
       "P7_ShankCuff","REF_Shank","HW_PinB_10","HW_JointBolts","HW_PinD_M8_Clevis"]
CARR =["P3_Carriage","HW_PinC_M8_Carriage"]
ROD  =["P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage"]
STATIC=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620",
        "A3_Motor_6374","REF_Thigh","REF_Knee"]
O=lambda n: doc.getObject(n)
for n in SHANK+CARR+ROD+STATIC:
    o=O(n)
    if o: o.ViewObject.Visibility=True
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency=82
def setpose(t):
    s=sm(t); r=FreeCAD.Rotation(V(0,0,1),s["theta"])
    for n in SHANK:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CARR:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0.0,s["carr"]-CARR0,0.0),FreeCAD.Rotation())
    R=FreeCAD.Rotation(V(0,0,1),s["phi"]-PHI0)
    base=V(s["Dx"],s["Dy"],0.0)-R.multVec(V(D0[0],D0[1],0.0))
    for n in ROD:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(base,R)
g['setpose']=setpose
old=g.get("_kx_timer")
if old is not None:
    try: old.stop()
    except Exception: pass
STEPS=120
def smooth(a,b,u):
    u=max(0.0,min(1.0,u)); return a+(b-a)*(u*u*(3-2*u))
def theta_at(i):
    u=(i%STEPS)/float(STEPS)
    if u<0.45: return smooth(0.0,TMAX,u/0.45)
    if u<0.90: return smooth(TMAX,TMIN,(u-0.45)/0.45)
    return smooth(TMIN,0.0,(u-0.90)/0.10)
class Runner(QtCore.QObject):
    def __init__(self): super(Runner,self).__init__(); self.i=0
    def tick(self):
        try:
            setpose(theta_at(self.i)); self.i+=1; FreeCADGui.updateGui()
        except Exception as e: FreeCAD.Console.PrintError("anim: %s\n"%e)
run=Runner(); t=QtCore.QTimer(); t.timeout.connect(run.tick); t.setInterval(40)
g['_kx_timer']=t; g['_kx_runner']=run
v=FreeCADGui.activeDocument().activeView(); v.viewTop()
FreeCADGui.SendMsgToActiveView("ViewFit")
t.start()
print("animating %d..%d deg over %d parts; rod group = %d bodies on one transform"%(
    TMIN,TMAX,len(SHANK)+len(CARR)+len(ROD)+len(STATIC),len(ROD)))
# prove the rod ends track the rod
setpose(60.0)
a=O("P4_Rod_M8").Placement.Base; b=O("P9a_RodEnd_SI8_Shank").Placement.Base
c=O("P9b_RodEnd_SI8_Carriage").Placement.Base
print("at 60 deg: rod %s  endA %s  endB %s  all-equal=%s"%(
    (round(a.x,2),round(a.y,2)),(round(b.x,2),round(b.y,2)),(round(c.x,2),round(c.y,2)),
    a.isEqual(b,1e-9) and a.isEqual(c,1e-9)))
