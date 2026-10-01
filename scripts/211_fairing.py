# -*- coding: utf-8 -*-
"""Sleek lofted fairing replacing the four blocky guards.

The enabling fact is the one you spotted: the pulley's INSIDE is what swings. Measured,
nothing moving occupies r 41..70 at Z 96..126, and nothing at all sits above Z=126 now the
pin is recessed. So the belt and the pulley's outer face can be fully enclosed by a STATIC
cover tied into the thigh fairing.

Form: superelliptical sections (exponent 3.4 -- rounded-square, not boxy) lofted along Y.
A closed nose over the knee, flaring into a tapered thigh shell. Open medially only.
Mounts on a central spine into the rail's MIDDLE outboard slot at X=0 -- the one channel
nothing else uses: the carriages take the X=+/-20 outboard slots and the X=+/-30 side
slots, so a spine at X=0 is never swept."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
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
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
N_EXP,N_PTS=3.4,64
def sell(y,a,b,zc):
    pts=[]
    for i in range(N_PTS):
        t=2.*math.pi*i/N_PTS; ct,st=math.cos(t),math.sin(t)
        x=a*math.copysign(abs(ct)**(2./N_EXP),ct)
        z=zc+b*math.copysign(abs(st)**(2./N_EXP),st)
        pts.append(V(x,y,z))
    pts.append(pts[0]); return Part.makePolygon(pts)
def loft(st):
    return Part.makeLoft([sell(*s) for s in st],True,False)
# ---- knee cap: closed nose over the pulley + belt wrap ----
CAP_O=[(-45.,18.,10.,112.),(-35.,32.,17.,112.),(-20.,44.,21.,111.5),(0.,49.,22.,111.),(28.,50.,21.,111.)]
CAP_I=[(-40.,22.,11.,112.),(-35.,29.,14.,112.),(-20.,41.,18.,111.5),(0.,46.,19.,111.),(29.,47.,18.,111.)]
cap=loft(CAP_O).cut(loft(CAP_I))
cap=cap.cut(bx(-60.,60.,-60.,40.,40.,95.))          # open inboard: the fork closes that side
cap=cap.removeSplitter()
assert len(cap.Solids)==1 and cap.isValid(),"cap solids=%d"%len(cap.Solids)
o=doc.getObject("P20_KneeShroud"); o.Shape=cap; o.Label="P20_KneeCap"
b=cap.BoundBox
print("P20_KneeCap    X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cap.Volume/1000))
# ---- thigh fairing ----
F_O=[(28.,50.,21.,111.),(44.,62.,23.,110.5),(58.,79.,25.,110.),(150.,83.,25.,110.),
     (240.,83.,25.,110.),(285.,80.,24.,110.5),(292.,74.,22.,111.)]
F_I=[(26.,47.,18.,111.),(44.,59.,20.,110.5),(58.,76.,22.,110.),(150.,80.,22.,110.),
     (240.,80.,22.,110.),(285.,77.,21.,110.5),(294.,70.,18.,111.)]
f=loft(F_O).cut(loft(F_I))
f=f.cut(bx(-31.,31.,20.,300.,40.,96.))              # medial opening: drops on over the rail
SPINE=(62.,112.,166.,220.,272.)
for y in SPINE:
    f=f.fuse(bx(-4.,4.,y-7.,y+7.,104.,133.))        # spine post to the free middle slot
    f=f.fuse(bx(-2.8,2.8,y-7.,y+7.,104.2,108.))
f=f.removeSplitter()
for y in SPINE: f=f.cut(cz(2.6,102.,124.,0.,y))
for i,y in enumerate((74.,126.,178.,230.)):          # vents, clear of the spine at X +/-4
    for sx in (-1.,1.):
        f=f.cut(bx(*sorted((sx*5.,sx*13.)),y,y+36.,126.,142.))
assert len(f.Solids)==1 and f.isValid(),"fairing solids=%d"%len(f.Solids)
o=doc.getObject("P21_ShellAnterior"); o.Shape=f; o.Label="P21_FairingThigh"
b=f.BoundBox
print("P21_FairingThigh X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,f.Volume/1000))
print("  spine at X=0 into the middle outboard slot at Y %s"%(SPINE,))
print("  8 vent slots at X +/-5..13 (finger-safe, and only the static rail is beneath)")
# ---- proximal nose over the coupling ----
N_O=[(292.,74.,22.,111.),(306.,70.,21.,111.),(318.,52.,17.,111.),(326.,26.,9.,111.)]
N_I=[(290.,71.,19.,111.),(306.,67.,18.,111.),(318.,49.,14.,111.)]
nz=loft(N_O).cut(loft(N_I))
nz=nz.cut(bx(-31.,31.,285.,330.,40.,96.)).removeSplitter()
assert len(nz.Solids)==1 and nz.isValid(),"nose solids=%d"%len(nz.Solids)
o=doc.getObject("P23_DriveCover"); o.Shape=nz; o.Label="P23_DriveNose"
b=nz.BoundBox
print("P23_DriveNose  X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,nz.Volume/1000))
if doc.getObject("P22_ShellPosterior"):
    doc.removeObject("P22_ShellPosterior"); print("retired P22_ShellPosterior (one fairing now covers both sides)")
doc.recompute(); doc.save()
