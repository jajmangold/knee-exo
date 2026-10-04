# -*- coding: utf-8 -*-
"""What moves when the knee bends. One authority, because four copies disagreed.

601_verify_fast.py, 406_coverage.py, 221_render_export.py and 222_anim_export.py each carried
their own copy of this list, and a part added to the device had to be remembered in all four.
P28b_IMUCover was not: it sits on the shank cuff, the cuff swung away from under it, and the
107-pose sweep reported the cover 0.893 cm3 inside its own host and 0.279 cm3 inside the
patient's shank. Nothing was wrong with the geometry. The list was wrong in one place out of
four, which is the same failure markframe.py exists to prevent for mark frames.

406_coverage.py's own comment already records the previous instance of it:

    "P31_InterfaceDist was: it sat at identity while the shank rotated, 88 mm from its host,
     and blocked rays from where it was not."

THE RULE. A part belongs in SHANK if it is rigidly attached to the shank segment, and in GANTRY
if it rides the ball nut. Reference solids count: REF_Shank is the limb and the limb moves.
Anything bolted to a part in a list belongs in the same list -- covers, brackets, hardware.
"""

# rigidly attached to the shank, and therefore rotated about the knee axis
SHANK = [
    "A4_Shank2020_VSlot",
    "P2a_KneeHingePlate",
    "P6_ShankSocket",
    "P7_ShankCuff",
    "P28b_IMUCover",            # bolted to P7's platform: it goes where the cuff goes
    "P31_InterfaceDist",
    "REF_Shank",
    "HW_JointBolts",
]

# rides the ball nut along the screw
GANTRY = [
    "P3_Carriage",
    "A2b_BallNut_SFU1620",
    "P10a_VWheel",
    "P10b_VWheel",
    "P10c_VWheel",
    "P10d_VWheel",
]

# P24_FairingShank used to be in SHANK. It left when 430_shank_inline_build.py moved the shank
# rail in-line under the knee joint and there was nothing left for it to fair.

# P28a_IMUCover is deliberately NOT here: it sits on P5_ThighCuff, which does not move.


def shank(include_ref=True):
    return [n for n in SHANK if include_ref or not n.startswith("REF_")]
