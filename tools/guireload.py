# -*- coding: utf-8 -*-
"""Make the running FreeCAD GUI show what is on disk.

    python tools/guireload.py                 # both legs
    python tools/guireload.py KneeExo_v6      # one

Everything in this repository is built by headless freecadcmd processes writing to
C:/Users/Josh/KneeExo_v6*.FCStd. A GUI instance that had the file open before that keeps its own
copy in memory for ever -- it does not notice the file changed -- so the window can show a capstan
with no teeth for hours after the teeth were cut. That is not a cosmetic problem: 223_cad_shots.py
photographs the GUI, and a stale window publishes stale pictures.

RESTORES VISIBILITY, because freecadcmd destroys it. A document written in console mode does not
maintain GuiDocument.xml, so the next GUI open brings every object back SWITCHED OFF. The window
is then empty and looks exactly like a build that did nothing -- KneeExo_v8 opened with all 50
objects hidden and KneeExo_v6_R with all 42, after both were rebuilt headlessly. Reopening without
switching them back on is how "I don't see it in freecad" happens.

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
    hidden = 0
    for n in want:
        if n not in FreeCAD.listDocuments():
            continue
        for o in FreeCAD.getDocument(n).Objects:
            vo = getattr(o, "ViewObject", None)
            if vo is not None and not vo.Visibility:
                vo.Visibility = True
                hidden += 1
    if hidden:
        print("  switched %%d object(s) back on -- freecadcmd does not keep GuiDocument.xml" %% hidden)
    if want:
        Gui.ActiveDocument = Gui.getDocument(want[0])
        try:
            Gui.activeDocument().activeView().viewAxonometric()
            Gui.SendMsgToActiveView("ViewFit")
        except Exception:
            pass
    for n in sorted(FreeCAD.listDocuments()):
        print("  %%-20s %%s" %% (n, fingerprint(FreeCAD.getDocument(n))))
    print("active: " + (Gui.ActiveDocument.Document.Name if Gui.ActiveDocument else "none"))
""" % (DOCS,)

try:
    p = xmlrpc.client.ServerProxy("http://127.0.0.1:%d" % PORT, allow_none=True)
    r = p.execute_code(CODE)
except Exception as e:
    # Switching several thousand ViewObjects on and fitting the view can exceed the RPC server's
    # 90 s dispatch limit. Overrunning it does NOT mean the work failed -- the same note 219_stl
    # and 397 carry applies: the GUI keeps going and only the reply is lost. Say so, rather than
    # reporting a failure that did not happen.
    if "timed out" in str(e).lower() or "timeout" in type(e).__name__.lower():
        print("GUI dispatch timed out after 90 s -- the reload itself keeps running in the GUI.")
        print("Re-run this with no arguments to read back what it ended up with.")
        raise SystemExit(0)
    print("no FreeCAD GUI answering on port %d (%s) -- nothing to reload" % (PORT, type(e).__name__))
    raise SystemExit(0)
out = r.get("message") or r.get("error") or ""
print(out.replace("Python code executed successfully.\nOutput: ", "").rstrip())
raise SystemExit(1 if "REFUSING" in out else 0)
