"""Original etude in the spirit of Chopin's 'Revolutionary' (C minor, fff):
non-stop 16th-note left-hand arpeggio storm, right hand in octaves and heavy chords."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pretty_midi as pm
from music import Piece, N, R

p = Piece(bpm=168, seed=5)
LH = pm.Instrument(0, name='Piano LH')
p.midi.instruments.append(LH)


def add_lh(n, a, b, v):
    LH.notes.append(pm.Note(max(1, min(120, v + p.rng.randint(-4, 4))), n, a + p.rng.uniform(0, .008), b))
PC = {'Cm': 'C Eb G', 'Fm': 'F Ab C', 'G7': 'G B D F', 'Ab': 'Ab C Eb', 'Eb': 'Eb G Bb',
      'Bb': 'Bb D F', 'Bdim': 'B D F Ab', 'C': 'C E G', 'Gdim': 'G Bb Db E'}
NAMES = {'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'Gb': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}


def tones(ch, lo, hi):
    pcs = {NAMES[x] for x in PC[ch].split()}
    return [m for m in range(lo, hi) if m % 12 in pcs]


def lh(ch, bar_i, t0, vel=88):
    """16 sixteenths: 9 chord tones up and 7 down (or the reverse on odd bars)."""
    ts = tones(ch, 36, 74)[:9]
    seq = ts + ts[-2:0:-1]
    if bar_i % 2: seq = seq[::-1]
    s = p.beat / 4
    for i, n in enumerate(seq):
        add_lh(n, t0 + i * s, t0 + i * s + s * 1.6, vel + (14 if i % 4 == 0 else 0) + (8 if i == 0 else 0))


def rh(ch, mel, t0, heavy=True, vel=112):
    x = t0
    mid = tones(ch, 60, 78)
    for n, d in mel:
        if n:
            m = N(n)
            on_beat = abs((x - t0) / p.beat % 1) < 1e-6
            v = vel + (6 if on_beat else 0)
            p._add(m, x, x + d * p.beat * 1.0, v)
            if heavy:
                p._add(m - 12, x, x + d * p.beat * 1.0, v - 4)            # octave doubling
                if d >= 1:                                                 # fill chord inside the octave
                    for k in [t for t in mid if m - 12 < t < m][-2:]:
                        p._add(k, x, x + d * p.beat * .95, v - 14)
        x += d * p.beat


def bar(ch, mel, bar_i, heavy=True, vel=112, lhv=88):
    t0 = p.t
    lh(ch, bar_i, t0, lhv)
    rh(ch, mel, t0, heavy, vel)
    cc = pm.ControlChange
    p.inst.control_changes += [cc(64, 127, t0 + .01), cc(64, 0, t0 + 4 * p.beat - .04)]
    p.t += 4 * p.beat


def hit(ch, t0, dur, vel=120):
    """Massive chord: bass octaves + 4-note chord in both hands."""
    for n in tones(ch, 24, 50)[:4]:
        add_lh(n, t0, t0 + dur, vel)
    for n in tones(ch, 55, 84):
        p._add(n, t0, t0 + dur, vel)


A = [('Cm', [('G5', 1), ('C6', 1), ('Eb6', 1.5), ('D6', .5)]),
     ('Cm', [('C6', 2), ('G5', 1), ('Eb5', 1)]),
     ('Fm', [('F5', 1), ('Ab5', 1), ('C6', 1.5), ('Bb5', .5)]),
     ('G7', [('B5', 2), ('D6', 1), ('G6', 1)]),
     ('Cm', [('Eb6', 1), ('D6', 1), ('C6', 1), ('G5', 1)]),
     ('Ab', [('Ab5', 1), ('C6', 1), ('Eb6', 1), ('Ab6', 1)]),
     ('Bdim', [('F6', 1.5), ('Eb6', .5), ('D6', 1), ('B5', 1)]),
     ('G7', [('G5', 2), ('B5', 1), ('D6', 1)])]
B = [('Eb', [('G5', 1), ('Bb5', 1), ('Eb6', 2)]),
     ('Bb', [('D6', 1), ('F6', 1), ('Bb6', 2)]),
     ('Cm', [('Eb6', 1), ('G6', 1), ('C7', 2)]),
     ('G7', [('B6', 1), ('G6', 1), ('D6', 1), ('B5', 1)]),
     ('Fm', [('Ab6', 1.5), ('G6', .5), ('F6', 1), ('Eb6', 1)]),
     ('Bdim', [('D6', 1), ('F6', 1), ('Ab6', 2)]),
     ('Cm', [('G6', 2), ('Eb6', 1), ('C6', 1)]),
     ('G7', [('D6', .5), ('F6', .5), ('G6', 1), ('B6', 2)])]
CLIMAX = [('Cm', [('Eb6', .5), ('G6', .5)] * 4), ('Fm', [('F6', .5), ('Ab6', .5)] * 4),
          ('Bdim', [('D6', .5), ('F6', .5)] * 4), ('G7', [('D6', .5), ('G6', .5), ('B6', .5), ('D7', .5), ('G6', 1), ('D7', 1)])]

# intro: crashing chord + descending storm
t0 = p.t
hit('G7', t0, 4 * p.beat, 118)
s = p.beat / 4
for i, n in enumerate(['C6', 'B5', 'Ab5', 'G5', 'F5', 'Eb5', 'D5', 'C5', 'B4', 'Ab4', 'G4', 'F4', 'Eb4', 'D4', 'C4', 'B3']):
    for o in (12, 0, -12):                      # run in triple octaves, fortissimo
        (add_lh if o < 0 else p._add)(N(n) + o, t0 + i * s, t0 + i * s + s * 1.5, 116 if i % 4 == 0 else 108)
p.inst.control_changes += [pm.ControlChange(64, 127, t0), pm.ControlChange(64, 0, t0 + 4 * p.beat - .04)]
p.t += 4 * p.beat

i = 0
for rep in range(2):
    for ch, mel in A:
        bar(ch, mel, i, heavy=True, vel=110 + 6 * rep); i += 1
    for ch, mel in B:
        bar(ch, mel, i, heavy=True, vel=114 + 4 * rep); i += 1
for ch, mel in CLIMAX:
    bar(ch, mel, i, heavy=True, vel=120, lhv=96); i += 1
# ending: C major, hammered chords
for k in range(4):
    t0 = p.t
    hit('G7' if k < 2 else 'C', t0, p.beat * .9, 120)
    p.t += p.beat
t0 = p.t
hit('C', t0, 4 * p.beat, 120)
p.inst.control_changes += [pm.ControlChange(64, 127, t0), pm.ControlChange(64, 0, t0 + 4 * p.beat)]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'etude')
os.makedirs(out, exist_ok=True)
LH.control_changes = list(p.inst.control_changes)
p.save(os.path.join(out, 'revolutionary_style_etude.mid'))
