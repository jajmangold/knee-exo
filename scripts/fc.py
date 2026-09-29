import socket, xmlrpc.client, sys, base64
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
socket.setdefaulttimeout(300)
PORT = 9880
s = xmlrpc.client.ServerProxy(f"http://127.0.0.1:{PORT}/", allow_none=True)
def run(path):
    code = open(path, encoding="utf-8").read()
    r = s.execute_code(code)
    print(r.get("message") or r)
    if not r.get("success"): sys.exit(1)
def shot(out, view="Isometric", w=1400, h=1000, focus=None):
    b = s.get_active_screenshot(view, w, h, focus)
    if not b: print("screenshot failed"); return
    open(out, "wb").write(base64.b64decode(b)); print("wrote", out)
if __name__ == "__main__":
    if sys.argv[1] == "run": run(sys.argv[2])
    elif sys.argv[1] == "shot": shot(*sys.argv[2:])
