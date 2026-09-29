# -*- coding: utf-8 -*-
"""Belt, constant-force spring and its bracket.

The belt's SHAPE is static in space: both runs are tangent lines from fixed anchors to
a circle centred on the knee axis, so they never move. Only the drive run's LENGTH
changes as the screw moves the carriage. I model the corridor up to the carriage's most
distal reach (Y=61.3); the remaining span is inside the anchor boss."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def bar(p0,p1,w0,w1,z0,z1):
    dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L=math.hypot(dx,dy)
    ux,uy=dx/L,dy/L; nx,ny=-uy,ux
    pts=[(p0[0]+nx*w0,p0[1]+ny*w0),(p1[0]+nx*w1,p1[1]+ny*w1),
         (p1[0]-nx*w1,p1[1]-ny*w1),(p0[0]-nx*w0,p0[1]-ny*w0)]
    w=Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    return Part.Face(w).extrude(V(0,0,z1-z0))
def sector(r_out,a0,a1,z0,z1,r_in):
    q=Part.makeCylinder(r_out,z1-z0,V(0,0,z0),V(0,0,1),(a1-a0)%360 or 360)
    q.rotate(V(0,0,0),V(0,0,1),a0)
    return q.cut(cz(r_in,z0-1,z1+1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
R=K["R"]-1.372            # belt inner surface rides the tooth OD, not the pitch line
S=K["samples"]; BZ=(116.,146.); TH=2.8
RB=R+TH                   # the belt CENTRELINE wraps here, so tangents come off this circle
carr=[s["carr"] for s in S]
DRIVE=(60.,min(carr)-24.-3.)         # the run end-cap is square to the RUN, not to Y,
                                     # so stop 3 mm short of the carriage face
SPRING=(-30.,200.)
def tangent(P,sign):
    d=math.hypot(*P); b=math.degrees(math.acos(RB/d)); a=math.degrees(math.atan2(P[1],P[0]))
    t=a+sign*b
    return (RB*math.cos(math.radians(t)),RB*math.sin(math.radians(t))), t, math.sqrt(d*d-RB*RB)
TA,angA,lenA=tangent(DRIVE,-1)
TB,angB,lenB=tangent(SPRING,+1)
wrap=(angA+360.0-angB)%360.0
print("pulley R %.3f; drive tangent at %.2f deg, spring tangent at %.2f deg -> wrap %.1f deg"%(
    R,angA,angB,wrap))
print("  free spans: drive %.1f mm, spring %.1f mm (both constant with knee angle)"%(lenA,lenB))
belt=sector(R+2*TH,angB,angA+360.0,*BZ,r_in=R)
belt=belt.fuse(bar(TA,DRIVE,TH,TH,*BZ))
belt=belt.fuse(bar(TB,SPRING,TH,TH,*BZ)).removeSplitter()
o=doc.getObject("A5_Belt_HTD8M") or doc.addObject("Part::Feature","A5_Belt_HTD8M")
o.Shape=belt; o.Label="A5_Belt_HTD8M_30mm"; o.ViewObject.Visibility=True
b=belt.BoundBox
print("A5 belt  X %.1f..%.1f  Y %.1f..%.1f  Z %.1f..%.1f"%(b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
# ---- constant-force spring + bracket ----
sp=cy(12.,200.,268.,SPRING[0],131.)
o2=doc.getObject("A6_Spring_ConstForce") or doc.addObject("Part::Feature","A6_Spring_ConstForce")
o2.Shape=sp; o2.Label="A6_Spring_ConstForce_119N"; o2.ViewObject.Visibility=True
br=bx(2.,10.,258.,292.,88.,108.)                      # pad on the rail's anterior face
br=br.fuse(bx(-42.,10.,266.,284.,98.,146.)).removeSplitter()   # overlap the pad in Z
br=br.cut(cy(12.5,265.,285.,SPRING[0],131.))
for y in (264.,286.):
    br=br.cut(Part.makeCylinder(2.6,14.,V(-2.,y,98.),V(1,0,0)))
assert len(br.Solids)==1 and br.isClosed() and br.isValid(),"P12 solids=%d"%len(br.Solids)
o3=doc.getObject("P12_SpringBracket") or doc.addObject("Part::Feature","P12_SpringBracket")
o3.Shape=br; o3.Label="P12_SpringBracket"; o3.ViewObject.Visibility=True
print("A6 spring r=12 at X %.0f Z 131, Y 200..268; P12 bracket %.1f cm3 on the rail's anterior face"%(
    SPRING[0],br.Volume/1000))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([o,o2,o3])
doc.recompute(); doc.save()
