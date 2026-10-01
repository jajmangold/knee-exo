# -*- coding: utf-8 -*-
"""Measure the lateral (Z) stack-up and the real limb clearance envelope vs Y."""
import FreeCAD, Part
from FreeCAD import Vector as V
g=globals()
doc=next(d for d in FreeCAD.listDocuments().values()
                if d.FileName.replace("\\", "/").endswith("KneeExo_v6.FCStd"))
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
print("=== lateral (Z) stack, zero pose.  Z = distance outboard of the knee centre ===")
rows=[]
for o in doc.Objects:
    if not hasattr(o,"Shape") or o.Shape.isNull(): continue
    if o.isDerivedFrom("App::DocumentObjectGroup"): continue
    b=o.Shape.BoundBox; rows.append((b.ZMin,b.ZMax,o.Name,b.YMin,b.YMax))
for z0,z1,n,y0,y1 in sorted(rows):
    tag="" if n.startswith("REF") else ("  <-- limb" if 0 else "")
    print("  Z %6.1f ..%6.1f  (%5.1f mm)  %-28s Y %7.1f..%7.1f"%(z0,z1,z1-z0,n,y0,y1))
hard=[r for r in rows if not r[2].startswith("REF")]
print("\ntotal hardware build: Z %.1f .. %.1f = %.1f mm"%(
    min(r[0] for r in hard),max(r[1] for r in hard),max(r[1] for r in hard)-min(r[0] for r in hard)))
print("\n=== limb radius vs Y (max |X| and |Z| of the REF cones in a 4 mm slab) ===")
refs=[doc.getObject(n) for n in ("REF_Thigh","REF_Knee","REF_Shank")]
print("     Y     thigh   knee   shank    max      inboard face of A1 is Z=88.0")
for y in (-300,-250,-200,-150,-100,-70,-45,-20,0,20,50,85,120,160,200,250,290):
    slab=Part.makeBox(400,4,400,V(-200,y-2,-200)); vals=[]
    for r in refs:
        if r is None: vals.append(None); continue
        try:
            c=r.Shape.common(slab)
            vals.append(None if c.isNull() or c.Volume<1e-6 else max(abs(c.BoundBox.ZMin),abs(c.BoundBox.ZMax)))
        except Exception: vals.append(None)
    mx=max([v for v in vals if v is not None] or [0])
    f=lambda v:"  --  " if v is None else "%6.1f"%v
    print("  %6d %s %s %s  %6.1f   gap to A1: %5.1f mm"%(y,f(vals[0]),f(vals[1]),f(vals[2]),mx,88.0-mx))
