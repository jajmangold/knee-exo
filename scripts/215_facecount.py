import FreeCAD
doc=FreeCAD.getDocument("KneeExo_v4")
tot=0
rows=[]
for o in doc.Objects:
    if not hasattr(o,"Shape") or o.Shape.isNull(): continue
    if o.isDerivedFrom("App::DocumentObjectGroup"): continue
    n=len(o.Shape.Faces); tot+=n; rows.append((n,o.Name))
for n,nm in sorted(rows,reverse=True)[:10]: print("  %5d faces  %s"%(n,nm))
print("  total faces in the document: %d"%tot)
