"""Original Vivaldi-style Allegro for piano (A minor, 4/4, ritornello form).
Playable by design: right hand is a single line (max span one octave inside a beat),
left hand is a single-note bass line in the low register. MIDI: instrument 0 = right hand, 1 = left hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pretty_midi as pm
from music import Piece, N, R

p = Piece(bpm=132, seed=11)
LHI = pm.Instrument(0, name='Piano LH'); p.midi.instruments.append(LHI)
b16 = p.beat / 4

# chord -> (root pc, third pc, fifth pc)
CH = {'Am': (9, 0, 4), 'Dm': (2, 5, 9), 'G': (7, 11, 2), 'C': (0, 4, 7), 'F': (5, 9, 0),
      'Em': (4, 7, 11), 'E': (4, 8, 11), 'E7': (4, 8, 11)}
A_MINOR = {9, 11, 0, 2, 4, 5, 7}


def near(pc, target):
    return min((m for m in range(24, 100) if m % 12 == pc), key=lambda m: abs(m - target))


def tones(ch, base):
    """root, third, fifth, octave: ascending from the root nearest to base."""
    r, t, f = CH[ch]
    r0 = near(r, base)
    out = [r0]
    for pc in (t, f):
        m = out[-1] + 1
        while m % 12 != pc: m += 1
        out.append(m)
    out.append(r0 + 12)
    return out


def scale_note_below(m, k, ch):
    """k steps down the A-minor scale (G# on E chords) from midi note m."""
    pcs = set(A_MINOR)
    if ch in ('E', 'E7'): pcs = (pcs - {7}) | {8}
    n = m
    for _ in range(k):
        n -= 1
        while n % 12 not in pcs: n -= 1
    return n


def add(inst, n, a, dur, v):
    inst.notes.append(pm.Note(max(1, min(120, v + p.rng.randint(-3, 3))), n, a + p.rng.uniform(0, .006), a + dur))


def lh_bass(ch, t0, style, v):
    r = near(CH[ch][0], 40) if near(CH[ch][0], 40) <= 52 else near(CH[ch][0], 40) - 12
    r = r if r >= 36 else r + 12
    tt = tones(ch, r)
    pat = {'octave': [tt[0], tt[3], tt[0], tt[3]], 'broken': [tt[0], tt[2], tt[1], tt[2]]}[style]
    for i, n in enumerate(pat):
        add(LHI, n, t0 + i * p.beat / 2, p.beat / 2 * (.8 if style == 'octave' else .95), v + (10 if i == 0 else 0))


def half_rh(kind, ch, t0, v, mel=None):
    if kind == 'mel':
        x = t0
        for n, d in mel:
            if n: add(p.inst, N(n), x, d * p.beat * .88, v + (6 if abs((x - t0) % p.beat) < 1e-6 else 0))
            x += d * p.beat
    elif kind == 'arp':           # 8 sixteenths over the chord, one octave span
        t = tones(ch, 72)
        seq = [t[0], t[1], t[2], t[1], t[3], t[2], t[1], t[2]]
        for i, n in enumerate(seq):
            add(p.inst, n, t0 + i * b16, b16 * .97, v + (8 if i % 4 == 0 else 0))
    elif kind == 'run':           # descending scale, 8 sixteenths, from the fifth of the chord
        top = near(CH[ch][2], 83)
        for i in range(8):
            add(p.inst, scale_note_below(top, i, ch), t0 + i * b16, b16 * .97, v + (8 if i % 4 == 0 else 0))


def bar(c1, c2, kind, v, bass, mel=None):
    t0 = p.t
    h = 2 * p.beat
    if kind == 'mel':
        half_rh('mel', c1, t0, v, mel)
    else:
        half_rh(kind, c1, t0, v); half_rh(kind, c2, t0 + h, v)
    lh_bass(c1, t0, bass, v - 22); lh_bass(c2, t0 + h, bass, v - 22)
    p.t += 4 * p.beat


# Ritornello (forte): bars as (chord1, chord2, melody for the whole bar)
RIT = [('Am', 'Am', [('A4', 1), ('C5', .5), ('E5', .5), ('A5', 1), ('E5', 1)]),
       ('Am', 'Am', [('A5', .5), ('G#5', .5), ('A5', .5), ('B5', .5), ('C6', 1), ('E5', 1)]),
       ('Dm', 'Dm', [('D5', .5), ('F5', .5), ('A5', .5), ('F5', .5), ('D6', 1), ('A5', 1)]),
       ('E', 'E', [('G#5', .5), ('B5', .5), ('E6', 1), ('D6', .5), ('C6', .5), ('B5', 1)]),
       ('Am', 'Am', [('A5', .5), ('C6', .5), ('E6', 1), ('C6', 1), ('A5', 1)]),
       ('F', 'F', [('F5', .5), ('A5', .5), ('C6', 1), ('A5', 1), ('F5', 1)]),
       ('Dm', 'E', [('D6', .5), ('C6', .5), ('B5', .5), ('A5', .5), ('G#5', 1), ('B5', 1)]),
       ('Am', 'Am', [('A5', 1.5), ('E5', .5), ('A4', 2)])]
EP1 = [('Am', 'Dm'), ('G', 'C'), ('F', 'Dm'), ('G', 'C'), ('Em', 'Am'), ('Dm', 'G'), ('C', 'F'), ('G', 'C')]
EP2 = [('Am', 'Dm'), ('G', 'C'), ('F', 'Dm'), ('E', 'E'), ('Am', 'Dm'), ('G', 'C'), ('F', 'E7'), ('Am', 'E')]
EP3 = [('Am', 'Dm'), ('G', 'C'), ('F', 'Dm'), ('E', 'E'), ('Am', 'Dm'), ('G', 'C'), ('F', 'E7'), ('Am', 'Am')]


def ritornello(v=100):
    for c1, c2, mel in RIT:
        bar(c1, c2, 'mel', v, 'octave', mel)


ritornello()
for c1, c2 in EP1: bar(c1, c2, 'arp', 78, 'broken')
for c1, c2 in EP2: bar(c1, c2, 'run', 84, 'broken')
for c1, c2 in EP3: bar(c1, c2, 'arp', 82, 'broken')
ritornello(104)
# final cadence: Am chord, hands within one octave each
t0 = p.t
for n in ('A4', 'C5', 'E5', 'A5'): add(p.inst, N(n), t0, 4 * p.beat, 108)
for n in ('A1', 'A2'): add(LHI, N(n), t0, 4 * p.beat, 100)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'vivaldi')
os.makedirs(out, exist_ok=True)
p.save(os.path.join(out, 'vivaldi_style_allegro.mid'))
