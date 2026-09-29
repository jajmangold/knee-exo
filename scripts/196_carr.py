# -*- coding: utf-8 -*-
"""Two carriages, each with an L-GIB: one Delrin tongue in the rail's outboard slot and
one in its side slot. Perpendicular faces, so X, Z, roll, pitch and yaw are all
constrained -- more than the two parallel tongues the C-Beam gave.

Carriage B carries the SPRUNG belt anchor (3 mm travel, ~500 N/mm) that holds pretension
through belt bedding-in, with a Hall sensor reading its deflection = live belt tension."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cx(r,x0,x1,y=0.0,z=0.0): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def rng(a,b): return (min(a,b),max(a,b))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_low.json"))
R=K["R"]; C0=K["C0"]; C1=K["C1"]; BIN,BOUT=K["belt_x"]; BZ=tuple(K["belt_z"])
SCR_Z=K["screw"]["z"]; NUT_R=14.0
PLATE=(108.,118.); OT_Z=(108.,114.); ST_Z=(95.,101.); BODY_Z=(90.,124.)
ANC_Z=(92.,130.); NUT_Y=(36.,78.)
SPEC=(("A",-1.,C0,"P3_Carriage","P10a_Slider_Delrin","P10b_Slider_Delrin",False),
      ("B", 1.,C1,"P3b_CarriageB","P10c_Slider_Delrin","P10d_Slider_Delrin",True))
for tag,g,C,cname,s1,s2,sprung in SPEC:
    Y0,Y1=C-24.,C+78.; SCX=g*58.
    ax=rng(g*(BIN-2.5),g*(BOUT+2.5))
    ca=bx(*rng(g*34.,g*17.),Y0,Y1,*PLATE)                       # over-rail plate
    ca=ca.fuse(bx(*rng(g*74.,g*34.),Y0,Y1,*BODY_Z))              # outboard body
    ca=ca.fuse(bx(ax[0],ax[1],Y0,Y0+38.,*ANC_Z)).removeSplitter() # belt anchor boss
    ca=ca.cut(cy(9.0,Y0-1,Y1+1,SCX,SCR_Z))                       # screw channel
    ca=ca.cut(cy(NUT_R+0.2,C+NUT_Y[0]-1.,C+NUT_Y[1]+1.,SCX,SCR_Z))
    ca=ca.cut(bx(*rng(g*23.,g*17.),Y0-1,Y1+1,*OT_Z))             # outboard tongue pocket
    ca=ca.cut(bx(*rng(g*34.,g*30.),Y0-1,Y1+1,*ST_Z))             # side tongue pocket
    ca=ca.cut(bx(*rng(g*30.,g*17.),Y0-1,Y1+1,PLATE[0]-22.,PLATE[0]))   # clear the rail
    ca=ca.cut(bx(*rng(g*30.,g*(-30.)),Y0-1,Y1+1,86.,PLATE[0]))
    if sprung:
        ca=ca.cut(bx(*rng(g*(BIN-2.),g*(BOUT+2.)),Y0-1.,Y0+34.,94.,128.))  # slide pocket
        ca=ca.cut(cy(5.5,Y0+30.,Y0+40.,g*(BIN+BOUT)/2,(BZ[0]+BZ[1])/2))    # spring bore
        ca=ca.cut(bx(*rng(g*(BOUT+2.),g*(BOUT+8.)),Y0+6.,Y0+22.,104.,116.))# Hall pocket
    else:
        ca=ca.cut(bx(*rng(g*BIN,g*BOUT),Y0+6.,Y0+13.,*BZ))       # rigid belt clamp slot
        for k in range(3): ca=ca.cut(cz(2.1,ANC_Z[1]-13.,ANC_Z[1]+1,g*(BIN+BOUT)/2,Y0+20.+k*7.))
    for k in range(4): ca=ca.cut(cz(2.1,SCR_Z+NUT_R-4.,SCR_Z+NUT_R+5.,SCX-9.+6.*k,C+42.+k*9.))
    ca=ca.cut(cz(3.1,ST_Z[1]-0.5,ST_Z[1]+3.5,g*32.,Y0+50.))      # endstop magnet pocket
    assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"%s solids=%d"%(cname,len(ca.Solids))
    o=doc.getObject(cname) or doc.addObject("Part::Feature",cname)
    o.Shape=ca; o.Label=cname; o.ViewObject.Visibility=True
    b=ca.BoundBox
    print("carriage %s X %6.1f..%6.1f Y %6.1f..%6.1f Z %.0f..%.0f  %5.1f cm3  %s"%(
        tag,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000,
        "SPRUNG anchor" if sprung else "rigid anchor"))
    # L-gib tongues
    for nm,xr,zr in ((s1,rng(g*23.,g*17.),(104.,OT_Z[1])),(s2,rng(g*34.,g*26.),ST_Z)):
        if nm==s1: s=bx(xr[0],xr[1],Y0,Y1,zr[0],zr[1])
        else:      s=bx(xr[0],xr[1],Y0,Y1,zr[0]+0.2,zr[1]-0.2)
        for y in (Y0+15.,(Y0+Y1)/2,Y1-15.):
            s=s.cut(cz(1.7,zr[0]-1,zr[1]+1,(xr[0]+xr[1])/2,y) if nm==s1
                    else cx(1.7,xr[0]-1,xr[1]+1,y,(zr[0]+zr[1])/2))
        assert len(s.Solids)==1 and s.isClosed(),nm
        oo=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
        oo.Shape=s; oo.Label=nm; oo.ViewObject.Visibility=True
    print("   outboard tongue X %.0f..%.0f (slot at X %+.0f) + side tongue Z %.0f..%.0f (side slot)"%(
        rng(g*23.,g*17.)[0],rng(g*23.,g*17.)[1],g*20.,ST_Z[0],ST_Z[1]))
# ---- sprung anchor block, spring, Hall board (carriage B) ----
Y0=C1-24.; g=1.
blk=bx(*rng(g*(BIN-1.5),g*(BOUT+1.5)),Y0,Y0+32.,95.,127.)
blk=blk.cut(bx(*rng(g*BIN,g*BOUT),Y0+5.,Y0+12.,*BZ))
for k in range(3): blk=blk.cut(cz(2.1,114.,128.,g*(BIN+BOUT)/2,Y0+18.+k*6.))
assert len(blk.Solids)==1 and blk.isClosed(),"P11"
o=doc.getObject("P11_SprungAnchor") or doc.addObject("Part::Feature","P11_SprungAnchor")
o.Shape=blk; o.Label="P11_SprungAnchor"; o.ViewObject.Visibility=True
sp=cy(5.0,Y0+32.,Y0+39.,g*(BIN+BOUT)/2,(BZ[0]+BZ[1])/2)
o2=doc.getObject("A8_TensionSpring") or doc.addObject("Part::Feature","A8_TensionSpring")
o2.Shape=sp; o2.Label="A8_TensionSpring_500Nmm"; o2.ViewObject.Visibility=True
hb=bx(*rng(g*(BOUT+2.5),g*(BOUT+7.5)),Y0+7.,Y0+21.,105.,115.)
o3=doc.getObject("P13_HallTension") or doc.addObject("Part::Feature","P13_HallTension")
o3.Shape=hb; o3.Label="P13_HallTension"; o3.ViewObject.Visibility=True
print("P11 sprung block Y %.1f..%.1f, 3 mm travel; A8 spring 500 N/mm; P13 Hall reads deflection")
print("   3 mm of take-up absorbs %.2f mm of belt bedding-in (worst case ~1.8 mm)"%3.0)
print("   lost motion at full load %.2f mm = %.2f deg of knee"%(791./500.,math.degrees(791./500./R)))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([o,o2,o3])
doc.recompute(); doc.save()
