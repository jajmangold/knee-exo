import bpy, os, sys, json, math, mathutils as mu
from bpy_extras.object_utils import world_to_camera_view
ARGS = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
SRC  = ARGS[0] if ARGS else "/work"
OUT  = ARGS[1] if len(ARGS)>1 else "/work/out/KneeExo"
F0   = int(ARGS[2]) if len(ARGS)>2 else 1
F1   = int(ARGS[3]) if len(ARGS)>3 else 940
SAMP = int(ARGS[4]) if len(ARGS)>4 else 64
# ---------------- scene ----------------
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in (bpy.data.meshes,bpy.data.materials,bpy.data.lights,bpy.data.cameras):
    for b in list(c):
        try: c.remove(b)
        except Exception: pass
sc=bpy.context.scene
def mat(n,rgba,me,ro,al=1.0):
    m=bpy.data.materials.new(n); m.use_nodes=True
    b=m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value=rgba
    b.inputs["Metallic"].default_value=me
    b.inputs["Roughness"].default_value=ro
    b.inputs["Alpha"].default_value=al
    return m
M={"alu":mat("Alu",(0.62,0.64,0.67,1),0.85,0.35),
   "alu_m":mat("AluM",(0.78,0.79,0.82,1),0.90,0.22),
   "print":mat("PA6CF",(0.13,0.14,0.16,1),0.0,0.75),
   "cuff":mat("Cuff",(0.88,0.55,0.10,1),0.0,0.60),
   "motor":mat("Motor",(0.06,0.06,0.07,1),0.55,0.35),
   "steel":mat("Steel",(0.72,0.73,0.76,1),0.95,0.15),
   "limb":mat("Limb",(0.72,0.72,0.76,1),0.0,0.90,0.07)}
A={"A1_Extrusion_20x60_VSlot":"alu","A4_Shank2020_VSlot":"alu","A2_BallScrew_SFU1620":"steel",
   "A3_Motor_6374":"motor","P1_KneeYoke":"print","P6_ShankSocket":"print",
   "P5_ThighCuff":"cuff","P7_ShankCuff":"cuff","P2a_KneeHingePlate":"alu_m",
   "P2b_RodClevisBlock":"alu_m","P3_Carriage":"alu_m","P4_Rod_8mm":"alu",
   "REF_Thigh":"limb","REF_Knee":"limb","REF_Shank":"limb"}
names=[]
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".stl"): continue
    n=f[:-4]
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC,f),global_scale=0.001,
                          forward_axis='Y',up_axis='Z')
    o=bpy.context.selected_objects[0]; o.name=n
    o.data.materials.clear(); o.data.materials.append(M[A[n]])
    bpy.ops.object.shade_smooth(); names.append(n)
print("imported",len(names))
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0))
rig=bpy.context.object; rig.name="RIG"; rig.rotation_euler=(math.radians(90),0,0)
for n in names:
    o=bpy.data.objects[n]; o.parent=rig; o.matrix_parent_inverse=mu.Matrix.Identity(4)
# world / ground / lights
w=bpy.data.worlds.new("W"); sc.world=w; w.use_nodes=True
bg=w.node_tree.nodes["Background"]
bg.inputs[0].default_value=(0.045,0.05,0.06,1); bg.inputs[1].default_value=1.0
bpy.ops.mesh.primitive_plane_add(size=8,location=(0,0,-0.40))
g=bpy.context.object; g.name="Ground"
gm=mat("Ground",(0.10,0.11,0.13,1),0.0,0.45); g.data.materials.append(gm)
def area(n,loc,rot,size,en,col=(1,1,1)):
    d=bpy.data.lights.new(n,'AREA'); d.size=size; d.energy=en; d.color=col
    o=bpy.data.objects.new(n,d); sc.collection.objects.link(o)
    o.location=loc; o.rotation_euler=rot; return o
area("Key",(1.1,-1.3,1.4),(math.radians(50),0,math.radians(41)),1.6,600)
area("Fill",(-1.3,-1.0,0.35),(math.radians(80),0,math.radians(-52)),1.8,160,(0.75,0.82,1.0))
area("Rim",(-0.3,1.5,1.1),(math.radians(125),0,math.radians(190)),1.4,380,(0.9,0.95,1.0))
cd=bpy.data.cameras.new("Cam"); cd.lens=50; cd.clip_start=0.01; cd.clip_end=50
cam=bpy.data.objects.new("Cam",cd); sc.collection.objects.link(cam); sc.camera=cam
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0)); piv=bpy.context.object; piv.name="CamPivot"
bpy.ops.object.empty_add(type='PLAIN_AXES',location=(0,0,0)); tgt=bpy.context.object; tgt.name="CamTarget"
tgt.parent=piv; tgt.matrix_parent_inverse=mu.Matrix.Identity(4); tgt.location=(0,0,0)
cam.parent=piv; cam.matrix_parent_inverse=mu.Matrix.Identity(4)
tc=cam.constraints.new('TRACK_TO'); tc.target=tgt; tc.track_axis='TRACK_NEGATIVE_Z'; tc.up_axis='UP_Y'
exec(open(os.path.join(SRC,"anim_common.py")).read())
# ---------------- render ----------------
sc.render.engine='CYCLES'
sc.cycles.device='GPU'
prefs=bpy.context.preferences.addons["cycles"].preferences
prefs.compute_device_type='CUDA'; prefs.get_devices()
ngpu=0
for d in prefs.devices:
    d.use = (d.type=='CUDA')
    if d.type=='CUDA': ngpu+=1
print("CUDA devices enabled:",ngpu)
sc.cycles.samples=SAMP
sc.cycles.use_adaptive_sampling=True
sc.cycles.adaptive_threshold=0.01
sc.cycles.use_denoising=False
try: sc.cycles.denoiser='OPENIMAGEDENOISE'
except Exception: pass
sc.cycles.max_bounces=4; sc.cycles.transmission_bounces=3; sc.cycles.transparent_max_bounces=6
sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.resolution_percentage=100
sc.render.fps=30; sc.frame_start=F0; sc.frame_end=F1
sc.render.image_settings.file_format='JPEG'
sc.render.image_settings.color_mode='RGB'
sc.render.image_settings.quality=94
sc.render.threads_mode='FIXED'; sc.render.threads=4
sc.render.filepath=OUT
print("rendering %d-%d @%d samples -> %s"%(F0,F1,SAMP,OUT))
bpy.ops.render.render(animation=True)
print("DONE")
