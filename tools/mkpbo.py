"""Pack a folder into an unsigned PBO: mkpbo.py <folder> <prefix> <out.pbo>"""
import hashlib, os, struct, sys
src, prefix, out = sys.argv[1], sys.argv[2], sys.argv[3]
KEEP = (".cpp", ".paa", ".rvmat", ".p3d", ".c", ".xml", ".json")
files = []
for root, _, names in os.walk(src):
    for n in names:
        if n.lower().endswith(KEEP):
            p = os.path.join(root, n)
            files.append((os.path.relpath(p, src).replace("/", "\\"), open(p, "rb").read()))
files.sort(key=lambda f: f[0].lower())
def entry(name, mime=0, size=0, ts=0, dsize=0):
    return name.encode() + b"\0" + struct.pack("<5I", mime, size, 0, ts, dsize)
buf = entry("", mime=0x56657273) + b"prefix\0" + prefix.encode() + b"\0\0"
for name, data in files:
    buf += entry(name, ts=int(os.path.getmtime(src)), dsize=len(data))
buf += entry("")
for _, data in files:
    buf += data
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "wb").write(buf + b"\0" + hashlib.sha1(buf).digest())
print(out, [f[0] for f in files])
