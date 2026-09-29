# -*- coding: utf-8 -*-
"""v3b: keep v1's clean sagittal layout (ALPHA=85 -> upright anterior X-52..-4, actuator
posterior X 26..39, no overlap). Get width from a +12 mm Z restack so the coaxial motor
clears the thigh, and LA 300->350 so the inline stack fits the pin-to-pin budget."""
import math
LA, ALPHA, PHI0, R_CRANK = 350.0, 85.0, 135.0, 60.0
FORK_IN, GAP, LINK, FORK_OUT = (100.0,110.0), (110.0,130.0), (112.0,128.0), (130.0,140.0)
Z_PLANE = 120.0
BOX_X, CAV_X = (-52.0,-4.0), (-47.0,-9.0)
BOX_Z, CAV_Z = (100.0,140.0), (105.0,135.0)
EYE, MOTL, CPL, BLKL = 16.0, 74.0, 12.0, 22.0
BLK_END = EYE+MOTL+CPL+BLKL
NUT, TANG, T_TUBE = 40.0, 25.0, 170.0
R_HUB,R_PLATE,PLATE_SEC = 24.0,76.0,(88.0,252.0)
R_PIN,D_PIN = 60.0,12.0
FLEX_HOLES=[(238,105),(228,95),(218,85),(208,75),(198,65),(188,55)]
EXT_HOLES=[(99.6,0),(109.6,10),(119.6,20)]
FINGER=(107.3,127.3)
Y_TWIN,Y_CLOSED = (25.0,84.0), 75.0
Y_TONGUE=(70.0,178.0); Y_TOP=390.0
g=globals(); 
for k in ("LA","ALPHA","PHI0","R_CRANK","FORK_IN","GAP","LINK","FORK_OUT","Z_PLANE","BOX_X","CAV_X",
          "BOX_Z","CAV_Z","EYE","MOTL","CPL","BLKL","BLK_END","NUT","TANG","T_TUBE","R_HUB","R_PLATE",
          "PLATE_SEC","R_PIN","D_PIN","FLEX_HOLES","EXT_HOLES","FINGER","Y_TWIN","Y_CLOSED",
          "Y_TONGUE","Y_TOP"): g[k]=locals()[k]
A = pinA(); g['A']=A
L_RET,L_EXT = ab(105.0),ab(-2.0); STROKE=L_EXT-L_RET
THREAD=(L_RET-T_TUBE-2.0, L_EXT-T_TUBE+NUT+1.0)
g.update(L_RET=L_RET,L_EXT=L_EXT,STROKE=STROKE,THREAD=THREAD)
assert THREAD[0]>=BLK_END and THREAD[1]<=L_RET-TANG
# motor clearance check
u=((pinB(0.0)[0]-A[0])/L_EXT,(pinB(0.0)[1]-A[1])/L_EXT)
mx = A[0]+u[0]*88.0
clr = math.hypot(mx, Z_PLANE)-31.5
print("pin A (%.1f,%.1f)  pin-pin %.1f..%.1f  stroke %.1f  arm@60 %.1f"%(*A,L_RET,L_EXT,STROKE,arm(60.0)))
print("thread %.1f..%.1f  BLK_END %.0f  tang start %.1f  margin %.1f"%(*THREAD,BLK_END,L_RET-TANG,L_RET-TANG-THREAD[1]))
print("motor coaxial at Z=%.0f: closest approach to limb axis %.1f mm (cuff 88, thigh ~87)"%(Z_PLANE,clr))
print("max lateral extent = motor %.1f mm"%(Z_PLANE+31.5))
assert clr>=89.0, "motor fouls the cuff"
# ---------- P1 ----------
def fork_plate(z0,z1): return sector(R_PLATE,*PLATE_SEC,z0,z1).fuse(cz(R_HUB,z0,z1))
low=fork_plate(*FORK_IN).fuse(fork_plate(*FORK_OUT))
for z0,z1 in (FORK_IN,FORK_OUT): low=low.fuse(bx(*BOX_X,*Y_TWIN,z0,z1))
low=low.fuse(bx(*BOX_X,Y_CLOSED,180.0,*BOX_Z)).cut(bx(*CAV_X,Y_CLOSED+4,182.0,*CAV_Z))
for z0,z1 in (FORK_IN,FORK_OUT):
    for b in (100,135,170,205,235): low=low.cut(cz(11.0,z0-1,z1+1,*pol(54.0,b)))
low=low.cut(cz(6.15,FORK_IN[0]-2,FORK_OUT[1]+2))
for b,_ in FLEX_HOLES+EXT_HOLES: low=low.cut(cz(D_PIN/2+0.1,FORK_IN[0]-2,FORK_OUT[1]+2,*pol(R_PIN,b)))
for y in (115.0,155.0): low=low.cut(cz(2.75,BOX_Z[0]-2,BOX_Z[1]+2,-28.0,y))
assert len(low.Solids)==1 and low.isValid() and low.isClosed(),"P1 %d"%len(low.Solids)
o=doc.getObject("P1_ThighUpright_Lower"); o.Shape=low
# ---------- P4 ----------
B0=pinB(0.0)
SLOT_Z,CHEEK_Z,R_CHEEK=(111.6,128.4),(106.0,134.0),(24.0,80.0)
ann_cheek=cz(R_CHEEK[1],*CHEEK_Z).cut(cz(R_CHEEK[0],CHEEK_Z[0]-1,CHEEK_Z[1]+1))
ann_slot =cz(R_CHEEK[1],*SLOT_Z ).cut(cz(R_CHEEK[0],SLOT_Z[0]-1, SLOT_Z[1]+1))
lk=cz(21.0,*LINK).fuse(sector(70.0,*FINGER,*LINK,r_in=20.0))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*LINK))
lk=lk.fuse(bar((0.0,0.0),B0,18.0,12.0,*CHEEK_Z).common(ann_cheek))
lk=lk.fuse(cz(16.0,*CHEEK_Z,*B0))
lk=lk.fuse(bar((0.0,-20.0),(0.0,-160.0),22.0,18.0,*LINK))
TONG=dict(x=(-13.0,13.0),y=(-197.0,-150.0),z=(114.0,126.0)); g['TONG']=TONG
lk=lk.fuse(bx(*TONG['x'],*TONG['y'],*TONG['z']))
slot=cz(24.0,*SLOT_Z,*B0).fuse(sector_at(B0,52.0,-46.0,126.0,*SLOT_Z,r_in=24.0))
lk=lk.cut(slot.common(ann_slot)).cut(cz(13.0,*SLOT_Z,*B0))
lk=lk.cut(cz(5.15,104.0,138.0,*B0)).cut(cz(6.25,LINK[0]-2,LINK[1]+2))
lk=lk.cut(cz(10.6,LINK[0]-0.5,LINK[0]+5.2)).cut(cz(10.6,LINK[1]-5.2,LINK[1]+0.5))
for p in [(0.0,-70.0),(0.0,-110.0),(0.0,-145.0)]: lk=lk.cut(cz(9.0,LINK[0]-1,LINK[1]+1,*p))
lk=lk.cut(cz(3.1,TONG['z'][0]-2,TONG['z'][1]+2,0.0,-178.0))
assert len(lk.Solids)==1 and lk.isValid() and lk.isClosed(),"P4 %d"%len(lk.Solids)
o=doc.getObject("P4_ShankLink_Horn"); o.Shape=lk
doc.getObject("HW_ROMpin_flexion_105deg").Shape=cz(6.0,96.0,144.0,*pol(R_PIN,FLEX_HOLES[0][0]))
doc.getObject("HW_ROMpin_extension_0deg").Shape=cz(6.0,96.0,144.0,*pol(R_PIN,EXT_HOLES[0][0]))
doc.getObject("HW_PinB_10").Shape=cz(5.0,104.0,138.0,*B0)
doc.recompute()
print("P1 %.1f  P4 %.1f cm3 single closed solids"%(low.Volume/1000,lk.Volume/1000))
