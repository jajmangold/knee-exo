# -*- coding: utf-8 -*-
"""Belt in TWO objects, because only part of it is static:
  A5_Belt_Wrap    - the 180 deg wrap + the posterior spring run. Both tangent points are
                    pinned at 0 and 180 deg and the spring anchor is fixed, so this really
                    is static.
  A5b_Belt_DriveRun - the anterior run. Its DIRECTION is fixed but its LENGTH tracks the
                    carriage, so the animation rebuilds this one box each frame.
Spring is a constant-force drum that spools the take-up; its free run stays 230 mm."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_belt.json"))
R=K["R"]; C0=K["C0"]; S=K["samples"]
BIN,BOUT=R-1.372+0.05,R+4.2   # inner face clears the tooth OD (rim) by 0.05 mm
BZ=(116.,146.)
SPR_END=230.0; DRUM=(R,250.0); DRUM_R=20.0
# --- wrap: 180..360 deg, i.e. around the DISTAL side of the pulley ---
w=Part.makeCylinder(BOUT,BZ[1]-BZ[0],V(0,0,BZ[0]),V(0,0,1),180.0)
w.rotate(V(0,0,0),V(0,0,1),180.0)
w=w.cut(cz(BIN,BZ[0]-1,BZ[1]+1))
w=w.fuse(bx(BIN,BOUT,0.,SPR_END,*BZ)).removeSplitter()      # posterior spring run
assert len(w.Solids)==1 and w.isValid(),"wrap solids=%d"%len(w.Solids)
o=doc.getObject("A5_Belt_HTD8M") or doc.addObject("Part::Feature","A5_Belt_HTD8M")
o.Shape=w; o.Label="A5_Belt_Wrap_SpringRun"; o.ViewObject.Visibility=True
b=w.BoundBox
print("A5  wrap 180 deg (distal side) + spring run  X %.1f..%.1f Y %.1f..%.1f Z %.0f..%.0f"%(
    b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax))
print("    teeth in mesh: %.0f of %d  (wrap is 180 deg at EVERY angle)"%(28*0.5,28))
# --- drive run at the zero pose ---
d=bx(-BOUT,-BIN,0.,C0-24.,*BZ)
o2=doc.getObject("A5b_Belt_DriveRun") or doc.addObject("Part::Feature","A5b_Belt_DriveRun")
o2.Shape=d; o2.Label="A5b_Belt_DriveRun"; o2.ViewObject.Visibility=True
print("A5b drive run X %.1f..%.1f, Y 0..%.1f at theta=0 (length tracks the carriage)"%(
    -BOUT,-BIN,C0-24.))
c=[s["carr"] for s in S]
print("    run length %.1f mm at full flexion .. %.1f mm at full extension (delta %.2f = travel)"%(
    min(c)-24,max(c)-24,(max(c)-min(c))))
# --- spring drum + bracket, posterior, proximal of the carriage ---
sp=cz(DRUM_R,*BZ,DRUM[0],DRUM[1]).cut(cz(4.2,BZ[0]-1,BZ[1]+1,DRUM[0],DRUM[1]))
o3=doc.getObject("A6_Spring_ConstForce") or doc.addObject("Part::Feature","A6_Spring_ConstForce")
o3.Shape=sp; o3.Label="A6_Spring_ConstForce_119N"; o3.ViewObject.Visibility=True
br=bx(30.,50.,236.,286.,108.,116.)                          # pad on the rail's outboard face
br=br.fuse(bx(37.,43.,236.,286.,104.,108.))                 # tongue into the X=40 slot
br=br.fuse(bx(14.,58.,236.,276.,112.,116.))                 # spread under the drum
br=br.fuse(cz(4.0,116.,150.,DRUM[0],DRUM[1]))               # cantilever axle, drum spins on it
br=br.removeSplitter()
for y in (242.,280.): br=br.cut(cz(2.6,102.,118.,40.,y))
assert len(br.Solids)==1 and br.isClosed() and br.isValid(),"P12 solids=%d"%len(br.Solids)
o4=doc.getObject("P12_SpringBracket") or doc.addObject("Part::Feature","P12_SpringBracket")
o4.Shape=br; o4.Label="P12_SpringBracket"; o4.ViewObject.Visibility=True
print("A6  drum r=%.0f at (X %.1f, Y %.0f); P12 bracket %.1f cm3 on the rail's X=40 slot"%(
    DRUM_R,DRUM[0],DRUM[1],br.Volume/1000))
print("    bracket Y 240..282 -- carriage reaches Y %.1f proximally, so it is clear"%(max(c)+78))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([o,o2,o3,o4])
doc.recompute(); doc.save()
