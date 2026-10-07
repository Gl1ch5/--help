"""Nocturne in G minor in two parts: I. Lento, sad, with an unusual melody (Dorian E natural, a 7th leap,
Neapolitan A-flat chord, chromatic sighs); II. Presto, the same theme in octaves plus a fiery toccata.
Left hand: bass + chords only. Part I at 58 bpm, part II at 152 bpm; merged into one MIDI with a tempo change."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from engine import *
import mido

T = None
# ---------- Part I ----------
THEME = [('Gm', 'Gm', [('D5', 1), ('A5', 2), ('G5', 1)]),
         ('Gm', 'Gm', [('F#5', 1.5), ('E5', .5), ('D5', 2)]),
         ('C', 'C', [('E5', 1), ('G5', 1), ('C6', 2)]),
         ('D7', 'D7', [('A5', 1.5), ('F#5', .5), ('D5', 2)]),
         ('Eb', 'Eb', [('D5', 1), ('C6', 1), ('A#5', 2)]),
         ('Ab', 'Ab', [('G#5', 1.5), ('G5', .5), ('D#5', 2)]),
         ('Cm', 'D7', [('C6', 1), ('A#5', 1), ('A5', 1), ('F#5', 1)]),
         ('Gm', 'Gm', [('G5', 3), (T, 1)])]
THEME2 = [('Gm', 'Gm', [('D5', .5), ('F5', .25), ('D5', .25), ('A5', 2), ('G5', .5), ('F#5', .5)]),
          ('Gm', 'Gm', [('F#5', 1), ('G5', .25), ('F#5', .25), ('E5', .5), ('D5', 1.5), ('A4', .5)]),
          ('C', 'C', [('E5', 1), ('G5', .5), ('C6', .5), ('E6', 1), ('D6', .5), ('C6', .5)]),
          ('D7', 'D7', [('A5', 1), ('C6', .5), ('A5', .5), ('F#5', 1), ('D5', .5), ('F#5', .5)]),
          ('Eb', 'Eb', [('D5', 1), ('C6', 1), ('A#5', 1), ('G5', 1)]),
          ('Ab', 'Ab', turn('G#5', 2, 'Gm') + [('G5', .5), ('D#5', 1.5)]),
          ('Cm', 'D7', [('C6', .5), ('D6', .25), ('C6', .25), ('A#5', 1), ('A5', .5), ('G5', .25), ('F#5', .25), ('D5', 1)]),
          ('Gm', 'Gm', [('G5', 2), ('F#5', .5), ('F5', .5), ('D5', 1)])]
P1_INTRO = [('Gm', 'Gm', [(T, 4)]), ('Gm', 'Gm', [(T, 4)])]
P1_END = [('Gm', 'Gm', [('G5', 4)]), ('D7', 'D7', [('A5', 2), ('F#5', 2)])]
# ---------- Part II ----------
FIRE = [('Gm', 'Gm', arp(['G4', 'A#4', 'D5', 'G5', 'D5', 'A#4', 'D5', 'G5'] * 2)),
        ('Gm', 'Gm', arp(['G4', 'A#4', 'D5', 'G5', 'A#5', 'G5', 'D5', 'A#4'] * 2)),
        ('Ab', 'Ab', arp(['G#4', 'C5', 'D#5', 'G#5', 'D#5', 'C5', 'D#5', 'G#5'] * 2)),
        ('D7', 'D7', arp(['D5', 'F#5', 'A5', 'C6', 'D6', 'C6', 'A5', 'F#5'] * 2)),
        ('Gm', 'Gm', run('Gm', 'G4', 8, 1) + run('Gm', 'G5', 8, -1)),
        ('Eb', 'Eb', arp(['D#5', 'G5', 'A#5', 'D#6', 'A#5', 'G5', 'D#5', 'G5'] * 2)),
        ('Cm', 'D7', arp(['C5', 'D#5', 'G5', 'C6', 'G5', 'D#5', 'C5', 'D#5']) + arp(['D5', 'F#5', 'A5', 'C6', 'D6', 'C6', 'A5', 'F#5'])),
        ('Gm', 'Gm', [('G5', 1), ('A#5', 1), ('D6', 1), ('G5', 1)])]
STORM = [('Gm', 'Gm', chromatic('G4', 'A#5')),
         ('Ab', 'Ab', arp(['G#4', 'C5', 'D#5', 'G#5', 'C6', 'G#5', 'D#5', 'C5'] * 2)),
         ('C', 'C', arp(['C5', 'E5', 'G5', 'C6', 'E6', 'C6', 'G5', 'E5'] * 2)),
         ('D7', 'D7', arp(['D5', 'F#5', 'A5', 'C6', 'D6', 'C6', 'A5', 'F#5'] * 2)),
         ('Gm', 'Gm', [('G5', .5), (T, .5), ('A#5', .5), (T, .5), ('D6', .5), (T, .5), ('G5', 1)]),
         ('Eb', 'Eb', arp(['D#5', 'G5', 'A#5', 'D#6', 'A#5', 'G5', 'D#5', 'G5'] * 2)),
         ('Cm', 'D7', arp(['C5', 'D#5', 'G5', 'C6', 'G5', 'D#5', 'C5', 'D#5']) + chromatic('D5', 'A5')),
         ('D7', 'D7', [('A5', 1), ('F#5', 1), ('D5', 1), (T, 1)])]
CODA = [('Cm', 'Cm', [('C6', 1), ('D#6', 1), ('D6', 1), ('C6', 1)]),
        ('D7', 'D7', [('A5', 1), ('C6', 1), ('D6', 2)]),
        ('Gm', 'Gm', arp(['G4', 'A#4', 'D5', 'G5', 'A#5', 'D6', 'A#5', 'G5']) + [('G5', 1), (T, 1)]),
        ('Gm', 'Gm', [('G5', 2), (T, 2)])]

e1 = Engine(58, 61)
e1.section(P1_INTRO, 'solo', 'hold', 44, 44, ped=True)
e1.section(THEME, 'sing', 'noct', 70, 54, ped=True, rub=.04)
e1.section(THEME2, 'sing', 'noct', 76, 58, ped=True, rub=.05)
e1.section(P1_END, 'chord', 'noct', 66, 52, ped=True, rub=.03)

e2 = Engine(152, 62)
e2.section(FIRE, 'solo', 'drive', 96, 82)
e2.section(THEME, 'oct', 'drive', 104, 88)
e2.section(STORM, 'solo', 'drive', 108, 92)
e2.section(THEME, 'oct', 'drive', 114, 98)
e2.section(CODA, 'oct', 'drive', 116, 100)
e2.final_chord(5)

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', '..', '..', '..', 'nocturne')
os.makedirs(out, exist_ok=True)
f1, f2, fm = [os.path.join(out, x) for x in ('_p1.mid', '_p2.mid', 'nocturne_g_minor_two_parts.mid')]
e1.p.save(f1); e2.p.save(f2)

# merge: part II follows part I track by track (tempo change at the join)
m1, m2 = mido.MidiFile(f1), mido.MidiFile(f2)
end = max(sum(msg.time for msg in tr) for tr in m1.tracks)
merged = mido.MidiFile(ticks_per_beat=m1.ticks_per_beat)
for i, t1 in enumerate(m1.tracks):
    tr = mido.MidiTrack()
    tr.extend(msg for msg in t1 if msg.type != 'end_of_track')
    pad = end - sum(msg.time for msg in t1 if msg.type != 'end_of_track')
    src = [msg for msg in m2.tracks[i] if msg.type != 'end_of_track']
    if src: src[0] = src[0].copy(time=src[0].time + pad)
    tr.extend(src); tr.append(mido.MetaMessage('end_of_track', time=0))
    merged.tracks.append(tr)
merged.save(fm)
os.remove(f1); os.remove(f2)
