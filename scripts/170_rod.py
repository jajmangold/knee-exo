# -*- coding: utf-8 -*-
"""Rod and both SI8 rod ends, now SKEWED: shank pivot at Z=130, carriage pivot at Z=148.
Each eye still turns on a Z pin; only the barrel and rod tilt 6.72 deg out of the XY
plane, which is a CONSTANT misalignment well inside the rod end's +/-13 deg."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
ZM_S,ZM_C=130.0,148.0
D=(D0[0],D0[1],ZM_S); C=(XE,s0,ZM_C)
vec=(C[0]-D[0],C[1]-D[1],C[2]-D[2]); L3=math.sqrt(sum(q*q for q in vec))
u=tuple(q/L3 for q in vec)
EYE_R,EYE_W=12.0,12.0; BORE_R=4.05; BAR_R=7.0; C_LEN=25.0; ENGAGE=16.0
ROD_R=4.0; PITCH_R=3.6; NUT_R,NUT_T=6.9,5.0
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cu(r,p,d,a,b):
    return Part.makeCylinder(r,b-a,V(p[0]+d[0]*a,p[1]+d[1]*a,p[2]+d[2]*a),V(*d))
print("rod 3D length %.2f mm, direction (%.4f, %.4f, %.4f), skew %.2f deg"%(
    L3,u[0],u[1],u[2],math.degrees(math.asin(abs(u[2])))))
def rodend(p,d,name,label):
    s=cz(EYE_R,p[2]-EYE_W/2,p[2]+EYE_W/2,p[0],p[1]).fuse(cu(BAR_R,p,d,6.0,C_LEN)).removeSplitter()
    s=s.cut(cz(BORE_R,p[2]-EYE_W/2-1,p[2]+EYE_W/2+1,p[0],p[1]))
    s=s.cut(cu(4.1,p,d,C_LEN-ENGAGE,C_LEN+1.0))
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(),name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=label; o.ViewObject.Visibility=True
    b=s.BoundBox
    print("  %-26s vol %5.2f cm3  Z %.1f..%.1f  (eye %.1f..%.1f)"%(
        name,s.Volume/1000,b.ZMin,b.ZMax,p[2]-EYE_W/2,p[2]+EYE_W/2))
    return o
a=rodend(D,u,"P9a_RodEnd_SI8_Shank","P9a_RodEnd_SI8_Shank")
b=rodend(C,tuple(-q for q in u),"P9b_RodEnd_SI8_Carriage","P9b_RodEnd_SI8_Carriage")
start=C_LEN-ENGAGE
r=cu(ROD_R,D,u,start,L3-start)
for p,d in ((D,u),(C,tuple(-q for q in u))):
    n=cu(NUT_R,p,d,C_LEN,C_LEN+NUT_T).cut(cu(PITCH_R,p,d,C_LEN-1,C_LEN+NUT_T+1))
    r=r.fuse(n)
r=r.removeSplitter()
assert len(r.Solids)==1 and r.isClosed() and r.isValid(),"rod solids=%d"%len(r.Solids)
ro=doc.getObject("P4_Rod_M8") or doc.addObject("Part::Feature","P4_Rod_M8")
ro.Shape=r; ro.Label="P4_Rod_M8_Threaded"; ro.ViewObject.Visibility=True
bb=r.BoundBox
print("  %-26s vol %5.2f cm3  Z %.1f..%.1f   cut length %.1f mm (was 134.7)"%(
    "P4_Rod_M8",r.Volume/1000,bb.ZMin,bb.ZMax,L3-2*start))
doc.recompute(); doc.save()
