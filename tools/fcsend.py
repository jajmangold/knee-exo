# -*- coding: utf-8 -*-
"""Send Python to the running FreeCAD instance over FreeCADMCP's XML-RPC endpoint.

The MCP tool is not always exposed to the agent session, but the RPC server always is.
This is the same transport.

  python tools/fcsend.py scripts/390_layout.py
  python tools/fcsend.py -c "print(App.ActiveDocument.Name)"

HARD LIMIT, learned the hard way: the GUI dispatch times out at 90 s and the RPC then
returns an error WHILE THE WORK CARRIES ON IN THE BACKGROUND. A timeout is therefore not
a failure you can retry -- it silently corrupts any accumulator the script was filling.
Keep every call well under 90 s and chunk long sweeps.
"""
import sys, socket, xmlrpc.client, io, time

PORT = 9880


def send(code, port=PORT, timeout=110):
    socket.setdefaulttimeout(timeout)
    s = xmlrpc.client.ServerProxy("http://127.0.0.1:%d" % port, allow_none=True)
    t0 = time.time()
    r = s.execute_code(code)
    dt = time.time() - t0
    msg = (r.get("message") or r.get("error") or "") if isinstance(r, dict) else str(r)
    ok = isinstance(r, dict) and r.get("success")
    if dt > 85:
        sys.stderr.write("\n!! %.0f s -- at or past the 90 s dispatch limit. Treat the\n"
                         "!! result as UNTRUSTWORTHY: the work may still be running.\n" % dt)
    return ok, msg, dt


POSE_CHECK = """
import FreeCAD as _A
_p = [o.Name for d in _A.listDocuments().values() for o in d.Objects
      if o.isDerivedFrom("Part::Feature") and not o.Placement.isIdentity()]
print("KX_POSED:%d:%s" % (len(_p), ",".join(_p[:6])))
"""


def posed(port=PORT):
    """Which parts are sitting at an animation pose right now.

    Worth a round trip after every dispatch. The animation scripts pose by writing Placements
    and leave the timer running; nothing saves, so the pose lives in the GUI session until the
    NEXT build script calls doc.save() and bakes it into the file. That is invisible --
    valid shapes, right volumes, clean save -- and every boolean against a posed reference then
    uses geometry that is not where the part is. It cost this project a wrong-looking cuff fit,
    a sweep run against a flexed limb, and the user asking why the leg no longer lined up with
    the machine. Cheap to detect, expensive to miss.
    """
    try:
        ok, msg, _ = send(POSE_CHECK, port=port, timeout=20)
    except Exception:
        return None
    for line in (msg or "").splitlines():
        if line.startswith("KX_POSED:"):
            _, n, names = line.split(":", 2)
            return int(n), [x for x in names.split(",") if x]
    return None


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    code = a[1] if a[0] == "-c" else io.open(a[0], encoding="utf-8").read()
    ok, msg, dt = send(code)
    print(msg.rstrip())
    print("[%s in %.1f s]" % ("ok" if ok else "FAILED", dt))
    p = posed()
    if p and p[0]:
        sys.stderr.write("\n!! %d parts are at an animation pose (%s%s).\n"
                         "!! Any save from here bakes it into the file and every boolean\n"
                         "!! against a posed reference reads the wrong geometry.\n"
                         "!! Clear it:  freecadcmd.exe tools/unpose.py\n"
                         % (p[0], ", ".join(p[1]), " ..." if p[0] > len(p[1]) else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
