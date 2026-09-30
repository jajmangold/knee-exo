# -*- coding: utf-8 -*-
import math
O = lambda n: doc.getObject(n)
print("=== locate the P4/P1 and P7/P2 overlaps ===")
for th in (15.0, -2.0):
    pose(th)
    for a, b in (("P4_ShankLink_Horn","P1_ThighUpright_Lower"),
                 ("P7_Actuator_ENVELOPE","P2_ThighUpright_Upper"),
                 ("P7_Actuator_ENVELOPE","P4_ShankLink_Horn")):
        c = O(a).Shape.common(O(b).Shape)
        if c.isNull() or c.Volume < 1: continue
        bb = c.BoundBox
        print(" th=%+5.0f %s^%s  V=%5.2f cm3  X[%6.1f,%6.1f] Y[%6.1f,%6.1f] Z[%6.1f,%6.1f]"
              % (th, a.split('_')[0], b.split('_')[0], c.Volume/1000,
                 bb.XMin,bb.XMax, bb.YMin,bb.YMax, bb.ZMin,bb.ZMax))

print()
print("=== DRIVE COMPARISON: COTS actuator  vs  6374 + SFU2020 + ODrive ===")
KV, R_PH, J_ROT = 190.0, 0.030, 2.5e-4      # 6374 typical
KT = 8.27/KV
LEAD, ETA = 20.0, 0.90                       # SFU2020 ball screw
F_PER_A = 2*math.pi*ETA*KT/(LEAD/1000.0)
N_RATIO = (arm(60)/1000.0)/(LEAD/1000.0)*2*math.pi
J_LIMB  = 0.29                               # shank+foot about knee, 80 kg
print("Kt = %.4f N.m/A   force per amp = %.1f N/A   screw lead %.0f mm" % (KT, F_PER_A, LEAD))
print()
print("%-22s %9s %9s %9s %9s" % ("", "cont", "peak", "tau@60d", "tau@90d"))
for nm, ic, ip in (("XDRIVE MINI (40/60 A)", 40, 60), ("ODrive S1   (40/80 A)", 40, 80)):
    fc_, fp = F_PER_A*ic, F_PER_A*ip
    print("%-22s %7.0f N %7.0f N %7.1f Nm %7.1f Nm  (peak %.0f Nm @60d)"
          % (nm, fc_, fp, fc_*arm(60)/1000, fc_*arm(90)/1000, fp*arm(60)/1000))
print()
print("speed:  %3.0f mm/s swing needs %5.0f rpm  (no-load %.0f rpm @22.2 V -> %.0f%% -> full current authority)"
      % (120, 120/LEAD*60, 22.2*KV, 120/LEAD*60/(22.2*KV)*100))
print("heat :  %.0f A cont -> %.0f W copper (I2R, 2 phases); duty ~30%% on stairs -> %.0f W avg"
      % (49, 49**2*R_PH*2, 49**2*R_PH*2*0.30))
print()
print("transparency (free swing):")
print("  reduction n = %.1f rad_motor/rad_knee" % N_RATIO)
print("  reflected rotor inertia = %.4f kg.m2   limb = %.2f  -> +%.0f%% swing inertia"
      % (J_ROT*N_RATIO**2, J_LIMB, J_ROT*N_RATIO**2/J_LIMB*100))
for lead in (5.0, 10.0, 20.0, 25.0):
    n = (arm(60)/1000.0)/(lead/1000.0)*2*math.pi
    print("    lead %2.0f mm -> n=%5.1f  reflected %.3f kg.m2 (+%3.0f%%)   %5.0f N at 49 A"
          % (lead, n, J_ROT*n**2, J_ROT*n**2/J_LIMB*100, 2*math.pi*ETA*KT*49/(lead/1000.0)))
print()
print("regen on stair DESCENT (the eccentric-quad deficit):")
E = 25.0*math.radians(60)
print("  absorbing 25 N.m over 60 deg = %.1f J/step -> %.0f%% back to pack; but the real win is" % (E, 80))
print("  controlled eccentric braking, which is exactly what a deconditioned quad cannot do.")
