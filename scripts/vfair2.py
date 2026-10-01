# -*- coding: utf-8 -*-
import math, json, itertools, os, FreeCAD, Part
from FreeCAD import Vector as V
I0=__I0__; I1=__I1__
ACC=r"C:/Users/Josh/KneeExo_anim/clash.json"
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
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
S=K["samples"]; C0=K["C0"]; C1=K["C1"]; BIN,BOUT=K["belt_x"]; BZ=tuple(K["belt_z"])
BI=BIN+0.05
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff","P24_FairingShank",
       "REF_Shank","HW_JointBolts"]
CA=["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
CB=["P3b_CarriageB","A2d_BallNut_LH","P10c_Slider_Delrin","P10d_Slider_Delrin",
    "P11_SprungAnchor","A8_TensionSpring","P13_HallTension"]
STAT=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
      "A2_BallScrew_SFU1620","A2c_BallScrew_LH","A3_Motor_6374","A7_DriveBox",
      "HW_PinB_10","A5_Belt_HTD8M","A5b_Belt_DriveRun","A5c_Belt_TakeRun",
      "P20_KneeShroud","P21_ShellAnterior"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+CA+CB+STAT if O(n)]
def pose(s):
    r=FreeCAD.Rotation(V(0,0,1),s["theta"])
    for n in SHANK:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CA:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,s["carrA"]-C0,0),FreeCAD.Rotation())
    for n in CB:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,s["carrB"]-C1,0),FreeCAD.Rotation())
    O("A5b_Belt_DriveRun").Shape=Part.makeBox(BOUT-BI,s["carrA"]-24.,BZ[1]-BZ[0],V(-BOUT,0.,BZ[0]))
    O("A5c_Belt_TakeRun").Shape=Part.makeBox(BOUT-BI,s["carrB"]-24.,BZ[1]-BZ[0],V(BI,0.,BZ[0]))
acc={"worst":{},"env":{"lo":1e9,"hi":-1e9,"loN":"","hiN":"","khi":-1e9,"khiN":"",
                       "ax":1e9,"px":-1e9,"n":0}}
if os.path.exists(ACC):
    try: acc=json.load(open(ACC))
    except Exception: pass
W=acc["worst"]; E=acc["env"]
for i in range(I0,min(I1,len(S))):
    s=S[i]; pose(s)
    for a,b in itertools.combinations(ALL,2):
        sa,sb=O(a).Shape,O(b).Shape
        if not sa.BoundBox.intersect(sb.BoundBox): continue
        try: c=sa.common(sb)
        except Exception: continue
        if c.isNull(): continue
        v=c.Volume/1000.0
        if v<=0.02: continue
        k=a+"^"+b
        if v>W.get(k,[0])[0]: W[k]=[v,s["theta"]]
    for n in ALL:
        if n.startswith("REF"): continue
        bb=O(n).Shape.BoundBox
        if bb.ZMin<E["lo"]: E["lo"],E["loN"]=bb.ZMin,n
        if bb.ZMax>E["hi"]: E["hi"],E["hiN"]=bb.ZMax,n
        if bb.XMin<E["ax"]: E["ax"]=bb.XMin
        if bb.XMax>E["px"]: E["px"]=bb.XMax
        if bb.YMin<150.0 and bb.ZMax>E["khi"]: E["khi"],E["khiN"]=bb.ZMax,n
    E["n"]+=1
pose(S[2]); json.dump(acc,open(ACC,"w"))
print("chunk %d..%d done; poses=%d; pairs=%d"%(I0,I1,E["n"],len(W)))
