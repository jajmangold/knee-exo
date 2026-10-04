# -*- coding: utf-8 -*-
"""Put the controller in the machine. It has never been in it.

Forty-two solids in the model and not one of them electronic: the MKS XDRIVE MINI is ordered
(BOM E1, four owned), routed in ELECTRONICS's topology, and has no board, no mount, no standoffs
and no space reserved. It also cannot be put in the backpack with the battery, which is the usual
answer for a controller, because its AS5047P is ON the board and reads the 6 x 2.5 mm diametric
magnet glued to the motor's shaft (BOM D5). From the AMS datasheet:

    air gap, package face to magnet     0.5 to 3 mm
    magnet centred on the package       within 0.5 mm

So the board sits a few millimetres off the end of the motor's free shaft, concentric with it.
433_drive_flip.py turned the motor over, which left exactly that space empty: the link belt used
to occupy Y 302..314 and now runs below the motor instead.

WHAT IS ASSUMED HERE, ALL OF IT FLAGGED, because no mechanical drawing of this board is
published anywhere -- Makerbase's repository carries a schematic and nothing else, the community
notes have a drawing as a PNG with no dimensions, and the 63 x 58 mm that circulates in search
results is not corroborated by the page it is attributed to:

    BOARD           63 x 58 x 1.6, components 10 mm       UNVERIFIED -- measure yours
    BOARD_HOLES     55 x 50 rectangle of M3               GUESSED -- measure yours
    IC_OFFSET       the AS5047P at the board's centre     GUESSED, and it is the one that
                                                          matters: the IC is the datum, not the
                                                          outline, because it must sit on the
                                                          shaft's axis within 0.5 mm
    SHAFT_PROUD     2 mm of shaft past the motor's rear   UNVERIFIED
    REAR_BOLTS      the same 25 mm square as the front    UNVERIFIED -- 428 flags this too

Every one of those is a number that should come off the bench, and the mount is parameterised so
that correcting one and re-running is the whole job. What the file does guarantee is the thing
the datasheet fixes: it refuses to finish if the air gap it has built falls outside 0.5..3 mm.

    freecadcmd.exe scripts/434_odrive_mount.py
"""
import math
import os
import sys

import FreeCAD
import Part
from FreeCAD import Vector as V

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
import limbcone                                                     # noqa: E402

DOCFILE = os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
_BASE = DOCFILE.rsplit("/", 1)[-1]
try:
    doc = next(d for d in FreeCAD.listDocuments().values()
               if d.FileName.replace(chr(92), "/").endswith(_BASE))
except StopIteration:
    doc = FreeCAD.openDocument(DOCFILE)

M5, M3 = 5.2, 3.2
BOARD = (63.0, 58.0, 1.6)       # UNVERIFIED
# SOURCED, NOT GUESSED, as of the "Size" drawing in Smurf/xdrive-mini-docs and a photograph of
# the board's encoder face. This used to read (55.0, 50.0) with a comment saying GUESSED, and it
# was wrong in both the spacing and the COUNT: there are SIX M3 holes, not four, in two columns
# of three, and the middle row is not centred.
#
#     board          63.00 x 58.00          (the drawing, and two vendor listings)
#     holes          dia 3.3 x 6
#     columns        56.60 apart            -> +-28.30, inset 3.20 from each edge
#     rows           51.50 corner to corner, the middle one 24.00 below the top and 27.50
#                    above the bottom -- so it sits 1.75 ABOVE the board's centre line
#
# The corner four are symmetric about the board's centre, which is what lets the sensor sit on
# the shaft axis with the board centred on them.
BOARD_HOLES = (56.60, 51.50)    # corner-to-corner, from the published Size drawing
MID_ROW_UP = 1.75               # the middle pair, above the centre line
COMPONENTS = 10.0               # GUESSED, the tall side faces away from the motor
SHAFT_PROUD = 2.0               # UNVERIFIED
MAGNET = (6.0, 2.5)             # BOM D5, and what the datasheet asks for
AIR_GAP = 2.0                   # target, inside the datasheet's 0.5..3.0
GAP_LIMITS = (0.5, 3.0)         # AS5047P
REAR_BOLTS = 12.5               # half of the 25 mm square -- UNVERIFIED
CAP_T = 5.0                     # the mount's own plate

mot = doc.getObject("A3_Motor_6374")
a7 = doc.getObject("A7_DriveBox")
assert mot is not None, "no motor in this document"
mb = mot.Shape.BoundBox
MOT_X, MOT_R = 0.5 * (mb.XMin + mb.XMax), 0.5 * mb.XLength
MOT_Z = 0.5 * (mb.ZMin + mb.ZMax)
REAR_Y = mb.YMax                # the free end, after 433 turned the motor over
mirrored = mb.ZMax < 0
sgn = -1.0 if mirrored else 1.0

print("=" * 98)
print("CONTROLLER MOUNT  --  %s, %s leg" % (_BASE, "right" if mirrored else "left"))
print("=" * 98)
print("  the motor's free shaft end is at Y %.0f, on the axis X %.0f Z %.0f"
      % (REAR_Y, MOT_X, MOT_Z))

# where everything lands, from the shaft outwards
shaft_end = REAR_Y + SHAFT_PROUD
magnet_face = shaft_end + MAGNET[1]
ic_face = magnet_face + AIR_GAP
board_y = (ic_face, ic_face + BOARD[2])
print("  shaft end Y %.1f -> magnet face %.1f -> board's sensor face %.1f (%.1f mm air gap)"
      % (shaft_end, magnet_face, ic_face, AIR_GAP))

# ---------------------------------------------------------------- THE LIMB DECIDES THE ROTATION
# 399_drivecap.py's central measurement: "motor axis sits 121.1 mm from the leg axis, can radius
# 31.5 -> can face at 89.6; thigh surface 84.9 + 3.0 comfort clearance -> 87.9; radial room for a
# cover between them -> 1.7 mm". The motor is tucked that hard against the quadriceps, and a
# 63 x 58 board centred on its shaft has CORNERS at radius 42.8 -- which reach r 78.3 from the
# limb axis, 6.6 mm INSIDE a thigh of 84.9. The mount's boss circle is 5.0 mm inside it.
#
# NOTHING IN THE MODEL SAID SO. REF_Thigh is truncated at Y 300 and the board sits at Y 311, so
# every interference check in the repository -- including the 107-pose sweep -- reported the board
# clear of the limb because the limb simply stops being modelled there. The real thigh does not
# stop at Y 300; it gets thicker toward the hip. So the check here is against 399's own cylinder,
# extended over the whole drive, and it is the reason for the two things that follow.
#
# THE BOARD IS ROTATED about the shaft axis so its 58 mm EDGE faces the limb instead of a corner:
# 42.8 becomes 29.0, and r 78.3 becomes r 92.1 -- 7.2 mm clear. The rotation is computed from
# where the limb actually is rather than typed, and it keeps the AS5047P on the axis, which is
# the one thing that may not move. (If the IC turns out NOT to be at the board's centre, this
# rotation moves it off-axis and the whole arrangement has to be re-derived -- which is why
# IC_OFFSET is flagged as the measurement that matters.)
LEG_R = 84.9                    # 399_drivecap.py's nominal thigh
LEG_CLEAR = 0.1                 # what 399 already accepts under the pod, and no more
LIMB_DIR = math.degrees(math.atan2(-MOT_Z, -MOT_X))
ROT = LIMB_DIR + 90.0           # puts the board's short edge toward the limb
AXIS_R = math.hypot(MOT_X, MOT_Z)
print("  the limb axis lies %.1f deg from +X as seen from the motor, %.1f mm away;"
      % (LIMB_DIR, AXIS_R))
print("  the board is turned %.1f deg so its %.0f mm edge faces it, not a corner: the nearest"
      % (ROT, BOARD[1]))
print("  point goes from r %.1f (%.1f mm INSIDE a %.1f thigh) to r %.1f"
      % (AXIS_R - math.hypot(BOARD[0] / 2.0, BOARD[1] / 2.0),
         LEG_R - (AXIS_R - math.hypot(BOARD[0] / 2.0, BOARD[1] / 2.0)), LEG_R,
         AXIS_R - BOARD[1] / 2.0))


def rot(dx, dz):
    """a point given in the board's own frame, placed in the model's"""
    t = math.radians(ROT)
    c, s_ = math.cos(t), math.sin(t)
    return (MOT_X + dx * c - dz * s_, MOT_Z + sgn * (dx * s_ + dz * c))

# ---------------------------------------------------------------- the mount
cap = Part.makeCylinder(MOT_R, CAP_T, V(MOT_X, REAR_Y, MOT_Z), V(0, 1, 0))
# clearance for the shaft and its magnet
cap = cap.cut(Part.makeCylinder(MAGNET[0] / 2.0 + 4.0, CAP_T + 4.0,
                                V(MOT_X, REAR_Y - 2.0, MOT_Z), V(0, 1, 0)))
# bolts into the motor's rear face -- the motor's own pattern, NOT rotated with the board
for dx in (-REAR_BOLTS, REAR_BOLTS):
    for dz in (-REAR_BOLTS, REAR_BOLTS):
        cap = cap.cut(Part.makeCylinder(M5 / 2.0, CAP_T + 4.0,
                                        V(MOT_X + dx, REAR_Y - 2.0, MOT_Z + sgn * dz),
                                        V(0, 1, 0)))
# four bosses carrying the board, their top face at the sensor plane, on the board's own frame
boss_h = ic_face - (REAR_Y + CAP_T)
assert boss_h > 0.5, "the board would sit inside the mount's own plate"
BOSSES = [(dx, dz)
          for dx in (-BOARD_HOLES[0] / 2.0, BOARD_HOLES[0] / 2.0)
          for dz in (-BOARD_HOLES[1] / 2.0, MID_ROW_UP, BOARD_HOLES[1] / 2.0)]
for dx, dz in BOSSES:
    px, pz = rot(dx, dz)
    p = V(px, REAR_Y + CAP_T, pz)
    cap = cap.fuse(Part.makeCylinder(4.0, boss_h, p, V(0, 1, 0)))
    cap = cap.cut(Part.makeCylinder(M3 / 2.0, boss_h + 6.0,
                                    V(p.x, p.y - 3.0, p.z), V(0, 1, 0)))
# the bosses sit outside the motor's circle, so tie them back with a web -- rotated with them,
# built as a polygon rather than a box because a box cannot be given an angle without a
# placement, and a placement on a shape that later gets cut is how this project lost an evening
# the web is the BOARD'S OWN OUTLINE now, not the hole pattern plus a guess: the holes are
# inset 3.2 mm from the edges, so the outline covers every one of the six and nothing more
wpts = []
for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
    px, pz = rot(dx * BOARD[0] / 2.0, dz * BOARD[1] / 2.0)
    wpts.append(V(px, REAR_Y, pz))
wpts.append(wpts[0])
web = Part.Face(Part.makePolygon(wpts)).extrude(V(0, CAP_T, 0))
cap = cap.fuse(web)
cap = cap.cut(Part.makeCylinder(MAGNET[0] / 2.0 + 4.0, CAP_T + 4.0,
                                V(MOT_X, REAR_Y - 2.0, MOT_Z), V(0, 1, 0)))
for dx in (-REAR_BOLTS, REAR_BOLTS):
    for dz in (-REAR_BOLTS, REAR_BOLTS):
        cap = cap.cut(Part.makeCylinder(M5 / 2.0, CAP_T + 4.0,
                                        V(MOT_X + dx, REAR_Y - 2.0, MOT_Z + sgn * dz),
                                        V(0, 1, 0)))
tidy = cap.removeSplitter()
try:
    tidy.check(True)
    cap = tidy
except Exception:
    pass
cap.check(True)
assert len(cap.Solids) == 1, "the mount came out as %d solids" % len(cap.Solids)
o = doc.getObject("P27_ControllerMount") or doc.addObject("Part::Feature", "P27_ControllerMount")
o.Shape = cap
o.Label = "P27_ControllerMount"
print("  mount %.1f cm3: a cap on the motor's rear bolts, %d bosses %.1f mm tall on the"
      % (cap.Volume / 1000.0, len(BOSSES), boss_h))
print("        board's %.2f x %.2f pattern -- six holes, from the published Size drawing"
      % BOARD_HOLES)

# ---------------------------------------------------------------- the board itself
zc = MOT_Z


def _slab(w, d, y0, h):
    """a rectangle in the board's own frame, extruded along the limb"""
    pts = []
    for dx, dz in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        px, pz = rot(dx * w / 2.0, dz * d / 2.0)
        pts.append(V(px, y0, pz))
    pts.append(pts[0])
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, h, 0))


board = _slab(BOARD[0], BOARD[1], board_y[0], BOARD[2])
board = board.fuse(_slab(BOARD[0] - 8.0, BOARD[1] - 8.0, board_y[1], COMPONENTS))
tidy = board.removeSplitter()
try:
    tidy.check(True)
    board = tidy
except Exception:
    pass
b = doc.getObject("HW_ODrive_XDriveMini") or doc.addObject("Part::Feature", "HW_ODrive_XDriveMini")
b.Shape = board
b.Label = "HW_ODrive_XDriveMini"
print("  board %.0f x %.0f x %.1f at Y %.1f, components to Y %.1f  -- DIMENSIONS UNVERIFIED"
      % (BOARD[0], BOARD[1], BOARD[2], board_y[0], board_y[1] + COMPONENTS))

# ---------------------------------------------------------------- the shell closes over it
# The board is 63 x 58 and the pod that covers the motor is a dia 70 tube, so the board's CORNERS
# stand at radius 42.8 where the pod's inner wall is at 32 -- they project straight through it.
#
# THE FIRST VERSION OF THIS PUT A BOX THERE, and 399_drivecap.py's own history says why that is
# wrong: "v1 was a rectangular box. It looked like a shoebox bolted to the end of the canopy."
# It also cost 0.206 cm3 of overlap into P22_DriveCap that nothing in this file was checking for,
# because the box was fused into the nacelle and then never compared against the other half of
# the same wall.
#
# So the rear end of the pod is re-lofted in the SAME superelliptical family as the cap, n = 5.5,
# and the exponent is what makes it cheap: a round tube has to grow to r 42.8 + wall to swallow a
# 63 x 58 rectangle, where an n = 5.5 section swallows it at 36.5 x 34.0 because it is already
# nearly a rounded rectangle. The visible bulge over the controller is 4 mm, not 16.
#
#   Y 296..312   the circle opens out into the superellipse
#   Y 312..324   full section, which is what clears the board and its 10 mm of components
#   Y 324..334   a 45 deg blunt nose, ending in the same plane as P22's proximal end
#
# 45 deg because 411_printability.py has already caught this exact mistake on this exact part at
# the other end: a short wide taper DIVERGES upward and every layer overhangs.
N_PTS = 32                      # 32, not 48: at n=5.5 the parameterisation crowds points into
                                # the corners, and 48 of them produced six BOPAlgo TooSmallEdge
                                # errors that Shape.check(True) caught and isValid() would not
WALL = 2.5
NOSE_Y = 334.0                  # P22_DriveCap's proximal end, measured below and asserted

# THE EXPONENT IS THE WHOLE TRICK. A superellipse reaches 2**(1/2 - 1/n) of its semi-axis on the
# diagonal -- 1.247x at n = 5.5 -- and the board's corners are at radius 42.8, at 42.6 deg. So a
# section with a = 36.5 swallows a 63 x 58 board with 2.6 mm to spare, where a CIRCLE would have
# to be r 45 to do it. The cover over the controller is 5 mm wider than the tube it grows out of,
# not 20.
#
# n RAMPS FROM 2, so the tube does not step into a rounded square: it is a true circle at the
# root and squares off gradually over 15 mm. The first version of this started the loft at n=5.5
# all the way down and put a visible square sleeve around the motor.
#
#   Y 286..301   circle r 34 opens out into the n=5.5 section
#   Y 301..322   full section: the mount's web and bosses, the board, its 10 mm of components
#   Y 322..334   45 deg to a blunt end in P22's own proximal plane
#
# 45 deg because 411_printability.py has already caught this mistake on this exact part at the
# other end: a short wide taper DIVERGES upward and every layer overhangs.
#
# (y, semi-axis, exponent), DERIVED rather than typed: the stack above this moved 3 mm when
# 433_drive_flip.py corrected the link belt from 12 mm wide to the 15 mm BOM D6 specifies, and a
# typed station list simply became wrong -- the full section ended 2.6 mm before the board's
# components did. These follow the board.
# TWO SEMI-AXES, NOT ONE, and the small one points at the limb. A uniform a = 39 reaches
# r 76.3 from the limb axis on its diagonal -- 8.6 mm inside a 84.9 thigh. Aligned to the board's
# own frame the section only needs to be WIDE across the board's 63 and SHALLOW across its 58,
# and the shallow one is the limb-facing one.
#
# B IS SET BY THE SLEEVE, NOT BY THE BOARD. 438_limb_clearance.py measures every part against the
# limb's own tapered radius plus the 3 mm neoprene of BOM S5, and the first version of this nose
# failed it by 2.9 mm: B was 36, chosen against 399_drivecap.py's r 85.0 CYLINDER, which is the
# bare leg at the top of the taper and says nothing about a sleeve. The motor axis is 121.1 mm
# out and the envelope at this station is r 88.0, so the limb-facing reach may be 33.1 at most.
#
# THAT DEPTH IS FREE. The cavity only has to swallow the board's 58 mm dimension on this axis, so
# b = 30.5 clears its edge by 1.5 mm. What it costs is the CORNER, and the corner is bought back
# with the exponent instead: at n = 6.5 the section would have to be 91 mm wide to reach a corner
# at radius 42.8, where at n = 10 it is 77. A squarer section for a rectangular board under a
# tight leg -- the alternative was swinging the motor out, and 433 records why that is the wrong
# lever and what it costs.
LIMB_ENV = 88.0                         # limb + sleeve + air at this station, measured by 438
A_FULL = 40.0                           # along the board's 63 mm dimension
B_FULL = 33.0                           # across its 58 -- the limb-facing one, set by LIMB_ENV
FULL_END = board_y[1] + COMPONENTS + 1.5
SWELL_END = REAR_Y - 0.5                # full section before the mount's web, which is as wide
SWELL_START = SWELL_END - 15.5          # 15.5 mm of blend: 5 mm of radius, and 43 deg on the
                                        # diagonals, which is what has to print
A_END = A_FULL - (NOSE_Y - FULL_END)    # a 45 deg nose, by construction
# THE CHECK FOR THE DEFECT THIS SECTION HAD: the nose's limb-facing reach is B_FULL from an
# axis AXIS_R out, so it must leave the sleeve's envelope standing. The first version of it
# was 2.9 mm inside and only 438_limb_clearance.py could see that, because every limb cut in
# the repository is a cylinder and the leg is a taper.
assert AXIS_R - B_FULL >= LIMB_ENV - 0.05, (
    "the nose reaches r %.1f toward the limb, inside the %.1f sleeve envelope"
    % (AXIS_R - B_FULL, LIMB_ENV))
assert A_END >= 24.0, (
    "the components reach Y %.1f and P22 ends at %.0f, which leaves no room for a 45 deg nose"
    % (board_y[1] + COMPONENTS, NOSE_Y))
assert FULL_END > SWELL_END, "the swell has not finished before the board's section ends"

B_END = A_END - (A_FULL - B_FULL)
# BOTH LOFTS START AT THE SAME STATION, at the tube's own radii: 35 outside, 32 inside. The
# first version started the cavity 6 mm above the outer loft, which left the bell SOLID over
# those 6 mm -- 18.7 cm3 of it containing the motor's own can. The sweep found that; nothing in
# this file did. Matching the tube's radii also means the wall continues with no step and no
# void, so the trim plane is the only joint.
# N_FULL IS 10, NOT THE CAP'S 5.5, and the limb is why -- see B_FULL above. The diagonal reach
# has to come from the exponent because the depth is spoken for by the sleeve.
N_FULL = 10.0
OUT = [(SWELL_START, 35.0, 35.0, 2.0), (SWELL_START + 8.0, 36.5, 35.5, 3.0),
       (SWELL_END, A_FULL, B_FULL, N_FULL), (FULL_END, A_FULL, B_FULL, N_FULL),
       (NOSE_Y, A_END, B_END, N_FULL)]
IN_ = [(SWELL_START, 32.0, 32.0, 2.0), (SWELL_START + 8.0, 33.5, 32.5, 3.0),
       (SWELL_END, A_FULL - WALL, B_FULL - WALL, N_FULL),
       (FULL_END, A_FULL - WALL, B_FULL - WALL, N_FULL),
       (NOSE_Y - WALL, A_END, B_END, N_FULL)]


def sell(y, a, bb, n):
    """one superelliptical wire in the BOARD's frame, in 399's own parameterisation"""
    pts = []
    for i in range(N_PTS):
        t = 2.0 * math.pi * i / N_PTS
        ct, st = math.cos(t), math.sin(t)
        px, pz = rot(a * math.copysign(abs(ct) ** (2.0 / n), ct),
                     bb * math.copysign(abs(st) ** (2.0 / n), st))
        pts.append(V(px, y, pz))
    pts.append(pts[0])
    return Part.makePolygon(pts)


def contains(a, bb, n, hx, hz):
    return (hx / a) ** n + (hz / bb) ** n


nac = doc.getObject("P25_MotorNacelle")
cap22 = doc.getObject("P22_DriveCap")
outer = Part.makeLoft([sell(*st) for st in OUT], True, True)
inner = Part.makeLoft([sell(*st) for st in IN_], True, True)

# THE MOUNT HAS TO FIT INSIDE ITS OWN COVER, and it did not. The cap is a disc of the motor's
# OWN radius, 31.5, because that is the face it bolts to -- and the cavity over it is only 30.5
# deep on the limb side, because the sleeve sets that and nothing else may. So the disc's rim
# stood 1 mm proud of the wall it lives in: 0.108 cm3, which this file's own pair check caught
# only after the section was flattened. Trim the mount to the cavity rather than deepen the
# cavity: a millimetre off a rim whose bolts are at radius 17.7 costs nothing, and deepening the
# cavity costs the patient's quadriceps.
_capped = o.Shape.common(inner)
assert len(_capped.Solids) == 1, "trimming the mount to its cover gave %d solids" % len(
    _capped.Solids)
_capped.check(True)
if o.Shape.Volume - _capped.Volume > 1.0:
    print("  mount trimmed to the cover's cavity: %.2f cm3 off the cap's rim"
          % ((o.Shape.Volume - _capped.Volume) / 1000.0))
o.Shape = _capped
if nac is not None:
    v = nac.Shape.Volume
    assert cap22 is not None, "no P22 to end flush with"
    p22y = cap22.Shape.BoundBox.YMax
    assert abs(p22y - NOSE_Y) < 0.6,         "P22 ends at Y %.1f, so the nose should too, not at %.1f" % (p22y, NOSE_Y)
    # the cavity must swallow the board at every station it covers, corners included
    for y, a, bb, n in IN_[2:4]:
        c = contains(a, bb, n, BOARD[0] / 2.0, BOARD[1] / 2.0)
        assert c <= 0.85,             "the cavity at Y %.0f is %.2f of the way to the board's corner -- too close" % (y, c)
    assert board_y[1] + COMPONENTS <= IN_[3][0] - 1.0,         "the board's components reach Y %.1f and the full section ends at %.1f"         % (board_y[1] + COMPONENTS, IN_[3][0])
    # TRIM, DO NOT CUT. Above the Y where the new cavity is wider than the tube's own OUTER skin,
    # keeping the tube would leave a void ring between the two walls belonging to neither -- the
    # exact defect 399_drivecap.py records from its v2. So the tube is removed there and the bell
    # is the only wall; below it the two overlap solidly and fuse. That also takes the nacelle's
    # old rear closure -- a disc across the whole bore at Y 302..304, measured -- which is where
    # the controller now lives and where the mount bolts straight through.
    # Above the Y where the cavity is wider than the tube's own OUTER skin, keeping the tube
    # would leave a void ring between the two walls belonging to neither part.
    pod_outer = 35.0
    y0, a0_, _, _ = IN_[1]
    y1, a1_, _, _ = IN_[2]
    TRIM_Y = y0 + (pod_outer - a0_) / (a1_ - a0_) * (y1 - y0) - 0.5
    assert y0 < TRIM_Y < y1, "the trim at Y %.1f is not inside the blend" % TRIM_Y
    cb = nac.Shape.BoundBox
    trimmed = nac.Shape.cut(Part.makeBox(cb.XLength + 8.0, (cb.YMax + 8.0) - TRIM_Y,
                                         cb.ZLength + 8.0,
                                         V(cb.XMin - 4.0, TRIM_Y, cb.ZMin - 4.0)))
    bell = outer.cut(inner)
    assert len(bell.Solids) == 1, "the nose came out as %d solids" % len(bell.Solids)
    grown = trimmed.fuse(bell)
    # THE BRACKET REACHES Y 300 AND THE BELL STARTS AT 289, so they share that band and the
    # cladding yields, as it does everywhere else here. Without this the sweep reports 0.430 cm3
    # of A7_DriveBox inside the nacelle, and this file -- which checks only the two parts it
    # adds -- reports everything clean.
    if a7 is not None:
        grown = grown.cut(a7.Shape)
    # AND THE CAN COMES THROUGH THE CAVITY, which is not a mistake but a measurement. On the limb
    # side the sleeve puts the cover's outer skin at r 88.0 from the limb axis and the motor's can
    # is at 89.6: 1.6 mm for a wall, and the nose asks for 2.5. So where the blend still overlaps
    # the motor -- Y 289..305, the last 16 mm of the can -- the can stands 1 mm inside the wall,
    # 0.044 cm3 of it, and the full 107-pose sweep is what found it.
    #
    # The cladding yields to the mechanism, as it does everywhere else in this file and in 433.
    # The alternative is to hold the blend off until the can has ended, and that pushes the
    # mount's own web out of the full section it needs. A locally thinner skin over a motor is
    # the cheaper of the two, and it is the same conflict the mount's cap had: a cover whose
    # cavity is shallower than the thing it covers, because the leg says so.
    _can = Part.makeCylinder(MOT_R + 0.25, (REAR_Y - mb.YMin) + 4.0,
                             V(MOT_X, mb.YMin - 2.0, MOT_Z), V(0, 1, 0))
    _v = grown.Volume
    grown = grown.cut(_can)
    if _v - grown.Volume > 1.0:
        print("  clad  the can relieved out of the nose's blend: -%.3f cm3"
              % ((_v - grown.Volume) / 1000.0))
    if len(grown.Solids) == 1:
        grown.check(True)
        # AND THE COVER CUTS ITSELF BACK FROM THE LEG, here, in the file that draws it.
        # 439_limb_trim.py used to do this afterwards, and re-running THIS file silently undid
        # it: the bell spans Y 289..334 and is fused on every run, so it put 0.414 cm3 straight
        # back inside the patient's sleeve with nothing reporting a thing. A trim that lives in
        # a later script is a trim that can be lost by re-running an earlier one.
        _ref = doc.getObject("REF_Thigh")
        if _ref is not None:
            _env = limbcone.envelope(_ref.Shape)
            _v = grown.Volume
            _cut = grown.cut(_env)
            assert len(_cut.Solids) == 1, (
                "cutting the limb's envelope gave %d solids" % len(_cut.Solids))
            _cut.check(True)
            if _v - _cut.Volume > 1.0:
                print("  clad  cut back from the limb's taper + sleeve: -%.3f cm3"
                      % ((_v - _cut.Volume) / 1000.0))
            grown = _cut
        nac.Shape = grown
        print("  clad  nacelle re-nosed: circle r %.0f swells to an n=%.1f %.0f x %.0f over the"
              % (OUT[0][1], N_FULL, 2 * OUT[2][1], 2 * OUT[2][2]))
        print("        controller, then 45 deg to a blunt end in P22's plane at Y %.0f"
              % NOSE_Y)
        print("        %.1f -> %.1f cm3, and the board's corners clear the wall by %.1f mm"
              % (v / 1000.0, grown.Volume / 1000.0,
                 math.hypot(BOARD[0] / 2.0, BOARD[1] / 2.0)
                 * (contains(IN_[2][1], IN_[2][2], IN_[2][3], BOARD[0] / 2.0, BOARD[1] / 2.0)
                    ** (-1.0 / IN_[2][3]) - 1.0)))
    else:
        print("  clad  REFUSED to re-nose the nacelle: %d solids" % len(grown.Solids))

# P22 AND P25 ARE ONE WALL SPLIT IN TWO, so the nose displacing the seam is P22's business too:
# whatever the new section occupies, P22 gives up. Without this the pair overlaps and the sweep
# is the only thing that says so -- which is exactly how the box's 0.206 cm3 got in.
if cap22 is not None:
    v22 = cap22.Shape.Volume
    # the mount, the board, and the nose's own outer surface -- all three, in one cut, because
    # chaining three booleans on a 150 cm3 shell is how "Unorientable shape" gets made here
    g = cap22.Shape.cut(o.Shape.fuse(b.Shape).fuse(outer))
    if len(g.Solids) == 1:
        g.check(True)
        cap22.Shape = g
        print("  clad  P22 gives up the seam the nose now owns: %.1f -> %.1f cm3"
              % (v22 / 1000.0, g.Volume / 1000.0))
    else:
        print("  clad  REFUSED to relieve P22: %d solids" % len(g.Solids))

doc.recompute()
doc.save()

# ---------------------------------------------------------------- verify
print()
print("  VERIFICATION")
fail = []
gap = ic_face - magnet_face
ok = GAP_LIMITS[0] <= gap <= GAP_LIMITS[1]
print("     air gap %.2f mm, datasheet allows %.1f..%.1f  %s"
      % (gap, GAP_LIMITS[0], GAP_LIMITS[1], "" if ok else "<-- OUT OF RANGE"))
if not ok:
    fail.append("air gap %.2f mm is outside the AS5047P's %.1f..%.1f" % (gap,) + GAP_LIMITS)
# THE LIMB, WHICH THE MODEL CANNOT SHOW. REF_Thigh is truncated at Y 300 and everything this
# file builds sits above it, so every interference check in the repository -- the 107-pose sweep
# included -- reports the board, the mount and the nose clear of the leg because the leg stops
# being modelled there. The real thigh does not stop at Y 300. So they are checked against
# 399_drivecap.py's own cylinder instead, extended over the whole drive: r 84.9 + 0.1, which is
# the clearance 399 already accepts under the pod and explicitly calls "skimming the quadriceps".
limb = Part.makeCylinder(LEG_R + LEG_CLEAR, 400.0, V(0.0, 10.0, 0.0), V(0, 1, 0))
print()
print("     against a limb of r %.1f extended past REF_Thigh's truncation at Y %.0f:"
      % (LEG_R + LEG_CLEAR, doc.getObject("REF_Thigh").Shape.BoundBox.YMax
         if doc.getObject("REF_Thigh") else 0.0))
for part, lbl in ((o, "mount"), (b, "board"), (doc.getObject("P25_MotorNacelle"), "nacelle")):
    if part is None:
        continue
    c = part.Shape.common(limb)
    v = 0.0 if c.isNull() else c.Volume / 1000.0
    print("     %-8s %7.3f cm3 %s" % (lbl, v, "" if v <= 0.02 else "<-- IN THE LEG"))
    if v > 0.02:
        fail.append("%s is %.3f cm3 inside a limb of r %.1f" % (lbl, v, LEG_R + LEG_CLEAR))
print()

# THE CHECK THE BOX GOT PAST. This file grows the nacelle, so the nacelle is one of the things
# it has to re-examine -- not just the two parts it adds. P22 and P25 are one wall split in two
# and are claimed in ASSEMBLY.md to tile with zero overlap and no void between them, so the pair
# is checked both ways: no common volume, and no gap along the seam the nose just moved.
for n1, n2 in (("P22_DriveCap", "P25_MotorNacelle"),):
    t1, t2 = doc.getObject(n1), doc.getObject(n2)
    if t1 is not None and t2 is not None:
        c = t1.Shape.common(t2.Shape)
        vv = 0.0 if c.isNull() else c.Volume / 1000.0
        print("     %-6s vs %-22s %7.3f cm3 %s"
              % ("P22", n2, vv, "" if vv <= 0.02 else "<-- CLASH"))
        if vv > 0.02:
            fail.append("%s overlaps %s by %.3f cm3" % (n1, n2, vv))
for nm in ("A3_Motor_6374", "A7_DriveBox", "P25_MotorNacelle", "P22_DriveCap", "A7b_LinkBelt",
           "A2_BallScrew_SFU1620"):
    t = doc.getObject(nm)
    if t is None:
        continue
    for part, lbl in ((o, "mount"), (b, "board")):
        c = part.Shape.common(t.Shape)
        v = 0.0 if c.isNull() else c.Volume / 1000.0
        if v > 0.02:
            print("     %-6s vs %-22s %7.3f cm3 <-- CLASH" % (lbl, nm, v))
            fail.append("%s overlaps %s by %.3f cm3" % (lbl, nm, v))
        else:
            print("     %-6s vs %-22s %7.3f cm3" % (lbl, nm, v))
print()
if fail:
    for f in fail:
        print("  FAIL %s" % f)
else:
    print("  the controller sits on the motor's free end with its sensor %.1f mm off the magnet," % gap)
    print("  inside the space the link belt vacated. Measure the board before printing the mount:")
    print("  its outline, its hole pattern, and above all where the AS5047P sits on it.")
sys.stdout.flush()
sys.exit(1 if fail else 0)
