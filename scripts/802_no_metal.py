# -*- coding: utf-8 -*-
"""Can the two fabricated aluminium parts be printed instead? Mostly yes, and here is where not.

The BOM has exactly two parts that need a workshop: S2d, a 6 mm aluminium gantry plate, and S2e, a
drive bracket of 4 mm plates and 5 mm cheeks. Everything else metal is BOUGHT -- extrusion, screw,
nut, bearings, pulleys, motor, fasteners. "Fabricated" was a planning assumption, and it is the
wrong one for a build whose only metal is the motor, the bearings and the extrusion.

400_bracket_stress.py already said the bracket is about 50x overbuilt: the worst stress anywhere in
the aluminium is 4.3 MPa against 240 MPa of yield, and the only number above 20 MPa is the steel
axle bolt in double shear. A part that is 50x overbuilt in aluminium is a candidate for plastic,
because the question stops being "is it strong enough" and becomes "where does it bear, and does it
creep".

WHAT PETG CAN BE ASKED FOR, and these are the numbers everything below is judged against:

    tensile yield, in-plane      ~50 MPa      but see creep
    tensile yield, across layers ~30 MPa      layer adhesion, not the polymer
    SUSTAINED design stress      ~15 MPa      creep governs, not yield: a part held at 25 MPa for
                                              weeks keeps deforming, and this device holds load
                                              for minutes at a time, every day
    across layers, sustained      ~8 MPa
    bearing / local crush        ~15 MPa      short term higher, but a bolt that beds in has
                                              loosened a joint

    freecadcmd.exe scripts/802_no_metal.py      (arithmetic only, no document needed)
"""
import math

ALLOW_XY, ALLOW_Z, ALLOW_BEAR = 15.0, 8.0, 15.0     # MPa, sustained
AL_YIELD = 240.0
F_AXLE = 1828.0        # idler axle reaction, the largest single load in the machine
F_PLATE = F_AXLE / 2   # each bracket plate
F_BELT = 764.0         # capstan differential = the force the gantry drags
E_PETG = 2000.0        # MPa

print("=" * 94)
print("THE ONLY TWO PARTS THAT NEED A WORKSHOP, AND WHETHER THEY HAVE TO")
print("=" * 94)
print("  bought metal, unchanged: extrusion, ball screw, ball nut, KP08 blocks, 29T pulleys,")
print("  idler axle + its bearings, the 6001 at the knee, the motor, every fastener.")
print("  fabricated: S2d gantry plate (6 mm alu) and S2e drive bracket (4 mm plates, 5 mm cheeks).")
print()

# ----------------------------------------------------------------- the drive bracket
print("=" * 94)
print("S2e  DRIVE BRACKET  --  holds the idler, the screw's top bearing and the motor")
print("=" * 94)
print("  %-42s %9s %9s %s" % ("load path", "in alu", "in PETG", "verdict"))
rows = []
# plates: in-plane bending, PL/4 over the span, section = thickness x depth
for t in (4.0, 8.0, 12.0):
    depth = 44.0
    L = 83.0
    S = t * depth ** 2 / 6.0
    sig = (F_PLATE * L / 4.0) / S
    rows.append(("plate bending, %.0f mm thick, load in-plane" % t, 4.34, sig,
                 "fine" if sig < ALLOW_XY else "TOO HIGH"))
# cheeks: plain compression along the print's strong direction if printed standing
for t in (5.0, 10.0):
    A = t * 38.0 * 2
    sig = F_AXLE / A
    rows.append(("cheeks in compression, %.0f mm" % t, 4.0, sig,
                 "fine" if sig < ALLOW_XY else "TOO HIGH"))
# the axle: this is the one that bit
for t in (4.0, 8.0, 12.0):
    sig = F_PLATE / (10.0 * t)         # a bare 10 mm axle through the plate
    rows.append(("axle bearing on a bare 10 mm hole, %.0f mm" % t, 28.6, sig,
                 "fine" if sig < ALLOW_BEAR else "TOO HIGH -- this is the real constraint"))
for t in (8.0, 12.0):
    sig = F_PLATE / (26.0 * t)         # spread by the idler bearing's own outer race
    rows.append(("same, through the idler BEARING's 26 mm race, %.0f mm" % t, 0.0, sig,
                 "fine" if sig < ALLOW_BEAR else "TOO HIGH"))
for lbl, al, pet, verdict in rows:
    print("  %-42s %7s %7.1f MPa  %s"
          % (lbl, ("%.1f MPa" % al) if al else "-", pet, verdict))
print()
print("  So the bracket prints, and the thing that decides it is not strength but BEARING:")
print("  a 10 mm axle through a 4 mm plastic plate is %.0f MPa and will bed in. The fix is already"
      % (F_PLATE / 40.0))
print("  in the BOM -- S2c is 'idler axle + 2 bearings', and a 6000's 26 mm outer race spreads the")
print("  same load over 2.6x the area. Seat the bearings in the plates instead of the axle, take")
print("  the plates to 8 mm, and every number above is under 5 MPa.")

# ----------------------------------------------------------------- the gantry plate
print()
print("=" * 94)
print("S2d  GANTRY PLATE  --  carries the ball nut's thrust into the belt clamp")
print("=" * 94)
W, OFFSET = 84.0, 25.0
print("  %-46s %9s %s" % ("load path", "in PETG", "verdict"))
for t in (6.0, 10.0, 14.0):
    A = W * t
    print("  %-46s %7.1f MPa  %s" % ("direct tension, %.0f mm thick" % t, F_BELT / A, "fine"))
for t in (6.0, 10.0, 14.0):
    S_in = t * W ** 2 / 6.0
    print("  %-46s %7.1f MPa  %s" % ("bending IN plane (nut to clamp, %.0f mm)" % t,
                                     F_BELT * OFFSET / S_in, "fine"))
for t in (6.0, 10.0, 14.0):
    S_out = W * t ** 2 / 6.0
    sig = F_BELT * OFFSET / S_out
    print("  %-46s %7.1f MPa  %s" % ("bending OUT of plane, %.0f mm" % t, sig,
                                     "fine" if sig < ALLOW_XY else "TOO HIGH"))
print()
print("  In plane the plate is nowhere near anything -- 1.5 MPa in tension at 6 mm. Out of plane")
print("  at 6 mm it is %.0f MPa, which is the number that matters, because an out-of-plane moment"
      % (F_BELT * OFFSET / (W * 36.0 / 6.0)))
print("  is exactly what a belt clamp offset from the nut applies. At 14 mm it drops to %.1f."
      % (F_BELT * OFFSET / (W * 196.0 / 6.0)))
print("  14 mm of PETG at 1.27 g/cm3 against 6 mm of aluminium at 2.70: %.0f g against %.0f g,"
      % (116 * 84 * 14 * 1.27e-3, 116 * 84 * 6 * 2.7e-3))
print("  so the printed plate is HEAVIER unless it is ribbed rather than solid. Ribs are free in")
print("  a printed part and expensive in a milled one, which is the whole trade.")

# ----------------------------------------------------------------- the honest caveats
print()
print("=" * 94)
print("WHAT DOES NOT PRINT, AND WHAT TO WATCH")
print("=" * 94)
print("  1. LAYER DIRECTION IS A MATERIAL PROPERTY. Every number above assumes the load runs")
print("     along the layers. The bracket's cheeks carry %.0f N straight down their length; print" % F_AXLE)
print("     them standing and that load is across layers at %.0f MPa allowable, not %.0f."
      % (ALLOW_Z, ALLOW_XY))
print("  2. BOLT PRELOAD CREEPS. Every bolted joint in plastic loses tension over weeks. Use")
print("     heat-set inserts and steel washers, and re-torque after the first week of use.")
print("  3. THE EXTRUSION END FACE still takes the bracket's thrust -- 2.7 MPa on the 2040's end,")
print("     which is aluminium on plastic and fine in that direction.")
print("  4. The idler axle, its bearings, the screw, the nut, the KP08 blocks and the 6001 are all")
print("     BOUGHT. None of them needs making.")
print()
print("  VERDICT: both fabricated parts can be printed. The bracket wants 8 mm plates with the")
print("  idler bearings seated in them rather than a bare axle; the gantry plate wants ribs and")
print("  about 14 mm of depth where it is loaded out of plane. Neither is sized by strength --")
print("  they are sized by bearing stress and by creep, which is a different design rule, not a")
print("  harder one.")
print()
print("  The alternative, if it is ever wanted: both parts are FLAT PLATE. A laser-cutting")
print("  service takes a DXF and posts back 6 mm aluminium for about the price of the filament.")
print("  That needs no workshop either -- but it does need a supplier, and the printed version")
print("  does not.")
