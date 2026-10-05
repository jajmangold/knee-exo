# -*- coding: utf-8 -*-
"""The SFU1605 + BK/BF12 set is bought. What it changes, and the one cut that saves the drive end.

Bought at the bench: "200mm SFU1605 Ball Screw Set, RM1605 Ball Screw with Metal Ball Screw Nut
and Set BK/BF12 for CNC Machine, Diameter 16mm, 5mm Lead", and the product photo shows what is
actually in the box: BK12, BF12, the M12 locknut, a circlip, the screw with its nut already on it,
a DSG16H aluminium nut housing, and a flexible shaft coupler.

THREE BOM LINES ARE ANSWERED BY THE BOX.
  D8   KP08/KFL08  -> BF12, included. 445_screw_foot.py went looking for a KP/KFL mounting face,
                      found none, and said the right part was an FF10/BF10. It is in the box.
  D8a  608-2RS     -> BK12, included, and the fixed end is machined for it.
  D9   coupler     -> included, and not needed: the motor is belted, not coaxial.

TWO BOM LINES ARE NOW KNOWN TO BE WRONG.
  D3 calls the nut FLANGELESS and has the gantry trap it axially between two plates with two M5
     set screws bearing on the body. The photo shows a flanged nut -- SFU/RM nuts always are --
     with a bolt circle through the flange. The set screws, the flat to file, and the reasoning
     in 424_belt_tunnel.py about a 36.4 mm bore severing a 40 mm housing are all answering a
     question that does not exist. Worse and better at once: the box also contains the DSG16H
     housing, which is the bought version of P3_GantryPlate's whole job.
  D7 specifies a 32T motor pulley. At a 5 mm lead that is the wrong pulley -- see section 1.

THE LEAD IS THE WHOLE RATIO, which 443_screw_sourcing.py said and this set makes real: 5 mm, not
10. N_screw = 2*pi*R_cap/lead doubles to 46.4:1 before the link belt, so the link belt has to give
some back or the leg feels 87% heavier with the power off.

THE AWKWARD PART IS THE STACK ORDER. 433_drive_flip.py put the 20T pulley INBOARD of the screw's
top bearing and seated that bearing in the motor plate itself -- one plate holding the motor and
the screw. BK12 machining inverts it: from the tip, dia 10 x 15 for the coupler/pulley, then
M12 x 1 x 14 for the locknut, then dia 12 x 25 for the bearing. The pulley ends up 39 mm OUTBOARD
of the bearing, past the motor's own face, and the motor has to climb to meet it.

So there are two ways, and they cost different things. Both are priced below.

    python scripts/446_sfu1605_set.py
"""
import math

# ---------------------------------------------------------------- what was bought
LEAD = 5.0
SCREW_L = 200.0
# The machined ends, from the vendor drawing for the same dia 16 / BK-BF12 family, and consistent
# with the product photo. MEASURE THESE: the screw is in hand and these four numbers set every Y
# station below.
FF_J = (10.0, 11.0)            # floating end: dia 10 x 11
FK_PULLEY = (10.0, 15.0)       # fixed end, outboard: dia 10 x 15, where the coupler was meant to go
FK_THREAD = (12.0, 14.0)       # fixed end, middle: M12 x 1 x 14, the locknut
FK_BRG = (12.0, 25.0)          # fixed end, inboard: dia 12 x 25, the bearing seat

# ---------------------------------------------------------------- the drivetrain as it stands
R_CAP = 29 * 8.0 / (2 * math.pi)        # 36.923, the bought 29T capstan
TAU_KNEE = 28.2                         # N.m at the knee
ETA = 0.90 * 0.97                       # screw x belt
J_ROTOR, J_LIMB = 3.10e-4, 0.30         # kg.m2
KT = 9.549 / 170.0                      # C6374 at 170 Kv
I_CONT = 40.0                           # A
RPM_SCREW_10 = 1160.0                   # screw rpm at a 10 mm lead, set by gait speed
PITCH5 = 5.0
C_LINK = 60.83                          # motor (X -104, Z 62) to screw (X -62, Z 106)
POD_INNER_R = 32.0                      # 433's belt-guard bore
CAN_D = 63.0                            # the motor pulley must stay inside this

# the model's current Y stations, 433_drive_flip.py
CUR = dict(screw=(57.0, 235.0), thread=(71.0, 204.0), belt=(208.0, 223.0),
           plate=(223.0, 231.0), brg=(223.0, 230.0), motor=(231.0, 305.0), cap=334.0)
NUT_SWEEP = 110.0                       # mm of thread the nut's travel consumes, D1
F_NUT = TAU_KNEE * 1000.0 / R_CAP       # 764 N


def pd(t):
    return t * PITCH5 / math.pi


def belt_len(t1, t2, c):
    d1, d2 = pd(t1), pd(t2)
    return 2 * c + math.pi * (d1 + d2) / 2.0 + (d1 - d2) ** 2 / (4 * c)


print("=" * 98)
print("1.  THE RATIO, now that the lead is %.0f mm" % LEAD)
print("=" * 98)
n_screw = 2 * math.pi * R_CAP / LEAD
print("  capstan R %.3f / lead %.0f  ->  %.2f screw turns per knee turn, before the link belt"
      % (R_CAP, LEAD, n_screw))
print()
print("  %-18s %9s %8s %9s %9s %9s %14s"
      % ("motor : screw", "N total", "amps", "refl J", "vs limb", "mot rpm", "link belt"))
for mt in (20, 25, 32, 38, 44):
    if pd(mt) > CAN_D:
        continue
    od = mt / 20.0
    n = n_screw / od
    amps = TAU_KNEE / (n * ETA) / KT
    j = J_ROTOR * n ** 2
    rpm = RPM_SCREW_10 * (10.0 / LEAD) / od
    teeth = belt_len(mt, 20, C_LINK) / PITCH5
    tag = ""
    if amps > I_CONT:
        tag = "  <-- over %.0f A" % I_CONT
    elif j / J_LIMB > 0.75:
        tag = "  <-- the leg feels %.0f%% heavier unpowered" % (100 * j / J_LIMB)
    elif abs(teeth - round(teeth)) < 0.1:
        tag = "  <-- and a whole %.0fT belt" % round(teeth)
    print("  %-18s %8.1f:1 %7.1f A %9.3f %8.2fx %9.0f %9.0f/%.1fT%s"
          % ("%dT : 20T" % mt, n, amps, j, j / J_LIMB, rpm,
             teeth * PITCH5, teeth, tag))
print()
print("  BUY THE 38T. It is the only pulley that fits inside the dia %.0f can, keeps the reflected"
      % CAN_D)
print("  inertia under 0.75x the limb, stays under the motor's %.0f A continuous, AND lands on a"
      % I_CONT)
print("  whole belt size. BOM line D7's 32T would be %.2fx the limb and want a %.1fT belt."
      % (J_ROTOR * (n_screw / 1.6) ** 2 / J_LIMB, belt_len(32, 20, C_LINK) / PITCH5))
print()
r38 = pd(38) / 2.0 + 2.0
print("  one interference it brings: the 38T belt run reaches r %.2f and 433's guard bore is"
      % r38)
print("  r %.1f -- the pod has to grow %.1f mm there." % (POD_INNER_R, r38 - POD_INNER_R))

print()
print("=" * 98)
print("2.  IS THERE ENOUGH THREAD ON A 200 mm SCREW?")
print("=" * 98)
machined = FF_J[1] + FK_PULLEY[1] + FK_THREAD[1] + FK_BRG[1]
thread = SCREW_L - machined
print("  %.0f mm bought, %.0f machined away (%.0f floating, then %.0f + %.0f + %.0f fixed),"
      % (SCREW_L, machined, FF_J[1], FK_PULLEY[1], FK_THREAD[1], FK_BRG[1]))
print("  leaving %.0f mm of thread. The nut's travel needs %.0f mm (D1), so %.0f mm spare.%s"
      % (thread, NUT_SWEEP, thread - NUT_SWEEP, "" if thread > NUT_SWEEP else "   <-- SHORT"))
print("  The model's thread is Y %.0f..%.0f; %.0f mm reaches Y %.0f, so it stays where it is."
      % (CUR["thread"][0], CUR["thread"][1], thread, CUR["thread"][0] + thread))

print()
print("=" * 98)
print("3.  PATH A -- use BK12 the way it is designed to be used")
print("=" * 98)
y0 = CUR["thread"][0] - FF_J[1]
t0 = CUR["thread"][0]
t1 = t0 + thread
b0, b1 = t1, t1 + FK_BRG[1]
l0, l1 = b1, b1 + FK_THREAD[1]
p0, p1 = l1, l1 + FK_PULLEY[1]
print("  screw bottom     Y %6.1f    (was %.0f: the floating journal is %.0f mm, not 14)"
      % (y0, CUR["screw"][0], FF_J[1]))
print("  BF12 on dia %-3.0f  Y %6.1f .. %6.1f    its flange bolts to a plate below Y %.0f"
      % (FF_J[0], y0, t0, y0))
print("  thread           Y %6.1f .. %6.1f" % (t0, t1))
print("  BK12 on dia %-3.0f  Y %6.1f .. %6.1f    its flange bolts to a plate at Y %.0f"
      % (FK_BRG[0], b0, b1, b0))
print("  M12 locknut      Y %6.1f .. %6.1f" % (l0, l1))
print("  20T pulley       Y %6.1f .. %6.1f    dia %.0f bore, %.0f mm wide"
      % (p0, p1, FK_PULLEY[0], FK_PULLEY[1]))
print("  screw top        Y %6.1f    (was %.0f)" % (p1, CUR["screw"][1]))
print()
shift = p1 - CUR["belt"][1]
print("  The belt plane moves from Y %.0f..%.0f to Y %.0f..%.0f and the motor's face has to"
      % (CUR["belt"][0], CUR["belt"][1], p0, p1))
print("  follow it: Y %.0f becomes Y %.0f, so the motor, the pod, P27 and P22_DriveCap all climb"
      % (CUR["motor"][0], p1))
print("  %+.0f mm and the cap goes from Y %.0f to Y %.0f." % (shift, CUR["cap"], CUR["cap"] + shift))
print("  And the screw's bearing plate (Y %.0f) and the motor's plate (Y %.0f) are now %.0f mm"
      % (b0, p1, p1 - b0))
print("  apart with the belt between them, so 433's ONE plate carrying both becomes a two-plate")
print("  cage. Stiffer -- and a redraw of the most finished part of the machine.")

print()
print("=" * 98)
print("4.  PATH B -- cut %.0f mm off the fixed end and keep 433's drive end"
      % (FK_PULLEY[1] + FK_THREAD[1]))
print("=" * 98)
print("  Part off the dia %.0f tip and the M12 thread. What is left of the fixed end is a plain"
      % FK_PULLEY[0])
print("  dia %.0f x %.0f journal, long enough for BOTH the pulley and a bearing -- which is the"
      % (FK_BRG[0], FK_BRG[1]))
print("  arrangement 433 already built and 438/439 already cleared, just on dia %.0f not dia 8."
      % FK_BRG[0])
print()
pw, bw = 15.0, 8.0
print("  dia %.0f journal  Y %6.1f .. %6.1f    (%.0f mm)" % (FK_BRG[0], b0, b1, FK_BRG[1]))
print("     20T pulley    Y %6.1f .. %6.1f    dia %.0f bore, %.0f wide"
      % (b0, b0 + pw, FK_BRG[0], pw))
print("     6001-2RS      Y %6.1f .. %6.1f    %.0f x %.0f x %.0f, in the motor plate"
      % (b1 - bw, b1, FK_BRG[0], 28.0, bw))
print("     %.0f mm of journal spare between them for the bearing's shoulder"
      % (FK_BRG[1] - pw - bw))
print("  screw top        Y %6.1f    -- %.0f mm of the %.0f bought, %.0f mm parted off"
      % (b1, b1 - y0, SCREW_L, SCREW_L - (b1 - y0)))
print()
print("  belt plane Y %.0f..%.0f against 433's Y %.0f..%.0f: %+.0f mm, and the motor does not move."
      % (b0, b0 + pw, CUR["belt"][0], CUR["belt"][1], b0 - CUR["belt"][0]))
print("  The motor plate's bearing pocket goes from dia %.0f x %.0f to dia %.0f x %.0f."
      % (22.0, 7.0, 28.0, 8.0))
print()
print("  WHAT IT COSTS. BK12 goes unused, and with it the preloaded pair: the screw's %.0f N of"
      % F_NUT)
print("  thrust then goes through one deep-groove 6001, which takes roughly a quarter of its")
print("  radial rating axially -- order 1.2 kN against %.0f N, so it holds, with less axial"
      % F_NUT)
print("  stiffness and a shorter life than the block already in the box. And parting a hardened")
print("  journal wants a cut-off wheel, a chamfer and a deburr, not enthusiasm.")

print()
print("=" * 98)
print("5.  THE NUT, WHICH IS FLANGED, AND THE HOUSING THAT CAME WITH IT")
print("=" * 98)
print("  BOM D3 says flangeless and has P3_GantryPlate trap the nut axially between two plates")
print("  with two M5 set screws on a filed flat. The photo shows a flanged nut and a DSG16H")
print("  aluminium housing, which is the bought version of that whole job: the nut bolts to the")
print("  housing through its flange, and the housing presents flat faces with tapped holes.")
print()
print("  That is a simplification, not a problem -- but it is a redraw of P3_GantryPlate either")
print("  way, and the housing is aluminium, so it does not deform under the %.0f N the way a"
      % F_NUT)
print("  printed pocket would. It also moves the nut's envelope: the model carries a %.0f x %.0f"
      % (36.0, 36.0))
print("  x %.0f box for a flangeless nut and a DSG16H is bigger than that in every direction."
      % 42.0)

print()
print("=" * 98)
print("  RECOMMENDATION")
print("=" * 98)
print("  Path B -- not because it is cheaper, but because of what each path puts at risk. Path A")
print("  moves the belt plane %+.0f mm and turns the single plate holding the motor and the screw"
      % shift)
print("  into a cage: that is 433, 434, 438 and 439 all redrawn, and the sleeve clearance at the")
print("  drive end is 1.6 mm. Every one of those scripts exists because something there was wrong")
print("  once. Path B changes two numbers -- a bearing pocket and a pulley bore -- and leaves the")
print("  geometry that has already been verified alone.")
print()
print("  Either way, keep BF12. It is exactly the part 445 asked for, the lower end is the end")
print("  that actually needed a block, and P32_ScrewFoot is now drawable because the flange is in")
print("  your hand.")
print()
print("  TO BUY, and it is a short list now:")
print("     * HTD-5M 38T pulley, dia 8 bore, 15 mm wide     (the motor -- NOT the 32T in D7)")
print("     * HTD-5M 20T pulley, 15 mm wide, bore dia %.0f for Path B or dia %.0f for Path A"
      % (FK_BRG[0], FK_PULLEY[0]))
print("                                                     (the screw. NOT the dia 8 in D7:")
print("                                                      the two paths put the pulley on")
print("                                                      different journals, so settle the")
print("                                                      path before ordering this one)")
print("     * HTD-5M closed loop, %.0f mm / %.0fT, 15 mm wide  (the link belt)"
      % (round(belt_len(38, 20, C_LINK) / PITCH5) * PITCH5, round(belt_len(38, 20, C_LINK) / PITCH5)))
print("     * 6001-2RS                                      (Path B only)")
print()
print("  MEASURE BEFORE ANY OF THIS GOES INTO CAD -- it is all in your hands now:")
print("     1. the screw's four machined lengths. Every Y station above is the vendor drawing")
print("        for a 1610, not a measurement of the screw you own.")
print("     2. BF12: flange bolt pattern and thickness, bore-to-mounting-face offset, body size.")
print("        This is what P32_ScrewFoot's plate is drawn around.")
print("     3. BK12: the same four, in case Path A comes back.")
print("     4. the nut: flange OD, bolt circle, hole count, body OD, total length.")
print("     5. the DSG16H housing: outside dimensions and its tapped faces.")
print("     6. whether the screw is RIGHT hand. The set says RM1605; 426_screw_ends.py assumes")
print("        RH and the control sign follows it.")
