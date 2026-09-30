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


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    code = a[1] if a[0] == "-c" else io.open(a[0], encoding="utf-8").read()
    ok, msg, dt = send(code)
    print(msg.rstrip())
    print("[%s in %.1f s]" % ("ok" if ok else "FAILED", dt))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
