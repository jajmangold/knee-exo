# -*- coding: utf-8 -*-
"""Front-mounted screws: what the layout actually costs now that the nut is OD 36.

The idea is to move both ball screws off the sides (X = +/-58) onto the extrusion's
lateral 60 mm face, side by side near the centreline, with each carriage a bracket that
wraps the corner from its nut to its belt anchor. It collapses the fore-aft spread and,
more importantly, lets the motor come off the X = -58 cantilever that currently sets both
extremes of the whole device.

When this was first measured the CAD nut was OD 28 -- an SFU1605 nut -- and the answer was
+6 mm of lateral protrusion. The build is now SFU1610, OD 36, which changes the stack by
more than the nut's extra radius, because the nut has to clear the rail's lateral face
before the carriage can wrap it.

Run:  python scripts/330_frontmount.py
"""

RAIL_Z = 108.0          # extrusion's lateral face
BELT_IN = 35.55         # belt run inner face -- pulley-determined, immovable
KNEE_R = 52.0           # reference knee radius, for "proud of the knee"

# current, measured off the model
CUR = dict(nut_axis=106.0, nut_r=18.0, carriage_z=130.0, fairing_z=138.0,
           core_x=80.0, fairing_x=84.0, motor_x=(-89.5, -26.5), cap_x=(-106.0, 84.0))

print("=" * 70)
print("CURRENT (screws beside the rail at X = +/-58)")
print("  nut axis Z %.0f, nut Z %.0f..%.0f" % (CUR["nut_axis"],
      CUR["nut_axis"] - CUR["nut_r"], CUR["nut_axis"] + CUR["nut_r"]))
print("  carriages reach Z %.0f, fairing Z %.0f -> %.0f mm proud of the knee"
      % (CUR["carriage_z"], CUR["fairing_z"], CUR["fairing_z"] - KNEE_R))
print("  core X +/-%.0f, fairing X +/-%.0f, drive cap X %.0f..%.0f (the motor sets it)"
      % (CUR["core_x"], CUR["fairing_x"], CUR["cap_x"][0], CUR["cap_x"][1]))

print("=" * 70)
print("FRONT-MOUNTED, by nut size")
print("  the nut must clear the rail's lateral face at Z %.0f before the carriage can" % RAIL_Z)
print("  wrap it, so its axis sits at Z >= %.0f + r" % RAIL_Z)
print()
print("  %-10s %5s %9s %9s %10s %10s %9s" %
      ("nut", "r", "axis Z", "nut top", "carriage", "fairing", "proud"))
for nm, r, lead in (("OD 28", 14.0, "SFU1605"), ("OD 36", 18.0, "SFU1610")):
    axis = RAIL_Z + r
    top = axis + r
    carr = top + 4.0              # carriage wall over the nut
    fair = carr + 8.0             # fairing wall + clearance
    print("  %-10s %5.0f %9.0f %9.0f %10.0f %10.0f %6.0f mm   (%s)"
          % (nm, r, axis, top, carr, fair, fair - KNEE_R, lead))

print()
print("  and side by side, two nuts need their centres 2r apart:")
for nm, r in (("OD 28", 14.0), ("OD 36", 18.0)):
    x = r + 1.0
    print("    %-8s screws at X = +/-%.0f, nuts span |X| %.0f..%.0f  (belt inner is %.2f,"
          % (nm, x, x - r, x + r, BELT_IN))
    print("             but the nut never shares Y with the belt -- see 311_nut_belt.py)")

print("=" * 70)
print("THE TRADE, with the nut we actually built (OD 36)")
d_lat = (RAIL_Z + 36.0 + 12.0) - CUR["fairing_z"]
print("  lateral   %.0f -> %.0f mm proud of the knee   %+.0f mm, all of it exposed"
      % (CUR["fairing_z"] - KNEE_R, RAIL_Z + 36.0 + 12.0 - KNEE_R, d_lat))
print("  fore-aft  core X +/-%.0f -> +/-%.0f (the belt at %.1f sets it)"
      % (CUR["core_x"], BELT_IN + 5.0, BELT_IN))
print("            fairing X +/-%.0f -> ~+/-50, drive cap %.0f..%.0f -> ~+/-45"
      % (CUR["fairing_x"], CUR["cap_x"][0], CUR["cap_x"][1]))
print()
print("  Measured against the reference limb earlier: fore-aft the fairing clears the")
print("  limb's own silhouette by only 2-12 mm, while laterally it stands 56-66 mm proud")
print("  at the thigh and 86 at the knee. So the fore-aft saving mostly removes material")
print("  that was already hidden behind the leg, and the lateral cost is fully exposed.")
print()
print("  With the OD 28 nut this was +6 mm lateral and clearly worth it.")
print("  With the OD 36 nut it is %+.0f mm, and it is not." % d_lat)
print("=" * 70)
print("WHAT WOULD MAKE IT WORTH IT AGAIN")
print("  * accept SFU1605 and its 2.22x reflected inertia -- no: that is the one number")
print("    that decides whether the leg feels normal with the power off")
print("  * a flangeless OD 32 nut, if a supplier has one: axis Z 124, fairing ~152,")
print("    %.0f mm proud -- still +%.0f" % (124.0 + 16.0 + 12.0 - KNEE_R,
                                            124.0 + 16.0 + 12.0 - CUR["fairing_z"]))
print("  * a smaller pulley, which would move the belt inboard -- but R IS the moment arm")
print("=" * 70)
