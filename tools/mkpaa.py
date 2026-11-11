import sys, struct, io
from PIL import Image
src, out, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
im = Image.open(src).convert("RGB").resize((size, size), Image.LANCZOS)
def dxt1(img):
    b = io.BytesIO(); img.save(b, "DDS", pixel_format="DXT1"); d = b.getvalue()
    n = max(1, img.width // 4) * max(1, img.height // 4) * 8
    assert len(d) == 128 + n, (len(d), n)
    return d[128:]
mips = []; w = size
while w >= 4:
    m = im if w == size else im.resize((w, w), Image.LANCZOS)
    mips.append((w, dxt1(m))); w //= 2
avg = im.resize((1, 1), Image.BOX).getpixel((0, 0))
def tagg(name, data): return b"GGAT" + name[::-1] + struct.pack("<I", len(data)) + data
head = struct.pack("<H", 0xFF01)
head += tagg(b"AVGC", bytes([avg[2], avg[1], avg[0], 255]))
head += tagg(b"MAXC", bytes([255, 255, 255, 255]))
off_pos = len(head) + 12
base = off_pos + 64 + 2
offs = []; body = b""
for w, d in mips:
    offs.append(base + len(body))
    body += struct.pack("<HH", w, w) + len(d).to_bytes(3, "little") + d
offs += [0] * (16 - len(offs))
head += tagg(b"OFFS", struct.pack("<16I", *offs))
open(out, "wb").write(head + struct.pack("<H", 0) + body + b"\0" * 6)
im.save(out.replace("_co.paa", "_co.png"))
print(out, len(head) + 2 + len(body) + 6, "bytes", len(mips), "mips")
