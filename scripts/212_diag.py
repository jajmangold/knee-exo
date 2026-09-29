import math, FreeCAD, Part
from FreeCAD import Vector as V
def bx(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
N_EXP,N_PTS=3.4,64
def sell(y,a,b,zc):
    pts=[]
    for i in range(N_PTS):
        t=2.*math.pi*i/N_PTS; ct,st=math.cos(t),math.sin(t)
        pts.append(V(a*math.copysign(abs(ct)**(2./N_EXP),ct),y,
                     zc+b*math.copysign(abs(st)**(2./N_EXP),st)))
    pts.append(pts[0]); return Part.makePolygon(pts)
def loft(st): return Part.makeLoft([sell(*s) for s in st],True,False)
F_O=[(28.,50.,21.,111.),(44.,62.,23.,110.5),(58.,79.,25.,110.),(150.,83.,25.,110.),
     (240.,83.,25.,110.),(285.,80.,24.,110.5),(292.,74.,22.,111.)]
F_I=[(26.,47.,18.,111.),(44.,59.,20.,110.5),(58.,76.,22.,110.),(150.,80.,22.,110.),
     (240.,80.,22.,110.),(285.,77.,21.,110.5),(294.,70.,18.,111.)]
o=loft(F_O); i=loft(F_I)
print("outer loft solids=%d vol=%.1f ; inner loft solids=%d vol=%.1f"%(
    len(o.Solids),o.Volume/1000,len(i.Solids),i.Volume/1000))
sh=o.cut(i)
print("shell solids=%d vol=%.1f"%(len(sh.Solids),sh.Volume/1000))
m=sh.cut(bx(-31.,31.,20.,300.,40.,96.))
print("after medial cut: solids=%d"%len(m.Solids))
for k,s in enumerate(m.Solids):
    b=s.BoundBox
    print("   solid %d  vol %7.1f cm3  X %6.1f..%5.1f Z %5.1f..%5.1f"%(
        k,s.Volume/1000,b.XMin,b.XMax,b.ZMin,b.ZMax))
