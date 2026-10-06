# -*- coding: utf-8 -*-
"""What is actually left to buy, after the screw set arrived and three pulleys became printed.

Asked at the bench: "ok so whats left to actually buy then".

The BOM is a design document -- every line carries the argument for why it is what it is, which
is what makes it long. This is the other view: one row per thing, a status, and a total. It is
hand-maintained against docs/BOM.md rather than parsed out of it, because "in the box" and
"owned" are facts about the bench, not about the design.

STATUS values:
    BUY      not here, nothing blocking it, order it
    BLOCKED  do not order yet -- something has to be measured or decided first, and the reason
             is in the note
    HAVE     owned, bought, or arrived in a kit
    PRINT    made, not bought
    n/a      deleted from the design

    python scripts/450_buy_list.py
"""

# (ref, what, qty, status, usd, note)
LINES = [
    # ---------------------------------------------------------------- drive
    ("D1", "Ball screw SFU1605 200 mm + BK/BF12 set", "1", "HAVE", 0,
     "arrived: screw, flanged nut, BK12, BF12, locknut, circlip, DSG16H housing, coupler"),
    ("D3", "Flanged ball nut + DSG16H housing", "1", "HAVE", 0, "in the screw set"),
    ("D4", "C6374 170 Kv outrunner", "1", "HAVE", 0, "owned, 4 of them"),
    ("D4a", "M5 x 16 motor bolts", "4", "BLOCKED", 2,
     "MEASURE THE MOTOR'S BOLT CIRCLE. 434 assumes a 25 mm square; 19 and 30 both exist"),
    ("D5", "Diametric magnet 6 x 2.5", "1", "BLOCKED", 3,
     "with E5 that is 2. You said you have 'the magnet' -- confirm whether that is one or two"),
    ("D6", "HTD-5M belt, 270 mm / 54T, 15 mm wide", "1", "BUY", 10,
     "54T is exact at the 60.8 mm centre distance with 38T:20T"),
    ("D7", "38T + 20T HTD-5M pulleys", "2", "PRINT", 0, "447, 449"),
    ("D7a", "Rigid flange shaft coupling, 8 mm bore", "1 (4-pack)", "BUY", 10,
     "the steel hub inside the printed 38T"),
    ("D7b", "3 mm aluminium plate, ~55 mm square", "1", "BUY", 3,
     "backing plate of the same sandwich, and the belt flange on that face"),
    ("D7c", "Steel spacers for the 4 bolt holes", "4", "BUY", 2,
     "cut 0.1 mm proud of the printed hub so the clamp load misses the plastic. 449"),
    ("D8", "BF12 floating-end support", "1", "HAVE", 0, "in the screw set"),
    ("D8a", "6001-2RS (12 x 28 x 8)", "1", "HAVE", 0,
     "the screw's upper bearing under Path B -- covered by the 6001s already bought, which K3 "
     "no longer needs now that the knee runs on 6904s in a bought pulley"),
    ("D9", "Flexible coupler", "1", "HAVE", 0, "in the box, unused -- the motor is belted"),

    # ---------------------------------------------------------------- knee transmission
    ("K1", "HTD-8M open-ended belt, 30 mm wide, 1 m", "1", "BUY", 20,
     "cut to length on the machine. 448"),
    ("K2", "dia 20 hardened ground shaft, h6, 150 mm", "1", "BUY", 12,
     "ONE 150 mm length cut into two: the knee stub axle and the idler's. dia 20 because "
     "the PRINTED capstan takes a 6904 with 14.3 mm of wall -- cantilever 94 -> 20 MPa. h6, "
     "and not HSS: brittle"),
    ("K3", "6904-2RS (20 x 37 x 9)", "4", "BUY", 14,
     "2 in the capstan, 2 in the idler, both printed. Seat dia 37.2, BONDED (418). 69 N.m of "
     "tilt against the 6001 pair's 52, and 1046 mm2 of bond area against 704"),
    ("S2b", "29T HTD-8M idler", "1", "PRINT", 0,
     "printed, with the capstan -- a bought pair was specced and dropped: 10 available from "
     "one seller is a window, not a part, and this has to be reproducible by anyone"),
    ("K4", "Compression spring, ~500 N/mm, 3 mm travel", "1", "BUY", 5,
     "idler carrier. Keep it even with a cut belt until the clamp is proven"),
    ("S2c", "Idler axle + bearings", "1", "HAVE", 0,
     "covered by K2 and K3 now: the idler runs on the same dia 20 shaft and the same 6904s as "
     "the knee. 1828 N over two of them is 914 N each -- 3.6x on C0, where the dia 8 axle and "
     "two 608s this line used to ask for were 1.5x"),

    # ---------------------------------------------------------------- structure
    ("S1", "V-slot extrusion 20x40 black, 160 mm", "1", "BUY", 12, "thigh rail, Y 51..207"),
    ("S1a", "V-slot extrusion 20x40 black, 240 mm", "1", "BUY", 16,
     "shank member. Order one 400 mm length and cut both from it"),
    ("S2", "Mini V-wheel, Delrin, OD 15.23", "4", "BLOCKED", 0,
     "BOM's cost table says owned -- confirm before ordering"),
    ("S2a", "Eccentric spacers + wheel bolts", "4", "BLOCKED", 10, "usually sold with the wheels"),
    ("S3", "M5 T-nuts + button heads", "~40", "BUY", 12, "at X +-10 on the 20x40, not X 0"),
    ("S3a", "M5 x 16 into the extrusion's end cores", "4", "BUY", 2,
     "2 for the drive bracket at the top, 2 for P32_ScrewFoot at the bottom. 445"),
    ("S4", "M3 / M4 cap screws, assorted", "~40", "BUY", 10, "fairings, cuffs, electronics"),
    ("S4b", "Brass heat-set inserts, M3 and M5", "~30", "BUY", 12,
     "NOT PREVIOUSLY ON THE BOM. P30/P31 want 6 x M5 each, the printed 20T wants one for its "
     "grub screw, and every printed-to-printed joint in the build assumes them"),
    ("S4c", "Dowel pins, 5 x 16", "4", "BUY", 4, "P30/P31's 2 x dia 5 locating dowels, both legs"),
    ("S4a", "Rubber grommets M5 + shoulder screws", "3", "BUY", 6, "the fairing's only mounts"),
    ("S5", "Neoprene sleeve, 3 mm, thigh and calf", "2", "BLOCKED", 30,
     "MEASURE THE PATIENT. The sleeve is 3 mm of the limb-cone envelope every clearance check "
     "in 438/439 is drawn around"),
    ("S5a", "Nylon webbing, 38 mm", "1.5 m", "BUY", 6, "cuff closure"),
    ("S5b", "Cam buckle + D-ring, 38 mm", "2 + 2", "BUY", 10, "2:1 through the D-ring"),
    ("S5c", "Side-release buckle, 38 mm", "2", "BUY", 6, "the whole thing drops off in one squeeze"),
    ("F1", "PETG filament", "3.5 kg", "BUY", 70,
     "1.64 kg and ~102 printer-hours per leg, plus the coupons and the bench rig"),

    # ---------------------------------------------------------------- electronics
    ("E1", "MKS XDRIVE MINI", "1", "HAVE", 0, "owned, 4 of them"),
    ("E1a", "ST-Link V2 clone", "1", "BUY", 5,
     "to back up the MINI's firmware. Buy it BEFORE you need it -- odrivetool offers an upgrade "
     "that bricks these clones"),
    ("E2", "Brake resistor ~2 ohm 50 W", "1", "HAVE", 0, "hooked up on the bench"),
    ("E3", "ESP32-C3 SuperMini", "2", "HAVE", 0, "owned"),
    ("E4", "AS5048A magnetic encoder breakout", "1", "BUY", 12,
     "absolute knee angle over SPI -- removes the power-on homing routine"),
    ("E5", "Diametric magnet 6 x 2.5", "1", "BLOCKED", 3, "see D5"),
    ("E6", "SN65HVD230 CAN transceiver", "1", "BUY", 4, "ESP32-C3 TWAI to the ODrive"),
    ("E7", "MPU-6050", "2", "HAVE", 0, "owned"),
    ("E8", "XT90-S anti-spark pair", "1", "BUY", 6, "the bus caps will arc a plain XT60"),
    ("E9", "Inline fuse holder + 15 A blade fuse", "1", "BUY", 6, "at the pack, before anything"),
    ("E10", "Latching e-stop, 22 mm, NC", "1", "BUY", 10, "on the waist belt"),
    ("E11", "Silicone wire 12 AWG", "4 m", "BUY", 12, "pack to leg"),
    ("E12", "Cable gland, strain relief, spiral wrap", "1 set", "BUY", 10, "the tether crosses the hip"),

    # ---------------------------------------------------------------- power
    ("B1", "A123 LiFePO4 36 V 736 Wh", "1", "HAVE", 0, "bought"),
    ("B2", "7-17S smart BMS, 100 A", "1", "HAVE", 0, "bought"),
    ("B3", "Backpack with an internal frame", "1", "BUY", 60,
     "the pack is 7-8 kg -- the waist belt has to carry it, not the shoulders"),
]

ORDER = ("BUY", "BLOCKED", "PRINT", "HAVE")
W = 98

print("=" * W)
print("WHAT IS LEFT TO BUY")
print("=" * W)

for status in ORDER:
    rows = [r for r in LINES if r[3] == status]
    if not rows:
        continue
    total = sum(r[4] for r in rows)
    head = {"BUY": "ORDER THESE", "BLOCKED": "DO NOT ORDER YET",
            "PRINT": "MADE, NOT BOUGHT", "HAVE": "ALREADY HERE"}[status]
    print()
    print("-" * W)
    print("  %s   (%d lines%s)" % (head, len(rows), ", ~$%d" % total if total else ""))
    print("-" * W)
    for ref, what, qty, _, usd, note in rows:
        print("  %-5s %-44s %-10s %s" % (ref, what[:44], qty, "$%d" % usd if usd else ""))
        if status in ("BUY", "BLOCKED") and note:
            for i in range(0, len(note), 86):
                print("        %s" % note[i:i + 86])

buy = sum(r[4] for r in LINES if r[3] == "BUY")
blocked = sum(r[4] for r in LINES if r[3] == "BLOCKED")
print()
print("=" * W)
print("  ORDER NOW            ~$%d over %d lines" % (buy, len([r for r in LINES if r[3] == "BUY"])))
print("  WAITING ON A FACT    ~$%d over %d lines"
      % (blocked, len([r for r in LINES if r[3] == "BLOCKED"])))
print("  TOTAL STILL TO SPEND ~$%d" % (buy + blocked))
print("=" * W)
print()
print("  THE SIX FACTS THAT UNBLOCK THE REST, all of them measurements and none of them CAD:")
print("     1. the motor's bolt circle            -> D4a, and A7_DriveBracket_Idler's end plate")
print("     2. how many 6x2.5 magnets you own     -> D5, E5")
print("     3. do you have the V-wheels           -> S2, S2a")
print("     4. your father's thigh and calf       -> S5, and REF_Thigh's taper, and the cuffs")
print("     5. the GY-521 outline and holes       -> blocks PRINTING P5 and P7, not buying")
print("     6. the screw's four machined lengths  -> settles Path A vs B, which sets the 20T's")
print("        and BF12/BK12's flange patterns        bore and whether BK12 gets used at all")
print()
print("  AND ONE DECISION ONLY YOU CAN MAKE: Path A or Path B from 446_sfu1605_set.py. Path B")
print("  parts 29 mm off a brand new screw. Nothing else in this list depends on it except the")
print("  20T's bore, which is printed anyway -- so it does not hold up a single order.")
