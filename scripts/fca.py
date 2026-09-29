import socket, xmlrpc.client, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
socket.setdefaulttimeout(300)
PORT = 9880
s = xmlrpc.client.ServerProxy(f"http://127.0.0.1:{PORT}/", allow_none=True)
def arun(path):
    code = open(path, encoding="utf-8").read()
    try:
        r = s.execute_code_async(code)
    except xmlrpc.client.Fault as e:
        print("no execute_code_async:", e); return
    print(r.get("message") or r)
if __name__ == "__main__":
    arun(sys.argv[1])
