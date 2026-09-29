import bpy, json, math, mathutils as mu
SRC=r"C:/Users/Josh/KneeExo_anim"
K=json.load(open(SRC+"/kinematics.json"))
S=K["samples"]; XE=K["XE"]; D0=K["D0"]
def samp(th):
    th=max(-2.0,min(105.0,th))
    i=min(range(len(S)), key=lambda j: abs(S[j]["theta"]-th))
    return S[i]
BASE=samp(0.0); PHI0=BASE["phi"]; CARR0=BASE["carr"]
sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=940
O=bpy.data.objects
THIGH=["A1_Extrusion_20x60_VSlot","P1_KneeYoke","P5_ThighCuff","A2_BallScrew_SFU1620","A3_Motor_6374"]
SHANK=["P2a_KneeHingePlate","A4_Shank2020_VSlot","P2b_RodClevisBlock","P6_ShankSocket","P7_ShankCuff"]
LIMB=["REF_Thigh","REF_Knee","REF_Shank"]
ALL=THIGH+SHANK+LIMB+["P3_Carriage","P4_Rod_8mm"]
# clear old animation
for n in ALL+["CamPivot","Cam"]:
    o=O.get(n)
    if o and o.animation_data: o.animation_data_clear()

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

def vis(o,frame,show):
    o.hide_render=not show; o.hide_viewport=not show
    o.keyframe_insert("hide_render",frame=frame); o.keyframe_insert("hide_viewport",frame=frame)
def const(o,paths=("hide_render","hide_viewport")):
    for fc in fcurves_of(o):
        if fc.data_path in paths:
            for kp in fc.keyframe_points: kp.interpolation='CONSTANT'
def flyin(name, off_mm, f0, f1):
    o=O[name]
    vis(o,1,False); vis(o,f0-1,False); vis(o,f0,True)
    o.location=mu.Vector(off_mm)*0.001; o.keyframe_insert("location",frame=f0)
    o.location=(0,0,0);                 o.keyframe_insert("location",frame=f1)
    const(o)
OFF={
 "A1_Extrusion_20x60_VSlot":(0,0,300), "P1_KneeYoke":(200,0,150), "P5_ThighCuff":(0,0,340),
 "A2_BallScrew_SFU1620":(0,340,0),     "A3_Motor_6374":(0,440,0),  "P3_Carriage":(0,0,270),
 "P2a_KneeHingePlate":(-210,0,160),    "A4_Shank2020_VSlot":(0,-330,180),
 "P2b_RodClevisBlock":(230,0,160),     "P6_ShankSocket":(0,-350,190),
 "P7_ShankCuff":(0,-300,290),          "P4_Rod_8mm":(290,0,200),
}
SEQ=[("A1_Extrusion_20x60_VSlot",10,46),("P1_KneeYoke",34,70),("P5_ThighCuff",58,94),
     ("A2_BallScrew_SFU1620",82,114),("A3_Motor_6374",102,134),("P3_Carriage",122,158),
     ("P2a_KneeHingePlate",280,316),("A4_Shank2020_VSlot",304,340),
     ("P2b_RodClevisBlock",328,364),("P6_ShankSocket",352,388),("P7_ShankCuff",376,412),
     ("P4_Rod_8mm",440,485)]
for n,f0,f1 in SEQ: flyin(n,OFF[n],f0,f1)
# limb appears for the motion act
for n in LIMB:
    o=O[n]; vis(o,1,False); vis(o,504,False); vis(o,505,True); const(o)
# ---- pose helpers ----
CAR=O["P3_Carriage"]; ROD=O["P4_Rod_8mm"]
def key_pose(th,frame,shank=True):
    s=samp(th)
    if shank:
        for n in SHANK+["REF_Shank"]:
            o=O[n]; o.rotation_euler=(0,0,math.radians(th)); o.keyframe_insert("rotation_euler",frame=frame)
    CAR.location=(0,(s["carr"]-CARR0)*0.001,0); CAR.keyframe_insert("location",frame=frame)
    dphi=math.radians(s["phi"]-PHI0)
    R=mu.Matrix.Rotation(dphi,2)
    d0=mu.Vector((D0[0],D0[1])); d=mu.Vector((s["Dx"],s["Dy"]))
    t=d-(R@d0)
    ROD.rotation_euler=(0,0,dphi); ROD.keyframe_insert("rotation_euler",frame=frame)
    ROD.location=(t.x*0.001,t.y*0.001,0); ROD.keyframe_insert("location",frame=frame)
# Act 2: carriage-only demo (rod not present yet)
def key_car(th,frame):
    s=samp(th); CAR.location=(0,(s["carr"]-CARR0)*0.001,0); CAR.keyframe_insert("location",frame=frame)
def smooth(a,b,u): u=max(0.0,min(1.0,u)); return a+(b-a)*(u*u*(3-2*u))
for f in range(175,266):
    u=(f-175)/90.0
    th = smooth(0,105,u*2) if u<=0.5 else smooth(105,0,(u-0.5)*2)
    key_car(th,f)
# Act 5: full motion 515-815
for f in range(515,816):
    u=(f-515)/300.0
    if u<1/3.:   th=smooth(0,105,u*3)
    elif u<2/3.: th=smooth(105,-2,(u-1/3.)*3)
    else:        th=smooth(-2,45,(u-2/3.)*3)
    key_pose(th,f)
# Act 6: orbit while holding 45 deg
piv=O["CamPivot"]
piv.rotation_euler=(0,0,0); piv.keyframe_insert("rotation_euler",frame=815)
piv.rotation_euler=(0,0,math.radians(-58)); piv.keyframe_insert("rotation_euler",frame=938)
for f in (816,938): key_pose(45.0,f)
# linear interp for the motion curves
for n in SHANK+["REF_Shank","P3_Carriage","P4_Rod_8mm"]:
    o=O[n]
    for fc in fcurves_of(o):
        if fc.data_path in ("location","rotation_euler"):
            for kp in fc.keyframe_points: kp.interpolation='LINEAR'
    const(o)
sc.frame_set(1)
print("animation built: %d frames, acts at 10/175/280/440/515/815"%sc.frame_end)
print("carriage travel %.1f mm, rod swing %.1f deg"%(samp(105)["carr"]-samp(-2)["carr"], samp(105)["phi"]-samp(-2)["phi"]))
