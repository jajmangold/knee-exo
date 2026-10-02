# -*- coding: utf-8 -*-
"""SUPERSEDED by b7_anim.py, which frames its camera once on the widest pose. Kept for the camera
direction it records -- (0.62, -0.76, 0.22) -- which with b3_frame's and anim_common's is the only
viewpoint this project ever wrote down.
"""
import bpy, math, mathutils as mu, time
sc=bpy.context.scene
def swept_bbox(frames):
    pts=[]
    for f in frames:
        sc.frame_set(f)
        bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground': continue
            if o.hide_render: continue
            pts+=[o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn=mu.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=mu.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx,(mn+mx)/2
# sample across assembly + full motion + orbit hold
mn,mx,ctr=swept_bbox([150,300,470,515,575,635,695,755,815,880])
size=mx-mn
print("swept volume %.0f x %.0f x %.0f mm  centre (%.3f,%.3f,%.3f)"
      %(size.x*1000,size.y*1000,size.z*1000,ctr.x,ctr.y,ctr.z))
cam=bpy.data.objects['Cam']; d=cam.data
radius=max(size.x,size.y,size.z)/2*1.20
vfov=2*math.atan(d.sensor_height/(2*d.lens))
dist=radius/math.tan(vfov/2)
v=mu.Vector((0.62,-0.76,0.22)).normalized()
for n in ('CamTarget','CamPivot'): bpy.data.objects[n].location=ctr
cam.location=v*dist
print("camera dist %.2f m, lens %.0f mm"%(dist,d.lens))
bpy.data.objects['Ground'].location=(0,0,mn.z-0.02)
sc.render.resolution_percentage=45
for f in (150,470,600,700,880):
    sc.frame_set(f); sc.render.filepath=r'C:/Users/Josh/KneeExo_anim/chk_%04d.png'%f
    bpy.ops.render.render(write_still=True)
print("reframed")
