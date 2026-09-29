# -*- coding: utf-8 -*-
"""Knee assembly for the low belt. Hub r=14->18 and 72->32 mm long; M12 pin.
Yoke disc r=40->30 so it clears the belt wrap at r=35.55.
Knee-angle reference: magnet in the fork cheek, Hall in the yoke disc -- both at Z<=91,
so continuous angle sensing costs ZERO lateral build."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
R=K["R"]; BIN=K["belt_x"][0]; BZ=tuple(K["belt_z"])
IN_Z=(70.,76.); YZ=(76.,88.); OUT_Z=(88.,94.)
HUB_R=18.0; HUB_Z=(94.,126.); RIM_Z=(96.,126.); RIM_IN=28.0
WEB_R=29.0; WEB_Z=(104.,112.); PIN_R=6.15   # must exceed RIM_IN=28 or the rim floats free
FB=(-90.,-110.,-125.); MAG=(0.,-25.); HALL_TH=30.0
# ---- P2a: fork + hub + 29T pulley ----
p =bar((0.,0.),(0.,-80.),24.,14.,*IN_Z)
p =p.fuse(bar((0.,0.),(0.,-135.),24.,14.,*OUT_Z))
p =p.fuse(bx(-10.,10.,-80.,-45.,IN_Z[0],OUT_Z[1]))
p =p.fuse(cz(HUB_R,*HUB_Z))
p =p.fuse(cz(BIN,*RIM_Z).cut(cz(RIM_IN,RIM_Z[0]-1,RIM_Z[1]+1)))
p =p.fuse(cz(WEB_R,*WEB_Z)).removeSplitter()
p =p.cut(cz(PIN_R,IN_Z[0]-2,HUB_Z[1]+2))
for y in FB: p=p.cut(cz(2.6,OUT_Z[0]-1,OUT_Z[1]+1,0.,y))
p =p.cut(cz(3.1,OUT_Z[0]-0.5,OUT_Z[0]+3.5,*MAG))              # knee-reference magnet
for k in range(6):
    aa=math.radians(60*k)
    p=p.cut(cz(8.0,WEB_Z[0]-1,WEB_Z[1]+1,22.5*math.cos(aa),22.5*math.sin(aa)))
assert len(p.Solids)==1 and p.isClosed() and p.isValid(),"P2a solids=%d"%len(p.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=p
doc.getObject("P2a_KneeHingePlate").Label="P2a_KneeHub_Pulley29T"
b=p.BoundBox
print("P2a  X %.1f..%.1f Y %.1f..%.1f Z %.0f..%.0f  %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,p.Volume/1000))
print("  rim Z %.0f..%.0f (was 136..166), hub r%.0f Z %.0f..%.0f = %.0f mm (was r14, 72 mm)"%(
    RIM_Z[0],RIM_Z[1],HUB_R,HUB_Z[0],HUB_Z[1],HUB_Z[1]-HUB_Z[0]))
hubS=math.pi*((2*HUB_R)**4-12.3**4)/(32*2*HUB_R)
M=1091*((RIM_Z[0]+RIM_Z[1])/2-OUT_Z[1])/1000.
print("  hub bending %.1f N.m -> %.1f MPa in PETG (design ~15) SF %.1f"%(M,M*1000/hubS,15/(M*1000/hubS)))
print("  M12 pin %.0f MPa (8.8 yield 640) SF %.1f"%(32*M*1000/(math.pi*12**3),640/(32*M*1000/(math.pi*12**3))))
# ---- yoke, disc cut back to r=30 ----
yk=cz(30.,*YZ)
yk=yk.fuse(bar((0.,0.),(0.,70.),28.,30.,*YZ))
yk=yk.fuse(bx(-30.,30.,58.,124.,*YZ)).removeSplitter()
yk=yk.cut(cz(PIN_R,YZ[0]-2,YZ[1]+2))
for x in (-20.,0.,20.):
    for y in (70.,112.): yk=yk.cut(cz(2.6,YZ[0]-1,YZ[1]+1,x,y))
hx,hy=25.*math.cos(math.radians(-90+HALL_TH)),25.*math.sin(math.radians(-90+HALL_TH))
yk=yk.cut(bx(hx-6.,hx+6.,hy-4.,hy+4.,YZ[1]-4.,YZ[1]+0.5))       # Hall board pocket
assert len(yk.Solids)==1 and yk.isClosed() and yk.isValid(),"P1 solids=%d"%len(yk.Solids)
doc.getObject("P1_KneeYoke").Shape=yk
print("P1 yoke disc r=30 (was 40) so the belt wrap at r=%.1f clears it; %.1f cm3"%(BIN,yk.Volume/1000))
print("  Hall pocket at (%.1f,%.1f) Z %.0f..%.0f reads the magnet at knee angle %.0f deg"%(
    hx,hy,YZ[1]-4,YZ[1],HALL_TH))
print("  -> continuous knee reference with NO lateral cost (all at Z<=91)")
# ---- M12 pin ----
pin=cz(6.0,68.,126.).fuse(cz(9.5,126.,132.)).fuse(cz(10.,62.,68.)).removeSplitter()
assert len(pin.Solids)==1 and pin.isClosed(),"PinB"
doc.getObject("HW_PinB_10").Shape=pin; doc.getObject("HW_PinB_10").Label="HW_PinB_M12_KneePin"
print("HW_PinB M12, Z 62..132 (was M10 to 174)")
bolts=None
for y in FB:
    bb=cz(2.5,82.,98.,0.,y).fuse(cz(4.6,82.,87.,0.,y))
    bolts=bb if bolts is None else bolts.fuse(bb)
doc.getObject("HW_JointBolts").Shape=bolts.removeSplitter()
doc.recompute(); doc.save()
