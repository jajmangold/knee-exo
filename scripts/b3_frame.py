import bpy, math, mathutils as mu, time
sc=bpy.context.scene
def bbox(names=None):
    pts=[]
    for o in bpy.data.objects:
        if o.type!='MESH' or o.name=='Ground': continue
        if names and o.name not in names: continue
        if o.hide_render: continue
        pts+=[o.matrix_world @ mu.Vector(c) for c in o.bound_box]
    mn=mu.Vector((min(p.x for p in pts),min(p.y for p in pts),min(p.z for p in pts)))
    mx=mu.Vector((max(p.x for p in pts),max(p.y for p in pts),max(p.z for p in pts)))
    return mn,mx,(mn+mx)/2
def frame_cam(dir_vec, margin=1.22, names=None):
    mn,mx,ctr=bbox(names)
    cam=bpy.data.objects['Cam']; d=cam.data
    size=(mx-mn); radius=max(size.x,size.y,size.z)/2*margin
    vfov=2*math.atan(d.sensor_height/(2*d.lens))
    hfov=2*math.atan(d.sensor_width/(2*d.lens))
    fov=min(vfov,hfov*sc.render.resolution_y/sc.render.resolution_x) if False else vfov
    dist=radius/math.tan(fov/2)
    v=mu.Vector(dir_vec).normalized()
    for n in ('CamTarget','CamPivot'): bpy.data.objects[n].location=ctr
    cam.location=v*dist
    return ctr,dist,radius
ctr,dist,rad=frame_cam((0.62,-0.76,0.20))
print("centre (%.3f,%.3f,%.3f) dist %.2f m radius %.3f"%(ctr.x,ctr.y,ctr.z,dist,rad))
mn,mx,_=bbox(); print("assembly %.0f x %.0f x %.0f mm"%((mx.x-mn.x)*1000,(mx.y-mn.y)*1000,(mx.z-mn.z)*1000))
# ground just under the lowest point
bpy.data.objects['Ground'].location=(0,0,mn.z-0.015)
# limb recedes
b=bpy.data.materials['Limb'].node_tree.nodes['Principled BSDF']
b.inputs['Alpha'].default_value=0.06
sc.render.resolution_percentage=50
sc.render.filepath=r'C:/Users/Josh/KneeExo_anim/test_frame.png'
t=time.time(); bpy.ops.render.render(write_still=True); print('%.1f s'%(time.time()-t))
