# -*- coding: utf-8 -*-
"""The bench concept: rod through two KFL001 blocks, pulley and rail clamped to it. Mostly right.

Brought from the bench as "knee concept test.FCStd", with the note that the bolt holes through the
aluminium plates, the flange couplings and the extrusion are not drawn but should be imagined
linking everything together.

WHAT IT IS. The knee axis becomes a dia 12 ROD running in two bought KFL001 flange bearing units
72 mm apart. Everything that belongs to the shank -- the HTD-8M capstan and the 2040 rail's socket
-- is clamped onto that rod as one bolted stack: aluminium plate, rail support, aluminium plate,
pulley, aluminium plate, with three rigid flange couplings inside holding the stack to the rod.
The blocks are the thigh side. The stack is the shank side.

WHAT IT REPLACES. 418_knee_bearing.py put ONE 6001 in the yoke, bonded into printed PETG, with the
hub's two printed lugs straddling it: "the load arrives symmetrically about the yoke ... one
bearing there is centred and sees no cocking moment". That is true of the limb's load and NOT true
of the belt's, which is applied across the capstan's 30 mm land at Z 96..126 while the bearing is
at Z 80..88 -- 30 mm off to one side, reacted as a couple by two printed bores. Two bearings 72 mm
apart retire that argument rather than winning it, and a bolt-in steel housing retires the bonded
seat with it. THAT IS THE REAL CONTRIBUTION HERE and it is worth the redesign it costs.

ONE NUMBER IN IT IS FATAL AND IT IS NOT THE ARCHITECTURE. The pulley is drawn dia 120.

    freecadcmd.exe scripts/453_concept_knee.py
"""
import math

import FreeCAD

CONCEPT = r"C:/Users/Josh/Downloads/knee concept test.FCStd"
MAIN = r"C:/Users/Josh/KneeExo_v6.FCStd"

PITCH = 8.0
PLD = 0.686
LEAD = 5.0
LINK = 38 / 20.0
TAU_KNEE = 28.2
J_ROTOR, J_LIMB = 3.10e-4, 0.30
THREAD = 135.0                  # mm of thread on the bought SFU1605, 446_sfu1605_set.py
NUT_BODY = 35.0
STROKE_NOW = 68.3               # BOM D1
R_NOW = 29 * PITCH / (2 * math.pi)
PETG_BEARING = 40.0

doc = FreeCAD.openDocument(CONCEPT)
g = {o.Label: o for o in doc.Objects if o.isDerivedFrom("Part::Feature")}
pul = g["htd 8m pulley"].Shape.BoundBox
brg = [g[k].Shape.BoundBox for k in g if k.startswith("KFL001")]
span = abs((brg[0].XMin + brg[0].XMax) / 2 - (brg[1].XMin + brg[1].XMax) / 2)

print("=" * 98)
print("1.  THE PULLEY DIAMETER, WHICH BREAKS THE SCREW")
print("=" * 98)
tip_r = max(pul.YLength, pul.ZLength) / 2.0
pitch_r = tip_r + PLD
teeth = 2 * math.pi * pitch_r / PITCH
print("  drawn dia %.0f -> tip r %.1f, pitch r %.2f, %.1f teeth. The capstan today is 29T at"
      % (2 * tip_r, tip_r, pitch_r, teeth))
print("  pitch r %.2f." % R_NOW)
print()
swing = STROKE_NOW / R_NOW
print("  the knee's modelled swing is %.3f rad (%.0f deg), set by the %.1f mm stroke at r %.2f."
      % (swing, math.degrees(swing), STROKE_NOW, R_NOW))
avail = THREAD - NUT_BODY
print("  travel available on the bought screw: %.0f mm of thread less the %.0f mm nut = %.0f mm."
      % (THREAD, NUT_BODY, avail))
print()
print("  %-14s %9s %10s %9s %9s %10s %9s"
      % ("capstan", "teeth", "stroke", "fits?", "N total", "refl J", "vs limb"))
for r in (tip_r, 45.0, R_NOW, 30.0):
    pr = r + PLD if r > 50 else r
    t = 2 * math.pi * pr / PITCH
    stroke = swing * pr
    n = (2 * math.pi * pr / LEAD) / LINK
    j = J_ROTOR * n ** 2
    tag = "" if stroke < avail else "   <-- NEEDS %.0f mm OF TRAVEL" % stroke
    if j / J_LIMB > 0.75 and not tag:
        tag = "   <-- %.2fx the limb unpowered" % (j / J_LIMB)
    print("  r %-12.2f %8.1f %8.1f mm %8s %8.1f:1 %9.3f %8.2fx%s"
          % (pr, t, stroke, "yes" if stroke < avail else "NO", n, j, j / J_LIMB, tag))
print()
print("  dia %.0f asks the ball nut for %.0f mm of travel and the screw has %.0f. It also puts"
      % (2 * tip_r, swing * pitch_r, avail))
print("  %.2fx the limb's own inertia back on the leg, which is the number 404_link_ratio.py"
      % (J_ROTOR * ((2 * math.pi * pitch_r / LEAD) / LINK) ** 2 / J_LIMB))
print("  rejected a 4:1 reduction over. The capstan has to come back to 29T / dia %.2f."
      % (2 * (R_NOW - PLD)))
print("  Nothing else in the concept depends on it: the coupling flanges are r 16 and sit inside")
print("  a 29T rim at r %.2f with %.1f mm of web to spare." % (R_NOW - PLD, R_NOW - PLD - 16.0))

print()
print("=" * 98)
print("2.  THE TORQUE PATH -- the thing the imagined bolts are actually doing")
print("=" * 98)
f_grub = TAU_KNEE * 1000.0 / 6.0
print("  If the knee's %.1f N.m had to reach the rod through the couplings' grub screws, that is"
      % TAU_KNEE)
print("  %.0f N tangential on a dia 12 shaft through M4 grubs. A coupling this size is rated"
      % f_grub)
print("  single figures of N.m. It would strip on the first stair.")
print()
print("  It does not have to, and this is the part the concept gets right: the stack is bolted")
print("  face to face, so the torque goes PULLEY -> PLATE -> RAIL SUPPORT -> 2040 and never")
print("  enters the rod at all. The rod is a shaft in two bearings, not a torque member, and the")
print("  couplings only locate the stack on it. But that makes the bolts structural:")
print()
print("  %-24s %9s %10s %10s %9s" % ("bolt pattern", "per bolt", "in pulley", "in support", "factor"))
for nb, r, d in ((4, 20.0, 5.0), (4, 25.0, 5.0), (6, 30.0, 5.0), (6, 35.0, 6.0)):
    f = TAU_KNEE * 1000.0 / (nb * r)
    s_pul = f / (d * pul.XLength)
    s_sup = f / (d * 20.0)
    print("  %-24s %7.0f N %8.2f MPa %8.2f MPa %8.0f"
          % ("%d x M%.0f at r %.0f" % (nb, d, r), f, s_pul, s_sup, PETG_BEARING / s_sup))
print()
print("  Anything at r 25 or beyond is comfortable. Put them OUTSIDE the couplings' dia 32")
print("  flanges, which also keeps them clear of the boss pockets.")
print()
print("  THE SAME CREEP WARNING AS 449_flange_hub.py APPLIES, HARDER. These bolts clamp aluminium")
print("  onto %.0f mm of PETG at the pulley and 20 mm at the support, and PETG flows under"
      % pul.XLength)
print("  sustained preload. Put a steel spacer in every through-hole, cut 0.1 mm proud of the")
print("  plastic, so the plates clamp steel to steel and the PETG only ever bears sideways.")

print()
print("=" * 98)
print("3.  WHAT THE TWO BEARINGS BUY")
print("=" * 98)
print("  bearing centres %.0f mm apart, pulley centred at X %.0f -- between them, %.0f mm from"
      % (span, (pul.XMin + pul.XMax) / 2, abs((pul.XMin + pul.XMax) / 2 - -63.0)))
print("  one and %.0f mm from the other." % abs((pul.XMin + pul.XMax) / 2 - 9.0))
print()
print("  Today the belt's 1064 N resultant lands on a 30 mm land at Z 96..126 while the only")
print("  bearing is at Z 80..88. The offset is reacted as a couple by two PRINTED bores on the")
print("  pin. Here both bearings are steel, bought, and the load lands between them. 451's 99 MPa")
print("  of pin bending becomes bending over the two short unsupported gaps instead -- about")
print("  11 and 12 mm -- because the bolted stack reinforces the rod everywhere else.")
print()
print("  It also deletes 418's bonded seat: 'a press fit into PETG does not hold: the plastic")
print("  creeps under hoop stress and thermal cycling and the interference is gone within")
print("  months'. A KFL001 is a steel housing on two bolts. That problem simply stops existing.")

print()
print("=" * 98)
print("4.  WHAT THE CONCEPT DOES NOT YET HAVE")
print("=" * 98)
allb = None
for o in g.values():
    b = o.Shape.BoundBox
    allb = b if allb is None else (allb.add(b) or allb)
rod = g["12mm steel rod"].Shape.BoundBox
rb = [b for b in brg if b.XMax > 0][0]
print("  a. THE ENCODER. The rod ends at X %.0f, inside the right-hand block's X %.0f..%.0f."
      % (rod.XMax, rb.XMin, rb.XMax))
print("     There is nowhere for E5's magnet or E4's AS5048A. Extend the rod ~10 mm past the")
print("     block and hang the sensor off that block's own flange: the block is the thigh and the")
print("     rod is the shank, so the relative rotation it reads is exactly the knee angle.")
print("  b. WHAT THE KFL001s BOLT TO. Both flanges want faces perpendicular to the knee axis,")
print("     %.0f mm apart, straddling the whole joint. That is P1_KneeYoke redrawn as a clevis,"
      % (rb.XMax - [b for b in brg if b.XMax < 0][0].XMin))
print("     and it is the single biggest piece of work this concept implies.")
print("  c. THE LIMB. There is no REF_Knee in the file, so the one dimension that decides whether")
print("     this is wearable is unchecked:")
main = FreeCAD.openDocument(MAIN)
mg = {o.Name: o for o in main.Objects}
kb = mg["REF_Knee"].Shape.BoundBox
sb = mg["P20_KneeShroud"].Shape.BoundBox
print("       today  the limb's lateral surface is Z %.0f and the outermost hardware is Z %.0f"
      % (kb.ZMax, sb.ZMax))
print("              -- %.0f mm of knee standing off the leg." % (sb.ZMax - kb.ZMax))
print("       this   %.0f mm across the whole assembly, before any yoke to carry the blocks."
      % allb.XLength)
print("     A knee brace hinge is usually 15-25 mm. %.0f is already a lot and %.0f is more, and"
      % (sb.ZMax - kb.ZMax, allb.XLength))
print("     it is the dimension that decides whether the leg can pass its neighbour when walking.")
print("     MEASURE IT AGAINST THE LIMB BEFORE ANYTHING ELSE IN THIS CONCEPT IS DRAWN PROPERLY.")

print()
print("=" * 98)
print("  VERDICT: the architecture is better than what it replaces and the dia 120 is not part")
print("  of it. Bring the capstan back to 29T, bolt the stack at r >= 25 with steel spacers in")
print("  the through-holes, extend the rod past the right-hand block for the encoder, and then")
print("  the open question is the only one that was ever hard: what carries the two blocks, and")
print("  how wide does that make the knee.")
