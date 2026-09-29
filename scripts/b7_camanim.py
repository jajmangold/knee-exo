import bpy, math, mathutils as mu
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; O=bpy.data.objects
cam=O['Cam']; piv=O['CamPivot']; tgt=O['CamTarget']
# target rides with the pivot so one keyframe moves both
tgt.parent=piv; tgt.matrix_parent_inverse=mu.Matrix.Identity(4); tgt.location=(0,0,0)
for n in ('Cam','CamPivot','CamTarget'):
    if O[n].animation_data: O[n].animation_data_clear()
DIR=mu.Vector((0.62,-0.76,0.22)).normalized()
def fit(frames, margin=1.18):
    """centre + distance that frames everything visible across `frames`"""
    pts=[]
    for f in frames:
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground' or o.hide_render: continue
            pts+=[o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn=mu.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=mu.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    ctr=(mn+mx)/2; size=mx-mn
    r=max(size.x,size.y,size.z)/2*margin
    vf=2*math.atan(cam.data.sensor_height/(2*cam.data.lens))
    return ctr, r/math.tan(vf/2)
SHOTS=[
 ("thigh",  [46,70,94,120,140,158,220,265], (1,265)),
 ("shank",  [316,340,364,388,412,430],      (300,430)),
 ("join",   [470,485,505],                  (455,505)),
 ("wide",   [515,575,635,695,755,815,880],  (540,940)),
]
key={}
for name,fr,(kf0,kf1) in SHOTS:
    ctr,dist=fit(fr)
    key[name]=(ctr,dist)
    print("%-6s centre (%.3f,%.3f,%.3f) dist %.2f m"%(name,ctr.x,ctr.y,ctr.z,dist))
def setcam(name,frame):
    ctr,dist=key[name]
    piv.location=ctr; piv.keyframe_insert("location",frame=frame)
    cam.location=DIR*dist; cam.keyframe_insert("location",frame=frame)
# hold each shot, then ease between
setcam("thigh",1); setcam("thigh",250)
setcam("shank",300); setcam("shank",430)
setcam("join",455);  setcam("join",505)
setcam("wide",540);  setcam("wide",940)
# orbit stays on the wide shot
piv.rotation_euler=(0,0,0); piv.keyframe_insert("rotation_euler",frame=815)
piv.rotation_euler=(0,0,math.radians(-58)); piv.keyframe_insert("rotation_euler",frame=938)
print("camera animated across 4 shots")
sc.frame_set(1)
