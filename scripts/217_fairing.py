# -*- coding: utf-8 -*-
"""Fairing, corrected. Two bugs from the first attempt:

 1. ruled=False spline loft OVERSHOT the sections (X +/-129 instead of +/-83) and
    self-intersected. Now ruled=True with closer stations.
 2. A superellipse NARROWS in Z at its X extremes, so containing a box of half-size
    (W,H) needs (W/a)^n + (H/b)^n <= 1. At n=3.4, b=22 that required a=108 -- I had 80,
    which is why the carriages, cuff, rail and belt all poked through the walls.
    Now n=5.5 (rounded rectangle) with a=81, b=25: carriage 0.901, nut 0.530, belt 0.110.

Open below Z=92: the thigh cuff tops out at Z=88 and the carriage bottom is at Z=90, so
there is no room for a wall between them -- the underside faces the limb anyway."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
N_EXP,N_PTS=5.5,32
def sell(y,a,b,zc):
    pts=[]
    for i in range(N_PTS):
        t=2.*math.pi*i/N_PTS; ct,st=math.cos(t),math.sin(t)
        pts.append(V(a*math.copysign(abs(ct)**(2./N_EXP),ct),y,
                     zc+b*math.copysign(abs(st)**(2./N_EXP),st)))
    pts.append(pts[0]); return Part.makePolygon(pts)
def loft(st): return Part.makeLoft([sell(*s) for s in st],True,True)
def sm(u): u=max(0.,min(1.,u)); return u*u*(3.-2.*u)
# ---------- knee cap: inner a=55 b=18 zc=113 contains the wrap (0.932) ----------
co=[(-46.,20.),(-36.,34.),(-24.,46.),(-10.,54.),(6.,58.),(28.,58.)]
ci=[(-41.,24.),(-30.,38.),(-16.,48.),(6.,55.),(29.,55.)]
cap=loft([(y,a,21.,112.) for y,a in co]).cut(loft([(y,a,19.,113.) for y,a in ci]))
cap=cap.cut(bx(-70.,70.,-60.,40.,40.,96.5)).removeSplitter()   # 96.5 not 95: at 95 the cut plane and the void bottom coincided, leaving a 0.13 mm lip over the hub
assert len(cap.Solids)==1 and cap.isValid(),"cap solids=%d"%len(cap.Solids)
o=doc.getObject("P20_KneeShroud"); o.Shape=cap; o.Label="P20_KneeCap"
b=cap.BoundBox
print("P20_KneeCap      X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,cap.Volume/1000))
# ---------- thigh fairing, now running out to Y=312 over the coupling ----------
def fa(y,d=0.):
    if y<=28.: return 58.-d
    if y< 58.: return 58.+26.*sm((y-28.)/30.)-d
    if y<=300.: return 84.-d
    return 84.-8.*sm((y-300.)/12.)-d
YS=[28.,38.,48.,58.,160.,270.,300.,312.]
f=loft([(y,fa(y),28.,110.) for y in YS]).cut(
  loft([(y,fa(y,3.),25.,110.) for y in [26.]+YS[1:-1]+[314.]]))
f=f.cut(bx(-95.,95.,20.,320.,40.,92.))               # open below Z=92
f=f.cut(bx(-95.,95.,20.,50.,40.,96.))                # distal bottom: the fork cheek sweeps to Z=94 here
SPINE=(62.,112.,166.,220.,272.)
for y in SPINE:
    f=f.fuse(bx(-4.,4.,y-7.,y+7.,109.,136.))         # stops at 109: rail tops out at 108
    f=f.fuse(bx(-2.8,2.8,y-7.,y+7.,104.2,109.))      # tongue into the free middle slot
f=f.removeSplitter()
for y in SPINE: f=f.cut(cz(2.6,102.,126.,0.,y))
for y in (76.,130.,184.,238.):
    for sx in (-1.,1.): f=f.cut(bx(*sorted((sx*6.,sx*14.)),y,y+38.,130.,146.))
assert len(f.Solids)==1 and f.isValid(),"fairing solids=%d"%len(f.Solids)
o=doc.getObject("P21_ShellAnterior"); o.Shape=f; o.Label="P21_FairingThigh"
b=f.BoundBox
print("P21_FairingThigh X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,f.Volume/1000))
print("  n=%.1f rounded-rectangle sections; flare 58->84 over Y 28..58; open below Z=92"%N_EXP)
print("  spine at X=0 into the middle outboard slot; 8 vents at X +/-6..14")
# ---------- shank fairing ----------
so=[(-100.,24.),(-140.,23.),(-180.,21.),(-208.,20.)]
si=[(-98.,21.),(-140.,20.),(-180.,18.),(-210.,17.)]   # inner must overrun the outer (-100) or an end WALL forms
sk=loft([(y,a,25.,100.) for y,a in so]).cut(loft([(y,a,22.,100.) for y,a in si]))
sk=sk.cut(bx(-30.,30.,-215.,-95.,40.,96.))
SSP=(-115.,-150.,-185.)
for y in SSP:
    sk=sk.fuse(bx(-4.,4.,y-7.,y+7.,114.,122.))
    sk=sk.fuse(bx(-2.8,2.8,y-7.,y+7.,110.2,114.))
sk=sk.removeSplitter()
for y in SSP: sk=sk.cut(cz(2.6,108.,124.,0.,y))
assert len(sk.Solids)==1 and sk.isValid(),"shank solids=%d"%len(sk.Solids)
o=doc.getObject("P24_FairingShank") or doc.addObject("Part::Feature","P24_FairingShank")
o.Shape=sk; o.Label="P24_FairingShank"; o.ViewObject.Visibility=True
b=sk.BoundBox
print("P24_FairingShank X %6.1f..%5.1f Y %6.1f..%5.1f Z %5.1f..%5.1f  %5.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,sk.Volume/1000))
print("  starts at Y=-100: at 104 deg a shell from -66 swings to X 57.7..70.3 where the")
print("  thigh fairing is already 63.5 wide. Y -45..-100 is a moving gap -> fabric gaiter.")
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="B_Shank": gg.addObject(o)
for dead in ("P22_ShellPosterior","P23_DriveCover"):
    if doc.getObject(dead): doc.removeObject(dead); print("retired %s"%dead)
doc.recompute(); doc.save()
