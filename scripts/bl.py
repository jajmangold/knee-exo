import socket, json, sys, base64, time
HOST, PORT = "127.0.0.1", 9876
def send(cmd, params=None, timeout=300):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout); s.connect((HOST, PORT))
    s.sendall(json.dumps({"type": cmd, "params": params or {}}).encode())
    buf = b""
    while True:
        chunk = s.recv(65536)
        if not chunk: break
        buf += chunk
        try:
            r = json.loads(buf.decode()); s.close(); return r
        except json.JSONDecodeError:
            continue
    s.close()
    return json.loads(buf.decode()) if buf else None
def code(src, timeout=300):
    r = send("execute_code", {"code": src}, timeout)
    if r is None: return "<no response>"
    if r.get("status") == "error": raise RuntimeError(r.get("message"))
    return r.get("result", {}).get("result", "")
def run(path, timeout=600):
    return code(open(path, encoding="utf-8").read(), timeout)
def shot(out, w=1200):
    r = send("get_viewport_screenshot", {"max_size": w})
    res = r.get("result", {})
    p = res.get("filepath")
    if p:
        import shutil; shutil.copy(p, out); return "copied "+p
    return str(res)[:200]
if __name__ == "__main__":
    a = sys.argv[1]
    if a == "ping":
        print(send("get_scene_info", {}, 10))
    elif a == "run":
        print(run(sys.argv[2]))
    elif a == "code":
        print(code(sys.argv[2]))
    elif a == "shot":
        print(shot(sys.argv[3] if len(sys.argv)>3 else "bl_view.png"))
