"""Write a waving-flag preview mesh (OBJ + MTL) for Blender: mkpreview.py <texture.png> <outdir>"""
import math, os, shutil, sys
tex, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
shutil.copy(tex, os.path.join(out, "flag_preview.png"))
W, H, NX, NY = 1.5, 1.0, 60, 40          # 3:2 flag, hoist edge at x=0
v, vt, f = [], [], []
for j in range(NY + 1):
    for i in range(NX + 1):
        u, t = i / NX, j / NY
        z = 0.06 * u * math.sin(u * 3.2 * math.pi + t * 1.2) + 0.02 * u * math.sin(t * 2 * math.pi)
        v.append((u * W, t * H, z)); vt.append((u, t))   # full 0-1 UV square, like the game texture
for j in range(NY):
    for i in range(NX):
        a = j * (NX + 1) + i + 1; b = a + 1; c = b + NX + 1; d = a + NX + 1
        f.append((a, b, c, d))
with open(os.path.join(out, "flag_preview.obj"), "w") as o:
    o.write("mtllib flag_preview.mtl\no flag_preview\n")
    o.writelines("v %.5f %.5f %.5f\n" % p for p in v)
    o.writelines("vt %.5f %.5f\n" % p for p in vt)
    o.write("usemtl flag\ns 1\n")
    o.writelines("f " + " ".join("%d/%d" % (k, k) for k in q) + "\n" for q in f)
with open(os.path.join(out, "flag_preview.mtl"), "w") as m:
    m.write("newmtl flag\nKd 1 1 1\nKs 0 0 0\nNs 10\nmap_Kd flag_preview.png\n")
print(len(v), "verts", len(f), "quads")
