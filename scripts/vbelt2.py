# -*- coding: utf-8 -*-
"""Chunked sweep. The drive run is REBUILT per pose (from parameters, never
read-modify-write) so its varying length is actually checked, not assumed."""
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
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
S=K["samples"]; C0=K["C0"]; R=K["R"]
BIN,BOUT=R-1.372+0.05,R+4.2; BZ=(116.,146.)
SHANK=["A4_Shank2020_VSlot","P2a_KneeHingePlate","P6_ShankSocket","P7_ShankCuff",
       "REF_Shank","HW_JointBolts"]
CARR =["P3_Carriage","A2b_BallNut_SFU1620","P10a_Slider_Delrin","P10b_Slider_Delrin"]
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","REF_Thigh","REF_Knee",
       "A2_BallScrew_SFU1620","A3_Motor_6374","HW_PinB_10","A5_Belt_HTD8M",
       "A5b_Belt_DriveRun","A6_Spring_ConstForce","P12_SpringBracket"]
O=lambda n: doc.getObject(n)
ALL=[n for n in SHANK+CARR+THIGH if O(n)]
def pose(s):
    r=FreeCAD.Rotation(V(0,0,1),s["theta"])
    for n in SHANK:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    for n in CARR:
        if O(n): O(n).Placement=FreeCAD.Placement(V(0,s["carr"]-C0,0),FreeCAD.Rotation())
    O("A5b_Belt_DriveRun").Shape=Part.makeBox(
        BOUT-BIN,s["carr"]-24.,BZ[1]-BZ[0],V(-BOUT,0.,BZ[0]))
acc={"worst":{},"env":{"lo":1e9,"hi":-1e9,"loN":"","hiN":"","khi":-1e9,"khiN":"","n":0}}
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
        if bb.YMin<150.0 and bb.ZMax>E["khi"]: E["khi"],E["khiN"]=bb.ZMax,n
    E["n"]+=1
pose(S[2])
json.dump(acc,open(ACC,"w"))
print("chunk %d..%d done; poses=%d; pairs=%d"%(I0,I1,E["n"],len(W)))
