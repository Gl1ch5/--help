"""Original dark hip-hop piano piece in the spirit of Eminem-style piano loops (G minor, 88 bpm).
Right hand: 16th-note ostinato (playable single line) and a simple hook (octaves).
Left hand: only single bass notes, fifths (power chords) or block triads.
MIDI: instrument 0 = right hand, 1 = left hand."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import pretty_midi as pm
from music import Piece, N

p = Piece(bpm=88, seed=21)
LHI = pm.Instrument(0, name='Piano LH'); p.midi.instruments.append(LHI)
beat = p.beat
CH = {'Gm': (7, 10, 2), 'Bb': (10, 2, 5), 'F': (5, 9, 0), 'Cm': (0, 3, 7), 'D': (2, 6, 9), 'Eb': (3, 7, 10)}


def up(pc, lo):
    m = lo
    while m % 12 != pc: m += 1
    return m


def rh_tones(ch, lo=67):
    r, t, f = CH[ch]
    a = up(r, lo); b = up(t, a + 1); c = up(f, b + 1)
    return [a, b, c]


def add(inst, n, a, dur, v, late=0.0):
    inst.notes.append(pm.Note(max(1, min(120, v + p.rng.randint(-3, 3))), n, a + late + p.rng.uniform(0, .012), a + late + dur))


def bass_note(ch):
    return up(CH[ch][0], 38)             # G2..F3 region, single notes, max 1 ledger line below the staff


def pedal(t0, on=True):
    if on:
        for inst in (p.inst, LHI):
            inst.control_changes += [pm.ControlChange(64, 127, t0 + .01), pm.ControlChange(64, 0, t0 + 4 * beat - .05)]


def left(ch, t0, style, v):
    b = bass_note(ch)
    r, t, f = CH[ch]
    hits = [(0, 1.4), (2.5, 1.4)] if style != 'long' else [(0, 4)]
    for off, d in hits:
        notes = {'boom': [b], 'power': [b, b + 7], 'chord': [b, up(t, b + 1), up(f, b + 2)] if False else [b, b + 7, b + 12], 'long': [b, b + 7]}[style]
        for n in notes: add(LHI, n, t0 + off * beat, d * beat, v + (8 if off == 0 else 0), late=.01)


def ost(ch, t0, v, lo=67, accent=True):
    """16th-note ostinato: 4 groups of 4 notes cycling over the chord tones (single line)."""
    a, b, c = rh_tones(ch, lo)
    groups = [[b, c, b, a], [c, b, a, b], [b, c, b, a], [c, b, a, c]]
    for g, notes in enumerate(groups):
        for i, n in enumerate(notes):
            add(p.inst, n, t0 + (g * 4 + i) * beat / 4, beat / 4 * .92, v + (10 if (i == 0 and accent) else 0), late=.012)


def hook_bar(ch, mel, t0, v, octave=True):
    x = t0
    for n, d in mel:
        if n:
            m = N(n)
            add(p.inst, m, x, d * beat * .92, v + (8 if abs((x - t0) % beat) < 1e-6 else 0), late=.008)
            if octave: add(p.inst, m - 12, x, d * beat * .92, v - 12, late=.008)
        x += d * beat


HOOK = [('Gm', [('D5', 1), ('D5', .5), ('F5', .5), ('G5', 1), ('F5', .5), ('D5', .5)]),
        ('Bb', [('D5', 1), ('D5', .5), ('F5', .5), ('A#5', 1), ('A5', .5), ('F5', .5)]),
        ('F',  [('C5', 1), ('C5', .5), ('F5', .5), ('A5', 1), ('G5', .5), ('F5', .5)]),
        ('Cm', [('D#5', 1), ('G5', 1), ('C6', 1), ('G5', 1)]),
        ('Gm', [('D5', 1), ('D5', .5), ('F5', .5), ('G5', 1), ('F5', .5), ('D5', .5)]),
        ('Bb', [('F5', 1), ('A#5', 1), ('D6', 1), ('A#5', 1)]),
        ('D',  [('A5', .5), ('A5', .5), ('F#5', 1), ('D5', 1), ('F#5', 1)]),
        ('D',  [('A4', 1), ('D5', 1), ('F#5', 2)])]
VERSE = ['Gm', 'Bb', 'F', 'Cm', 'Gm', 'Bb', 'D', 'D']
BRIDGE = ['Cm', 'Cm', 'D', 'D']


def run(chs, kind, v, lstyle, lv, ped=False, hook=None, silent_left=0):
    for i, ch in enumerate(chs):
        t0 = p.t
        if kind == 'ost': ost(ch, t0, v)
        else: hook_bar(ch, hook[i][1], t0, v)
        if i >= silent_left: left(ch, t0, lstyle, lv)
        pedal(t0, ped)
        p.t += 4 * beat


run(['Gm'] * 4, 'ost', 58, 'boom', 66, silent_left=2)                           # intro: motif alone, bass enters
run(VERSE, 'ost', 70, 'boom', 74)                                                # verse: motif + single bass notes
run([h[0] for h in HOOK], 'hook', 98, 'power', 84, ped=True, hook=HOOK)          # hook: octaves + fifths
run(BRIDGE, 'ost', 84, 'power', 90)                                              # bridge: tension
run([h[0] for h in HOOK], 'hook', 108, 'power', 96, ped=True, hook=HOOK)         # final hook, louder
run(['Gm', 'Gm', 'Cm', 'D'], 'ost', 62, 'boom', 66)                              # outro
t0 = p.t
for n in rh_tones('Gm', 67): add(p.inst, n, t0, 4 * beat, 80)
for n in (bass_note('Gm'), bass_note('Gm') + 7): add(LHI, n, t0, 4 * beat, 80)
pedal(t0)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'eminem')
os.makedirs(out, exist_ok=True)
p.save(os.path.join(out, 'eminem_style_piano.mid'))
