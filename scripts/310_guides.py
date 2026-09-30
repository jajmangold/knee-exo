# -*- coding: utf-8 -*-
"""Carriage guide sizing: Delrin L-gibs in the V-slot vs. a recirculating linear guide.

The question is not load capacity -- everything here is enormously overspecified for the
actual reaction. It is friction, and specifically stick-slip, because this is a
torque-controlled assist that has to deliver smoothly at 10% of full assist.

Geometry is read off the model (194_layout.py, and the bounding boxes of the carriages,
nuts and belt runs), not assumed.

Run:  python scripts/310_guides.py
"""
import math

# ------------------------------------------------------------------ geometry
F_BELT = 764.0          # N, differential belt tension at peak knee torque
F_PRE = 150.0           # N, pretension
F = F_BELT + F_PRE      # N, worst-case pull on one carriage, along +Y

BELT_X = (35.55 + 41.12) / 2.0     # 38.34, belt run centreline
BELT_Z = (96.0 + 126.0) / 2.0      # 111.0
NUT_X = 58.0                        # ball screw / nut axis
NUT_Z = 106.0
CARRIAGE_L = 102.0                  # P3 spans Y 128..230

# the two Delrin gibs, from the model
GIB_OUT = dict(x=20.0, z=109.0, w=6.0, l=CARRIAGE_L)    # outboard slot tongue
GIB_SIDE = dict(x=30.0, z=98.0, w=8.0, l=CARRIAGE_L)    # side slot tongue

print("=" * 70)
print("LOAD ON THE GUIDE")
print("  belt pulls %.0f N along +Y at X = %.2f, Z = %.1f" % (F, BELT_X, BELT_Z))
print("  ball nut reacts it at X = %.1f, Z = %.1f" % (NUT_X, NUT_Z))
dx = NUT_X - BELT_X
dz = BELT_Z - NUT_Z
Mz = F * dx / 1000.0
Mx = F * dz / 1000.0
print("  offset %.2f mm in X -> %.1f N.m yaw about Z" % (dx, Mz))
print("  offset %.2f mm in Z -> %.1f N.m roll about X" % (dz, Mx))
# the guide reacts the yaw as a couple over the carriage length
R = Mz * 1000.0 / CARRIAGE_L
print("  reacted as a couple over the %.0f mm carriage: %.0f N at each end" % (CARRIAGE_L, R))
print("  (the %.0f N of belt pull itself goes straight into the screw, not the guide)" % F)

# --------------------------------------------------------------- Delrin gibs
print("=" * 70)
print("A) DELRIN L-GIBS IN THE V-SLOT  (what is drawn)")
MU_ACETAL = 0.20        # acetal on dry aluminium, 0.15-0.25
area = GIB_OUT["w"] * GIB_OUT["l"]      # mm2, one tongue flank
p = R / area
f_fric = MU_ACETAL * 2.0 * R            # both ends of the couple bear
print("  bearing area per tongue   %.0f mm2" % area)
print("  contact pressure          %.2f MPa   (acetal takes 10-20 MPa static)" % p)
print("  sliding friction          %.0f N  at mu = %.2f" % (f_fric, MU_ACETAL))
print("  as a fraction of the belt pull: %.1f%%" % (100 * f_fric / F))
print("  mass                      ~%.0f g of acetal" % (4 * 5.1 * 1.41))
print("  -> capacity is a non-issue. The problem is that this is SLIDING contact:")
print("     stick-slip, a breakaway force that differs from the running force, and")
print("     a friction coefficient that moves with wear, temperature and swarf.")

# ------------------------------------------------------- recirculating rails
print("=" * 70)
print("B) RECIRCULATING LINEAR GUIDE")
MU_ROLL = 0.004
RAIL_L = 230.0          # A1 spans Y 58..284.7
print("  %-10s %8s %8s %9s %9s %9s %8s" %
      ("guide", "C_dyn", "rail h", "block h", "rail g/m", "block g", "total g"))
opts = [("MGN7H",  1.00, 4.8,  8.0, 220.0,  22.0),
        ("MGN9H",  1.86, 6.5, 10.0, 350.0,  35.0),
        ("MGN12H", 2.94, 8.0, 13.0, 600.0,  55.0),
        ("MGN15H", 4.51, 10.0, 16.0, 900.0, 100.0),
        ("HGR15",  7.84, 15.0, 24.0, 1200.0, 170.0)]
for name, cdyn, rh, bh, rg, bg in opts:
    tot = RAIL_L / 1000.0 * rg + 2 * bg
    print("  %-10s %6.2f kN %6.1f mm %7.1f mm %8.0f %8.0f %7.0f"
          % (name, cdyn, rh, bh, rg, bg, tot))
print("  friction at %.0f N reaction, mu = %.3f: %.1f N  (%.2f%% of the belt pull)"
      % (R, MU_ROLL, MU_ROLL * 2 * R, 100 * MU_ROLL * 2 * R / F))
print()
print("  TWO blocks per carriage, not one. A single block would have to react the")
print("  %.1f N.m yaw as a MOMENT, and a miniature block is rated under 10 N.m." % Mz)
for SPACING, who in ((54.0, "carriage A"), (34.0, "carriage B, shortened by the anchor")):
    print("    %-38s %2.0f mm apart -> %4.0f N per block"
          % (who, SPACING, Mz * 1000.0 / SPACING))
print("  So 2 rails and 4 blocks: %.0f g of MGN7, against %.0f g of acetal."
      % (2 * (RAIL_L / 1000.0 * 220.0) + 4 * 22.0, 4 * 5.1 * 1.41))
print("  every one of these is 10x+ overspecified on load: we need %.2f kN, "
      "the smallest offers %.2f" % (R / 1000.0, opts[0][1]))

# ------------------------------------------------------------------ the call
print("=" * 70)
print("VERDICT")
d = MU_ACETAL * 2 * R
r = MU_ROLL * 2 * R
mgn7 = 2 * (RAIL_L / 1000.0 * 220.0) + 4 * 22.0
print("  friction saved        %.0f N -> %.1f N   (%.1f%% of belt pull recovered)"
      % (d, r, 100 * (d - r) / F))
print("  mass added (MGN7H)    %.0f g of rail and blocks, less ~%.0f g of acetal = +%.0f g"
      % (mgn7, 4 * 5.1 * 1.41, mgn7 - 4 * 5.1 * 1.41))
print("  dimensional cost      none: the rail sits in the 5.6 mm between the side face")
print("                        and the belt, the block inside the carriage's own envelope")
print("  HGR15 is the wrong size: %.0f g for load nobody needs." % (RAIL_L/1000.*1200 + 340))
print("  MGN7H is what fits. MGN9 is 0.9 mm too tall for the belt.")
print("=" * 70)
print("WHERE IT GOES  (measured against the model, see the rails section in the README)")
print("  MGN12H envelope is rail 12x8 + block 27x13, so 13 mm proud of its mounting face")
print("  and 27 mm across. Three candidate faces on the 20x60:")
print("  BLOCKS never share length with the belt: run A ends at carrA-24 and carriage A's")
print("  first block starts later, the same construction that keeps the ball nut clear.")
print("  The RAIL is continuous, so it does. The belt's inner face is at |X| 35.6 and the")
print("  side face at |X| 30 -- 5.6 mm:")
print("    MGN9 rail stands 6.5 proud -> reaches 36.5, 0.9 mm INTO the belt")
print("    MGN7 rail stands 4.8 proud -> reaches 34.8, clear by 0.8 mm")
print("  MOUNTING, which no interference sweep can ask: the face's V-slot is cut at")
print("  Z 95..101, so a rail centred at 98 has every M2 screw dropping into the slot")
print("  with nothing to grip, and M2 T-nuts do not exist for a 6 mm slot. The two solid")
print("  bands are Z 88..95 and Z 101..108, each 6.9 mm against the rail's 7. The inboard")
print("  band puts the block back into the thigh cuff, so the rail goes on the OUTBOARD")
print("  band at Z 101..108, block at Z 96..113.")
print("  Posterior also needs: blocks distal of the sprung anchor, the anchor outboard to")
print("  X 35.6..44.2, and the spring up to Z 119 to clear the raised block.")
print("  Rail length is what the blocks sweep, not the extrusion: 165 mm anterior")
print("  (blocks sweep Y 67.0..220.8), 145 mm posterior (Y 146.7..280.5).")
print("  Block spacing then drops to 34 mm on carriage B, so the yaw becomes %.0f N per"
      % (Mz * 1000.0 / 34.0))
print("  block against MGN7H's ~1.0 kN dynamic rating -- 1.9x on a peak load.")
print("  This keeps the LATERAL face free, which the front-mounted screw layout needs.")
print("  BUILT: 250_mgn7.py.")
print("=" * 70)
print("  The mass lands on the THIGH, which does not swing about the knee, so it")
print("  costs hip effort -- not the reflected inertia that 300_drivetrain.py is")
print("  fighting. That is the cheap place to spend %.0f g." % (mgn7 - 29))
print("=" * 70)
