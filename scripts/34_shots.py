# -*- coding: utf-8 -*-
import FreeCADGui
O = lambda n: doc.getObject(n)
# confirm the last 0.072 cm3 is the designed ROM stop contact, not a graze
pose(105.0)
for p in ("HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"):
    c = O("P4_ShankLink_Horn").Shape.common(O(p).Shape)
    if not c.isNull() and c.Volume > 1:
        print("flexion stop engaged: finger bears on %s (%.3f cm3)" % (p.split('_')[1], c.Volume/1000))
pose(-2.0)
for p in ("HW_ROMpin_flexion_105deg","HW_ROMpin_extension_0deg"):
    c = O("P4_ShankLink_Horn").Shape.common(O(p).Shape)
    if not c.isNull() and c.Volume > 1:
        print("extension stop engaged: finger bears on %s (%.3f cm3)" % (p.split('_')[1], c.Volume/1000))
for n in ("REF_Thigh","REF_Knee","REF_Shank"):
    if O(n): O(n).ViewObject.Transparency = 80
for n in ("P3_ThighCuff","P6_ShankCuff"):
    O(n).ViewObject.Transparency = 35
pose(0.0)
FreeCADGui.ActiveDocument.ActiveView.viewIsometric()
FreeCADGui.SendMsgToActiveView("ViewFit")
doc.recompute()
print("ready")
