# -*- coding: utf-8 -*-
"""Replace the 20x20 rod + printed 608 housings with an M8 threaded rod and two
SI8 spherical rod ends. Built in the t=0 pose (identity placements) like 121_shank.py.

SI8 / SIQK8 nominal: bore 8, eye width B=12, eye OD 24, pivot centre to rear face 25,
M8 internal thread, 16 mm engagement."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
def _kx_doc():
    """The model, in the GUI instance or headless under freecadcmd.

    The bare next(...) this replaces raises StopIteration when no document is open, which
    surfaces from freecadcmd as the unhelpful "<unknown exception data>" -- and is why these
    older build scripts could not be re-run without the GUI at all.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace(chr(92), "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace(chr(92), "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=tuple(K["D0"])
def sm(t): return min(S,key=lambda q:abs(q["theta"]-t))
s0=sm(0.0)["carr"]
D=(D0[0],D0[1]); C=(XE,s0)
L=math.hypot(C[0]-D[0],C[1]-D[1]); u=((C[0]-D[0])/L,(C[1]-D[1])/L)

ZM=146.0                       # rod centreline / mid-plane (was bar 126..146)
EYE_R, EYE_W = 12.0, 12.0      # eye OD 24, width 12  -> Z 130..142
BORE_R  = 4.05                 # 8 mm pin
BAR_R   = 7.0                  # rod-end threaded barrel
C_LEN   = 25.0                 # pivot centre -> rear face of rod end
ENGAGE  = 16.0                 # thread engagement
ROD_R   = 4.0                  # M8 nominal
PITCH_R = 3.6                  # M8 pitch radius, so the nut fuses to the rod
NUT_R, NUT_T = 6.9, 5.0        # M8 thin/jam nut

def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cu(r,p,d,a,b):
    return Part.makeCylinder(r,b-a,V(p[0]+d[0]*a,p[1]+d[1]*a,ZM),V(d[0],d[1],0.0))

def rodend(p,d,name,label):
    s=cz(EYE_R,ZM-EYE_W/2,ZM+EYE_W/2,*p).fuse(cu(BAR_R,p,d,6.0,C_LEN)).removeSplitter()
    s=s.cut(cz(BORE_R,ZM-EYE_W/2-1,ZM+EYE_W/2+1,*p))          # spherical-bearing bore
    s=s.cut(cu(4.1,p,d,C_LEN-ENGAGE,C_LEN+1.0))               # M8 thread
    assert len(s.Solids)==1 and s.isClosed() and s.isValid(), name
    o=doc.getObject(name) or doc.addObject("Part::Feature",name)
    o.Shape=s; o.Label=label
    print("  %-26s vol %5.2f cm3  Z %.1f..%.1f"%(name,s.Volume/1000,s.Shape.BoundBox.ZMin if 0 else s.BoundBox.ZMin,s.BoundBox.ZMax))
    return o

print("rod axis L=%.2f mm, u=(%.4f,%.4f)"%(L,u[0],u[1]))
a=rodend(D,u,               "P9a_RodEnd_SI8_Shank",   "P9a_RodEnd_SI8_Shank")
b=rodend(C,(-u[0],-u[1]),   "P9b_RodEnd_SI8_Carriage","P9b_RodEnd_SI8_Carriage")

# --- M8 threaded rod + 2 jam nuts ---
start=C_LEN-ENGAGE                                  # 9 mm from each pivot centre
r=cu(ROD_R,D,u,start,L-start)
for p,d in ((D,u),(C,(-u[0],-u[1]))):
    n=cu(NUT_R,p,d,C_LEN,C_LEN+NUT_T).cut(cu(PITCH_R,p,d,C_LEN-1,C_LEN+NUT_T+1))
    r=r.fuse(n)
r=r.removeSplitter()
print("cut length of threaded rod: %.1f mm (exposed %.1f + 2x%.0f engaged)"%(L-2*start,L-2*C_LEN,ENGAGE))
assert len(r.Solids)==1 and r.isClosed() and r.isValid(),"rod solids=%d"%len(r.Solids)
ro=doc.getObject("P4_Rod_M8") or doc.addObject("Part::Feature","P4_Rod_M8")
ro.Shape=r; ro.Label="P4_Rod_M8_Threaded"
print("  %-26s vol %5.2f cm3  Z %.1f..%.1f"%("P4_Rod_M8",r.Volume/1000,r.BoundBox.ZMin,r.BoundBox.ZMax))

# --- adopt the group the old rod lived in, then retire the old parts ---
grp=None
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and any(
            m.Name=="P4_Rod_8mm" for m in gg.Group): grp=gg; break
if grp:
    grp.addObjects([a,b,ro]); print("added to group %s"%grp.Name)
for dead in ("P4_Rod_8mm","P8_RodEndHousing_PETG","P8b_RodEndHousing_Carriage"):
    if doc.getObject(dead): doc.removeObject(dead); print("removed %s"%dead)
for o in (a,b,ro): o.ViewObject.Visibility=True
doc.recompute(); doc.save()
print("rod assembly now Z %.1f..%.1f (was 126.0..146.0)"%(min(x.Shape.BoundBox.ZMin for x in (a,b,ro)),
                                                          max(x.Shape.BoundBox.ZMax for x in (a,b,ro))))
