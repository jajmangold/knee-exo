# -*- coding: utf-8 -*-
"""Headless Cycles render of the knee orthosis, v2.

Fixes over v1: rig stood upright (limb axis Y -> world Z), exposure cut ~5x so the blue
reads deep instead of washed out, and both a clad and an open variant so the black
extrusion and the mechanism are actually visible.

argv after "--":  STL_DIR  OUT_DIR  SAMPLES  [W H]
"""
import bpy, sys, os, math, glob
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, SAMPLES = argv[0], argv[1], int(argv[2])
W, H = (int(argv[3]), int(argv[4])) if len(argv) > 4 else (1500, 2000)
THETA = math.radians(float(argv[5])) if len(argv) > 5 else math.radians(40.0)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'GPU'
sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = True
sc.cycles.max_bounces = 12
sc.cycles.transmission_bounces = 8
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.image_settings.file_format = 'PNG'
sc.view_settings.view_transform = 'AgX'
try:
    sc.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass

cp = bpy.context.preferences.addons['cycles'].preferences
cp.compute_device_type = 'CUDA'
cp.get_devices()
ngpu = sum(1 for d in cp.devices if d.type == 'CUDA')
for d in cp.devices:
    d.use = (d.type == 'CUDA')
print("CUDA devices enabled: %d" % ngpu)


def newmat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL':
            nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (-300, 0)
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m, nt, bsdf


def S(b, k, v):
    if k in b.inputs:
        b.inputs[k].default_value = v


def noise_rough(nt, bsdf, scale, lo, hi):
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.location = (-900, -200)
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 6.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.location = (-620, -200)
    ramp.color_ramp.elements[0].color = (lo, lo, lo, 1)
    ramp.color_ramp.elements[1].color = (hi, hi, hi, 1)
    nt.links.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Roughness'])


def bump(nt, bsdf, scale, strength):
    tex = nt.nodes.new('ShaderNodeTexNoise')
    tex.location = (-900, -520)
    tex.inputs['Scale'].default_value = scale
    tex.inputs['Detail'].default_value = 8.0
    bmp = nt.nodes.new('ShaderNodeBump')
    bmp.location = (-620, -520)
    bmp.inputs['Strength'].default_value = strength
    nt.links.new(tex.outputs['Fac'], bmp.inputs['Height'])
    nt.links.new(bmp.outputs['Normal'], bsdf.inputs['Normal'])


MATS = {}

# black anodised extrusion
m, nt, b = newmat('ALU')
S(b, 'Base Color', (0.018, 0.019, 0.022, 1))
S(b, 'Metallic', 1.0)
S(b, 'Roughness', 0.33)
S(b, 'Anisotropic', 0.5)
noise_rough(nt, b, 260.0, 0.25, 0.42)
bump(nt, b, 700.0, 0.06)
MATS['ALU'] = m

# blue PETG, printed structure. deep saturated blue: AgX desaturates highlights hard
m, nt, b = newmat('PETG')
S(b, 'Base Color', (0.010, 0.040, 0.215, 1))
S(b, 'Roughness', 0.30)
S(b, 'IOR', 1.57)
S(b, 'Coat Weight', 0.45)
S(b, 'Coat Roughness', 0.14)
S(b, 'Subsurface Weight', 0.09)
S(b, 'Subsurface Radius', (1.0, 1.8, 4.2))
noise_rough(nt, b, 150.0, 0.22, 0.38)
bump(nt, b, 480.0, 0.14)
MATS['PETG'] = m

# blue PETG fairings, finished smoother
m, nt, b = newmat('FAIR')
S(b, 'Base Color', (0.014, 0.052, 0.245, 1))
S(b, 'Roughness', 0.22)
S(b, 'IOR', 1.57)
S(b, 'Coat Weight', 0.70)
S(b, 'Coat Roughness', 0.11)
S(b, 'Subsurface Weight', 0.08)
S(b, 'Subsurface Radius', (1.0, 1.8, 4.2))
noise_rough(nt, b, 90.0, 0.17, 0.27)
bump(nt, b, 300.0, 0.05)
MATS['FAIR'] = m

# bought aluminium: the V-wheel gantry plate and the drive bracket. Deliberately NOT the
# same material as the extrusion -- that is black anodised, these are machined 6061, and
# the renders should show at a glance which parts are bought metal rather than printed.
m, nt, b = newmat('ALUM')
S(b, 'Base Color', (0.42, 0.435, 0.45, 1))
S(b, 'Metallic', 1.0)
S(b, 'Roughness', 0.38)
S(b, 'Anisotropic', 0.35)
noise_rough(nt, b, 320.0, 0.14, 0.44)
bump(nt, b, 900.0, 0.04)
MATS['ALUM'] = m

m, nt, b = newmat('STEEL')
S(b, 'Base Color', (0.58, 0.60, 0.63, 1))
S(b, 'Metallic', 1.0)
S(b, 'Roughness', 0.17)
noise_rough(nt, b, 400.0, 0.11, 0.27)
MATS['STEEL'] = m

m, nt, b = newmat('NUT')
S(b, 'Base Color', (0.34, 0.35, 0.375, 1))
S(b, 'Metallic', 1.0)
S(b, 'Roughness', 0.31)
noise_rough(nt, b, 320.0, 0.23, 0.43)
MATS['NUT'] = m

m, nt, b = newmat('BELT')
S(b, 'Base Color', (0.013, 0.013, 0.015, 1))
S(b, 'Roughness', 0.74)
S(b, 'Sheen Weight', 0.3)
S(b, 'Sheen Roughness', 0.4)
bump(nt, b, 900.0, 0.22)
MATS['BELT'] = m

m, nt, b = newmat('DELRIN')
S(b, 'Base Color', (0.74, 0.735, 0.71, 1))
S(b, 'Roughness', 0.38)
S(b, 'Subsurface Weight', 0.20)
S(b, 'Subsurface Radius', (2.2, 2.0, 1.7))
MATS['DELRIN'] = m

m, nt, b = newmat('MOTOR')
S(b, 'Base Color', (0.042, 0.044, 0.050, 1))
S(b, 'Metallic', 1.0)
S(b, 'Roughness', 0.25)
S(b, 'Anisotropic', 0.6)
noise_rough(nt, b, 500.0, 0.17, 0.33)
MATS['MOTOR'] = m

m, nt, b = newmat('DARK')
S(b, 'Base Color', (0.024, 0.025, 0.029, 1))
S(b, 'Roughness', 0.40)
S(b, 'Metallic', 0.7)
MATS['DARK'] = m

m, nt, b = newmat('PCB')
S(b, 'Base Color', (0.015, 0.075, 0.033, 1))
S(b, 'Roughness', 0.45)
MATS['PCB'] = m

m, nt, b = newmat('MISC')
S(b, 'Base Color', (0.16, 0.16, 0.17, 1))
S(b, 'Roughness', 0.45)
MATS['MISC'] = m

files = sorted(glob.glob(os.path.join(SRC, "*.stl")))
print("importing %d stl" % len(files))
objs = []
fairings = []
for f in files:
    tag = os.path.basename(f).split("__")[0]
    before = set(bpy.data.objects)
    try:
        bpy.ops.wm.stl_import(filepath=f)
    except Exception:
        bpy.ops.import_mesh.stl(filepath=f)
    for o in set(bpy.data.objects) - before:
        o.data.materials.clear()
        o.data.materials.append(MATS.get(tag, MATS['MISC']))
        for p in o.data.polygons:
            p.use_smooth = True
        if hasattr(o.data, 'use_auto_smooth'):
            o.data.use_auto_smooth = True
            o.data.auto_smooth_angle = math.radians(32)
        objs.append(o)
        if tag == 'FAIR':
            fairings.append(o)
print("imported %d objects (%d fairings)" % (len(objs), len(fairings)))

mn = Vector((1e9, 1e9, 1e9))
mx = Vector((-1e9, -1e9, -1e9))
for o in objs:
    for c in o.bound_box:
        w = o.matrix_world @ Vector(c)
        for i in range(3):
            mn[i] = min(mn[i], w[i])
            mx[i] = max(mx[i], w[i])
ctr = (mn + mx) / 2.0
size = mx - mn
print("raw bbox mm: %s .. %s" % (["%.0f" % v for v in mn], ["%.0f" % v for v in mx]))

# stand it up: FreeCAD +Y is proximal -> world +Z.
# Rx(-90) maps +Y to -Z (upside down); Rx(+90) gives y'=-z, z'=y, which is what we want.
SCALE = 0.001
ROT = Matrix.Rotation(math.radians(90.0), 3, 'X')
rig = bpy.data.objects.new("RIG", None)
bpy.context.collection.objects.link(rig)
for o in objs:
    o.parent = rig
    o.matrix_parent_inverse = rig.matrix_world.inverted()
rig.rotation_euler = (math.radians(90.0), 0, 0)
rig.scale = (SCALE, SCALE, SCALE)
rig.location = -(SCALE * (ROT @ ctr))
bpy.context.view_layer.update()
DIAG = size.length * SCALE
KNEE = -(SCALE * (ROT @ ctr))          # FreeCAD origin (the knee axis) in world
print("rig diagonal %.3f m ; knee at world %s" % (DIAG, ["%.3f" % v for v in KNEE]))


def fcw(p):
    """FreeCAD mm -> world metres."""
    return KNEE + SCALE * (ROT @ Vector(p))


# The knee axis runs along FreeCAD +Z, and we view nearly down it, so aiming at the
# FreeCAD origin (Z=0) puts the visible pulley ~60 mm off frame centre. Aim at the
# pulley's mid-height instead.
KNEEC = fcw((0.0, 0.0, 110.0))         # centre of the 29T capstan
TOPC = fcw((0.0, 225.0, 95.0))         # drive head: motor, twin screw tops
FOOTC = fcw((0.0, -155.0 * math.cos(THETA), -155.0 * math.sin(THETA)))  # shank mid, follows the pose
print("kneec %s topc %s footc %s" % tuple(["%.3f" % v for v in q]
                                          for q in (KNEEC, TOPC, FOOTC)))
sys.stdout.flush()

# environment
wd = bpy.data.worlds.new("W")
sc.world = wd
wd.use_nodes = True
nt = wd.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
wout = nt.nodes.new('ShaderNodeOutputWorld')
bg = nt.nodes.new('ShaderNodeBackground')
texc = nt.nodes.new('ShaderNodeTexCoord')
texc.location = (-1300, 0)
mapn = nt.nodes.new('ShaderNodeMapping')
mapn.location = (-1100, 0)
grad = nt.nodes.new('ShaderNodeTexGradient')
grad.location = (-900, 0)
ramp = nt.nodes.new('ShaderNodeValToRGB')
ramp.location = (-620, 0)
mapn.inputs['Rotation'].default_value = (0, math.radians(90), 0)
e = ramp.color_ramp.elements
e[0].position = 0.30
e[0].color = (0.010, 0.011, 0.014, 1)
e[1].position = 0.80
e[1].color = (0.050, 0.055, 0.065, 1)
nt.links.new(texc.outputs['Generated'], mapn.inputs['Vector'])
nt.links.new(mapn.outputs['Vector'], grad.inputs['Vector'])
nt.links.new(grad.outputs['Color'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
bg.inputs['Strength'].default_value = 1.0
nt.links.new(bg.outputs['Background'], wout.inputs['Surface'])

bpy.ops.mesh.primitive_plane_add(size=DIAG * 9.0, location=(0, 0, -DIAG * 0.56))
floor = bpy.context.object
floor.name = "FLOOR"
m, ntf, b = newmat('FLOORMAT')
S(b, 'Base Color', (0.030, 0.032, 0.038, 1))
S(b, 'Roughness', 0.36)
S(b, 'Coat Weight', 0.30)
S(b, 'Coat Roughness', 0.30)
noise_rough(ntf, b, 14.0, 0.30, 0.46)
floor.data.materials.append(m)

bpy.ops.mesh.primitive_plane_add(size=DIAG * 9.0,
                                 location=(0, DIAG * 2.1, DIAG * 1.2),
                                 rotation=(math.radians(90), 0, 0))
back = bpy.context.object
back.name = "BACKDROP"
m2, ntb, b2 = newmat('BACKMAT')
S(b2, 'Base Color', (0.045, 0.048, 0.056, 1))
S(b2, 'Roughness', 0.66)
noise_rough(ntb, b2, 9.0, 0.58, 0.72)
back.data.materials.append(m2)


def area(name, loc, rot, size_, energy, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'AREA')
    d.size = size_
    d.energy = energy
    d.color = color
    o = bpy.data.objects.new(name, d)
    bpy.context.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = rot
    return o


k = DIAG
# exposure cut ~5x from v1: the blue was blowing out to pale sky
area('KEY', (-1.30 * k, -1.15 * k, 1.05 * k),
     (math.radians(56), 0, math.radians(-46)), 2.7 * k, 62 * k * k,
     (1.0, 0.972, 0.938))
area('RIM', (1.45 * k, 0.85 * k, 0.80 * k),
     (math.radians(68), 0, math.radians(124)), 2.0 * k, 44 * k * k,
     (0.76, 0.85, 1.0))
area('FILL', (0.70 * k, -1.45 * k, -0.10 * k),
     (math.radians(88), 0, math.radians(26)), 2.2 * k, 14 * k * k,
     (0.92, 0.95, 1.0))
area('TOP', (0.0, 0.30 * k, 1.75 * k), (0, 0, 0), 2.4 * k, 22 * k * k)

cam_d = bpy.data.cameras.new("CAM")
cam_d.sensor_width = 36.0
cam_d.sensor_fit = 'AUTO'
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 11.0
cam = bpy.data.objects.new("CAM", cam_d)
bpy.context.collection.objects.link(cam)
sc.camera = cam


def aim(pos, target):
    """Point the camera at `target` directly -- no constraint, no depsgraph lag."""
    d = (Vector(pos) - Vector(target))
    q = d.to_track_quat('Z', 'Y')
    cam.location = Vector(pos)
    cam.rotation_euler = q.to_euler()
    return d.length


D = DIAG
PORT = (W, H)
LAND = (H, W)
ORIGIN = Vector((0.0, 0.0, 0.0))


def shoot(name, direction, target, frame, lens, res, hide_fair, shift=(0.0, 0.0)):
    """frame = metres covered along the image's LONG axis."""
    for o in fairings:
        o.hide_render = hide_fair
    v = Vector(direction).normalized()
    dist = frame * lens / cam_d.sensor_width
    cam_d.lens = lens
    cam_d.shift_x, cam_d.shift_y = shift
    f = aim(Vector(target) + v * dist, target)
    cam_d.dof.focus_distance = f
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(OUT, "%s.png" % name)
    bpy.context.view_layer.update()
    print("rendering %-22s lens %3.0f  dist %.3f m  fairings %s"
          % (name, lens, f, "OFF" if hide_fair else "ON"))
    sys.stdout.flush()
    bpy.ops.render.render(write_still=True)


HERO = (-0.58, -0.80, 0.17)
HERO_C = (-0.82, -0.52, 0.21)   # rake across the thigh fairing so it reads as a form
TQ = (0.60, -0.76, 0.28)

shoot("01_hero_clad", HERO_C, ORIGIN, 1.11 * D, 85.0, PORT, False)
shoot("02_hero_open", HERO, ORIGIN, 1.11 * D, 85.0, PORT, True)
shoot("03_knee_open", (-0.52, -0.80, 0.18), KNEEC, 0.34, 110.0, LAND, True)
shoot("04_knee_clad", (-0.52, -0.80, 0.18), KNEEC, 0.36, 110.0, LAND, False)
shoot("05_profile_clad", (-1.0, -0.06, 0.05), ORIGIN, 1.13 * D, 100.0, PORT, False)
shoot("06_threequarter_open", TQ, ORIGIN, 1.08 * D, 85.0, PORT, True)
shoot("07_drive_open", (-0.50, -0.82, 0.24), TOPC, 0.40, 105.0, LAND, True)
shoot("08_shank_clad", (0.30, -0.88, 0.12), FOOTC, 0.62, 85.0, LAND, False)
print("ALL RENDERS DONE")
sys.stdout.flush()
