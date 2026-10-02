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
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration when no document is open, which
    surfaces from freecadcmd as the unhelpful "<unknown exception data>" -- and is why these
    older build scripts could not be re-run without the GUI at all.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace(chr(92), "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()

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
         "P24_FairingShank", "HW_JointBolts", "REF_Shank", "P31_InterfaceDist"]
# Updated for the ONE-SCREW build (391-397). One moving group, not two: the gantry, the
# single nut and the four mini V-wheels. The belt is a closed loop whose strands and
# wraps are all STATIC geometry -- only the clamp slides along the -X strand -- so
# nothing here is rebuilt per pose, unlike the two-screw version.
GANTRY = ["P3_Carriage", "A2b_BallNut_SFU1620",
          "P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"]
# P25_MotorNacelle belongs here: 399 split the drive wall into TWO printed parts, and a "clad"
# shot that hides P22 but leaves P25 showing has a hole in exactly the place the shot is about.
FAIR = ["P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P25_MotorNacelle",
        "P24_FairingShank"]
REFS = ["REF_Thigh", "REF_Knee", "REF_Shank"]
O = lambda n: doc.getObject(n)
ALL = [o.Name for o in doc.Objects if o.TypeId.startswith("Part::")]

# flat, legible, deliberately not photoreal -- these should read as CAD
COL = {}
for n in ("A1_Extrusion_20x60_VSlot", "A4_Shank2020_VSlot"):
    COL[n] = (0.16, 0.17, 0.19)
for n in ("P1_KneeYoke", "P2a_KneeHingePlate", "A6_Idler29T",
          "P5_ThighCuff", "P6_ShankSocket", "P7_ShankCuff"):
    COL[n] = (0.13, 0.31, 0.72)              # printed PETG
COL["P3_Carriage"] = (0.66, 0.68, 0.72)      # the gantry is bought aluminium, not printed
COL["A7_DriveBox"] = (0.58, 0.60, 0.64)      # so is the drive bracket
for n in ("P20_KneeShroud", "P21_ShellAnterior", "P22_DriveCap", "P24_FairingShank"):
    COL[n] = (0.22, 0.44, 0.85)
for n in ("A2_BallScrew_SFU1620", "HW_PinB_10", "HW_JointBolts"):
    COL[n] = (0.72, 0.74, 0.78)
COL["A2b_BallNut_SFU1620"] = (0.45, 0.47, 0.50)
for n in ("A5_Belt_HTD8M", "A5b_Belt_DriveRun", "A5c_Belt_TakeRun",
          "A5d_Belt_WrapIdler", "A7b_LinkBelt"):
    COL[n] = (0.10, 0.10, 0.11)
for n in ("P10a_VWheel", "P10b_VWheel", "P10c_VWheel", "P10d_VWheel"):
    COL[n] = (0.85, 0.85, 0.83)   # Delrin mini V-wheels
COL["A3_Motor_6374"] = (0.20, 0.20, 0.22)
COL["A7_DriveBox"] = (0.25, 0.25, 0.27)

for n, c in COL.items():
    o = O(n)
    if o:
        if getattr(o, "ViewObject", None) is not None:  # absent headless
            o.ViewObject.ShapeColor = c
        if getattr(o, "ViewObject", None) is not None:  # absent headless
            o.ViewObject.Transparency = 0
for n in REFS:
    o = O(n)
    if o:
        if getattr(o, "ViewObject", None) is not None:  # absent headless
            o.ViewObject.ShapeColor = (0.80, 0.66, 0.58)
        if getattr(o, "ViewObject", None) is not None:  # absent headless
            o.ViewObject.Transparency = 75

# The knee axis is Z, so Z is medial-lateral and the limb swings in the XY plane.
# Looking along -Z therefore views the SAGITTAL plane; looking along -X views the
# CORONAL one. These two names were the wrong way round until measured.
CAMS = {
    "sagittal": Rot(),
    "coronal":  Rot(V(0, 1, 0), 90),
    "tq":       Rot(V(0, 1, 0), 40).multiply(Rot(V(1, 0, 0), -16)),
    # anterior-lateral, for the drive end: the motor went anterior in 402 and the drive is at
    # +Z, so neither of the two technical cameras shows the pod and the shell at the same time.
    "antlat":   Rot(V(0, 1, 0), -50).multiply(Rot(V(1, 0, 0), -12)),
}


A0 = 161.0          # clamp Y at theta = 0, from 391_onescrew_build.py


def pose(th):
    r = Rot(V(0, 0, 1), th)
    yc = A0 - R * math.radians(th)
    for n in SHANK:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0, 0, 0), r, V(0, 0, 0))
    for n in GANTRY:
        if O(n):
            O(n).Placement = FreeCAD.Placement(V(0., yc - A0, 0.), Rot())
    return yc


def show(names, on):
    for n in names:
        o = O(n)
        if o:
            if getattr(o, "ViewObject", None) is not None:  # absent headless
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
     focus=["A1_Extrusion_20x60_VSlot", "P3_Carriage",
            "A2_BallScrew_SFU1620", "A6_Idler29T"])
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

# THE FOUR SHOTS THAT WERE NEVER IN A SCRIPT. renders/cad carried cuff_thigh, cuff_shank,
# drive_antlat_clad and drive_antlat_open, and nothing in the repository produced them -- they
# were framed by hand in a GUI session, which means they could not be regenerated when the parts
# changed, and they are now the oldest images in the set. Same failure as vs_leg() and SUFFIX:
# it worked because the session remembered, and the session is not the project.
prep(0.0, fair=True, refs=True, cam="antlat", focus=["P22_DriveCap", "P25_MotorNacelle"])
save("drive_antlat_clad", 1400, 1300)
prep(0.0, fair=False, refs=False, cam="antlat",
     focus=["A3_Motor_6374", "A7_DriveBox", "A6_Idler29T", "A2_BallScrew_SFU1620"])
save("drive_antlat_open", 1400, 1300)
prep(0.0, fair=True, refs=True, cam="tq", focus=["P5_ThighCuff"])
save("cuff_thigh", 1300, 1200)
prep(0.0, fair=True, refs=True, cam="tq", focus=["P7_ShankCuff"])
save("cuff_shank", 1300, 1200)

# LEAVE THE DOCUMENT AT THE DESIGN POSE. This used to end with pose(30.0), which looks
# harmless -- nothing here saves -- but the pose lives in the GUI session until the next build
# script calls doc.save() and bakes it into the file. That is invisible afterwards: valid
# shapes, right volumes, clean save, and every boolean against a posed reference quietly using
# geometry that is not where the part is. It cost this project a cuff fit that appeared to fail,
# a sweep run against a flexed limb, and a session spent asking why the leg no longer lined up
# with the machine. tools/unpose.py exists for the same reason; this is the leak it was built
# to catch.
pose(0.0)
# leave the session usable: the last shot hides the fairings, and leaving them hidden
# makes it look as though the motor has no cover
show(ALL, True)
show(REFS, True)
doc.recompute()
print("done -- all parts visible, document at the 0 deg design pose")
