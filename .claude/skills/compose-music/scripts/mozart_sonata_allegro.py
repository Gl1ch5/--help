"""Example: Mozart-style sonata Allegro in C major (Alberti bass, 4/4)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from music import Piece, R

p = Piece(bpm=126, seed=3)
q, e, s = 1, .5, .25

A = [('C',  [('C5', q), ('E5', q), ('G5', q), ('E5', e), ('C5', e)]),
     ('G',  [('D5', 1.5), ('B4', e), ('G4', 2)]),
     ('C',  [('C5', q), ('E5', q), ('G5', q), ('C6', q)]),
     ('G7', [('B5', 1.5), ('A5', e), ('G5', 2)]),
     ('F',  [('A5', q), ('F5', q), ('A5', q), ('C6', q)]),
     ('C',  [('G5', q), ('E5', q), ('G5', q), ('C6', q)]),
     ('G7', [('B5', e), ('A5', e), ('G5', e), ('F5', e), ('E5', q), ('D5', q)]),
     ('C',  [('C5', 3), (R, 1)])]
A2 = [('C',  [('E5', q), ('G5', q), ('C6', q), ('G5', e), ('E5', e)]),
      ('G',  [('F5', 1.5), ('D5', e), ('B4', 2)]),
      ('C',  [('E5', q), ('G5', q), ('C6', q), ('E6', q)]),
      ('G7', [('D6', 1.5), ('B5', e), ('G5', 2)]),
      ('F',  [('A5', e), ('C6', e), ('F6', q), ('C6', q), ('A5', q)]),
      ('Dm', [('F5', q), ('A5', q), ('D6', q), ('F5', q)]),
      ('G7', [('G5', q), ('B5', q), ('D6', q), ('F6', q)]),
      ('C',  [('E6', 3), (R, 1)])]
BRIDGE = [('C',  [(n, s) for n in 'C5 D5 E5 F5 G5 A5 B5 C6 D6 E6 F6 G6 A6 G6 F6 E6'.split()]),
          ('G7', [(n, s) for n in 'D6 C6 B5 A5 G5 F5 E5 D5 C5 D5 E5 F5 G5 A5 B5 D6'.split()]),
          ('Am', [('C6', e), ('B5', e), ('A5', e), ('G#5', e), ('A5', q), ('E5', q)]),
          ('D7', [('F#5', q), ('A5', q), ('C6', q), ('A5', q)])]
B = [('G',  [('D5', q), ('G5', q), ('B5', q), ('G5', q)]),
     ('D7', [('A5', 1.5), ('F#5', e), ('D5', 2)]),
     ('G',  [('G5', e), ('A5', e), ('B5', e), ('C6', e), ('D6', 2)]),
     ('D7', [('C6', 1.5), ('A5', e), ('F#5', 2)]),
     ('C',  [('E6', q), ('C6', q), ('E6', q), ('G6', q)]),
     ('G',  [('D6', q), ('B5', q), ('D6', q), ('G6', q)]),
     ('D7', [('F#6', e), ('E6', e), ('D6', e), ('C6', e), ('B5', q), ('A5', q)]),
     ('G',  [('G5', 3), (R, 1)])]
END = [('F',  [('A5', q), ('F5', q), ('C6', q), ('A5', q)]),
       ('G7', [('B5', q), ('D6', q), ('F6', q), ('D6', q)]),
       ('C',  [('E6', q), ('C6', q), ('G5', q), ('E5', q)]),
       ('G7', [('D5', 1.5), ('F5', e), ('B5', 2)]),
       ('C',  [('C6', 4)])]

for chord, mel in A + A2 + BRIDGE + B + A + END:
    p.bar(chord, mel, accomp='alberti')
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'mozart')
os.makedirs(out, exist_ok=True)
p.save(os.path.join(out, 'mozart_style_sonata_allegro.mid'))
