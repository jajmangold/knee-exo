# expects in scope: bpy, math, mu, os, sc, SRC, world_to_camera_view
K=json.load(open(os.path.join(SRC,"kinematics.json")))
S=K["samples"]; XE=K["XE"]; D0=K["D0"]
def samp(th):
    th=max(-2.0,min(105.0,th))
    return min(S,key=lambda s:abs(s["theta"]-th))
BASE=samp(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
O=bpy.data.objects
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620","A3_Motor_6374"]
SHANK=["P2a_KneeHingePlate","A4_Shank2020_VSlot","P2b_RodClevisBlock","P6_ShankSocket","P7_ShankCuff"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
sc.frame_start=1; sc.frame_end=940
def fcurves_of(o):
    ad=o.animation_data
    if not ad or not ad.action: return []
    act=ad.action
    if hasattr(act,"fcurves"): return list(act.fcurves)
    out=[]; slot=getattr(ad,"action_slot",None)
    for L in act.layers:
        for st in L.strips:
            try:
                cb=st.channelbag(slot)
                if cb: out+=list(cb.fcurves)
            except Exception: pass
    return out
def const(o):
    for fc in fcurves_of(o):
        if fc.data_path in ("hide_render","hide_viewport"):
            for kp in fc.keyframe_points: kp.interpolation='CONSTANT'
def vis(o,f,show):
    o.hide_render=not show; o.hide_viewport=not show
    o.keyframe_insert("hide_render",frame=f); o.keyframe_insert("hide_viewport",frame=f)
def flyin(n,off,f0,f1):
    o=O[n]; vis(o,1,False); vis(o,f0-1,False); vis(o,f0,True)
    o.location=mu.Vector(off)*0.001; o.keyframe_insert("location",frame=f0)
    o.location=(0,0,0); o.keyframe_insert("location",frame=f1); const(o)
OFF={"A1_Extrusion_20x60_VSlot":(0,0,130),"P1_KneeYoke":(95,0,70),"P5_ThighCuff":(0,0,150),
     "A2_BallScrew_SFU1620":(0,150,0),"A3_Motor_6374":(0,190,0),"P3_Carriage":(0,0,120),
     "P2a_KneeHingePlate":(-100,0,75),"A4_Shank2020_VSlot":(0,-140,80),
     "P2b_RodClevisBlock":(110,0,75),"P6_ShankSocket":(0,-150,85),
     "P7_ShankCuff":(0,-130,130),"P4_Rod_8mm":(130,0,90)}
SEQ=[("A1_Extrusion_20x60_VSlot",10,46),("P1_KneeYoke",34,70),("P5_ThighCuff",58,94),
     ("A2_BallScrew_SFU1620",82,114),("A3_Motor_6374",102,134),("P3_Carriage",122,158),
     ("P2a_KneeHingePlate",280,316),("A4_Shank2020_VSlot",304,340),
     ("P2b_RodClevisBlock",328,364),("P6_ShankSocket",352,388),("P7_ShankCuff",376,412),
     ("P4_Rod_8mm",440,485)]
for n,a,b in SEQ: flyin(n,OFF[n],a,b)
for n in LIMB:
    o=O[n]; vis(o,1,False); vis(o,504,False); vis(o,505,True); const(o)
CAR=O["P3_Carriage"]; ROD=O["P4_Rod_8mm"]
def key_car(th,f):
    s=samp(th); CAR.location=(0,(s["carr"]-CARR0)*0.001,0); CAR.keyframe_insert("location",frame=f)
def key_pose(th,f):
    s=samp(th)
    for n in SHANK+["REF_Shank"]:
        o=O[n]; o.rotation_euler=(0,0,math.radians(th)); o.keyframe_insert("rotation_euler",frame=f)
    key_car(th,f)
    dphi=math.radians(s["phi"]-PHI0); R=mu.Matrix.Rotation(dphi,2)
    t=mu.Vector((s["Dx"],s["Dy"]))-(R@mu.Vector((D0[0],D0[1])))
    ROD.rotation_euler=(0,0,dphi); ROD.keyframe_insert("rotation_euler",frame=f)
    ROD.location=(t.x*0.001,t.y*0.001,0); ROD.keyframe_insert("location",frame=f)
def sm(a,b,u): u=max(0.0,min(1.0,u)); return a+(b-a)*(u*u*(3-2*u))
for f in range(175,266):
    u=(f-175)/90.0
    key_car(sm(0,105,u*2) if u<=0.5 else sm(105,0,(u-0.5)*2), f)
for f in range(515,816):
    u=(f-515)/300.0
    th = sm(0,105,u*3) if u<1/3. else (sm(105,-2,(u-1/3.)*3) if u<2/3. else sm(-2,45,(u-2/3.)*3))
    key_pose(th,f)
for f in (816,938): key_pose(45.0,f)
for n in SHANK+["REF_Shank","P3_Carriage","P4_Rod_8mm"]:
    for fc in fcurves_of(O[n]):
        if fc.data_path in ("location","rotation_euler"):
            for kp in fc.keyframe_points: kp.interpolation='LINEAR'
    const(O[n])
# ---------------- camera: four fitted shots ----------------
cam=O['Cam']; piv=O['CamPivot']
DIR=mu.Vector((0.62,-0.78,0.13)).normalized()
def fit(frames,margin=1.18,only=None):
    pts=[]
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground' or o.hide_render: continue
            if only and o.name not in only: continue
            pts+=[o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn=mu.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=mu.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    ctr=(mn+mx)/2; size=mx-mn
    r=max(size.x,size.y,size.z)/2*margin
    vf=2*math.atan(cam.data.sensor_height/(2*cam.data.lens))
    return ctr, r/math.tan(vf/2)
KNEE=["P1_KneeYoke","P2a_KneeHingePlate","P2b_RodClevisBlock","A4_Shank2020_VSlot",
      "P6_ShankSocket","P7_ShankCuff","P3_Carriage","P4_Rod_8mm"]
def fit(frames,margin=1.18,only=None):
    pts=[]
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground' or o.hide_render: continue
            if only and o.name not in only: continue
            pts+=[o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn=mu.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=mu.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    ctr=(mn+mx)/2; size=mx-mn
    r=max(size.x,size.y,size.z)/2*margin
    vf=2*math.atan(cam.data.sensor_height/(2*cam.data.lens))
    return ctr, r/math.tan(vf/2)
def fit_about(center,frames,margin=1.12,only=None):
    c=mu.Vector(center); r=0.0
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground' or o.hide_render: continue
            if only and o.name not in only: continue
            for bc in o.bound_box:
                r=max(r,(o.matrix_world @ mu.Vector(bc)-c).length)
    vf=2*math.atan(cam.data.sensor_height/(2*cam.data.lens))
    return c, r*margin/math.tan(vf/2)
def setcam(ctr,dist,frame):
    piv.location=ctr; piv.keyframe_insert("location",frame=frame)
    cam.location=DIR*dist; cam.keyframe_insert("location",frame=frame)
# camera GROWS with each subassembly instead of sitting at its final extent
T1=fit([46],1.30,{"A1_Extrusion_20x60_VSlot"})
T2=fit([94],1.22,{"A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff"})
T3=fit([158,220,265],1.16,set(THIGH+["P3_Carriage"]))
S1=fit([316],1.34,{"P1_KneeYoke","P2a_KneeHingePlate"})
S2=fit([364],1.24,{"P1_KneeYoke","P2a_KneeHingePlate","A4_Shank2020_VSlot","P2b_RodClevisBlock"})
S3=fit([412,430],1.16,set(SHANK+["P1_KneeYoke"]))
JN=fit(list(range(440,506,11)),1.12,set(KNEE))
WD=fit_about((0.0,-0.055,0.02),[515,575,635,695,755,815,880],1.06)
for lbl,(c,d) in (("T1",T1),("T2",T2),("T3",T3),("S1",S1),("S2",S2),("S3",S3),("join",JN),("wide",WD)):
    print("  shot %-5s dist %.2f m  z %.3f"%(lbl,d,c.z))
setcam(*T1,1);   setcam(*T1,50)
setcam(*T2,110); setcam(*T3,205); setcam(*T3,265)
setcam(*S1,300); setcam(*S2,355); setcam(*S3,420); setcam(*S3,432)
setcam(*JN,458); setcam(*JN,505)
setcam(*WD,542); setcam(*WD,940)
piv.rotation_euler=(0,0,0); piv.keyframe_insert("rotation_euler",frame=815)
piv.rotation_euler=(0,0,math.radians(-58)); piv.keyframe_insert("rotation_euler",frame=938)
sc.frame_set(1)
print("animation + camera ready")
