import bpy, math, mathutils
sc=bpy.context.scene
# --- render engine ---
eng=None
for cand in ("BLENDER_EEVEE_NEXT","BLENDER_EEVEE","CYCLES"):
    try: sc.render.engine=cand; eng=cand; break
    except Exception: pass
print("engine:",eng)
sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.fps=30
sc.render.film_transparent=False
try: sc.eevee.use_raytracing=True
except Exception: pass
# --- world ---
w=bpy.data.worlds.get("World") or bpy.data.worlds.new("World"); sc.world=w
w.use_nodes=True
bg=w.node_tree.nodes["Background"]
bg.inputs[0].default_value=(0.045,0.05,0.06,1); bg.inputs[1].default_value=1.0
# --- ground ---
bpy.ops.mesh.primitive_plane_add(size=6, location=(0,0,-0.42))
g=bpy.context.object; g.name="Ground"
gm=bpy.data.materials.new("Ground"); gm.use_nodes=True
gb=gm.node_tree.nodes["Principled BSDF"]
gb.inputs["Base Color"].default_value=(0.10,0.11,0.13,1)
gb.inputs["Roughness"].default_value=0.45
g.data.materials.append(gm)
# --- lights ---
def area(name,loc,rot,size,energy,color=(1,1,1)):
    d=bpy.data.lights.new(name,'AREA'); d.size=size; d.energy=energy; d.color=color
    o=bpy.data.objects.new(name,d); sc.collection.objects.link(o)
    o.location=loc; o.rotation_euler=rot; return o
area("Key",(1.1,-1.3,1.4),(math.radians(50),0,math.radians(41)),1.6,420)
area("Fill",(-1.3,-1.0,0.35),(math.radians(80),0,math.radians(-52)),1.8,110,(0.75,0.82,1.0))
area("Rim",(-0.3,1.5,1.1),(math.radians(125),0,math.radians(190)),1.4,260,(0.9,0.95,1.0))
# --- camera ---
cd=bpy.data.cameras.new("Cam"); cd.lens=58; cd.clip_start=0.01; cd.clip_end=50
cam=bpy.data.objects.new("Cam",cd); sc.collection.objects.link(cam); sc.camera=cam
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,-0.12,0.02))
tgt=bpy.context.object; tgt.name="CamTarget"
tc=cam.constraints.new('TRACK_TO'); tc.target=tgt; tc.track_axis='TRACK_NEGATIVE_Z'; tc.up_axis='UP_Y'
# orbit pivot so the camera can swing later
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,-0.12,0.02))
piv=bpy.context.object; piv.name="CamPivot"
cam.parent=piv; cam.matrix_parent_inverse=mathutils.Matrix.Identity(4)
cam.location=(0.72,-0.95,0.30)
# --- report extents ---
import mathutils as mu
pts=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.name=="Ground": continue
    pts += [o.matrix_world @ mu.Vector(c) for c in o.bound_box]
print("assembly world  X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f"%(
  min(p.x for p in pts),max(p.x for p in pts),min(p.y for p in pts),max(p.y for p in pts),
  min(p.z for p in pts),max(p.z for p in pts)))
print("height %.0f mm"%((max(p.z for p in pts)-min(p.z for p in pts))*1000))
print("look ok")
