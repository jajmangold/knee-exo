import bpy,sys,time
sys.argv=["b","--","/work","/work/out/b_","1","1","64"]
exec(open("/work/remote_build.py").read().split("# ---------------- render ----------------")[0])
sc=bpy.context.scene
sc.render.engine="CYCLES"; sc.cycles.device="GPU"
p=bpy.context.preferences.addons["cycles"].preferences
p.compute_device_type="CUDA"; p.get_devices()
for d in p.devices: d.use=(d.type=="CUDA")
sc.cycles.use_adaptive_sampling=True; sc.cycles.use_denoising=False
sc.render.image_settings.file_format="JPEG"; sc.render.image_settings.quality=95
def go(lbl,samp,bounce,resx,thr=0.01):
    sc.cycles.samples=samp; sc.cycles.max_bounces=bounce
    sc.cycles.transmission_bounces=min(bounce,3); sc.cycles.transparent_max_bounces=4
    sc.cycles.adaptive_threshold=thr
    sc.render.resolution_x=resx; sc.render.resolution_y=int(resx*9/16)
    tot=0.0
    for f in (1,300,600):
        sc.frame_set(f); sc.render.filepath="/work/out/b_%s_%04d"%(lbl.replace(" ","_"),f)
        t=time.time(); bpy.ops.render.render(write_still=True); tot+=time.time()-t
    print("BENCH2 %-24s avg %.2f s/frame"%(lbl,tot/3.0))
go("256s_6b_1080p",256,6,1920)
go("128s_4b_1080p",128,4,1920)
go("96s_3b_1080p",96,3,1920,0.02)
go("96s_3b_720p",96,3,1280,0.02)
