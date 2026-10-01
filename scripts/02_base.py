# -*- coding: utf-8 -*-
"""KneeExo v1 - parameters, helpers, document.
CS:  X = posterior(+)/anterior(-)   Y = proximal(+)/distal(-)   Z = lateral(+) from limb midline
Knee flexion axis = line X=0,Y=0 along Z.  +Z is LATERAL, so the built model is the
LEFT leg; the right is mirrored Z -> -Z into its own document by 701_mirror_build.py.
(This line read "Right leg (MIRROR flag for left)" from v1 onward and was simply
wrong by the time anything was built against it.)
"""
import math, FreeCAD, Part
from FreeCAD import Vector as V

DOC = "KneeExo_v1"
if DOC in FreeCAD.listDocuments(): FreeCAD.closeDocument(DOC)
doc = FreeCAD.newDocument(DOC)

P = dict(
    # ---- anthropometry (1.75 m / 80 kg) ----
    R_TH=78.0, R_SH=58.0, PAD=6.0, SHELL=4.0,
    Y_THC=(170.0, 290.0),      # thigh cuff span
    Y_SHC=(-278.0, -158.0),    # shank cuff span
    # ---- mechanism ----
    LA=250.0, R_CRANK=60.0, PHI0=135.0, ALPHA=85.0,
    ROM=(-2.0, 105.0), F_ACT=600.0,
    # ---- lateral (Z) stack ----
    Z_CUFF_TH=88.0,            # thigh cuff outer radius = upright inboard datum
    Z_CUFF_SH=68.0,
    FORK_IN=(88.0, 98.0), GAP=(98.0, 118.0), FORK_OUT=(118.0, 128.0),
    LINK=(100.0, 116.0),       # shank link thickness (16) inside 20 gap
    Z_PLANE=108.0,             # actuator centre plane
    # ---- sections ----
    BOX_X=(-34.0, 14.0), BOX_Z=(88.0, 128.0), WALL=5.0,
    R_HUB=30.0, R_PLATE=72.0, PLATE_SEC=(88.0, 246.0),   # fork sector plate bearings
    R_PIN=60.0, D_PIN=12.0, D_PIVOT=12.0,
    FLEX_HOLES=[(240,105),(230,95),(220,85),(210,75),(200,65),(190,55)],
    EXT_HOLES=[(103.3,0),(113.3,10),(123.3,20)],
    FINGER=(109.0, 129.0),     # stop-finger bearings at theta=0
)
g = globals(); g.update(P)
TAU_MAX = 0.0

def rad(d): return math.radians(d)
def pol(r, bearing): return (r*math.cos(rad(bearing)), r*math.sin(rad(bearing)))
def pinA(): return pol(LA, ALPHA)
def pinB(th): return pol(R_CRANK, ALPHA - PHI0 + th)
def ab(th):  return math.sqrt(LA**2 + R_CRANK**2 - 2*LA*R_CRANK*math.cos(rad(PHI0-th)))
def arm(th): return LA*R_CRANK*math.sin(rad(PHI0-th))/ab(th)

# ---------- shape helpers ----------
def bx(x0,x1,y0,y1,z0,z1):
    return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0,y0,z0))
def cz(r, z0, z1, x=0.0, y=0.0):
    return Part.makeCylinder(r, z1-z0, V(x,y,z0), V(0,0,1))
def cy(r, y0, y1, x=0.0, z=0.0):
    return Part.makeCylinder(r, y1-y0, V(x,y0,z), V(0,1,0))
def sector(r_out, b0, b1, z0, z1, r_in=0.0):
    """annular sector about the knee axis, bearings b0->b1 CCW"""
    s = Part.makeCylinder(r_out, z1-z0, V(0,0,z0), V(0,0,1), (b1-b0) % 360 or 360)
    s.rotate(V(0,0,0), V(0,0,1), b0)
    if r_in > 0: s = s.cut(cz(r_in, z0-1, z1+1))
    return s
def bar(p0, p1, w0, w1, z0, z1, cap0=True, cap1=True):
    """tapered bar in the XY plane extruded in Z, with round end caps"""
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy)
    ux, uy = dx/L, dy/L; nx, ny = -uy, ux
    pts = [(p0[0]+nx*w0, p0[1]+ny*w0), (p1[0]+nx*w1, p1[1]+ny*w1),
           (p1[0]-nx*w1, p1[1]-ny*w1), (p0[0]-nx*w0, p0[1]-ny*w0)]
    w = Part.makePolygon([V(x,y,z0) for x,y in pts]+[V(pts[0][0],pts[0][1],z0)])
    s = Part.Face(w).extrude(V(0,0,z1-z0))
    if cap0: s = s.fuse(cz(w0, z0, z1, *p0))
    if cap1: s = s.fuse(cz(w1, z0, z1, *p1))
    return s
def arc_shell(r_in, r_out, y0, y1, b_start=250.0, b_sweep=170.0):
    """limb cuff shell: annular sector whose axis is +Y, bearings in the global XZ sense"""
    s = Part.makeCylinder(r_out, y1-y0, V(0,0,0), V(0,0,1), b_sweep)
    s = s.cut(Part.makeCylinder(r_in, y1-y0+2, V(0,0,-1), V(0,0,1)))
    s.rotate(V(0,0,0), V(0,0,1), b_start)
    s.rotate(V(0,0,0), V(1,0,0), -90)     # local +Z -> global +Y
    s.translate(V(0, y0, 0))
    return s
def insert_holes(shape, pts, d=6.4, depth=11.0, axis="z"):
    """M5 heat-set insert bores"""
    for p in pts:
        if axis == "z":
            x,y,z0,dr = p[0],p[1],p[2],(1 if len(p)<4 or p[3]>0 else -1)
            shape = shape.cut(cz(d/2, z0, z0+depth*dr) if dr>0 else cz(d/2, z0-depth, z0))
        else:
            shape = shape.cut(cy(d/2, p[1], p[1]+depth, p[0], p[2]))
    return shape
def add(name, shape, rgb, grp=None):
    o = doc.addObject("Part::Feature", name); o.Shape = shape
    if getattr(o, "ViewObject", None) is not None:  # absent headless
        o.ViewObject.ShapeColor = rgb; o.ViewObject.Transparency = 0
    if grp is not None: grp.addObject(o)
    return o

G_TH  = doc.addObject("App::DocumentObjectGroup", "A_Thigh_Assembly")
G_SH  = doc.addObject("App::DocumentObjectGroup", "B_Shank_Assembly")
G_ACT = doc.addObject("App::DocumentObjectGroup", "C_Actuator")
G_HW  = doc.addObject("App::DocumentObjectGroup", "D_Hardware")
G_REF = doc.addObject("App::DocumentObjectGroup", "E_Reference_Limb")
g.update({k:v for k,v in locals().items() if k.startswith(("G_","DOC","doc"))})

print("doc:", DOC)
print("pin A  =", tuple(round(v,2) for v in pinA()))
print("pin B0 =", tuple(round(v,2) for v in pinB(0)))
print("stroke = %.1f mm  (%.1f .. %.1f)" % (ab(ROM[0])-ab(ROM[1]), ab(ROM[1]), ab(ROM[0])))
print("peak torque %.1f N.m at 60 deg" % (F_ACT*arm(60)/1000))
