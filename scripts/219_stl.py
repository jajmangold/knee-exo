import os, FreeCAD, Mesh, MeshPart
g=globals()
doc=FreeCAD.getDocument("KneeExo_v4")
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
OUT=r"C:/Users/Josh/KneeExo_v6_STL"
for f in os.listdir(OUT):
    if f.endswith(".stl"): os.remove(os.path.join(OUT,f))
# P3 is no longer printed -- it is a bought aluminium V-wheel gantry (392_gantry.py) --
# and P3b, P11 are deleted with the second screw. See 390_onescrew_section.py.
STRUCT=["P1_KneeYoke","P2a_KneeHingePlate","P5_ThighCuff",
        "P6_ShankSocket","P7_ShankCuff","P30_InterfaceProx","P31_InterfaceDist"]
FAIR=["P20_KneeShroud","P21_ShellAnterior","P22_DriveCap","P25_MotorNacelle","P24_FairingShank",
      # posterior side-face mounts; the only thing holding the canopy now that the
      # spine is gone (398_sidemounts.py)
      "P23a_FairingMount","P23b_FairingMount","P23c_FairingMount",
]
MACH=[]   # gibs -> MGN7H blocks (250_mgn7.py) -> mini V-wheels (396_fixes.py)
ts=tf=0.
for n in STRUCT+FAIR+MACH:
    o=doc.getObject(n)
    if not o: print("  %-22s MISSING"%n); continue
    assert len(o.Shape.Solids)==1, n
    # A VALID SOLID DOES NOT GUARANTEE A MANIFOLD MESH. P5_ThighCuff exported with 92
    # unpaired edges while isValid() and isClosed() both said fine -- adjacent faces simply
    # tessellated inconsistently along a shared edge. 411_printability.py found it by reading
    # the STL back, which is the only place it is visible. Repair, then refine until the mesh
    # really is closed, then assert. A slicer would silently "repair" this its own way.
    mm=None
    for ld,ad in ((0.08,0.35),(0.04,0.2),(0.02,0.12),(0.01,0.08)):
        m=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=ld,AngularDeflection=ad,Relative=False)
        mm=Mesh.Mesh(m.Topology)
        mm.removeDuplicatedPoints(); mm.removeDuplicatedFacets(); mm.harmonizeNormals()
        if mm.isSolid(): 
            if (ld,ad)!=(0.08,0.35): print("    %s needed deflection %.2f/%.2f to mesh closed"%(o.Label,ld,ad))
            break
    assert mm.isSolid(), ("%s will not mesh into a closed solid at any deflection tried -- "
                          "%d facets, %d points"%(o.Label,mm.CountFacets,mm.CountPoints))
    mm.write(os.path.join(OUT,o.Label+".stl"))
    v=o.Shape.Volume/1000
    if n in STRUCT: ts+=v
    if n in FAIR: tf+=v
    print("  %-24s %6.1f cm3  %s"%(o.Label,v,"PETG struct" if n in STRUCT else
          ("PETG fairing" if n in FAIR else "Delrin")))
print("\nstructural %.0f cm3 (~%.0f g) + fairings %.0f cm3 (~%.0f g at 2-wall/low infill)"%(
    ts,ts*1.27,tf,tf*0.55))
ALU = [("P3 gantry", 192.), ("A7 drive bracket", 286.)]
print("total ~%.0f g PETG + %.0f g of 2040 rail + %.0f g of aluminium (%s)"
      % (ts * 1.27 + tf * 0.55, 164., sum(m for _, m in ALU),
         ", ".join("%s %.0f" % (n, m) for n, m in ALU)))
print("      -- the one-screw build moves the two structural carriages out of PETG and")
print("      into a bought plate. See 390_onescrew_section.py.")
