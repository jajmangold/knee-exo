# -*- coding: utf-8 -*-
"""Belt-capstan animation. The pose law is now linear -- carriage Y = C0 - R*theta --
so there is no phi, no rod transform, and no sample-vs-requested-angle mismatch to get
wrong. Placements only; never assigns .Shape."""
import math, json, FreeCAD, FreeCADGui
from FreeCAD import Vector as V
from PySide import QtCore
g=globals()
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration under freecadcmd, where no document is
    open yet -- which is why these older build scripts could not be re-run without the GUI.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
S=K["samples"]; C0=K["C0"]; R=K["R"]
TMIN=S[0]["theta"]; TMAX=S[-1]["theta"]
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff",
       "REF_Shank","HW_JointBolts"]
CARR =["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
STATIC=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620",
        "A3_Motor_6374","REF_Thigh","REF_Knee","HW_PinB_10","A5_Belt_HTD8M",
        "A6_Spring_ConstForce","P12_SpringBracket"]
O=lambda n: doc.getObject(n)
for n in SHANK+CARR+STATIC:
    o=O(n)
    if o: o.ViewObject.Visibility=True
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency=82
if O("A5_Belt_HTD8M"): O("A5_Belt_HTD8M").ViewObject.Transparency=35
def setpose(t):
    t=max(TMIN,min(TMAX,t))
    r=FreeCAD.Rotation(V(0,0,1),t)
    dy=-R*math.radians(t)                      # carriage follows the belt take-up
    for n in SHANK:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CARR:
        o=O(n)
        if o: o.Placement=FreeCAD.Placement(V(0.0,dy,0.0),FreeCAD.Rotation())
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
print("animating %d..%d deg, %d parts (shank %d, carriage %d, static %d)"%(
    TMIN,TMAX,len(SHANK)+len(CARR)+len(STATIC),len(SHANK),len(CARR),len(STATIC)))
print("pose law: carriage dY = -%.3f * theta_rad  (linear, moment arm constant)"%R)
