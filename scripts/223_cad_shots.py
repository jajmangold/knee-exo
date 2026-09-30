# -*- coding: utf-8 -*-
"""FreeCAD viewport screenshots for the README.

These are the CAD itself, not renders -- flat shading, edge lines, orthographic where the
view is a technical one. The Cycles stills live in renders/flexed_40deg and friends.

Three things this has to get right that the earlier export scripts did not:

1. REF_Shank belongs with the shank. vlow.py has always posed it; 221/222 never did,
   which was invisible while the reference limb was hidden and wrong the moment it was
   shown -- the limb stayed straight while the device flexed.
2. None of FreeCAD's standard views stand the device up. The axes are: +Y proximal, Z
   medial-lateral (the knee pin runs along Z, so this is a lateral upright), +X
   posterior -- the shank swings toward +X in flexion. Camera orientation maps the
   camera frame into world and the camera looks down its own -Z with +Y up, so identity
   is the SAGITTAL view with the limb vertical.
3. The MCP's get_active_screenshot forces one of the standard views, overwriting any
   custom camera. Use the view's own saveImage instead.

Run over the XML-RPC client:  python scripts/fc.py run scripts/223_cad_shots.py
Images land in OUT and want autocropping afterwards (see crop_cad.py).
"""
import os, math, json, FreeCAD, Part, FreeCADGui as Gui
from FreeCAD import Vector as V, Rotation as Rot

OUT = r"C:/Users/Josh/KneeExo_render/cad"
doc = FreeCAD.getDocument("KneeExo_v4")

t = globals().get("_kx_timer")
if t is not None:
    try:
        t.stop()
    except Exception:
        pass
globals()["_kx_timer"] = None

K = json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
C0, C1, R = K["C0"], K["C1"], K["R"]
BZ = tuple(K["belt_z"])
BIN, BOUT = K["belt_x"][0] + 0.05, K["belt_x"][1]

SHANK = ["A4_Shank2020_VSlot", "P2a_KneeHingePlate", "P6_ShankSocket", "P7_ShankCuff",
         "P24_FairingShank", "HW_JointBolts", "REF_Shank"]
# ---------------------------------------------------------------------------------------
# PART LISTS BELOW ARE THE TWO-SCREW BUILD AND ARE STALE.
# The model in KneeExo_v4 is now the ONE-SCREW build (391-396): A2c, A2d, P3b, A9, A9b,
# P10a-d_Slider_Delrin, P11, A8 and P13 no longer exist, and A6_Idler29T, A7b_LinkBelt,
# A5d_Belt_WrapIdler and P10a-d_VWheel do. The lists are kept verbatim so the render and
# screenshot pipeline still reproduces the published two-screw images; regenerating any of
# them for the new build means updating these lists first. Nothing here has been re-run
# against the one-screw model.
# ---------------------------------------------------------------------------------------
CA = ["P3_Carriage", "A2b_BallNut_SFU1620", "P10a_Slider_Delrin", "P10b_Slider_Delrin"]
CB = ["P3b_CarriageB", "A2d_BallNut_LH", "P10c_Slider_Delrin", "P10d_Slider_Delrin",
      "P11_SprungAnchor", "A8_TensionSpring", "P13_HallTension"]
FAIR = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P24_FairingShank"]
REFS = ["REF_Thigh", "REF_Knee", "REF_Shank"]
O = lambda n: doc.getObject(n)
ALL = [o.Name for o in doc.Objects if o.TypeId.startswith("Part::")]

# flat, legible, deliberately not photoreal -- these should read as CAD
COL = {}
for n in ("A1_Extrusion_20x60_VSlot", "A4_Shank2020_VSlot"):
    COL[n] = (0.16, 0.17, 0.19)
for n in ("P1_KneeYoke", "P2a_KneeHingePlate", "P3_Carriage", "P3b_CarriageB",
          "P5_ThighCuff", "P6_ShankSocket", "P7_ShankCuff", "P11_SprungAnchor"):
    COL[n] = (0.13, 0.31, 0.72)
for n in ("P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P24_FairingShank"):
    COL[n] = (0.22, 0.44, 0.85)
for n in ("A2_BallScrew_SFU1620", "A2c_BallScrew_LH", "HW_PinB_10", "HW_JointBolts",
          "A9_RailMGN9_A", "A9b_RailMGN9_B"):
    COL[n] = (0.72, 0.74, 0.78)
for n in ("A2b_BallNut_SFU1620", "A2d_BallNut_LH", "A8_TensionSpring"):
    COL[n] = (0.45, 0.47, 0.50)
for n in ("A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun"):
    COL[n] = (0.10, 0.10, 0.11)
for n in ("P10a_Slider_Delrin", "P10b_Slider_Delrin",
          "P10c_Slider_Delrin", "P10d_Slider_Delrin"):
    COL[n] = (0.45, 0.47, 0.50)   # MGN9H blocks, bought steel
COL["A3_Motor_6374"] = (0.20, 0.20, 0.22)
COL["A7_DriveBox"] = (0.25, 0.25, 0.27)
COL["P13_HallTension"] = (0.10, 0.45, 0.30)

for n, c in COL.items():
    o = O(n)
    if o:
        o.ViewObject.ShapeColor = c
        o.ViewObject.Transparency = 0
for n in REFS:
    o = O(n)
    if o:
        o.ViewObject.ShapeColor = (0.80, 0.66, 0.58)
        o.ViewObject.Transparency = 75

# The knee axis is Z, so Z is medial-lateral and the limb swings in the XY plane.
# Looking along -Z therefore views the SAGITTAL plane; looking along -X views the
# CORONAL one. These two names were the wrong way round until measured.
CAMS = {
    "sagittal": Rot(),
    "coronal":  Rot(V(0, 1, 0), 90),
    "tq":       Rot(V(0, 1, 0), 40).multiply(Rot(V(1, 0, 0), -16)),
}


def pose(th):
    r = Rot(V(0, 0, 1), th)
    rad = math.radians(th)
    cA, cB = C0 - R * rad, C1 + R * rad
    for n in SHANK:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in CA:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0., cA - C0, 0.), Rot())
    for n in CB:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0., cB - C1, 0.), Rot())
    O("A5b_Belt_DriveRun").Shape = Part.makeBox(BOUT - BIN, cA - 24., BZ[1] - BZ[0],
                                                V(-BOUT, 0., BZ[0]))
    O("A5c_Belt_TakeRun").Shape = Part.makeBox(BOUT - BIN, cB - 24., BZ[1] - BZ[0],
                                               V(BIN, 0., BZ[0]))
    return cA, cB


def show(names, on):
    for n in names:
        o = O(n)
        if o:
            o.ViewObject.Visibility = bool(on)


def prep(theta, fair=True, refs=True, cam="tq", focus=None, ortho=False):
    pose(theta)
    doc.recompute()
    show(ALL, True)
    show(FAIR, fair)
    show(REFS, refs)
    v = Gui.ActiveDocument.ActiveView
    try:
        Gui.ActiveDocument.resetEdit()     # a live dragger gets baked into saveImage
        v.setAxisCross(False)
    except Exception:
        pass
    v.setCameraType('Orthographic' if ortho else 'Perspective')
    v.setCameraOrientation(CAMS[cam])
    Gui.Selection.clearSelection()
    if focus:
        for n in focus:
            if O(n):
                Gui.Selection.addSelection(doc.Name, n)
        Gui.SendMsgToActiveView("ViewSelection")
        Gui.Selection.clearSelection()
    else:
        Gui.SendMsgToActiveView("ViewFit")
    Gui.updateGui()


def save(name, w, h):
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    p = os.path.join(OUT, name + ".png")
    Gui.ActiveDocument.ActiveView.saveImage(p, w, h, 'Current')
    print("%-16s %7d bytes" % (name, os.path.getsize(p)))


# technical views: orthographic
prep(0.0, fair=True, refs=True, cam="coronal", ortho=True)
save("coronal_clad", 1000, 1700)
prep(0.0, fair=False, refs=False, cam="sagittal", ortho=True)
save("sagittal_open", 1000, 1700)

# the differential pair -- fit once on the wider pose, then change pose WITHOUT refitting
# so the two frames are directly comparable
prep(104.0, fair=False, refs=False, cam="sagittal", ortho=True,
     focus=["A1_Extrusion_20x60_VSlot", "P3_Carriage", "P3b_CarriageB",
            "A2_BallScrew_SFU1620", "A2c_BallScrew_LH"])
save("diff_flexed", 1100, 1500)
pose(0.0)
doc.recompute()
Gui.updateGui()
save("diff_extended", 1100, 1500)

# pictorial views: perspective
prep(30.0, fair=True, refs=True, cam="tq")
save("tq_clad", 1400, 1700)
prep(30.0, fair=False, refs=False, cam="tq")
save("tq_open", 1400, 1700)
prep(55.0, fair=False, refs=False, cam="tq", focus=["P2a_KneeHingePlate", "P1_KneeYoke"])
save("knee_detail", 1500, 1150)

pose(30.0)
# leave the session usable: the last shot hides the fairings, and leaving them hidden
# makes it look as though the motor has no cover
show(ALL, True)
show(REFS, True)
doc.recompute()
print("done -- all parts left visible")
