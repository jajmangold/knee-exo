# -*- coding: utf-8 -*-
"""The linkage never needed moving. Flip ONLY the motor + belt cover to the anterior side.
Solve for the anterior offset that clears the thigh cuff (outer R 88)."""
import math, FreeCAD
if "KneeExo_v2" in FreeCAD.listDocuments(): FreeCAD.closeDocument("KneeExo_v2")
doc = FreeCAD.getDocument("KneeExo_v1"); globals()['doc']=doc
FreeCAD.setActiveDocument("KneeExo_v1")
A = pinA()
print("solving motor anterior offset (motor r=31.5 at Z=%.0f, must clear cuff R=88):" % Z_PLANE)
best=None
for off in (62.0, 70.0, 80.0, 85.0, 90.0, 95.0):
    cx = A[0] - off                      # motor axis X near pin A
    d  = math.hypot(cx, Z_PLANE) - 31.5  # closest approach to limb axis
    ok = d >= 89.0
    print("   offset %5.1f -> axis X=%7.1f, clears limb axis by %6.1f mm  %s"
          % (off, cx, d, "OK" if ok else "hits cuff"))
    if ok and best is None: best = off
MOT_OFF = -best
print("   adopt anterior offset %.0f mm\n" % best)
DR2 = dict(tube_len=190.0, tang=35.0, blk=(20.0,56.0))
L_RET, L_EXT = ab(ROM[1]), ab(ROM[0])
THREAD = (L_RET-DR2['tube_len']-2.0, L_EXT-DR2['tube_len']+50.0+1.0)
def _plc(th):
    B=pinB(th); L=ab(th); ux,uy=(B[0]-A[0])/L,(B[1]-A[1])/L
    return FreeCAD.Placement(V(A[0],A[1],0.0),
           FreeCAD.Rotation(V(0,0,1),math.degrees(math.atan2(-ux,uy)))), L
def build_drive(th):
    plc,L=_plc(th); p=L-DR2['tube_len']
    def cyl(r,y0,y1,x=0.0,z=None): return Part.makeCylinder(r,y1-y0,V(x,y0,z or Z_PLANE),V(0,1,0))
    d = cz(11.0,101.0,115.0).fuse(cyl(7.5,8.0,DR2['blk'][0]+2.0)).fuse(cyl(20.0,*DR2['blk']))
    d = d.fuse(bx(-20.0, 88.0, DR2['blk'][0]+6.0, DR2['blk'][1], 94.0, 122.0))   # cover FLIPPED
    d = d.fuse(cyl(10.0,*THREAD)).fuse(cyl(23.0,p,p+55.0))
    d = d.fuse(cyl(13.0,p+55.0,L-DR2['tang']))
    d = d.fuse(bx(-8.0,8.0,L-DR2['tang'],L,101.0,115.0)).fuse(cz(11.0,101.0,115.0,0.0,L))
    m = cyl(31.5, DR2['blk'][0], DR2['blk'][0]+74.0, x=MOT_OFF)                  # motor FLIPPED
    d.Placement=plc; m.Placement=plc; return d,m,L
globals()['build_drive']=build_drive
def pose(t):
    r=FreeCAD.Rotation(V(0,0,1),t)
    for o in SHANK_OBJS: o.Placement=FreeCAD.Placement(V(0,0,0),r,V(0,0,0))
    d,m,_=build_drive(t)
    doc.getObject("P7_Actuator_ENVELOPE").Shape=d
    doc.getObject("P8_Motor_6374").Shape=m
    doc.getObject("P9_GasSpring").Shape=build_gas(t)
    doc.recompute()
globals()['pose']=pose
O=lambda n: doc.getObject(n)
print("=== SEATED (knee 90 deg): anything posterior of the thigh line X=+78? ===")
pose(90.0)
worst=-999
for n in ("P8_Motor_6374","P7_Actuator_ENVELOPE","P9_GasSpring","P1_ThighUpright_Lower",
          "P2_ThighUpright_Upper","P3_ThighCuff","P4_ShankLink_Horn"):
    xm=O(n).Shape.BoundBox.XMax; worst=max(worst,xm)
    flag = "CRUSHED %.0f mm proud"%(xm-78) if xm>78 else "clear"
    print("   %-26s XMax %6.1f   %s" % (n, xm, flag))
print("   worst %.1f  -> %s" % (worst, "SEAT CLEAR (cuff shell only)" if worst<=88.1 else "STILL BLOCKED"))
doc.recompute()
