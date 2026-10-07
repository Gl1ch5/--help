"""Shared helpers for two-hand piano pieces in G minor (right hand = instrument 0, left hand = instrument 1).
Left hand uses only bass notes and chords; right hand can be a melody, chords, octaves, runs.
Used by tango_g_minor.py. (fantasy_g_minor.py carries its own copy of the same helpers.)"""
import pretty_midi as pm
from music import Piece, N

CH = {'Gm': [7, 10, 2], 'Gm7': [7, 10, 2, 5], 'Cm': [0, 3, 7], 'Cm7': [0, 3, 7, 10], 'D7': [2, 6, 9, 0],
      'Eb': [3, 7, 10], 'Bb': [10, 2, 5], 'F': [5, 9, 0]}
NAT = [7, 9, 10, 0, 2, 3, 5]; HARM = [7, 9, 10, 0, 2, 3, 6]


def midi(n): return n if isinstance(n, int) else N(n)


def up(pc, lo):
    m = lo
    while m % 12 != pc: m += 1
    return m


def step(m, k, ch):
    """k scale steps from m in G minor (harmonic on D7)."""
    pcs = HARM if ch == 'D7' else NAT
    d = 1 if k > 0 else -1
    for _ in range(abs(k)):
        m += d
        while m % 12 not in pcs: m += d
    return m


def run(ch, start, n, direction, dur=.25):
    m, out = midi(start), []
    for _ in range(n):
        out.append((m, dur)); m = step(m, direction, ch)
    return out


def arp(notes, dur=.25): return [(midi(x), dur) for x in notes]


def chromatic(lo, hi, dur=.25): return [(m, dur) for m in range(midi(lo), midi(hi) + 1)]


def below(ch, top, n=2, gap=3, lo=0):
    out, last, m = [], top, top - 1
    while len(out) < n and m > lo:
        if m % 12 in CH[ch] and last - m >= gap: out.append(m); last = m
        m -= 1
    return out


def lh_chord(ch): return [m for m in range(50, 70) if m % 12 in CH[ch]][:3]   # three tones from D3 up
def lh_bass(ch): return up(CH[ch][0], 38)                                       # root between D2 and C#3


class Engine:
    def __init__(self, bpm, seed):
        self.p = Piece(bpm=bpm, seed=seed)
        self.lhi = pm.Instrument(0, name='Piano LH'); self.p.midi.instruments.append(self.lhi)
        self.B = self.p.beat

    def add(self, inst, n, a, dur, v, late=0.0):
        r = self.p.rng
        inst.notes.append(pm.Note(max(1, min(120, int(v) + r.randint(-3, 3))), n, a + late + r.uniform(0, .01), a + late + dur))

    def pedal(self, t0, dur=4):
        for inst in (self.p.inst, self.lhi):
            inst.control_changes += [pm.ControlChange(64, 127, t0 + .01), pm.ControlChange(64, 0, t0 + dur * self.B - .06)]

    def lh(self, c1, c2, t0, pat, v):
        B, add, L = self.B, self.add, self.lhi
        if pat in ('tango', 'tango_big', 'tango_soft'):     # 3+3+2 accents: beats 0, 1.5 and 3
            b = lh_bass(c1)
            add(L, b, t0, B * 1.3, v + 10)
            if pat == 'tango_big': add(L, b + 12, t0, B * 1.3, v + 4)
            for n in lh_chord(c1): add(L, n, t0 + 1.5 * B, B * (1.2 if pat != 'tango_soft' else 1.8), v - (14 if pat == 'tango_soft' else 0))
            if pat != 'tango_soft':
                for n in lh_chord(c2): add(L, n, t0 + 3 * B, B * .9, v)
        elif pat == 'hold':
            b = lh_bass(c1)
            for n in (b, b + 12): add(L, n, t0, 4 * B, v + 8)

    def rh(self, c1, c2, mel, t0, mode, v, rub=0.0):
        B, add, P = self.B, self.add, self.p
        assert abs(sum(d for _, d in mel) - 4) < 1e-6, (c1, c2, mel)
        x = t0
        for note, d in mel:
            ch = c1 if (x - t0) < 2 * B - 1e-6 else c2
            if note is not None:
                m = midi(note); dur = d * B * .95
                late = P.rng.uniform(0, rub) if (rub and d >= .5) else 0
                vv = v + (8 if abs((x - t0) % B) < 1e-6 else 0) - (6 if d < .3 else 0)
                add(P.inst, m, x, dur, vv, late)
                if mode == 'chord':
                    for k in below(ch, m): add(P.inst, k, x, dur, vv - 10, late)
                elif mode == 'oct':
                    add(P.inst, m - 12, x, dur, vv - 2, late)
                    for k in below(ch, m, 1, 3, m - 11): add(P.inst, k, x, dur, vv - 12, late)
                elif mode == 'sing' and d >= 1:
                    k = .5
                    while k < d - 1e-6:
                        for q in below(ch, m, 2, 3, m - 10): add(P.inst, q, x + k * B, B * .45, vv - 32, late)
                        k += 1
            x += d * B

    def section(self, bars, mode, pat, v, lv, ped=False, rub=0.0):
        for c1, c2, mel in bars:
            t0 = self.p.t
            self.rh(c1, c2, mel, t0, mode, v, rub); self.lh(c1, c2, t0, pat, lv)
            if ped: self.pedal(t0)
            self.p.t += 4 * self.B

    def final_chord(self, beats=6, v=116):
        t0 = self.p.t
        for n in ('G4', 'A#4', 'D5', 'G5'): self.add(self.p.inst, N(n), t0, beats * self.B, v)
        for n in ('G2', 'D3', 'G3'): self.add(self.lhi, N(n), t0, beats * self.B, v - 8)
        self.pedal(t0, beats)

    def save(self, folder, name):
        import os
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', folder)
        os.makedirs(out, exist_ok=True)
        self.p.save(os.path.join(out, name))
