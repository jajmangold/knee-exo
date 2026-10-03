import os, FreeCAD, Mesh, MeshPart
g=globals()
def _kx_doc():
    """The model, whether we are in the GUI instance or under freecadcmd.

    KX_DOC overrides the file, which is how the mirrored right leg is checked with the same
    scripts. Headless matters: 397 and 409 both exceed the RPC server's 90 s dispatch limit,
    and overrunning it does not fail cleanly -- it keeps working and leaves a half-built
    document the next script reads as finished.
    """
    import os as _os
    want = _os.environ.get("KX_DOC", r"C:/Users/Josh/KneeExo_v6.FCStd").replace("\\", "/")
    base = want.rsplit("/", 1)[-1]
    for d in FreeCAD.listDocuments().values():
        if d.FileName.replace("\\", "/").endswith(base):
            return d
    return FreeCAD.openDocument(want)


doc = _kx_doc()
t=g.get("_kx_timer")
if t is not None:
    try: t.stop()
    except Exception: pass
for o in doc.Objects:
    if hasattr(o,"Placement") and not o.Placement.isIdentity(): o.Placement=FreeCAD.Placement()
doc.recompute()
# One directory PER DOCUMENT, named after it, so the two legs cannot overwrite each other:
# the parts have the same object names in both files and a single shared folder would silently
# leave you with one leg's worth of STLs under names that look like a full set.
OUT=os.environ.get("KX_STL") or (r"C:/Users/Josh/%s_STL"
                                 % os.path.basename(doc.FileName)[:-6])
if not os.path.isdir(OUT):
    os.makedirs(OUT)
for f in os.listdir(OUT):
    if f.endswith(".stl"): os.remove(os.path.join(OUT,f))
# and P3b, P11 are deleted with the second screw. See 390_onescrew_section.py.
# P3 and A7 were "fabricated aluminium" and so were never exported. They are printed now
# (802_no_metal.py): the bracket at 6 mm plates with the idler bearings seated in them, the
# gantry plate as drawn. Printing both SAVES 241 g, because PETG is 1.27 g/cm3 against 2.70
# and the sections barely had to grow -- the parts were sized by what was convenient to fuse,
# not by load.
STRUCT=["P1_KneeYoke","P2a_KneeHingePlate","P5_ThighCuff",
        "P6_ShankSocket","P7_ShankCuff","P30_InterfaceProx","P31_InterfaceDist",
        "P3_Carriage","A7_DriveBox",
        # The controller's mount (434_odrive_mount.py). Printed, and the one part in the set
        # whose dimensions are not yet known: every board figure in 434 is flagged GUESSED or
        # UNVERIFIED, so this STL is for fit-checking against the real board, not for the shelf.
        "P27_ControllerMount"]
# P24_FairingShank is gone, not merely unexported: 430_shank_inline_build.py moved the shank
# rail in-line under the knee joint and there was nothing left for it to fair.
FAIR=["P20_KneeShroud","P21_ShellAnterior","P22_DriveCap","P25_MotorNacelle",
      # posterior side-face mounts; the only thing holding the canopy now that the
      # spine is gone (398_sidemounts.py)
      "P23a_FairingMount","P23b_FairingMount","P23c_FairingMount",
]
MACH=[]   # gibs -> MGN7H blocks (250_mgn7.py) -> mini V-wheels (396_fixes.py)
# Not a part of the device: a three-tooth arc of the capstan, to push a real HTD-8M belt into
# before committing ten hours to the 135 cm3 pulley. The tooth profile here is an approximation
# of the HTD curvilinear form (421_pulley_teeth.py explains how much of it is known), so it is
# the one thing in the build that has to be proven against hardware rather than arithmetic.
# Exported so it can be sliced; excluded from the part counts and the mass totals.
TEST=["TEST_ToothCoupon"]
ts=tf=0.
for n in STRUCT+FAIR+MACH+TEST:
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
          ("PETG fairing" if n in FAIR else ("test coupon" if n in TEST else "Delrin"))))
print("\nstructural %.0f cm3 (~%.0f g) + fairings %.0f cm3 (~%.0f g at 2-wall/low infill)"%(
    ts,ts*1.27,tf,tf*0.55))
# No fabricated aluminium left. P3 and A7 were the only two parts needing a workshop and both
# print: 802_no_metal.py sizes them against PETG's ~15 MPa sustained allowable instead of
# aluminium's 240 MPa yield, and they come out 241 g LIGHTER between them because the density
# ratio beats the extra section. The only metal in the build is now bought: extrusion, screw,
# nut, bearings, pulleys, motor, fasteners.
print("total ~%.0f g PETG + %.0f g of 2040 rail; NO fabricated metal -- every metal part is bought"
      % (ts * 1.27 + tf * 0.55, 164.))
print("      P3 gantry plate 91 g printed against 192 as aluminium; A7 bracket 171 against 311.")
print("      See 802_no_metal.py: they were never sized by load, so plastic costs only section.")
