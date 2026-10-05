# -*- coding: utf-8 -*-
"""Every number the docs assert about v8, checked against the v8 document.

902_doc_audit.py does this for v6 and catches volume claims that have drifted -- README said
"P2a 148 cm3" for a while after 457 took it to 134. v8 is a separate document that 902 does not
look at, and this session put a lot of new figures into README and BOM: the screw's stations, the
ratio, the belt's tooth count, five part volumes. Numbers in prose rot faster than anything else
in this repository, so they get a check of their own.

The failures this guards against are not hypothetical. In one afternoon: 446_sfu1605_set.py
predicted 0.2 mm of pod interference where the truth was 3.8 mm, because it used the pulley's
pitch radius and never added the belt's thickness; 459's first clearance check named its suspects
and left the belt out, so it reported 0.271 cm3 and missed 6.917; and the first fix for that cut
the nacelle's dome off and discarded it as "0.058 cm3 of loose fragment".

    freecadcmd.exe scripts/460_v8_claims.py
"""
import math, FreeCAD
d = FreeCAD.openDocument(r"C:/Users/Josh/KneeExo_v8.FCStd")
g = {o.Name: o for o in d.Objects}
ok = bad = 0
def claim(what, got, want, tol=0.15):
    global ok, bad
    good = abs(got - want) <= tol
    print("   %-52s %10.2f vs %-9.2f %s" % (what, got, want, "ok" if good else "<-- WRONG"))
    if good: ok += 1
    else: bad += 1

s = g["A2_BallScrew_SFU1620"].Shape.BoundBox
claim("screw Y min", s.YMin, 60.0)
claim("screw Y max", s.YMax, 231.0)
claim("screw length", s.YLength, 171.0)
b = g["A6c_MotorPulley38T"].Shape.BoundBox
claim("38T tip radius", max(b.XLength, b.ZLength) / 2, 38 * 5.0 / (2 * math.pi) - 0.571)
claim("38T belt plane Y min", b.YMin, 206.0)
claim("38T belt plane width", b.YLength, 15.0)
b = g["A6b_ScrewPulley20T"].Shape.BoundBox
claim("20T tip radius", max(b.XLength, b.ZLength) / 2, 20 * 5.0 / (2 * math.pi) - 0.571)
claim("P25_MotorNacelle cm3", g["P25_MotorNacelle"].Shape.Volume / 1000., 116.7, 0.2)
claim("P25 reaches down to Y", g["P25_MotorNacelle"].Shape.BoundBox.YMin, 146.0, 0.5)
claim("P21_ShellAnterior cm3", g["P21_ShellAnterior"].Shape.Volume / 1000., 163.8, 0.2)
# the blend's own promise: a ramp no steeper than 30 degrees across the pod's leading edge
import Part as _P
def _sect_r(y):
    best = 0.0
    for w in (g["P21_ShellAnterior"].Shape.fuse(g["P22_DriveCap"].Shape)
              .fuse(g["P25_MotorNacelle"].Shape)).slice(FreeCAD.Vector(0, 1, 0), y):
        for q in w.discretize(Distance=1.0):
            a = math.degrees(math.atan2(q.z, q.x)) % 360.0
            if 138.0 <= a <= 172.0:
                best = max(best, math.hypot(q.x, q.z))
    return best
_prev, _worst = 0.0, 0.0
for _y in range(160, 206, 5):
    _r = _sect_r(float(_y))
    if _prev and _r:
        _worst = max(_worst, math.degrees(math.atan2(_r - _prev, 5.0)))
    _prev = _r
claim("steepest face on the pod ramp, deg", _worst, 31.0, 1.5)
claim("A7_DriveBox cm3", g["A7_DriveBox"].Shape.Volume / 1000., 121.4, 0.2)
claim("P22_DriveCap cm3", g["P22_DriveCap"].Shape.Volume / 1000., 149.8, 0.2)
claim("P32_ScrewFoot cm3", g["P32_ScrewFoot"].Shape.Volume / 1000., 13.3, 0.2)
claim("P1_KneeYoke cm3", g["P1_KneeYoke"].Shape.Volume / 1000., 134.4, 0.2)
claim("P2a_KneeHingePlate cm3", g["P2a_KneeHingePlate"].Shape.Volume / 1000., 134.2, 0.2)
# the ratio the docs quote
R_CAP = 29 * 8.0 / (2 * math.pi)
n = (2 * math.pi * R_CAP / 5.0) / (38 / 20.0)
claim("total ratio", n, 24.4, 0.1)
claim("reflected J vs limb", 3.10e-4 * n ** 2 / 0.30, 0.62, 0.01)
# belt length
pd = lambda t: t * 5.0 / math.pi
C = math.hypot(-104.0 + 62.0, 62.0 - 106.0)
L = 2 * C + math.pi * (pd(38) + pd(20)) / 2 + (pd(38) - pd(20)) ** 2 / (4 * C)
claim("link belt teeth", L / 5.0, 54.0, 0.1)
# the knee
br = g["HW_Bearing_6001"].Shape.BoundBox
claim("knee bearings span Z", br.ZLength, 30.0)
print()
print("   %d claims checked, %d wrong" % (ok + bad, bad))
