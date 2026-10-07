"""Original Rachmaninoff-style piece in G minor (84 bpm): march, lyrical section, climax, coda.
Harmony: i - iv - V7 - i, VI, III, VII (all diatonic G minor, with sevenths).
Left hand = bass note(s) + root-position-ish chords (stride, hand stays within ~an octave per grip).
Right hand = melody on top of closed chords (A), melody + off-beat inner dyads (B), octaves + chords (A').
MIDI: instrument 0 = right hand, 1 = left hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pretty_midi as pm
from music import Piece, N

p = Piece(bpm=84, seed=33)
LHI = pm.Instrument(0, name='Piano LH'); p.midi.instruments.append(LHI)
B = p.beat
CH = {'Gm': [7, 10, 2], 'Gm7': [7, 10, 2, 5], 'Cm': [0, 3, 7], 'Cm7': [0, 3, 7, 10], 'D7': [2, 6, 9, 0],
      'Eb': [3, 7, 10], 'Bb': [10, 2, 5], 'F': [5, 9, 0]}


def add(inst, n, a, dur, v):
    inst.notes.append(pm.Note(max(1, min(120, v + p.rng.randint(-3, 3))), n, a + p.rng.uniform(0, .012), a + dur))


def up(pc, lo):
    m = lo
    while m % 12 != pc: m += 1
    return m


def below(ch, top, n=2, gap=3, lo=0):
    """n chord tones under `top`, at least `gap` semitones apart, highest first."""
    out, last = [], top
    m = top - 1
    while len(out) < n and m > lo:
        if m % 12 in CH[ch] and last - m >= gap: out.append(m); last = m
        m -= 1
    return out


def lh_chord(ch):                     # three chord tones just above D3
    return [m for m in range(50, 70) if m % 12 in CH[ch]][:3]


def lh_bass(ch):
    return up(CH[ch][0], 38)           # G2..F#3 region


def pedal(t0, dur=4):
    for inst in (p.inst, LHI):
        inst.control_changes += [pm.ControlChange(64, 127, t0 + .01), pm.ControlChange(64, 0, t0 + dur * B - .06)]


def lh(c1, c2, t0, pat, v):
    for h, ch in enumerate((c1, c2)):
        x = t0 + 2 * h * B
        b = lh_bass(ch)
        if pat == 'march':             # bass octave, chord, (repeat in the next half)
            for n in (b, b + 12): add(LHI, n, x, B * .85, v + 10)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .85, v)
        elif pat == 'pad':             # long bass, soft chord stabs
            add(LHI, b, x, 2 * B, v + 6); add(LHI, b + 12, x, 2 * B, v)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .9, v - 14)
        elif pat == 'hold':
            for n in (b, b + 12): add(LHI, n, x, 2 * B, v + 6)
        elif pat == 'big':             # climax: bass octave + chord on every beat pair, louder
            for n in (b, b + 12): add(LHI, n, x, B * .9, v + 12)
            for n in lh_chord(ch): add(LHI, n, x + B, B * .9, v + 2)


def rh(c1, c2, mel, t0, mode, v):
    x = t0
    for note, d in mel:
        ch = c1 if (x - t0) < 2 * B - 1e-6 else c2
        if note:
            m = N(note)
            dur = d * B * .95
            add(p.inst, m, x, dur, v + 8)
            if mode == 'chord':
                for k in below(ch, m): add(p.inst, k, x, dur, v - 8)
            elif mode == 'oct':
                add(p.inst, m - 12, x, dur, v)
                for k in below(ch, m, 1, 3, m - 11): add(p.inst, k, x, dur, v - 10)
            elif mode == 'sing':       # held melody, off-beat dyads underneath (inside an octave)
                k = 0.5
                while k < d - 1e-6:
                    for q in below(ch, m, 2, 3, m - 10): add(p.inst, q, x + k * B, B * .45, v - 30)
                    k += 1
        x += d * B


A = [('Gm', 'Gm', [('G5', 1.5), ('F5', .5), ('D5', 1), ('A#4', 1)]),
     ('Gm', 'Gm', [('D5', 1.5), ('D#5', .5), ('D5', 1), ('C5', 1)]),
     ('Cm', 'Cm', [('D#5', 1.5), ('D5', .5), ('C5', 1), ('G4', 1)]),
     ('D7', 'D7', [('D5', 1), ('F#5', 1), ('A5', 1), ('C6', 1)]),
     ('Gm', 'Gm', [('A#5', 1.5), ('A5', .5), ('G5', 1), ('D5', 1)]),
     ('Eb', 'Eb', [('G5', 1.5), ('F5', .5), ('D#5', 1), ('A#4', 1)]),
     ('Cm7', 'D7', [('C5', 1), ('D#5', 1), ('F#5', 1), ('A5', 1)]),
     ('Gm', 'Gm', [('G5', 3), (None, 1)])]
LY = [('Eb', 'Eb', [('G5', 2), ('A#5', 1), ('G5', 1)]),
      ('Bb', 'Bb', [('D6', 2), ('C6', 1), ('A#5', 1)]),
      ('Cm7', 'Cm7', [('C6', 1.5), ('A#5', .5), ('G5', 2)]),
      ('D7', 'D7', [('A5', 2), ('F#5', 1), ('A5', 1)]),
      ('Gm', 'Gm', [('A#5', 2), ('G5', 1), ('D5', 1)]),
      ('Eb', 'Eb', [('D#6', 2), ('D6', 1), ('C6', 1)]),
      ('Cm7', 'D7', [('C6', 1), ('A#5', 1), ('A5', 1), ('F#5', 1)]),
      ('Gm7', 'Gm', [('G5', 4)])]
INTRO = [('Gm', 'Gm', [('G5', 4)]), ('Cm', 'Cm', [('G5', 2), ('D#5', 2)]),
         ('D7', 'D7', [('A5', 4)]), ('D7', 'D7', [('F#5', 2), ('A5', 2)])]
CODA = [('Gm', 'Gm', [('G5', 2), ('A#5', 2)]), ('Cm7', 'Cm7', [('C6', 2), ('G5', 2)]),
        ('D7', 'D7', [('A5', 2), ('F#5', 2)]), ('Gm', 'Gm', [('G5', 4)])]


def section(bars, mode, pat, v, lv, ped=True):
    for c1, c2, mel in bars:
        t0 = p.t
        rh(c1, c2, mel, t0, mode, v); lh(c1, c2, t0, pat, lv)
        if ped: pedal(t0)
        p.t += 4 * B


section(INTRO, 'oct', 'hold', 100, 80)
section(A, 'chord', 'march', 88, 76)
section(LY, 'sing', 'pad', 84, 70)
section(A, 'oct', 'big', 104, 88)
section(LY, 'sing', 'pad', 94, 78)
section(A, 'oct', 'big', 114, 96)
section(CODA, 'oct', 'big', 112, 94)
t0 = p.t                                         # final chord
for n in ('G4', 'A#4', 'D5', 'G5'): add(p.inst, N(n), t0, 6 * B, 112)
for n in ('G2', 'D3', 'G3'): add(LHI, N(n), t0, 6 * B, 104)
pedal(t0, 6)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'rachmaninoff')
os.makedirs(out, exist_ok=True)
p.save(os.path.join(out, 'rachmaninoff_style_g_minor.mid'))
