# -*- coding: utf-8 -*-
"""Sleek lofted fairing. RULED loft (ruled=True): a spline loft overshot the sections
badly -- X +/-129 instead of +/-83 -- and self-intersected, so stations are closely
spaced instead and interpolated linearly.

Superelliptical sections (exponent 3.4: rounded-square, not boxy). Closed nose over the
knee, flaring into a tapered thigh shell, open medially only. Mounts on a central spine
into the rail's MIDDLE outboard slot at X=0 -- the one channel nothing else uses (the
carriages take X=+/-20 outboard and X=+/-30 side), so it is never swept."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
N_EXP,N_PTS=3.4,56
def sell(y,a,b,zc):
    pts=[]
    for i in range(N_PTS):
        t=2.*math.pi*i/N_PTS; ct,st=math.cos(t),math.sin(t)
        pts.append(V(a*math.copysign(abs(ct)**(2./N_EXP),ct),y,
                     zc+b*math.copysign(abs(st)**(2./N_EXP),st)))
    pts.append(pts[0]); return Part.makePolygon(pts)
def loft(st): return Part.makeLoft([sell(*s) for s in st],True,True)
def smooth(u): u=max(0.,min(1.,u)); return u*u*(3.-2.*u)
# ---------- knee cap ----------
CO_B,CO_Z,CI_B,CI_Z=21.,112.,18.,113.
co=[(-45.,18.),(-40.,26.),(-35.,32.),(-28.,38.),(-20.,44.),(-10.,47.),(0.,49.),(14.,50.),(28.,50.)]
ci=[(-40.,22.),(-35.,29.),(-28.,35.),(-20.,41.),(-10.,44.),(0.,46.),(14.,47.),(29.,47.)]
cap=loft([(y,a,CO_B,CO_Z) for y,a in co]).cut(loft([(y,a,CI_B,CI_Z) for y,a in ci]))
cap=cap.cut(bx(-60.,60.,-60.,40.,40.,95.)).removeSplitter()
assert len(cap.Solids)==1 and cap.isValid(),"cap solids=%d"%len(cap.Solids)
o=doc.getObject("P20_KneeShroud"); o.Shape=cap; o.Label="P20_KneeCap"
b=cap.BoundBox
print("P20_KneeCap      X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cap.Volume/1000))
# ---------- thigh fairing ----------
def fa(y,d=0.):                                      # flare completes by Y=58, before
    if y<=28.: return 50.-d                          # carriage A's distal limit at 61
    if y< 58.: return 50.+33.*smooth((y-28.)/30.)-d
    if y<=245.: return 83.-d
    return 83.-9.*smooth((y-245.)/47.)-d
YS=[28.,34.,40.,46.,52.,58.,110.,170.,215.,245.,262.,278.,292.]
fo=[(y,fa(y),25.,110.) for y in YS]
fi=[(y,fa(y,3.),22.,110.) for y in [26.]+YS[1:-1]+[294.]]
f=loft(fo).cut(loft(fi))
f=f.cut(bx(-31.,31.,20.,300.,40.,96.))               # medial opening: drops on over the rail
SPINE=(62.,112.,166.,220.,272.)
for y in SPINE:
    f=f.fuse(bx(-4.,4.,y-7.,y+7.,104.,133.))
    f=f.fuse(bx(-2.8,2.8,y-7.,y+7.,104.2,108.))
f=f.removeSplitter()
for y in SPINE: f=f.cut(cz(2.6,102.,124.,0.,y))
for y in (74.,126.,178.,230.):
    for sx in (-1.,1.): f=f.cut(bx(*sorted((sx*5.,sx*13.)),y,y+36.,126.,142.))
assert len(f.Solids)==1 and f.isValid(),"fairing solids=%d"%len(f.Solids)
o=doc.getObject("P21_ShellAnterior"); o.Shape=f; o.Label="P21_FairingThigh"
b=f.BoundBox
print("P21_FairingThigh X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,f.Volume/1000))
print("  flare 50 -> 83 mm half-width over Y 28..58, then held to 245, then tapered")
print("  spine at X=0 into the free middle slot at Y %s ; 8 vents at X +/-5..13"%(SPINE,))
# ---------- proximal nose ----------
no=[(292.,74.),(302.,71.),(312.,62.),(320.,45.),(326.,24.)]
ni=[(290.,71.),(302.,68.),(312.,58.),(320.,40.)]
nz=loft([(y,a,22.,111.) for y,a in no]).cut(loft([(y,a,19.,111.) for y,a in ni]))
nz=nz.cut(bx(-31.,31.,285.,330.,40.,96.)).removeSplitter()
assert len(nz.Solids)==1 and nz.isValid(),"nose solids=%d"%len(nz.Solids)
o=doc.getObject("P23_DriveCover"); o.Shape=nz; o.Label="P23_DriveNose"
b=nz.BoundBox
print("P23_DriveNose    X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,nz.Volume/1000))
if doc.getObject("P22_ShellPosterior"):
    doc.removeObject("P22_ShellPosterior"); print("retired P22 (one fairing now spans both sides)")
doc.recompute(); doc.save()
