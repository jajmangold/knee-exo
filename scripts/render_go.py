import sys, time
sys.path.insert(0,r"C:\Users\Josh\AppData\Local\Temp\claude\C--Users-Josh\e4e947ae-e8f0-4332-bd5d-a7cfde49e72b\scratchpad\exo")
import bl
t=time.time()
out = bl.code("""
import bpy, time
t=time.time()
bpy.ops.render.render(animation=True)
print('RENDER DONE in %.0f s'%(time.time()-t))
""", timeout=14400)
print(out)
print("wall %.0f s"%(time.time()-t))
