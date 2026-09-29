import bpy, math, mathutils as mu
from bpy_extras.object_utils import world_to_camera_view
sc=bpy.context.scene; cam=bpy.data.objects['Cam']
FR=[150,300,470,515,575,635,695,755,815,880]
def ndc_bounds():
    xs=[];ys=[]
    for f in FR:
        sc.frame_set(f); bpy.context.view_layer.update()
        for o in bpy.data.objects:
            if o.type!='MESH' or o.name=='Ground' or o.hide_render: continue
            for c in o.bound_box:
                p=world_to_camera_view(sc,cam,o.matrix_world @ mu.Vector(c))
                xs.append(p.x); ys.append(p.y)
    return min(xs),max(xs),min(ys),max(ys)
for it in range(6):
    x0,x1,y0,y1=ndc_bounds()
    over=max(0.5-x0,x1-0.5,0.5-y0,y1-0.5)/0.5     # 1.0 = exactly fills
    print("iter %d  ndc x %.2f..%.2f  y %.2f..%.2f  fill %.2f"%(it,x0,x1,y0,y1,over))
    if 0.80 <= over <= 0.94: break
    d=cam.location.length; cam.location = cam.location.normalized()*(d*over/0.88)
    # recentre pivot on the projected middle
    bpy.context.view_layer.update()
print("final cam dist %.2f m"%cam.location.length)
sc.render.resolution_percentage=45
for f in (150,470,600,700,880):
    sc.frame_set(f); sc.render.filepath=r'C:/Users/Josh/KneeExo_anim/chk_%04d.png'%f
    bpy.ops.render.render(write_still=True)
print("fitted")
