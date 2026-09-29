import bpy,sys
sys.argv=["b","--","/work","/work/out/s_","1","1","64"]
exec(open("/work/remote_build.py").read().split("# ---------------- render ----------------")[0])
sc=bpy.context.scene
sc.render.engine="CYCLES"; sc.cycles.device="GPU"
p=bpy.context.preferences.addons["cycles"].preferences
p.compute_device_type="CUDA"; p.get_devices()
for d in p.devices: d.use=(d.type=="CUDA")
sc.cycles.samples=128; sc.cycles.max_bounces=4; sc.cycles.use_denoising=False
sc.cycles.use_adaptive_sampling=True
sc.render.resolution_x=1920; sc.render.resolution_y=1080
sc.render.image_settings.file_format="JPEG"; sc.render.image_settings.quality=92
for f in (40,120,205,300,355,420,470,640):
    sc.frame_set(f); sc.render.filepath="/work/out/s_%04d"%f
    bpy.ops.render.render(write_still=True)
print("SPOTS DONE")
