# -*- coding: utf-8 -*-
"""Put the view state back after a headless rebuild, and mirror it onto the right leg.

freecadcmd has no ViewObject, so nothing built or rebuilt headlessly carries a colour or a
visibility flag: open the result in the GUI and every part is default grey and HIDDEN. That is
not a cosmetic detail -- it reads as "the model is gone" (and once before, as "P25 looks like a
bare motor", which is how the drive nacelle's missing colour was first noticed).

So: harvest ShapeColor / Transparency / Visibility per object NAME from a reference document
that still has them, and apply to one or more targets. Names, not labels: labels change when a
part is renamed (P20_KneeShroud -> P20_KneeCap) and the name never does.

Must run inside the GUI instance -- that is where ViewObject exists:

    python tools/fcsend.py tools/restyle.py
"""
import FreeCAD

# The style table lives in the REPOSITORY, not in whichever scratch document happened to have
# the colours last. It was read from C:/Users/Josh/KneeExo_v6.guistale.FCStd -- a parked,
# half-built GUI copy -- which worked exactly as long as nobody deleted it. Harvest once from a
# document that has the styles, commit the JSON, and restyle from that forever after.
# Absolute, because inside the GUI's RPC server __file__ is the server module, not this script --
# a relative path resolved from it lands in the FreeCAD Mod directory and the open() fails.
STYLE_JSON = os.environ.get("KX_STYLES", r"C:/Users/Josh/knee-exo/model/styles.json")
REF = os.environ.get("KX_STYLE_REF", r"C:/Users/Josh/KneeExo_v6.guistale.FCStd")
TARGETS = ["KneeExo_v6", "KneeExo_v6_R"]
# The reference limbs are context, not parts. They were shown translucent while fitting and
# are in the way of everything else, so default them off rather than inheriting whatever state
# the reference document happened to be left in.
HIDE = ("REF_",)
DEFAULT = (0.78, 0.78, 0.80)


def style_of(doc):
    out = {}
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None or not hasattr(vo, "ShapeColor"):
            continue
        out[o.Name] = (vo.ShapeColor, getattr(vo, "Transparency", 0), vo.Visibility)
    return out


def _open_ref():
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(REF.rsplit("/", 1)[-1]):
            return d, False
    return FreeCAD.openDocument(REF), True


if os.path.exists(STYLE_JSON) and not os.environ.get("KX_REHARVEST"):
    raw = json.load(open(STYLE_JSON))
    style = {k: (tuple(v["color"]), v["transparency"], v["visible"]) for k, v in raw.items()}
    ref, opened = None, False
    print("%d styles from %s" % (len(style), os.path.basename(STYLE_JSON)))
else:
    ref, opened = _open_ref()
    style = style_of(ref)
    json.dump({k: {"color": list(c), "transparency": t, "visible": v}
               for k, (c, t, v) in style.items()}, open(STYLE_JSON, "w"), indent=1, sort_keys=True)
    print("harvested %d styles from %s and wrote %s"
          % (len(style), ref.Name, os.path.basename(STYLE_JSON)))

for nm in TARGETS:
    try:
        doc = FreeCAD.getDocument(nm)
    except Exception:
        print("  %s not open -- skipped" % nm)
        continue
    took = miss = 0
    for o in doc.Objects:
        vo = getattr(o, "ViewObject", None)
        if vo is None or not hasattr(vo, "ShapeColor"):
            continue
        hide = o.Name.startswith(HIDE)
        if o.Name in style:
            col, tr, vis = style[o.Name]
            vo.ShapeColor = col
            vo.Transparency = tr
            vo.Visibility = (not hide) and True
            took += 1
        else:
            vo.ShapeColor = DEFAULT
            vo.Visibility = not hide
            miss += 1
    print("  %-13s %2d styled from the reference, %2d defaulted, REF_* hidden" % (nm, took, miss))

if opened and ref is not None:
    FreeCAD.closeDocument(ref.Name)
