# -*- coding: utf-8 -*-
"""COAXIAL INLINE: rear eye -> 6374 -> coupling -> bearing block -> SFU2020 -> nut tube
-> tang -> pin B.  No belt, no lateral offset. Motor now eats pin-to-pin length, so LA
must grow; ALPHA must swing anterior far enough that the 63 mm can clears the thigh cuff."""
import math
R, PHI0 = 60.0, 135.0
ROMx = (-2.0, 105.0)
EYE, MOTL, CPL, BLKL = 14.0, 74.0, 12.0, 22.0      # inline stack from pin A
BLK_END = EYE+MOTL+CPL+BLKL
NUT, TANG = 40.0, 25.0
def AB(LA,t): return math.sqrt(LA*LA+R*R-2*LA*R*math.cos(math.radians(PHI0-t)))
def ARM(LA,t): return LA*R*math.sin(math.radians(PHI0-t))/AB(LA,t)
NEED = 96.5+NUT+TANG
print("inline stack from pin A: eye %.0f + motor %.0f + coupling %.0f + block %.0f = %.0f mm"
      % (EYE,MOTL,CPL,BLKL,BLK_END))
print("need L_ret >= %.1f + %.1f = %.1f\n" % (NEED, BLK_END, NEED+BLK_END))
print(" LA  | L_ret  L_ext stroke | arm@60 | margin | pinA@105deg      | motor->limb axis")
pick=None
for LA in (300.,320.,335.,345.,360.):
    r_,e_ = AB(LA,ROMx[1]), AB(LA,ROMx[0])
    marg = r_ - (NEED+BLK_END)
    ax,ay = LA*math.cos(math.radians(105.0)), LA*math.sin(math.radians(105.0))
    # motor sits at local y 14..88; take its mid-span axis point
    t=51.0; ux,uy=(60*math.cos(math.radians(-30.0))-ax)/e_,(60*math.sin(math.radians(-30.0))-ay)/e_
    mx = ax+ux*t
    clr = math.hypot(mx,108.0)-31.5
    ok = marg>=5 and clr>=90
    print("%4.0f | %6.1f %6.1f %6.1f | %6.1f | %6.1f | (%6.1f,%6.1f) | %6.1f %s"
          % (LA,r_,e_,e_-r_,ARM(LA,60.),marg,ax,ay,clr,"OK" if ok else ""))
    if ok and pick is None: pick=LA
LA=pick; AL=105.0
r_,e_=AB(LA,ROMx[1]),AB(LA,ROMx[0]); st=e_-r_
T = st+NUT+TANG+2.0
THR=(r_-T-2.0, e_-T+NUT+1.0)
print("\nADOPT LA=%.0f ALPHA=%.0f  beta0=%.0f" % (LA,AL,AL-PHI0))
print("  pin A (%.1f, %.1f) -> %.0f%% up a 429 mm thigh, %.0f mm anterior of the knee axis"
      % (LA*math.cos(math.radians(AL)), LA*math.sin(math.radians(AL)),
         LA*math.sin(math.radians(AL))/429*100, -LA*math.cos(math.radians(AL))))
print("  pin-to-pin %.1f..%.1f  stroke %.1f" % (r_,e_,st))
print("  tube %.0f, thread %.1f..%.1f (%.1f), screw tip %.1f vs tang start %.1f  %s"
      % (T,THR[0],THR[1],THR[1]-THR[0],THR[1],r_-TANG,"OK" if THR[1]<=r_-TANG else "CLASH"))
assert THR[0]>=BLK_END-2 and THR[1]<=r_-TANG
print("\n  WIDTH: motor r31.5 centred on the drive plane Z=108 -> Z 76.5..139.5")
print("         max lateral extent ~140 mm  (was 184)  = %.0f mm outboard of thigh skin" % (139.5-78))
print("\n  torque (motor only, gas spring removed from the lateral stack):")
KT=8.27/190.0; FA=2*math.pi*0.90*KT/0.020
for t in (0,30,45,60,75,90,105):
    a_=ARM(LA,float(t)); print("   %4d deg  arm %5.1f  %5.1f N.m @40A   %5.1f N.m @80A"
                               % (t,a_,FA*40*a_/1000,FA*80*a_/1000))
