#!/usr/bin/env python3
"""Generate OurWorld's music loops and sound effects as tiny 8-bit WAV files.

Everything is synthesized from math (square/triangle/noise), so there is no
copyrighted audio. Deterministic: running it again produces identical files.

    python tools/make_audio.py            # writes assets/audio/*.wav

11025 Hz, 8-bit unsigned, mono: a 4-bar loop is ~60-90 KB.
"""
import array
import math
import os
import random
import wave

RATE = 11025
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}


def freq(name, octave):
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octave + 1) - 69) / 12)


def midi_f(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def square(ph, duty=0.5):
    return 1.0 if (ph % 1.0) < duty else -1.0


def tri(ph):
    p = ph % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def render(buf, start, n, f, wave_fn, vol, attack=0.005, release=0.06, **kw):
    ph = 0.0
    step = f / RATE
    a, r = int(attack * RATE), int(release * RATE)
    for i in range(n):
        j = start + i
        if j >= len(buf):
            break
        env = min(1.0, i / a if a else 1.0) * min(1.0, (n - i) / r if r else 1.0)
        buf[j] += wave_fn(ph, **kw) * vol * env
        ph += step


def noise_hit(buf, start, n, vol, rng):
    for i in range(n):
        j = start + i
        if j >= len(buf):
            break
        buf[j] += (rng.random() * 2 - 1) * vol * (1 - i / n) ** 2


def write(name, buf):
    peak = max(1e-6, max(abs(x) for x in buf))
    k = min(1.0, 0.95 / peak)
    data = array.array("B", (max(0, min(255, int(128 + x * k * 127))) for x in buf))
    os.makedirs(OUT, exist_ok=True)
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(RATE)
        w.writeframes(data.tobytes())


# ------------------------------------------------------------------ music
SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10],
          "penta": [0, 2, 4, 7, 9]}
# name: (root midi, scale, bpm, chord degrees per bar, lead duty, lead vol, seed, swing hats)
THEMES = {
    "home":     (60, "major", 92,  [0, 5, 3, 4], 0.25, 0.22, 1, True),
    "town":     (67, "major", 112, [0, 4, 5, 3], 0.5, 0.20, 2, True),
    "shop":     (65, "major", 124, [0, 3, 4, 0], 0.125, 0.18, 3, True),
    "arcade":   (57, "minor", 138, [0, 5, 6, 4], 0.25, 0.20, 4, True),
    "calm":     (62, "penta", 72,  [0, 3, 4, 3], 0.5, 0.14, 5, False),
    "woods":    (57, "minor", 86,  [0, 3, 6, 4], 0.5, 0.16, 6, False),
    "festival": (64, "major", 132, [0, 4, 5, 3], 0.25, 0.22, 7, True),
    "night":    (55, "penta", 66,  [0, 2, 3, 1], 0.5, 0.11, 8, False),
    "winter":   (64, "major", 96,  [0, 5, 3, 4], 0.125, 0.16, 9, False),
}


def deg(root, scale, d, octave=0):
    sc = SCALES[scale]
    return root + sc[d % len(sc)] + 12 * (d // len(sc) + octave)


def make_theme(name):
    root, scale, bpm, prog, duty, lead_vol, seed, hats = THEMES[name]
    rng = random.Random(seed)
    beat = 60.0 / bpm
    eighth = int(beat / 2 * RATE)
    bars = len(prog)
    n = eighth * 8 * bars
    buf = [0.0] * n
    melody_bar = None
    for b, chord in enumerate(prog):
        bstart = b * eighth * 8
        # bass: root on 1 and 3, fifth on 2 and 4 (triangle)
        for q in range(4):
            d = chord if q % 2 == 0 else chord + 4
            render(buf, bstart + q * eighth * 2, eighth * 2 - 40, midi_f(deg(root, scale, d, -2)), tri, 0.32)
        # pad: soft arpeggio of chord tones
        for e in range(8):
            d = chord + (0, 2, 4, 2)[e % 4]
            render(buf, bstart + e * eighth, eighth - 30, midi_f(deg(root, scale, d, -1)), square,
                   0.05, duty=0.5)
        # lead: a motif repeated with variation on bars 2/4
        if melody_bar is None or b % 2 == 0:
            melody_bar = []
            e = 0
            while e < 8:
                ln = rng.choice((1, 1, 2, 2, 3)) if e < 7 else 1
                ln = min(ln, 8 - e)
                rest = rng.random() < 0.18
                d = chord + rng.choice((0, 2, 4, 4, 5, 7, 2))
                melody_bar.append((e, ln, None if rest else d))
                e += ln
        for e, ln, d in melody_bar:
            if d is None:
                continue
            if b % 2 == 1 and e == 6:
                d = chord + 7
            render(buf, bstart + e * eighth, ln * eighth - 60, midi_f(deg(root, scale, d, 1)), square,
                   lead_vol, duty=duty)
        # percussion
        if hats:
            for e in range(8):
                noise_hit(buf, bstart + e * eighth, int(0.03 * RATE), 0.05 if e % 2 else 0.08, rng)
            for q in (0, 2):
                render(buf, bstart + q * eighth * 2, int(0.08 * RATE), 60.0, tri, 0.25, release=0.06)
    write("music_" + name, buf)


# -------------------------------------------------------------------- sfx
def sweep(f0, f1, secs, wave_fn=square, vol=0.5, **kw):
    n = int(secs * RATE)
    buf = [0.0] * n
    ph = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        buf[i] = wave_fn(ph, **kw) * vol * (1 - i / n) ** 0.7
        ph += f / RATE
    return buf


def seq(notes, step, wave_fn=square, vol=0.45, tail=1.0, **kw):
    n = int(step * RATE * (len(notes) + tail))
    buf = [0.0] * n
    for i, m in enumerate(notes):
        render(buf, int(i * step * RATE), int(step * RATE * (1 + tail)), midi_f(m), wave_fn, vol,
               release=step * 0.8, **kw)
    return buf


def make_sfx():
    rng = random.Random(42)
    write("sfx_move", sweep(900, 900, 0.03, vol=0.25, duty=0.25))
    write("sfx_select", seq([76, 83], 0.05, duty=0.25, vol=0.4))
    write("sfx_back", seq([72, 65], 0.05, duty=0.25, vol=0.35))
    write("sfx_coin", seq([83, 88], 0.06, duty=0.5, vol=0.4, tail=2))
    write("sfx_quest", seq([72, 76, 79, 84, 88], 0.08, duty=0.25, vol=0.45, tail=3))
    write("sfx_sparkle", seq([88, 91, 95, 100], 0.045, wave_fn=tri, vol=0.6, tail=3))
    write("sfx_levelup", seq([67, 72, 76, 79, 84], 0.07, duty=0.5, vol=0.45, tail=4))
    write("sfx_sad", seq([67, 64, 60], 0.12, wave_fn=tri, vol=0.6))
    write("sfx_eat", seq([60, 64, 60, 64], 0.06, duty=0.125, vol=0.35))
    write("sfx_play", sweep(400, 900, 0.18, duty=0.5, vol=0.35))
    write("sfx_rest", seq([72, 67, 64], 0.16, wave_fn=tri, vol=0.5, tail=2))
    n = int(0.35 * RATE)
    splash = [0.0] * n
    noise_hit(splash, 0, n, 0.6, rng)
    write("sfx_splash", splash)
    shutter = [0.0] * int(0.12 * RATE)
    noise_hit(shutter, 0, len(shutter) // 3, 0.7, rng)
    noise_hit(shutter, len(shutter) // 2, len(shutter) // 3, 0.5, rng)
    write("sfx_photo", shutter)
    write("sfx_bite", seq([84, 84], 0.05, duty=0.5, vol=0.4))
    write("sfx_catch", seq([79, 84, 91], 0.07, duty=0.25, vol=0.45, tail=3))
    write("sfx_talk", sweep(600, 650, 0.025, vol=0.18, duty=0.5))
    write("sfx_place", seq([60, 67], 0.05, wave_fn=tri, vol=0.6))


def main():
    for name in THEMES:
        make_theme(name)
    make_sfx()
    total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print(f"wrote {len(os.listdir(OUT))} files to {OUT} ({total // 1024} KB)")


if __name__ == "__main__":
    main()
