# -*- coding: utf-8 -*-
"""Two carriages, each on its own half of the C-Beam's 80 mm outboard face, each with
TWO Delrin sliders. They must overlap in Y (A is most distal exactly when B is most
proximal) which is why they need separate X bands.

Each belt run only ever meets its OWN carriage: run A at X=-35.65 never crosses
carriage B (X 0..40) and vice versa. That is what makes the two-carriage layout clean."""
import math, json, FreeCAD, Part
from FreeCAD import Vector as V
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cz(r,z0,z1,x=0.0,y=0.0): return Part.makeCylinder(r,z1-z0,V(x,y,z0),V(0,0,1))
def cy(r,y0,y1,x=0.0,z=0.0): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
K=json.load(open(r"C:/Users/Josh/KneeExo_anim/kin_diff.json"))
R=K["R"]; C0=K["C0"]; C1=K["C1"]; SCR_Z=K["screw"]["z"]; BZ=tuple(K["belt_z"])
BIN,BOUT=R-1.372+0.05,R+4.2
PLATE=(128.,140.); SLID_TOP=134.0; SLID_W=3.0; RAIL_TOP=128.0
NUT_R=14.0; ANC_Z=(128.,BZ[1]+8.)
SPEC=(("A",-1.,C0,-18.,(-30.,-10.),(-40.,0.),"P3_Carriage","P10a_Slider_Delrin","P10b_Slider_Delrin"),
      ("B", 1.,C1, 18.,( 10., 30.),(  0.,40.),"P3b_CarriageB","P10c_Slider_Delrin","P10d_Slider_Delrin"))
for tag,sgn,C,scx,slid,px,cname,s1,s2 in SPEC:
    Y0,Y1=C-24.,C+78.
    bxn=sgn*BIN; bxo=sgn*BOUT
    ax0,ax1=min(bxn,bxo)-3.2,max(bxn,bxo)+3.2
    ca=bx(px[0],px[1],Y0,Y1,*PLATE)                              # plate on the rail
    ca=ca.fuse(bx(min(scx-16,-0.),max(scx+16,0.),Y0+30.,Y0+92.,PLATE[0],SCR_Z+NUT_R+4.))
    ca=ca.fuse(bx(ax0,ax1,Y0,Y0+34.,*ANC_Z)).removeSplitter()     # belt anchor boss
    ca=ca.cut(cy(9.0,Y0-1,Y1+1,scx,SCR_Z))                        # screw channel
    ca=ca.cut(cy(NUT_R+0.2,C+35.,C+79.,scx,SCR_Z))                # nut seat
    for cxx in slid:
        ca=ca.cut(bx(cxx-SLID_W,cxx+SLID_W,Y0-1,Y1+1,PLATE[0],SLID_TOP))
    ca=ca.cut(bx(min(bxn,bxo),max(bxn,bxo),Y0+5.,Y0+12.,*BZ))      # belt clamp slot
    for k in range(3): ca=ca.cut(cz(2.1,ANC_Z[1]-13.,ANC_Z[1]+1,(bxn+bxo)/2,Y0+18.+k*7.))
    for k in range(4): ca=ca.cut(cz(2.1,SCR_Z+NUT_R-4.,SCR_Z+NUT_R+5.,scx-9.+6.*k,C+40.+k*9.))
    assert len(ca.Solids)==1 and ca.isClosed() and ca.isValid(),"%s solids=%d"%(cname,len(ca.Solids))
    o=doc.getObject(cname) or doc.addObject("Part::Feature",cname)
    o.Shape=ca; o.Label=cname; o.ViewObject.Visibility=True
    b=ca.BoundBox
    print("carriage %s  X %6.1f..%5.1f  Y %6.1f..%6.1f  Z %.0f..%.0f  %5.1f cm3"%(
        tag,b.XMin,b.XMax,b.YMin,b.YMax,b.ZMin,b.ZMax,ca.Volume/1000))
    print("   sliders at X %s ; nut X %+.0f ; belt run X %+.2f"%(slid,scx,sgn*R))
    for nm,cxx in ((s1,slid[0]),(s2,slid[1])):
        s=bx(cxx-2.8,cxx+2.8,Y0,Y1,RAIL_TOP-3.8,SLID_TOP)
        for y in (Y0+15.,(Y0+Y1)/2,Y1-15.): s=s.cut(cz(1.7,130.,SLID_TOP+1,cxx,y))
        assert len(s.Solids)==1 and s.isClosed(),nm
        oo=doc.getObject(nm) or doc.addObject("Part::Feature",nm)
        oo.Shape=s; oo.Label=nm; oo.ViewObject.Visibility=True
    print("   2 Delrin tongues, %.0f mm long, %.1f mm into the rail slots"%(Y1-Y0,SLID_TOP-RAIL_TOP+3.8-3.8+3.8))
for gg in doc.Objects:
    if gg.isDerivedFrom("App::DocumentObjectGroup") and gg.Name=="C_Drive":
        gg.addObjects([doc.getObject(n) for n in
            ("P3b_CarriageB","P10c_Slider_Delrin","P10d_Slider_Delrin")])
doc.recompute(); doc.save()
