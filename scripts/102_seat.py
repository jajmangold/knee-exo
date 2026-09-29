# -*- coding: utf-8 -*-
import FreeCAD, Part
from FreeCAD import Vector as V
doc=FreeCAD.getDocument("KneeExo_v4")
cb=doc.getObject("P2b_RodClevisBlock").Shape
A4=doc.getObject("A4_Shank2020_VSlot").Shape
bb=cb.BoundBox
# slide the block inboard by its residual gap so it seats on the 2020 face
gap=cb.distToShape(A4)[0]
cb2=cb.copy(); cb2.translate(V(-gap,0,0))
print("P2b shifted %.3f mm -> gap now %.3f mm"%(gap, cb2.distToShape(A4)[0]))
assert len(cb2.Solids)==1 and cb2.isClosed()
doc.getObject("P2b_RodClevisBlock").Shape=cb2
doc.recompute(); doc.save()
