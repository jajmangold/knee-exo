# -*- coding: utf-8 -*-
"""P2a becomes fork + knee hub + HTD-8M 28T pulley, all one part.

The pulley must be OUTBOARD of the rail (Z 88..108) or the belt runs would cut through
it, so the rim sits at Z 110..140. That means the rim cannot cantilever off the 6 mm
outer cheek -- the hub runs solid from Z 94 to 140 around the pin, so the belt load is
torsion/shear on a hub rather than bending on a plate."""
import math, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0)).fuse(cz(w0,z0,z1,*p0)).fuse(cz(w1,z0,z1,*p1))
TEETH=28; PITCH=8.0; PLD=1.372
R=TEETH*PITCH/(2*math.pi); OD=2*(R-PLD); FLANGE=OD/2   # rim = TOOTH OD; flanges are edge-only
IN_Z=(70.,76.); OUT_Z=(88.,94.); PIN_R=5.15
HUB_R=14.0; HUB_Z=(94.,166.)
RIM_Z=(136.,166.); RIM_IN=28.0
WEB_R=29.0; WEB_Z=(146.,154.)
BOLTS=(-90.,-110.,-125.)
print("HTD-8M %dT: pitch R %.3f, tooth OD %.2f, flange OD %.1f, belt 30 mm"%(
    TEETH,R,OD,2*FLANGE))
p =bar((0.,0.),(0.,-80.),24.,14.,*IN_Z)
p =p.fuse(bar((0.,0.),(0.,-135.),24.,14.,*OUT_Z))
p =p.fuse(bx(-10.,10.,-80.,-45.,IN_Z[0],OUT_Z[1]))
p =p.fuse(cz(HUB_R,*HUB_Z))                                     # hub around the pin
p =p.fuse(cz(FLANGE,*RIM_Z).cut(cz(RIM_IN,RIM_Z[0]-1,RIM_Z[1]+1)))   # rim annulus
p =p.fuse(cz(WEB_R,*WEB_Z)).removeSplitter()                    # web tying hub to rim
p =p.cut(cz(PIN_R,IN_Z[0]-2,HUB_Z[1]+2))                        # pin bore
for y in BOLTS: p=p.cut(cz(2.6,OUT_Z[0]-1,OUT_Z[1]+1,0.,y))
for k in range(6):                                              # lightening the web
    a=math.radians(60*k)
    p=p.cut(cz(9.0,WEB_Z[0]-1,WEB_Z[1]+1,23.*math.cos(a),23.*math.sin(a)))
assert len(p.Solids)==1 and p.isClosed() and p.isValid(),"P2a solids=%d"%len(p.Solids)
doc.getObject("P2a_KneeHingePlate").Shape=p
doc.getObject("P2a_KneeHingePlate").Label="P2a_KneeHub_Pulley28T"
b=p.BoundBox
print("P2a hub+pulley X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f  vol %.1f cm3"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,p.Volume/1000))
print("  rim Z %.0f..%.0f (clear of the rail at Z<=108); pulley OD %.1f < knee dia 104"%(
    RIM_Z[0],RIM_Z[1],2*FLANGE))
print("  -> never protrudes behind the knee when sitting")
# ---- knee pin lengthened to carry the hub ----
pin=cz(5.0,68.,168.).fuse(cz(8.0,168.,174.)).fuse(cz(8.5,62.,68.)).removeSplitter()
assert len(pin.Solids)==1 and pin.isClosed(),"PinB"
doc.getObject("HW_PinB_10").Shape=pin
print("HW_PinB_10 now Z 62..174 to carry the hub up to the raised rim")
# ---- retire the whole rod chain ----
for dead in ("P4_Rod_M8","P9a_RodEnd_SI8_Shank","P9b_RodEnd_SI8_Carriage",
             "P2b_RodClevisBlock","HW_PinD_M8_Clevis","HW_PinC_M8_Carriage"):
    if doc.getObject(dead): doc.removeObject(dead); print("retired %s"%dead)
doc.recompute(); doc.save()
