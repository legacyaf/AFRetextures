"""Synthesises the reel soundtrack (original, no samples). Usage: mkaudio.py out.wav"""
import sys, wave
import numpy as np

SR, DUR = 48000, 22.0
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

# wind bed
w = band(rs.randn(N), 150, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.13 * t + 1)) ** 2
add(w * (1 - 0.6 * ramp(t, 11, 12)), gain=0.10, pan=-0.3)
w2 = band(rs.randn(N), 300, 1800) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.09 * t)) ** 2
add(w2, gain=0.05, pan=0.3)

# low drone through the intro, growing
dr = pad([D1, D2, D2 * 1.5], 11.2, 2.5, 0.3, bright=0.8) * (0.5 + 0.5 * ramp(t[:int(11.2 * SR)], 0, 10))
add(dr, gain=0.55)
add(pad([D3, A3], 3.6, 1.2, 0.5), at=3.5, gain=0.16)        # dawn lift
add(bell(D4), at=0.8, gain=0.10, pan=-0.2); add(bell(A3), at=2.2, gain=0.09, pan=0.2)
add(bell(F4), at=3.9, gain=0.11, pan=0.2); add(bell(E4), at=5.4, gain=0.10, pan=-0.2)

# beat hits
add(boom(80, 34, 2.2, 0.3), at=3.6, gain=0.5)
for i, at in enumerate([7.0, 8.0, 9.0, 10.0]):
    add(boom(105 + i * 6, 34, 1.4, 0.7), at=at, gain=0.85)
    tick = band(rs.randn(int(0.5 * SR)), 2500, 9000) * np.exp(-np.arange(int(0.5 * SR)) / SR * 16)
    add(tick, at=at + 0.5, gain=0.12, pan=0.4 if i % 2 else -0.4)
    add(pad([[D2, D3], [Bb2 / 2, Bb2], [G3 / 2, G3], [A2, A3]][i], 1.0, 0.02, 0.25, bright=1.3), at=at, gain=0.3)

# gunfire texture under FIGHT
for k in range(9):
    n = int(0.16 * SR); x = np.arange(n) / SR
    add(band(rs.randn(n), 400, 5000) * np.exp(-x * 45), at=9.08 + k * 0.095 + rs.rand() * 0.02, gain=0.22, pan=rs.uniform(-0.6, 0.6))

# riser into the title
n = int(2.0 * SR); x = np.arange(n) / SR; p = x / 2.0
rz = band(rs.randn(n), 400, 9000) * p ** 2.5 * 0.5
rz += np.sin(2 * np.pi * np.cumsum(110 * 2 ** (p * 2)) / SR) * p ** 3 * 0.25
rz += np.sin(2 * np.pi * np.cumsum(165 * 2 ** (p * 2)) / SR) * p ** 3 * 0.15
add(rz, at=10.0, gain=0.5)
# reverse swell
sw = boom(60, 60, 1.0, 1.0)[::-1] * np.linspace(0, 1, int(1.0 * SR)) ** 2
add(sw, at=11.0, gain=0.35)

# title impact + chords
add(boom(120, 30, 4.5, 1.0), at=12.0, gain=1.1)
add(boom(70, 28, 3.0, 0.2), at=12.02, gain=0.6)
chords = [(12.0, [D2, D3, F3, A3, D4], 3.4), (15.2, [Bb2 / 2, Bb2, D3, F3, Bb3], 1.8), (16.8, [F3 / 2, F3 / 1, A3, C4], 1.9),
          (18.5, [D2, D3, A3, D4, F4], 3.5)]
for at, fr, d in chords:
    add(pad(fr, d + 0.5, 0.25 if at > 12 else 0.01, 0.9, bright=1.25), at=at, gain=0.42)
add(pad([D1, D2], 10, 0.01, 1.5, bright=0.8), at=12.0, gain=0.5)
for at, f in [(12.0, D4 * 2), (13.0, A4), (14.0, F4 * 2), (15.2, D4 * 2), (16.0, F4), (16.8, C4 * 2), (17.6, A4), (18.5, D4 * 2), (19.5, A4), (20.3, D4)]:
    add(bell(f, 3.2), at=at, gain=0.13, pan=rs.uniform(-0.4, 0.4))
add(boom(90, 32, 3.0, 0.5), at=18.5, gain=0.8)
# slow pulse under the title
for k in range(13):
    add(boom(58, 40, 0.5, 0.05), at=12.5 + k * 0.5, gain=0.16 if k % 2 else 0.24)

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
