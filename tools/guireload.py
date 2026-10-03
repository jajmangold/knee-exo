# -*- coding: utf-8 -*-
"""Make the running FreeCAD GUI show what is on disk.

    python tools/guireload.py                 # both legs
    python tools/guireload.py KneeExo_v6      # one

Everything in this repository is built by headless freecadcmd processes writing to
C:/Users/Josh/KneeExo_v6*.FCStd. A GUI instance that had the file open before that keeps its own
copy in memory for ever -- it does not notice the file changed -- so the window can show a capstan
with no teeth for hours after the teeth were cut. That is not a cosmetic problem: 223_cad_shots.py
photographs the GUI, and a stale window publishes stale pictures.

REFUSES TO DISCARD WORK. If a document is touched -- edited in the GUI and not saved -- this stops
rather than closing it, because reopening is how you lose whatever was in that window. Save it or
revert it yourself first.

Prints the geometry fingerprint of each document afterwards, so "the GUI is current" is something
checked rather than assumed. tools/fingerprint.py explains what the hash covers.
"""
import os
import sys
import xmlrpc.client

PORT = int(os.environ.get("KX_PORT", "9880"))
DOCS = sys.argv[1:] or ["KneeExo_v6", "KneeExo_v6_R"]

CODE = """
import FreeCAD, FreeCADGui as Gui, sys
sys.path.insert(0, "C:/Users/Josh/knee-exo/tools")
from fingerprint import fingerprint
want = %r
busy = [n for n in want if n in FreeCAD.listDocuments() and FreeCAD.getDocument(n).isTouched()]
if busy:
    print("REFUSING: unsaved GUI changes in " + ", ".join(busy))
else:
    for n in want:
        if n in FreeCAD.listDocuments():
            FreeCAD.closeDocument(n)
        FreeCAD.openDocument("C:/Users/Josh/%%s.FCStd" %% n)
    if want:
        Gui.ActiveDocument = Gui.getDocument(want[0])
    for n in sorted(FreeCAD.listDocuments()):
        print("  %%-20s %%s" %% (n, fingerprint(FreeCAD.getDocument(n))))
    print("active: " + (Gui.ActiveDocument.Document.Name if Gui.ActiveDocument else "none"))
""" % (DOCS,)

try:
    p = xmlrpc.client.ServerProxy("http://127.0.0.1:%d" % PORT, allow_none=True)
    r = p.execute_code(CODE)
except Exception as e:
    print("no FreeCAD GUI answering on port %d (%s) -- nothing to reload" % (PORT, type(e).__name__))
    raise SystemExit(0)
out = r.get("message") or r.get("error") or ""
print(out.replace("Python code executed successfully.\nOutput: ", "").rstrip())
raise SystemExit(1 if "REFUSING" in out else 0)
