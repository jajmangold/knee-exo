import bpy, os, json, math, mathutils
# KX_SRC chooses which export to build the scene from. It was hardcoded to the ANIMATION export
# directory, which meant the still-render export (221_render_export.py, which writes
# KneeExo_render/p00 and /p40) could not be fed to this script without editing it -- and editing a
# path by hand before each run is how the published stills ended up predating the geometry in them.
SRC = os.environ.get("KX_SRC", r"C:/Users/Josh/KneeExo_anim")
# --- wipe ---
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for c in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
    for b in list(c):
        try: c.remove(b)
        except Exception: pass
sc = bpy.context.scene
sc.unit_settings.system='METRIC'; sc.unit_settings.length_unit='MILLIMETERS'
# --- materials ---
def mat(name, rgba, metal, rough, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes=True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if alpha < 1.0:
        b.inputs["Alpha"].default_value = alpha
        m.blend_method = 'BLEND'
    return m
M = {
 "alu":    mat("Alu_Extrusion",(0.62,0.64,0.67,1),0.85,0.35),
 "alu_m":  mat("Alu_Machined", (0.78,0.79,0.82,1),0.90,0.22),
 "print":  mat("PETG_Printed", (0.16,0.34,0.62,1),0.00,0.55),
 "cuff":   mat("Cuff_PETG",    (0.88,0.55,0.10,1),0.00,0.60),
 "fair":   mat("PETG_Fairing", (0.13,0.30,0.58,1),0.00,0.45),
 "motor":  mat("Motor",        (0.06,0.06,0.07,1),0.55,0.35),
 "steel":  mat("Steel_Screw",  (0.72,0.73,0.76,1),0.95,0.15),
 "belt":   mat("Belt_Rubber",  (0.05,0.05,0.06,1),0.00,0.80),
 "delrin": mat("Delrin_Wheel", (0.90,0.90,0.88,1),0.00,0.40),
 "limb":   mat("Limb",         (0.85,0.72,0.64,1),0.00,0.85,0.18),
}

# TAG -> material, for the MAT__ prefix 221_render_export.py writes into every filename. The
# README has described the Blender side as keyed off that prefix for a long time; the script that
# did so was never in the repository, and what WAS here is this file's old ASSIGN table -- keyed by
# bare part name, and still listing P2b_RodClevisBlock and P4_Rod_8mm, both deleted with the rod
# linkage. Feeding it the current export failed on the first file with KeyError: 'ALUM__A7_DriveBox'.
# Prefix first, ASSIGN as the fallback for the older animation export whose names carry no tag.
TAG = {"ALU": "alu", "ALUM": "alu_m", "PETG": "print", "FAIR": "fair", "STEEL": "steel",
       "NUT": "alu_m", "BELT": "belt", "DELRIN": "delrin", "MOTOR": "motor", "LIMB": "limb",
       "MISC": "print"}
# The cuffs are the one case where the tag is not specific enough: 221 tags them PETG with the
# other printed structure, and they are the parts a reader most wants to pick out of a render.
CUFFS = ("P5_ThighCuff", "P7_ShankCuff")

# --- import ---
names=[]
missing=set()
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".stl"): continue
    n=f[:-4]
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC,f), global_scale=0.001,
                          forward_axis='Y', up_axis='Z')
    o=bpy.context.selected_objects[0] if bpy.context.selected_objects else bpy.context.object
    tag, _, part = n.partition("__")
    if part:                                   # tagged export: the prefix names the material
        key = "cuff" if part in CUFFS else TAG.get(tag)
        o.name = part
    else:                                      # untagged animation export
        key = ASSIGN.get(n)
        part = n
    if key is None:
        missing.add(tag if part != n else n)
        key = "print"                          # render it rather than abort on it
    o.data.materials.clear(); o.data.materials.append(M[key])
    bpy.ops.object.shade_smooth()
    names.append(part)
if missing:
    print("NO MATERIAL for %s -- rendered as printed PETG" % ", ".join(sorted(missing)))
print("imported:", len(names))
# --- rig empty: model +Y (proximal) -> world +Z (up) ---
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0,0,0))
rig=bpy.context.object; rig.name="RIG"; rig.rotation_euler=(math.radians(90),0,0)
for n in names:
    o=bpy.data.objects[n]; o.parent=rig; o.matrix_parent_inverse=mathutils.Matrix.Identity(4)
# --- sanity: knee axis should sit at world origin ---
o=bpy.data.objects["P1_KneeYoke"]
bb=[rig.matrix_world @ mathutils.Vector(c) for c in o.bound_box]
print("yoke bbox world Z: %.3f..%.3f m"%(min(v.z for v in bb),max(v.z for v in bb)))
print("scene ok")
