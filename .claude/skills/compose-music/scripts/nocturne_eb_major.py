"""«Вечерняя вода» — original nocturne in E-flat major, 12/8, in the style of Chopin's Op. 9 No. 2
(singing melody over a rocking 12/8 bass, ornamented repeats, fioritura, a cadenza and a quiet coda).
Not a copy: melody and harmony are new. Beats are quarter notes; one bar = 6 beats (12 eighths)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsl_piano import *
from nocturne_concerto import play

M = Movement('Nocturne in E-flat', 6, 'Eb', 88, seed=9)
A = [('Eb', 'Bb4:3 G5:1.5 F5:.5 Eb5:.5 F5:.5'),
     ('Eb Bb7', 'G5:1.5 F5:.5 Eb5:1 D5:1.5 C5:.5 Bb4:1'),
     ('Eb Ab', 'Eb5:3 Ab5:1.5 G5:.5 F5:.5 Eb5:.5'),
     ('Bb7', 'D5:3 F5:1.5 Eb5:.5 D5:.5 C5:.5'),
     ('Cm', 'Eb5:1.5 G5:1.5 C6:3'),
     ('Ab', 'Ab5:3 G5:1.5 F5:.5 Eb5:1'),
     ('Eb/Bb Bb7', 'G5:1.5 Bb5:1.5 Ab5:1.5 F5:1.5'),
     ('Eb', 'Eb5:4.5 _:1.5')]
A2 = [('Eb', 'Bb4:2 gC5 Bb4:1 G5:1.5 F5:.5 Eb5:.5 F5:.5'),
      ('Eb Bb7', 'G5:1.5 F5:.5 Eb5:1 D5:.5 Eb5:.5 F5:.5 D5:.5 C5:.5 Bb4:.5'),
      ('Eb Ab', 'Eb5:2 G5:1 Ab5:1.5 G5:.5 F5:.5 Eb5:.5'),
      ('Bb7', 'D5:2 F5:1 Eb5:.5 D5:.5 C5:.5 D5:.5 Eb5:.5 D5:.5'),
      ('Cm', 'Eb5:1 G5:1 C6:1.5 Bb5:.5 Ab5:.5 G5:.5 Ab5:.5 Bb5:.5'),
      ('Ab', '~Ab5:3 G5:1.5 F5:.5 Eb5:1'),
      ('Eb/Bb Bb7', 'G5:1.5 Bb5:1.5 C6:.5 Bb5:.5 Ab5:.5 G5:.5 F5:.5 Ab5:.5'),
      ('Eb', 'gF5 Eb5:6')]
B = [('Cm', 'G5:3 C6:1.5 Eb6:1.5'), ('Cm Fm', 'D6:1.5 C6:1.5 Ab5:3'), ('Bb7', 'Bb5:1.5 Ab5:1.5 G5:1.5 F5:1.5'),
     ('Eb Bb7', 'Eb5:3 D5:1.5 F5:1.5'), ('Cm7', 'Eb5:1.5 G5:1.5 Bb5:3'), ('Fm7 Bb7', 'Ab5:3 G5:1.5 F5:1.5'),
     ('Eb', 'G5:2 Bb5:1 Eb6:3'), ('Ab Bb7', 'Ab5:1.5 C6:1.5 D6:3')]
A3 = [('Eb', 'Bb4:2 >Bb4-F5:.2 G5:1.5 F5:.5 Eb5:.5 F5:.5'),
      ('Eb Bb7', 'G5:1.5 F5:.5 Eb5:1 D5:1.5 C5:.5 Bb4:.5 A4:.25 Bb4:.25'),
      ('Eb Ab', 'Eb5:1 G5:.5 Bb5:.5 Eb6:1 Ab5:1.5 G5:.5 F5:.5 Eb5:.5'),
      ('Bb7', 'D5:1 F5:.5 Ab5:.5 Bb5:1 Ab5:.5 G5:.5 F5:.5 Eb5:.5 D5:.5 C5:.25 D5:.25'),
      ('Cm', 'Eb5:.5 G5:.5 C6:1 Eb6:1 D6:.5 C6:.5 Bb5:.5 Ab5:.5 G5:1'),
      ('Ab Fm', 'Ab5:2 >Bb5-Eb6:.25 D6:.5 C6:.5 Bb5:.5 Ab5:1.5'),
      ('Eb/Bb Bb7', 'G5:1.5 Bb5:1.5 C6:1 Bb5:.5 Ab5:.5 G5:.5 F5:.5'),
      ('Eb', '~Eb5:5 Eb5:1')]
play(M, A, v=64, lv=44, lh='n12', rub=.05)
play(M, A2, v=70, lv=46, lh='n12', rub=.06)
M.tempo(94, 12)
play(M, B, vs=(70, 90), lvs=(52, 62), lh='n12', rub=.05)
M.tempo(84, 6)
play(M, A3, vs=(76, 82), lv=50, lh='n12', rub=.05)
M.tempo(112, 1)
M.bar('Bb7', '>Bb3-Bb5:.125 >C6-Eb6:.125 ~Eb6:.75 >D6-F5:.125 G5:.5 F5:.5 Eb5:.5 D5:.5 _:.25', lh='bell', v=74, lv=40)
M.tempo(104, 1)
M.bar('Bb7', '>Eb4-Db6:.125 Eb6:.125 >D6-Bb4:.125 Bb4:.5 _:.375', lh='bell', v=70, lv=38, key='chrom')
M.tempo(62, 4)
M.bar('Bb7', '~Bb5:3 Ab5:.5 G5:.5 F5:.5 D5:.5 Bb4:1', lh='bell', v=64, lv=36)
M.tempo(66, 6)
play(M, [('Eb', 'G5:1.5 Bb5:1.5 Eb6:3'), ('Ab Bb7', 'Ab5:3 G5:1.5 F5:1.5'), ('Eb', 'Eb5:6')], vs=(54, 40), lvs=(40, 30), lh='n12', rub=.05)
play(M, [('Eb', 'Eb4+G4+Bb4+Eb5:6')], v=38, lv=30, lh='bell')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'nocturne_eb')
    os.makedirs(out, exist_ok=True)
    write_midi([M], os.path.join(out, 'evening_water_nocturne_eb_major.mid'), gap=3.0)
