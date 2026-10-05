# -*- coding: utf-8 -*-
"""Open-ended HTD-8M cut to length instead of a 742 mm closed loop? Yes, and the clamp exists.

Asked at the bench: "do I really need closed loop htd 8m belt? That is much harder to find than
open loop and we can just close it ourselves with some screws on the gantry right?"

THE GANTRY IS ALREADY THE CLAMP. ASSEMBLY step 13 describes the belt tunnel: "the tunnel's
inboard wall carries five HTD-8M grooves at 8 mm pitch over Y 144...186, and the belt's own teeth
sit in them -- the outboard wall at X -38.70 stops it backing out of mesh, the floor and roof stop
it climbing". So the carriage does not grip the belt by friction and it is not a special part to
be designed: it is a toothed channel the belt already lies in, transmitting 764 N through five
teeth at 153 N each.

Cutting the loop inside that channel changes the topology not at all. 390_onescrew_section.py's
argument survives intact -- "move the clamp by d and the belt circulates by d, turning both
pulleys by d/R", and both strands still join the carriage to the capstan as springs in parallel,
which is 380's corrected lost-motion figure of +0.14 deg.

THE ONE REAL DIFFERENCE IS WHAT THE CLAMP HOLDS. A continuous belt through a toothed channel
transmits only the DIFFERENCE between the tensions either side of it: 764 N, which is where
ASSEMBLY's 153 N per tooth comes from. Two cut ends each hold their OWN tension, and the tight
side's is the full preload-plus-differential. That is the number this file is really about.

    python scripts/448_open_belt.py
"""
import math

import FreeCAD

DOC = r"C:/Users/Josh/KneeExo_v6.FCStd"
PITCH = 8.0
R_CAP = 29 * PITCH / (2 * math.pi)
TAU_KNEE = 28.2
F_DIFF = TAU_KNEE * 1000.0 / R_CAP          # 764 N differential
T_IDLER = 1828.0                            # BOM S2c: the idler axle reaction = 2 x tight side
BELT_W = 30.0
GROOVE_H = 3.45                             # 421's half-ellipse radial semi-axis
TUNNEL_Y = (144.0, 186.0)                   # ASSEMBLY step 13
N_GROOVE = 5
ACCEPTED_PER_TOOTH = F_DIFF / N_GROOVE      # 153 N -- the load this design already accepts
BELT_T = 5.6                                # HTD-8M total thickness, back to tooth tip
LOOP_EXACT = 2 * math.pi * R_CAP + 2 * 255.0

doc = FreeCAD.openDocument(DOC)
g = {o.Name: o for o in doc.Objects}

print("=" * 98)
print("1.  WHAT THE CARRIAGE HAS TO WORK WITH")
print("=" * 98)
cb = g["P3_Carriage"].Shape.BoundBox
print("  P3_Carriage        X %6.1f..%6.1f  Y %6.1f..%6.1f  Z %6.1f..%6.1f   (%.0f mm of Y)"
      % (cb.XMin, cb.XMax, cb.YMin, cb.YMax, cb.ZMin, cb.ZMax, cb.YLength))
print("  the belt tunnel    Y %6.1f..%6.1f   %d grooves at %.0f mm pitch = %.0f mm"
      % (TUNNEL_Y[0], TUNNEL_Y[1], N_GROOVE, PITCH, TUNNEL_Y[1] - TUNNEL_Y[0]))
print("  so there is %.0f mm of carriage above the tunnel and %.0f mm below it."
      % (cb.YMax - TUNNEL_Y[1], TUNNEL_Y[0] - cb.YMin))

print()
print("=" * 98)
print("2.  THE TENSIONS, WHICH IS THE WHOLE ANSWER")
print("=" * 98)
t_tight = T_IDLER / 2.0
t_slack = t_tight - F_DIFF
print("  idler axle reaction  %.0f N   (BOM S2c, the largest single load in the machine)" % T_IDLER)
print("  tight side           %.0f N   = half of it" % t_tight)
print("  slack side           %.0f N   = tight - the %.0f N differential" % (t_slack, F_DIFF))
print()
print("  A CONTINUOUS belt through the tunnel transmits only the difference, %.0f N over %d"
      % (F_DIFF, N_GROOVE))
print("  teeth = %.0f N each. That is the number ASSEMBLY step 14 quotes and the design accepts."
      % ACCEPTED_PER_TOOTH)
print()
print("  TWO CUT ENDS each hold their own tension. The tight end holds %.0f N, not %.0f --"
      % (t_tight, F_DIFF))
print("  %.2fx more -- and the slack end holds %.0f N." % (t_tight / F_DIFF, t_slack))

need_tight = int(math.ceil(t_tight / ACCEPTED_PER_TOOTH))
need_slack = max(2, int(math.ceil(t_slack / ACCEPTED_PER_TOOTH)))
print()
print("  at the same %.0f N per tooth this design already signs up to:" % ACCEPTED_PER_TOOTH)
print("     tight end   %2d teeth = %3.0f mm of channel" % (need_tight, need_tight * PITCH))
print("     slack end   %2d teeth = %3.0f mm" % (need_slack, need_slack * PITCH))
print("     together    %2d teeth = %3.0f mm, against the %.0f mm the tunnel has now and the"
      % (need_tight + need_slack, (need_tight + need_slack) * PITCH,
         TUNNEL_Y[1] - TUNNEL_Y[0]))
print("                 %.0f mm of carriage it has to fit inside." % cb.YLength)
fits = (need_tight + need_slack) * PITCH <= cb.YLength
print("     %s" % ("END TO END IN ONE CHANNEL: it fits, with %.0f mm to spare."
                   % (cb.YLength - (need_tight + need_slack) * PITCH) if fits else
                   "ONE CHANNEL IS NOT ENOUGH -- the ends have to stack."))

print()
print("=" * 98)
print("3.  HOW THE ENDS ACTUALLY TERMINATE")
print("=" * 98)
print("  Two ways, and the usual printer trick is the worse one here.")
print()
print("  DOUBLE BACK (what a 3D printer does): the end turns 180 and its teeth mesh with its own.")
print("  HTD-8M's minimum pulley is about 14T, so the minimum bend diameter is %.0f mm -- and the"
      % (14 * PITCH / math.pi))
print("  belt is %.1f mm thick and %.0f mm wide. A U-turn that size inside the carriage costs"
      % (BELT_T, BELT_W))
print("  more room than the straight teeth it is trying to save. Do not.")
print()
print("  STRAIGHT TOOTHED CLAMP: the end lies flat in the channel, teeth in the grooves, and a")
print("  toothed plate screws down over it. The screws supply only the normal force that keeps")
print("  the teeth meshed -- the LOAD goes through the teeth in shear, exactly as it does in the")
print("  tunnel today. This is the one to build, and it is the tunnel it already is, lengthened,")
print("  with a lid.")
print()
sq = BELT_W * GROOVE_H
print("  groove wall %.0f x %.2f mm = %.0f mm2 per tooth; %.0f N on the worst one is %.2f MPa,"
      % (BELT_W, GROOVE_H, sq, ACCEPTED_PER_TOOTH, ACCEPTED_PER_TOOTH / sq))
print("  which is the 1.5 MPa ASSEMBLY step 14 already quotes. Nothing changes but the count.")

print()
print("=" * 98)
print("4.  WHAT YOU GAIN, BESIDES BEING ABLE TO BUY IT")
print("=" * 98)
print("  LENGTH STOPS BEING QUANTISED. The loop wants %.1f mm. The nearest closed-loop size is"
      % LOOP_EXACT)
std = round(LOOP_EXACT / PITCH) * PITCH
print("  %.0f mm (%dT), so a bought loop arrives %+.1f mm long and the idler has to swallow it"
      % (std, int(std / PITCH), std - LOOP_EXACT))
print("  on a spring with %.0f mm of working travel -- %.1f mm of centre distance out of %.0f."
      % (3.0, (std - LOOP_EXACT) / 2.0, 3.0))
print("  Cut to length, that error is zero and the idler's slot is pure adjustment again.")
print()
print("  RE-TENSIONING BECOMES POSSIBLE. A belt beds in and stretches perhaps 0.2% in its first")
print("  hours -- %.1f mm here. On a closed loop that is the spring's entire job. With a clamped"
      % (LOOP_EXACT * 0.002))
print("  end you simply pull it through one tooth, %.0f mm, and re-clamp." % PITCH)
print()
print("  AND IT SURVIVES A MISTAKE. If the belt is cut short, you have lost a belt. If a closed")
print("  loop turns out to be the wrong length, you have lost a belt AND a week.")

print()
print("=" * 98)
print("5.  WHAT YOU GIVE UP")
print("=" * 98)
print("  222_anim_export.py records the reason the loop was chosen: \"one clamp on a closed loop")
print("  cannot drift\". A loop has no termination to fail; cut ends have two, and the tight one")
print("  holds %.0f N on a leg that a person is standing on. That is a real difference in kind," % t_tight)
print("  not degree -- but it is the same difference every printed part in this machine already")
print("  carries, and a toothed clamp loaded in tooth shear is not a friction joint waiting to")
print("  slip. Torque the lid, mark it, and check it at the same interval as the pretension.")
print()
print("  P3_GantryPlate_Printed is redrawn either way -- the flanged nut and the DSG16H housing")
print("  from 446_sfu1605_set.py already force that. Lengthening the tunnel to %d grooves and"
      % (need_tight + need_slack))
print("  adding a lid is work that lands in the same redraw rather than on top of it.")

print()
print("=" * 98)
order = LOOP_EXACT + (need_tight + need_slack) * PITCH + 100.0
print("  VERDICT: yes, buy it open-ended. %.0f mm of path, %d teeth of clamped end (%.0f mm), and"
      % (LOOP_EXACT, need_tight + need_slack, (need_tight + need_slack) * PITCH))
print("  100 mm to hold on to while threading it = %.0f mm. It is sold by the metre, so order a"
      % order)
print("  metre and have %.0f mm of spare to re-terminate with if the first clamp is wrong."
      % (1000.0 - order))
print("  Keep the idler's slotted mount. Drop K4's spring only once the clamp is proven, not now.")
