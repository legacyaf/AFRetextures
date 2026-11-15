"""Synthesises the reel soundtrack (original, no samples). Usage: mkaudio.py out.wav"""
import sys, wave
import numpy as np

SR, DUR = 48000, 23.5
N = int(SR * DUR)
t = np.arange(N) / SR
rs = np.random.RandomState(7)
L = np.zeros(N); R = np.zeros(N)

def add(sig, at=0.0, pan=0.0, gain=1.0):
    i = int(at * SR); n = min(len(sig), N - i)
    if n <= 0: return
    L[i:i + n] += sig[:n] * gain * (1 - max(0, pan))
    R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))

def band(noise, lo, hi):
    F = np.fft.rfft(noise); f = np.fft.rfftfreq(len(noise), 1 / SR)
    F *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(F, len(noise))

def ramp(x, a, b):
    return np.clip((x - a) / (b - a), 0, 1)

def boom(f0=95, f1=32, dur=2.6, noise=0.5):
    n = int(dur * SR); x = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-x * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.2)
    s = np.tanh(s * 2.2)
    s += band(rs.randn(n), 60, 900) * np.exp(-x * 7) * noise
    s += band(rs.randn(n), 1500, 7000) * np.exp(-x * 40) * noise * 0.5
    return s * np.minimum(1, x * 400)

def pad(freqs, dur, attack, release, bright=1.0):
    n = int(dur * SR); x = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.0, 0.005):
            for h in range(1, 7):
                s += np.sin(2 * np.pi * f * (1 + det) * h * x + rs.rand() * 6.28) / h ** (2.2 / bright)
    s /= len(freqs) * 3
    return s * ramp(x, 0, attack) * (1 - ramp(x, dur - release, dur))

def bell(f, dur=3.0):
    n = int(dur * SR); x = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * x) * np.exp(-x * 1.6) + 0.35 * np.sin(2 * np.pi * f * 2.01 * x) * np.exp(-x * 3) \
        + 0.15 * np.sin(2 * np.pi * f * 3.0 * x) * np.exp(-x * 5)
    return s * np.minimum(1, x * 200)

D1, D2, A2, D3, F3, A3, C4, D4, E4, F4, A4 = 36.71, 73.42, 110.0, 146.83, 174.61, 220.0, 261.63, 293.66, 329.63, 349.23, 440.0
Bb2, Bb3, G3 = 116.54, 233.08, 196.0

TT, CT = 15.4, 20.2   # title and call-to-action times

# wind bed
w = band(rs.randn(N), 150, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1)) ** 2
add(w * (1 - 0.6 * ramp(t, TT - 1, TT)), gain=0.10, pan=-0.3)
w2 = band(rs.randn(N), 300, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.09 * t)) ** 2
add(w2, gain=0.05, pan=0.3)

# low drone through the intro, growing
n = int(14.6 * SR)
add(pad([D1, D2, D2 * 1.5], 14.6, 2.5, 0.3, bright=0.8) * (0.5 + 0.5 * ramp(t[:n], 0, 12)), gain=0.55)
add(bell(D4), at=0.8, gain=0.10, pan=-0.2); add(bell(A3), at=2.2, gain=0.09, pan=0.2)

# the dead: hit, dissonant bed, growls
add(boom(80, 34, 2.4, 0.3), at=3.4, gain=0.6)
add(pad([D3, D3 * 1.06, A3 * 1.03], 3.3, 0.8, 0.4, bright=0.9), at=3.4, gain=0.16)
for k, at in enumerate([3.7, 4.5, 5.1, 5.8]):
    m = int(0.9 * SR); x = np.arange(m) / SR
    g = band(rs.randn(m), 90 + 30 * k, 420) * (0.6 + 0.4 * np.sin(2 * np.pi * (27 + 5 * k) * x)) * np.sin(np.pi * x / 0.9) ** 2
    add(g, at=at, gain=0.5, pan=[-0.5, 0.4, -0.2, 0.5][k])

# beat hits: fight, loot, gear, build, cannibals
beats = [6.6, 7.8, 9.0, 11.4, 12.6]
add(boom(100, 34, 1.2, 0.6), at=10.2, gain=0.7)
add(pad([F3 / 2, F3], 1.2, 0.02, 0.25, bright=1.3), at=10.2, gain=0.3)
for i, at in enumerate(beats):
    add(boom(105 + i * 6, 34, 1.5, 0.7), at=at, gain=0.85)
    add(pad([[D2, D3], [Bb2 / 2, Bb2], [D2, D3, A3], [G3 / 2, G3], [A2 / 2, A2, A2 * 1.06]][i], 1.2, 0.02, 0.25, bright=1.3), at=at, gain=0.3)
    if i in (0, 1, 3):
        m = int(0.5 * SR)
        add(band(rs.randn(m), 2500, 9000) * np.exp(-np.arange(m) / SR * 16), at=at + 0.6, gain=0.12, pan=0.4 if i % 2 else -0.4)
for k in range(11):   # gunfire under FIGHT
    m = int(0.16 * SR); x = np.arange(m) / SR
    add(band(rs.randn(m), 400, 5000) * np.exp(-x * 45), at=6.68 + k * 0.095 + rs.rand() * 0.02, gain=0.22, pan=rs.uniform(-0.6, 0.6))
for k, f in enumerate([D4 * 2, F4 * 2, A4 * 2, D4 * 4]):   # loot sparkle
    add(bell(f, 1.2), at=7.85 + k * 0.09, gain=0.08, pan=-0.3 + 0.2 * k)
for k in range(3):    # heartbeat under the cannibals
    add(boom(62, 38, 0.45, 0.03), at=12.6 + k * 0.7, gain=0.6)
    add(boom(54, 36, 0.45, 0.03), at=12.6 + k * 0.7 + 0.18, gain=0.42)

# riser into the title
n = int(2.0 * SR); x = np.arange(n) / SR; p = x / 2.0
rz = band(rs.randn(n), 400, 9000) * p ** 2.5 * 0.5
rz += np.sin(2 * np.pi * np.cumsum(110 * 2 ** (p * 2)) / SR) * p ** 3 * 0.25
rz += np.sin(2 * np.pi * np.cumsum(165 * 2 ** (p * 2)) / SR) * p ** 3 * 0.15
add(rz, at=TT - 2.0, gain=0.5)
sw = boom(60, 60, 1.0, 1.0)[::-1] * np.linspace(0, 1, int(1.0 * SR)) ** 2
add(sw, at=TT - 1.0, gain=0.35)

# title impact + chords
add(boom(120, 30, 4.5, 1.0), at=TT, gain=1.1)
add(boom(70, 28, 3.0, 0.2), at=TT + 0.02, gain=0.6)
chords = [(TT, [D2, D3, F3, A3, D4], 3.4), (TT + 3.2, [Bb2 / 2, Bb2, D3, F3, Bb3], 1.6),
          (CT, [D2, D3, A3, D4, F4], 3.4)]
for at, fr, d in chords:
    add(pad(fr, d + 0.5, 0.25 if at > TT else 0.01, 0.9, bright=1.25), at=at, gain=0.42)
add(pad([D1, D2], DUR - TT, 0.01, 1.5, bright=0.8), at=TT, gain=0.5)
for dt, f in [(0, D4 * 2), (1.0, A4), (2.0, F4 * 2), (3.2, D4 * 2), (4.0, F4), (4.8, D4 * 2), (5.8, A4), (6.6, D4)]:
    add(bell(f, 3.2), at=TT + dt, gain=0.13, pan=rs.uniform(-0.4, 0.4))
add(boom(90, 32, 3.0, 0.5), at=CT, gain=0.8)
for k in range(9):   # slow pulse under the title
    add(boom(58, 40, 0.5, 0.05), at=TT + 0.5 + k * 0.5, gain=0.16 if k % 2 else 0.24)

# reverb: convolve with decaying noise
def reverb(x, pre):
    n = int(2.6 * SR); ir = rs.randn(n) * np.exp(-np.arange(n) / SR * 2.6); ir = band(ir, 200, 5000)
    ir = np.concatenate([np.zeros(pre), ir])
    m = 1 << int(np.ceil(np.log2(len(x) + len(ir))))
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[:len(x)]
wl, wr = reverb(L, 400), reverb(R, 700)
wl /= np.abs(wl).max(); wr /= np.abs(wr).max()
L = L + wl * 0.22 * np.abs(L).max(); R = R + wr * 0.22 * np.abs(R).max()

fade = ramp(t, 0, 0.4) * (1 - ramp(t, DUR - 1.3, DUR - 0.05))
st = np.stack([L, R], 1) * fade[:, None]
st = np.tanh(st / np.abs(st).max() * 1.6) / np.tanh(1.6) * 0.89
with wave.open(sys.argv[1], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((st * 32767).astype('<i2').tobytes())
