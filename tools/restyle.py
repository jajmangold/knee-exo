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

REF = r"C:/Users/Josh/KneeExo_v6.guistale.FCStd"
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


ref, opened = _open_ref()
style = style_of(ref)
print("harvested %d styles from %s" % (len(style), ref.Name))

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

if opened:
    FreeCAD.closeDocument(ref.Name)
