import bpy, sys, addon_utils
print("BLENDER", bpy.app.version_string)
print("stl_import:", hasattr(bpy.ops.wm, "stl_import"))
print("import_mesh.stl:", hasattr(bpy.ops, "import_mesh") and hasattr(bpy.ops.import_mesh,"stl"))
print("engines:", [e.bl_idname for e in bpy.types.RenderEngine.__subclasses__()][:8])
print("eevee names:", [n for n in ('BLENDER_EEVEE','BLENDER_EEVEE_NEXT','CYCLES')])
sc=bpy.context.scene
for eng in ("BLENDER_EEVEE_NEXT","BLENDER_EEVEE","CYCLES"):
    try:
        sc.render.engine=eng; print("  OK ->",eng)
    except Exception as e: print("  no",eng)
print("ffmpeg:", 'FFMPEG' in [i.identifier for i in bpy.types.Image.bl_rna.properties['file_format'].enum_items] if False else "check")
