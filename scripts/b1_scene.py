import bpy, os, json, math, mathutils
SRC = r"C:/Users/Josh/KneeExo_anim"
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
 "print":  mat("PA6CF_Printed",(0.13,0.14,0.16,1),0.00,0.75),
 "cuff":   mat("Cuff_PA6CF",   (0.88,0.55,0.10,1),0.00,0.60),
 "motor":  mat("Motor",        (0.06,0.06,0.07,1),0.55,0.35),
 "steel":  mat("Steel_Screw",  (0.72,0.73,0.76,1),0.95,0.15),
 "green":  mat("PETG_Housing", (0.15,0.55,0.35,1),0.00,0.55),
 "limb":   mat("Limb",         (0.85,0.72,0.64,1),0.00,0.85,0.18),
}
ASSIGN = {
 "A1_Extrusion_20x60_VSlot":"alu", "A4_Shank2020_VSlot":"alu",
 "A2_BallScrew_SFU1620":"steel",   "A3_Motor_6374":"motor",
 "P1_KneeYoke":"print", "P6_ShankSocket":"print",
 "P5_ThighCuff":"cuff", "P7_ShankCuff":"cuff",
 "P2a_KneeHingePlate":"alu_m", "P2b_RodClevisBlock":"alu_m",
 "P3_Carriage":"alu_m", "P4_Rod_8mm":"alu",
 "REF_Thigh":"limb","REF_Knee":"limb","REF_Shank":"limb",
}
# --- import ---
names=[]
for f in sorted(os.listdir(SRC)):
    if not f.endswith(".stl"): continue
    n=f[:-4]
    bpy.ops.wm.stl_import(filepath=os.path.join(SRC,f), global_scale=0.001,
                          forward_axis='Y', up_axis='Z')
    o=bpy.context.selected_objects[0]; o.name=n
    o.data.materials.clear(); o.data.materials.append(M[ASSIGN[n]])
    bpy.ops.object.shade_smooth()
    names.append(n)
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
