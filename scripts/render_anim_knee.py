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
SRC, OUT, SAMPLES = argv[0], argv[1], int(argv[2])   # SRC = anim root
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


# ---------------------------------------------------------------- animation
# One directory per frame. The rig transform is computed ONCE, from the union of the
# two extreme poses, and then held fixed -- otherwise the per-frame bounding box would
# move and the whole device would jitter inside the frame instead of the shank swinging
# about a stationary knee.
FRAMES = sorted(d for d in os.listdir(SRC) if d.startswith("f")
                and os.path.isdir(os.path.join(SRC, d)))
print("frames: %d" % len(FRAMES))


def load(frame):
    objs, fairings = [], []
    for f in sorted(glob.glob(os.path.join(SRC, frame, "*.stl"))):
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
            objs.append(o)
            if tag == 'FAIR':
                fairings.append(o)
    return objs, fairings


def purge(objs):
    for o in objs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)


def bbox(objs):
    mn = Vector((1e9,) * 3)
    mx = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i])
                mx[i] = max(mx[i], w[i])
    return mn, mx


# fixed framing from the two extremes of the cycle
MN = Vector((1e9,) * 3)
MX = Vector((-1e9,) * 3)
for ref in (FRAMES[0], FRAMES[len(FRAMES) // 2]):
    o_, _ = load(ref)
    a, b = bbox(o_)
    for i in range(3):
        MN[i] = min(MN[i], a[i])
        MX[i] = max(MX[i], b[i])
    purge(o_)
ctr = (MN + MX) / 2.0
size = MX - MN
SCALE = 0.001
ROT = Matrix.Rotation(math.radians(90.0), 3, 'X')
RIG_LOC = -(SCALE * (ROT @ ctr))
DIAG = size.length * SCALE
KNEE = RIG_LOC
fcw = lambda p: KNEE + SCALE * (ROT @ Vector(p))
KNEEC = fcw((0.0, 0.0, 110.0))
print("fixed rig: diag %.3f m, knee at %s" % (DIAG, ["%.3f" % v for v in KNEE]))
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



D = DIAG
HERO = (-0.58, -0.80, 0.17)
TQ = (0.60, -0.76, 0.28)
cam_d.dof.aperture_fstop = 18.0        # motion + shallow DOF at GIF size is mush

VIEWS = [
    ("knee_open",  (-0.52, -0.80, 0.18), fcw((0.0, -40.0, 110.0)), 0.52, 105.0,
     (800, 600), False),
]
for name, _, _, _, _, _, _ in VIEWS:
    d = os.path.join(OUT, name)
    if not os.path.isdir(d):
        os.makedirs(d)

for fi, frame in enumerate(FRAMES):
    objs, fairings = load(frame)
    rig = bpy.data.objects.new("RIG", None)
    bpy.context.collection.objects.link(rig)
    for o in objs:
        o.parent = rig
        o.matrix_parent_inverse = rig.matrix_world.inverted()
    rig.rotation_euler = (math.radians(90.0), 0, 0)
    rig.scale = (SCALE,) * 3
    rig.location = RIG_LOC
    bpy.context.view_layer.update()

    for name, direction, target, frame_m, lens, res, clad in VIEWS:
        for o in fairings:
            o.hide_render = not clad
        v = Vector(direction).normalized()
        dist = frame_m * lens / cam_d.sensor_width
        cam_d.lens = lens
        f = aim(Vector(target) + v * dist, target)
        cam_d.dof.focus_distance = f
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = os.path.join(OUT, name, "%03d.png" % fi)
        bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(rig, do_unlink=True)
    purge(objs)
    print("frame %03d / %d  (%s)" % (fi, len(FRAMES), frame))
    sys.stdout.flush()

print("ALL FRAMES DONE")
sys.stdout.flush()
