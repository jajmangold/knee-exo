# -*- coding: utf-8 -*-
"""What two leg IMUs can tell apart that the knee encoder cannot. Arithmetic, nothing built.

Asked at the bench: "the imus though, we can tell lots of stuff using those. For example we can
sense the difference between laying in bed and standing. Or laying with legs up and knees bent
and sitting. We can tell if the person is upside down, etc."

That is a different job from the gait phase ELECTRONICS.md already assigns an IMU, and it is a
stronger one. The AS5048A on the knee pin measures the ANGLE BETWEEN two segments. It cannot
measure where either of them is pointing, so it reads the same number sitting in a chair as lying
in bed with the knees up -- and those two want opposite things from a powered brace.

WHAT A STATIC IMU ACTUALLY GIVES YOU, and why it is the reliable half of the sensor. At rest an
accelerometer reads one thing: the direction of gravity in its own frame. That is two degrees of
freedom per segment -- how far the segment's long axis is from vertical, and which way it is
rolled about that axis -- and it needs NO gyro, NO integration and NO fusion, so it cannot drift.
Posture is the part of this that works while the patient is asleep. Gait phase is the part that
needs the gyro, and it is the part that can go wrong.

So: enumerate the postures, compute what each IMU reads in each, and report how far apart they
are. Thresholds for the state machine then come from this table rather than from intuition.

I EXPECTED A LEG-ONLY SENSOR SET TO HAVE A BLIND SPOT -- two IMUs on the thigh and shank see the
LEG's attitude, not the TRUNK's, so any pair of postures that puts both leg segments in the same
place should be invisible however good the sensors are. The table below does not find one that
matters: the only pair closer than 10 degrees is standing against mid-stance, which are 8 apart
because mid-stance very nearly IS standing, and both are handled the same way. A near-duplicate
inside one class is not an ambiguity. Nothing crosses the assist gate, so the trunk sensor this
was written to justify is not needed for that job.

    python scripts/441_posture.py
"""
import itertools
import math

DEG = math.pi / 180.0


def rot(axis, deg):
    c, s = math.cos(deg * DEG), math.sin(deg * DEG)
    if axis == "x":
        return ((1, 0, 0), (0, c, -s), (0, s, c))
    if axis == "y":
        return ((c, 0, s), (0, 1, 0), (-s, 0, c))
    return ((c, -s, 0), (s, c, 0), (0, 0, 1))


def mul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


def apply(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def ang(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, dot(a, b)))))


# Body frame: +x anterior, +y to the left, +z up (head). Standing, the thigh points along -z.
DOWN_BODY = (0.0, 0.0, -1.0)
ANT_BODY = (1.0, 0.0, 0.0)

# Trunk attitude -- the rotation from body axes into the world. Standing is the identity.
ATT = {
    "upright": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "stooped 30": rot("y", -30),
    "supine": rot("y", -90),                      # on the back, anterior up
    "prone": rot("y", 90),                        # face down
    "side-lying": mul(rot("y", -90), rot("x", 90)),
    "inverted": rot("y", 180),                    # head down: fallen, or hanging
}

# (label, trunk attitude, hip flexion, knee flexion)
POSTURES = [
    ("standing",                   "upright",    0.0,   2.0),
    ("walking, mid-swing",         "upright",   25.0,  60.0),
    ("walking, mid-stance",        "upright",    5.0,  15.0),
    ("sitting in a chair",         "upright",   90.0,  90.0),
    ("sit-to-stand, mid",          "stooped 30", 45.0,  45.0),
    ("stair ascent, mid",          "upright",   60.0,  80.0),
    ("kneeling",                   "upright",    0.0, 110.0),
    ("supine, legs flat",          "supine",     0.0,   2.0),
    ("supine, knees bent up",      "supine",    45.0,  90.0),
    ("supine, legs on a pillow",   "supine",    20.0,  20.0),
    ("prone, legs flat",           "prone",      0.0,   2.0),
    ("side-lying, curled",         "side-lying", 30.0,  60.0),
    ("inverted / fallen",          "inverted",   0.0,  10.0),
]

ASSIST_OK = ("standing", "walking, mid-swing", "walking, mid-stance", "sitting in a chair",
             "sit-to-stand, mid", "stair ascent, mid")
SENSOR = 2.0        # deg: what a well-mounted static accelerometer is good for
SEPARABLE = 10.0    # deg: five times the sensor, which is where a threshold stops being luck


def segment_frames(att, hip, knee):
    """gravity as each IMU sees it, in its own segment frame"""
    b = ATT[att]
    out = []
    for turn in (-hip, knee - hip):
        r = rot("y", turn)
        z_s = apply(r, DOWN_BODY)       # the segment's long axis, proximal -> distal
        x_s = apply(r, ANT_BODY)        # the segment's own anterior
        y_s = (z_s[1] * x_s[2] - z_s[2] * x_s[1],
               z_s[2] * x_s[0] - z_s[0] * x_s[2],
               z_s[0] * x_s[1] - z_s[1] * x_s[0])
        g_world = (0.0, 0.0, -1.0)
        axes = [apply(b, v) for v in (x_s, y_s, z_s)]
        out.append(tuple(dot(g_world, a) for a in axes))
    return out


# sanity, because a sign error here would quietly invert the whole table
_t, _s = segment_frames("upright", 0.0, 0.0)
assert abs(_t[2] - 1.0) < 1e-9, "standing: gravity should run down the thigh's own axis, got %s" % (_t,)
assert abs(_s[2] - 1.0) < 1e-9, "standing: and down the shank's, got %s" % (_s,)
_t, _s = segment_frames("upright", 90.0, 90.0)
assert abs(_t[2]) < 1e-9, "sitting: the thigh is horizontal, so gravity is across it, got %s" % (_t,)
assert abs(_s[2] - 1.0) < 1e-9, "sitting: the shank hangs, got %s" % (_s,)

print("=" * 98)
print("WHAT TWO LEG IMUs SEE  --  static attitude, accelerometer only, no gyro, no drift")
print("=" * 98)
print("  tilt = angle of the segment's long axis from straight DOWN (0 = hanging, 180 = pointing up)")
print("  roll = where gravity sits around that axis (0 = toward the segment's own front)")
print()
print("  %-26s %5s %5s   %-16s %-16s" % ("posture", "hip", "knee", "thigh IMU", "shank IMU"))
table = {}
for lbl, att, hip, knee in POSTURES:
    g = segment_frames(att, hip, knee)
    table[lbl] = (g, knee)
    cells = []
    for v in g:
        tilt = math.degrees(math.acos(max(-1.0, min(1.0, v[2]))))
        roll = math.degrees(math.atan2(v[1], v[0]))
        cells.append("tilt %5.1f r %+6.1f" % (tilt, roll))
    print("  %-26s %5.0f %5.0f   %-16s %-16s" % (lbl, hip, knee, cells[0], cells[1]))

print()
print("=" * 98)
print("  THE PAIRS THE KNEE ENCODER CANNOT SEPARATE")
print("  Same knee angle to within %.0f deg -- the AS5048A reads the same number in both." % 8.0)
print()
blind, saved = [], []
for a, b in itertools.combinations(table, 2):
    (ga, ka), (gb, kb) = table[a], table[b]
    if abs(ka - kb) > 8.0:
        continue
    sep = max(ang(ga[0], gb[0]), ang(ga[1], gb[1]))
    (saved if sep >= SEPARABLE else blind).append((sep, a, b, abs(ka - kb)))
for sep, a, b, dk in sorted(saved, reverse=True):
    print("     %-26s vs %-26s  knee differs %4.1f, IMUs differ %5.1f deg"
          % (a, b, dk, sep))
print()
print("  Every one of those is separated by the IMUs by at least %.0f deg, which is %.0fx what a"
      % (min(s for s, _, _, _ in saved), min(s for s, _, _, _ in saved) / SENSOR))
print("  well-mounted static accelerometer is good for. They are not close calls.")

print()
print("=" * 98)
print("  THE BLIND SPOT, which is the point of computing this rather than assuming it")
allpairs = []
for a, b in itertools.combinations(table, 2):
    (ga, _), (gb, _) = table[a], table[b]
    sep = max(ang(ga[0], gb[0]), ang(ga[1], gb[1]))
    allpairs.append((sep, a, b))
tight = [q for q in sorted(allpairs) if q[0] < SEPARABLE]
# A close pair only MATTERS if the two postures want different things from the brace. Standing
# and mid-stance are 8 deg apart because mid-stance very nearly IS standing; calling that a
# blind spot would be counting a near-duplicate as a failure.
across = [q for q in tight if (q[1] in ASSIST_OK) != (q[2] in ASSIST_OK)]
for sep, a_, b_ in tight:
    side = "both armed" if (a_ in ASSIST_OK and b_ in ASSIST_OK) else (
        "both disarmed" if (a_ not in ASSIST_OK and b_ not in ASSIST_OK) else "ACROSS THE GATE")
    print("     %-26s vs %-26s  %5.1f deg apart   %s" % (a_, b_, sep, side))
print()
if across:
    print("  The ones ACROSS THE GATE are the only ones that matter, and they need something the")
    print("  leg cannot see. A third IMU on the TRUNK settles them, and note what that sensor")
    print("  does NOT have to be: it never carries load, never sees the belt, and only has to")
    print("  report which way is down -- so it can live in the backpack with the battery.")
else:
    print("  None of them crosses the assist gate: every close pair is two postures that are")
    print("  genuinely alike and are handled the same way, which is a near-duplicate rather than")
    print("  an ambiguity. The leg alone is enough to decide whether to arm.")

print()
print("=" * 98)
print("  WHAT IT IS FOR: an assist gate that does not depend on the gait code")
print()
print("  Assist is armed only in: %s" % ", ".join(ASSIST_OK))
worst = 999.0
for a in ASSIST_OK:
    for b in table:
        if b in ASSIST_OK:
            continue
        (ga, _), (gb, _) = table[a], table[b]
        worst = min(worst, max(ang(ga[0], gb[0]), ang(ga[1], gb[1])))
print("  and the closest any armed posture comes to any disarmed one is %.1f deg." % worst)
print()
print("  This is worth more than the classification it enables. 28.2 N.m on a post-operative")
print("  knee, in bed, at three in the morning, because the gait state machine mis-fired, is the")
print("  failure this design should be most afraid of -- and the gate against it is two numbers")
print("  from an accelerometer that cannot drift, evaluated outside the gait code entirely.")
print("  ELECTRONICS.md's existing argument is the same one a level down: 'keeping the gait")
print("  logic off the motor controller means a bug in the gait code can only ever' misbehave")
print("  within limits something else is enforcing.")
print()
print("  WHAT IT IS NOT FOR. Fused well, a pair of MPU-6050s is good for about a degree")
print("  dynamically. The structural compliance 431_shank_2040.py measured when it sized the")
print("  shank rail is the same order, so an IMU pair CANNOT see it, and must not be used as an")
print("  angle reference against the AS5048A's 0.022 deg. It is a gross-disagreement detector:")
print("  cuff slip, a skipped tooth at 12.9 deg, and which way the patient is lying.")
