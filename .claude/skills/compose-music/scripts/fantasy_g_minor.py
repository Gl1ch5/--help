"""Fantasy in G minor blending Mozart (clear periods, runs, light chords), Chopin (ornamented singing
melody, turns, rubato, nocturne) and Rachmaninoff (heavy chords/octaves, climax).
Left hand: only bass notes and root-position-ish chords on I, IV, V7, VI, III. Right hand: complex.
MIDI: instrument 0 = right hand, 1 = left hand. 92 bpm."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pretty_midi as pm
from music import Piece, N

p = Piece(bpm=92, seed=44)
LHI = pm.Instrument(0, name='Piano LH'); p.midi.instruments.append(LHI)
B = p.beat
CH = {'Gm': [7, 10, 2], 'Gm7': [7, 10, 2, 5], 'Cm': [0, 3, 7], 'Cm7': [0, 3, 7, 10], 'D7': [2, 6, 9, 0],
      'Eb': [3, 7, 10], 'Bb': [10, 2, 5]}
NAT = [7, 9, 10, 0, 2, 3, 5]; HARM = [7, 9, 10, 0, 2, 3, 6]


def midi(n): return n if isinstance(n, int) else N(n)


def add(inst, n, a, dur, v, late=0.0):
    inst.notes.append(pm.Note(max(1, min(120, int(v) + p.rng.randint(-3, 3))), n, a + late + p.rng.uniform(0, .01), a + late + dur))


def up(pc, lo):
    m = lo
    while m % 12 != pc: m += 1
    return m


def scale_for(ch): return HARM if ch == 'D7' else NAT


def step(m, k, ch):
    """k scale steps from midi note m (k<0 = down) in G minor (harmonic on D7)."""
    pcs = scale_for(ch); d = 1 if k > 0 else -1
    for _ in range(abs(k)):
        m += d
        while m % 12 not in pcs: m += d
    return m


def run(ch, start, n, direction, dur=.25):
    m = midi(start); out = []
    for _ in range(n):
        out.append((m, dur)); m = step(m, direction, ch)
    return out


def arp(notes, dur=.25): return [(midi(x), dur) for x in notes]


def turn(note, dur, ch):
    """Chopin-style turn after an initial half beat: main, upper, main, lower, main, then hold."""
    m = midi(note)
    return [(m, .5), (step(m, 1, ch), .125), (m, .125), (step(m, -1, ch), .125), (m, .125), (m, dur - 1)]


def below(ch, top, n=2, gap=3, lo=0):
    out, last, m = [], top, top - 1
    while len(out) < n and m > lo:
        if m % 12 in CH[ch] and last - m >= gap: out.append(m); last = m
        m -= 1
    return out


def lh_chord(ch): return [m for m in range(50, 70) if m % 12 in CH[ch]][:3]
def lh_bass(ch): return up(CH[ch][0], 38)


def pedal(t0, dur=4):
    for inst in (p.inst, LHI):
        inst.control_changes += [pm.ControlChange(64, 127, t0 + .01), pm.ControlChange(64, 0, t0 + dur * B - .06)]


def lh(c1, c2, t0, pat, v):
    for h, ch in enumerate((c1, c2)):
        x = t0 + 2 * h * B; b = lh_bass(ch)
        if pat == 'mozart':      # oom-pah, light and short
            add(LHI, b, x, B * .5, v + 6)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .45, v)
        elif pat == 'noct':      # singing bass held, soft chord
            add(LHI, b, x, 2 * B * .98, v + 4)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .92, v - 12)
        elif pat == 'big':       # Rachmaninoff: bass octave, then full chord
            for n in (b, b + 12): add(LHI, n, x, B * .9, v + 12)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .9, v + 2)
        elif pat == 'hold':
            for n in (b, b + 12): add(LHI, n, x, 2 * B, v + 8)


def rh(c1, c2, mel, t0, mode, v, rub=0.0):
    assert abs(sum(d for _, d in mel) - 4) < 1e-6, (c1, c2, mel)
    x = t0
    for note, d in mel:
        ch = c1 if (x - t0) < 2 * B - 1e-6 else c2
        if note is not None:
            m = midi(note); dur = d * B * .95
            late = p.rng.uniform(0, rub) if (rub and d >= .5) else 0
            on = abs((x - t0) % B) < 1e-6
            vv = v + (8 if on else 0) - (6 if d < .3 else 0)
            add(p.inst, m, x, dur, vv, late)
            if mode == 'third':
                for k in below(ch, m, 1, 3, m - 5): add(p.inst, k, x, dur, vv - 22, late)
            elif mode == 'chord':
                for k in below(ch, m): add(p.inst, k, x, dur, vv - 10, late)
            elif mode == 'oct':
                add(p.inst, m - 12, x, dur, vv - 2, late)
                for k in below(ch, m, 1, 3, m - 11): add(p.inst, k, x, dur, vv - 12, late)
            elif mode == 'sing' and d >= 1:
                k = .5
                while k < d - 1e-6:
                    for q in below(ch, m, 2, 3, m - 10): add(p.inst, q, x + k * B, B * .45, vv - 32, late)
                    k += 1
        x += d * B


def section(bars, mode, pat, v, lv, ped=False, rub=0.0):
    for c1, c2, mel in bars:
        t0 = p.t
        rh(c1, c2, mel, t0, mode, v, rub); lh(c1, c2, t0, pat, lv)
        if ped: pedal(t0)
        p.t += 4 * B


# ---------- Mozart: period (antecedent + consequent) ----------
A = [('Gm', 'Gm', [('G4', 1), ('A#4', .5), ('D5', .5), ('G5', 1.5), ('F#5', .5)]),
     ('Gm', 'D7', [('A5', 1), ('A#5', .5), ('A5', .5), ('F#5', 2)]),
     ('Cm', 'Gm', [('D#5', 1), ('G5', .5), ('C6', .5), ('A#5', 1), ('G5', 1)]),
     ('D7', 'D7', [('F#5', 1), ('A5', 1), ('C6', 1), ('A5', 1)]),
     ('Gm', 'Gm', [('G4', 1), ('A#4', .5), ('D5', .5), ('G5', 1.5), ('A5', .5)]),
     ('Gm', 'Eb', [('A#5', 1.5), ('A5', .5), ('G5', 2)]),
     ('Cm', 'D7', [('C6', 1), ('A#5', .5), ('A5', .5), ('F#5', 1), ('A5', 1)]),
     ('Gm', 'Gm', [('G5', 3), (None, 1)])]
A2 = [('Gm', 'Gm', run('Gm', 'G4', 8, 1) + [('A#5', 1), ('A5', .5), ('G5', .5)]),
      ('Gm', 'D7', [('A5', .5), ('A#5', .5), ('C6', .5), ('A#5', .5)] + run('D7', 'D6', 8, -1)),
      ('Cm', 'Gm', arp(['D#5', 'G5', 'C6', 'G5'] * 2) + [('A#5', 1), ('G5', 1)]),
      ('D7', 'D7', arp(['F#5', 'A5', 'C6', 'A5', 'F#5', 'A5'], .5) + [('D6', 1)]),
      ('Gm', 'Gm', [('G4', 1), ('A#4', .5), ('D5', .5), ('G5', 1.5), ('A5', .5)]),
      ('Gm', 'Eb', [('A#5', 1.5), ('A5', .5)] + turn('G5', 2, 'Gm')),
      ('Cm', 'D7', [('C6', 1), ('A#5', .5), ('A5', .5), ('F#5', 1), ('A5', 1)]),
      ('Gm', 'Gm', arp(['D6', 'C6', 'A#5', 'A5'], .5) + [('G5', 2)])]
# ---------- Chopin: nocturne in B-flat / E-flat, then ornamented repeat ----------
B1 = [('Bb', 'Bb', [('F5', 1.5), ('G5', .25), ('F5', .25), ('D5', 1), ('F5', 1)]),
      ('Bb', 'Bb', [('A#5', 1.5), ('A5', .5), ('G5', 2)]),
      ('Eb', 'Eb', [('G5', 1), ('A#5', 1), ('D#6', 1.5), ('D6', .5)]),
      ('Eb', 'Eb', [('A#5', 2), ('G5', 1), ('D#5', 1)]),
      ('Cm', 'Cm', [('C6', 1.5), ('A#5', .5), ('G5', 1), ('D#5', 1)]),
      ('Gm', 'Gm', [('D5', 1), ('G5', 1), ('A#5', 1.5), ('A5', .5)]),
      ('Cm', 'D7', [('C6', 1), ('D#6', 1), ('D6', 1), ('A5', 1)]),
      ('Gm', 'Gm', [('G5', 2), ('D5', 2)])]
B2 = [('Bb', 'Bb', [('F5', 1)] + arp(['G5', 'F5', 'G5', 'F5'], .125) + [('D5', .5), ('F5', 1), ('A#4', 1)]),
      ('Bb', 'Bb', [('A#5', 1.5), ('C6', .25), ('A#5', .25), ('A5', .5), ('G5', 1.5)]),
      ('Eb', 'Eb', [('G5', 1), ('A#5', 1)] + turn('D#6', 2, 'Gm')),
      ('Eb', 'Eb', [('D6', 1), ('C6', .25), ('A#5', .25), ('A5', .25), ('G#5', .25), ('G5', 1), ('D#5', 1)]),
      ('Cm', 'Cm', [('C6', 1.5), ('D6', .25), ('C6', .25), ('A#5', 1), ('G5', 1)]),
      ('Gm', 'Gm', [('D5', 1), ('G5', 1)] + turn('A#5', 2, 'Gm')),
      ('Cm', 'D7', [('C6', 1), ('D#6', 1)] + run('D7', 'D6', 4, -1, .25) + [('A5', 1)]),
      ('Gm', 'D7', [('G5', 1)] + arp(['D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5'], .25) + [('A5', 1)])]
# ---------- Rachmaninoff: climax ----------
C = [('Gm', 'Gm', [('G5', 1.5), ('A5', .5), ('A#5', 1), ('D6', 1)]),
     ('Gm', 'Eb', [('C6', 1.5), ('A#5', .5), ('G5', 1), ('A#5', 1)]),
     ('Cm', 'Cm', [('D#6', 1.5), ('D6', .5), ('C6', 1), ('D#6', 1)]),
     ('D7', 'D7', arp(['D5', 'F#5', 'A5', 'C6', 'D6', 'C6', 'A5', 'F#5']) + [('A5', 1), ('F#5', 1)]),
     ('Gm', 'Gm', [('A#5', 1), ('D6', 1), ('A#5', 1), ('G5', 1)]),
     ('Eb', 'Cm', [('A#5', 1), ('G5', 1), ('C6', 1), ('D#6', 1)]),
     ('D7', 'D7', [('D6', 1.5), ('C6', .5), ('A5', 1), ('F#5', 1)]),
     ('Gm', 'Gm', arp(['G4', 'A#4', 'D5', 'G5', 'A#5', 'D6', 'A#5', 'G5']) + [('G5', 1), ('D5', 1)])]
CODA = [('Gm', 'Gm', run('D7', 'D6', 16, -1)),
        ('Cm', 'Cm', [('C6', 1), ('D#6', 1), ('D6', 1), ('C6', 1)]),
        ('D7', 'D7', [('A5', 1), ('C6', 1), ('D6', 2)]),
        ('Gm', 'Gm', [('A#5', 2), ('G5', 2)])]

section(A, 'third', 'mozart', 84, 58)
section(A2, 'solo', 'mozart', 88, 60)
section(B1, 'sing', 'noct', 74, 56, ped=True, rub=.03)
section(B2, 'sing', 'noct', 80, 58, ped=True, rub=.035)
section(C, 'oct', 'big', 112, 96, ped=True)
section(A2, 'solo', 'mozart', 92, 64)
section(CODA, 'oct', 'big', 114, 98, ped=True)
t0 = p.t
for n in ('G4', 'A#4', 'D5', 'G5'): add(p.inst, N(n), t0, 6 * B, 114)
for n in ('G2', 'D3', 'G3'): add(LHI, N(n), t0, 6 * B, 106)
pedal(t0, 6)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'fantasy')
os.makedirs(out, exist_ok=True)
p.save(os.path.join(out, 'fantasy_g_minor.mid'))
