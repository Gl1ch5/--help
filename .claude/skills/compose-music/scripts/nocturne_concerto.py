"""«Хрупкий день» — Ноктюрн-концерт для фортепиано в четырёх частях (с элементами вальса).
I.   Утро (Allegro giocoso, вальс)     — всё хорошо: радость, весёлые встречи; тучи потихоньку сгущаются
II.  Тревога (Agitato)                  — торопливая тревога, поиски, всё плохо
III. Угасание (Lento funebre)           — сердце замедляется, воспоминание о вальсе, агония
IV.  Тишина (Largo)                     — его больше нет; тема как музыкальная шкатулка и покой
One theme (a rising waltz figure in G major) is transformed through all four movements."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from dsl_piano import *


def play(m, bars, vs=None, lvs=None, **kw):
    n = len(bars)
    for i, b in enumerate(bars):
        chords, mel = b[0], b[1]
        o = dict(kw); o.update(b[2] if len(b) > 2 else {})
        if vs: o['v'] = vs[0] + (vs[1] - vs[0]) * i / n; o['v2'] = vs[0] + (vs[1] - vs[0]) * (i + 1) / n
        if lvs: o['lv'] = lvs[0] + (lvs[1] - lvs[0]) * i / n
        m.bar(chords, mel, **o)


def up8(bars, s=12): return [(b[0], shift_mel(b[1], s)) + tuple(b[2:]) for b in bars]


# =========================== I. Утро ===========================
I = Movement('I. Утро', 3, 'G', 152, seed=1)
THEME = [('G', 'B4:1 D5:1 G5:1'), ('G', 'F#5:1.5 E5:.5 D5:1'), ('C', 'E5:1 G5:1 C6:1'), ('D7', 'B5:1.5 A5:.5 F#5:1'),
         ('G', 'B4:1 D5:1 G5:1'), ('Em', 'G5:1.5 F#5:.5 E5:1'), ('Am D7', 'C6:1 B5:.5 A5:.5 F#5:1'), ('G', 'G5:2 _:1')]
THEME2 = [('G', 'B4:1 D5:.5 E5:.5 G5:1'), ('G', 'F#5:1 gG5 E5:.5 D5:.5 B4:1'), ('C', 'E5:.5 G5:.5 C6:1 E6:1'),
          ('D7', 'D6:1 B5:.5 A5:.5 F#5:1'), ('G', 'B4:.5 D5:.5 G5:1 B5:1'), ('Em', 'G5:1 B5:.5 G5:.5 E5:1'),
          ('Am D7', 'C6:.5 B5:.5 A5:.5 G5:.5 F#5:1'), ('G', '~G5:2 _:1')]
JOKER = [('D', 'F#5:.5 F#5:.5 A5:1 D6:1'), ('D', 'C#6:.5 B5:.5 A5:1 F#5:1'), ('A7', 'E5:.5 E5:.5 G5:1 A5:1'),
         ('D', 'F#5:1 gA5 D5:1 _:1'), ('Bm', 'D5:.5 F#5:.5 B5:1 A5:.5 G5:.5'), ('G', 'G5:.5 B5:.5 D6:1 B5:1'),
         ('A7', 'C#6:.5 E6:.5 D6:.5 C#6:.5 B5:.5 A5:.5'), ('D', 'D6:2 _:1')]
TENDER = [('Em', 'B4:1.5 E5:.5 G5:1'), ('C', 'E5:1.5 D5:.5 C5:1'), ('Am', 'A4:1 C5:1 E5:1'), ('B7', 'D#5:1.5 F#5:.5 B5:1'),
          ('Em', 'B5:1.5 A5:.5 G5:1'), ('C', 'G5:1 E5:.5 G5:.5 C6:1'), ('Am B7', 'A5:1 F#5:.5 G5:.5 D#5:1'), ('Em', 'E5:2 _:1')]
DANCE = [('C', 'E5:.5 C6:.5 E5:.5 C6:.5 E5:.5 C6:.5'), ('C', 'E5:.5 C6:.5 G5:1 E5:1'),
         ('G', 'D5:.5 B5:.5 D5:.5 B5:.5 D5:.5 B5:.5'), ('G', 'D5:.5 B5:.5 G5:1 D5:1'), ('F', 'F5:.5 A5:.5 C6:1 A5:1'),
         ('C', 'E6:1 C6:1 G5:1'), ('G7', 'B5:.5 D6:.5 F6:1 D6:1'), ('C', 'C6:2 _:1')]
WRONG = [('G', 'B4:1 D5:1 G5:1'), ('G', 'F#5:1.5 E5:.5 D5:1'), ('Cm', 'Eb5:1 G5:1 C6:1'), ('D7', 'B5:1.5 A5:.5 F#5:1'),
         ('G', 'B4:1 _:.5 D5:.5 G5:1'), ('Em', 'G5:1.5 F#5:.5 E5:1'), ('Am D7', 'C6:1 B5:.5 A5:.5 F#5:1'), ('G', 'G5:1 _:2')]
CLOUDS = [('G', 'B4:1 D5:1 G5:1'), ('Bdim', 'F5:1.5 E5:.5 D5:1'), ('Cm', 'Eb5:1 G5:1 Bb5:1'), ('D7', 'Eb6:1.5 D6:.5 C6:1'),
          ('Gm', 'Bb4:1 D5:1 G5:1'), ('Eb', 'G5:1.5 F5:.5 Eb5:1'), ('Cdim7 D7', 'C6:1 B5:.5 A5:.5 F#5:1'), ('D7sus4 D7', 'A5:2 F#5:1')]
play(I, [('G', '>D4-D5:.25 G5:.5 B5:.5'), ('D7', '>A4-A5:.25 F#5:.5 A5:.5')], vs=(60, 80), lv=48)
play(I, THEME, v=80, lv=54)
play(I, THEME2, v=86, lv=56, rh='chord')
play(I, JOKER, v=84, lv=52, stac=.55)
play(I, TENDER, v=72, lv=50, lh='noct', rub=.03)
play(I, DANCE, v=90, lv=56, rh='oct')
play(I, up8(JOKER), v=88, lv=54, stac=.55, rh='chord')
I.tempo(138, 24)
play(I, WRONG, v=74, lv=50, rub=.04)
I.tempo(112, 24)
play(I, CLOUDS, vs=(66, 40), lvs=(50, 30), rub=.03)

# =========================== II. Тревога ===========================
II = Movement('II. Тревога', 3, 'Gm', 164, seed=2)
HURRY = [('Gm', 'Bb4:.5 D5:.5 G5:.5 Bb5:.5 G5:.5 D5:.5'), ('Gm', 'F#5:.5 G5:.5 A5:.5 F#5:.5 D5:1'),
         ('Cm', 'Eb5:.5 G5:.5 C6:.5 G5:.5 Eb5:.5 C5:.5'), ('D7', 'A5:.5 F#5:.5 D5:.5 F#5:.5 A5:1'),
         ('Gm', 'D5:.5 G5:.5 Bb5:.5 D6:.5 Bb5:.5 G5:.5'), ('Eb', 'G5:.5 Bb5:.5 Eb6:.5 Bb5:.5 G5:.5 Eb5:.5'),
         ('Cm D7', 'C6:.5 Bb5:.5 A5:.5 G5:.5 F#5:.5 A5:.5'), ('Gm', 'G5:1 _:.5 G5:.5 _:1')]


def chrom(a, up=True):
    b = name_of(nn(a) + (5 if up else -5))
    return '>%s-%s:.5' % (a, b)


SEARCH = [('D7', chrom('G4')), ('D7', chrom('E5', False)), ('D7', chrom('A4')), ('D7', chrom('F5', False)),
          ('Bdim7', chrom('Bb4')), ('Bdim7', chrom('G5', False)), ('D7', chrom('B4')), ('D7', chrom('Ab5', False))]
ASK = [('Gm', 'D5:.5 G5:.5 Bb5:1 _:1'), ('Cm', 'Eb5:.5 G5:.5 C6:1 _:1'), ('Fm', 'F5:.5 Ab5:.5 C6:1 _:1'),
       ('Bdim7', 'B5:.5 D6:.5 F6:1 _:1')]
CRASH = [('D7', '>E6-F5:.25', {'key': 'chrom', 'lh': 'trem'}), ('D7', 'A4:1 F#4:1 D4:1', {'lh': 'trem'})]
CLIMB = [('Gm', 'Bb5:1 D6:1 G6:1'), ('Gm', 'F#6:1.5 E6:.5 D6:1'), ('Cm', 'Eb6:1 G6:1 C7:1'), ('D7', 'Bb6:1.5 A6:.5 F#6:1'),
         ('Gm', 'Bb5:1 D6:1 G6:1'), ('Eb', 'G6:1.5 F6:.5 Eb6:1'), ('Cm D7', 'C7:1 Bb6:.5 A6:.5 F#6:1'), ('Gm', '~G6:3')]
FALL = [('Gm', 'D6:1 Bb5:1 G5:1'), ('Gm', 'D6:1.5 C6:.5 Bb5:1'), ('Gm', 'Bb5:2 A5:1'), ('D7', 'F#5:3')]
play(II, HURRY, v=92, lv=62, lh='hurry', ped='seg')
play(II, up8(HURRY), v=98, lv=64, lh='hurry', rh='oct', ped='seg')
play(II, SEARCH, vs=(72, 104), lvs=(64, 90), lh='trem', key='chrom', rub=0)
play(II, ASK, vs=(84, 96), lv=64, lh='bell', stac=.8)
play(II, CRASH, v=104, lv=88)
play(II, [(c, shift_mel(m, -12)) + tuple(o) for c, m, *o in [(b[0], b[1]) for b in SEARCH]], vs=(80, 108), lvs=(70, 92), lh='trem', key='chrom')
play(II, HURRY, v=100, lv=72, lh='hurry', rh='chord', ped='seg')
II.tempo(196, 24)
play(II, CLIMB, v=108, lv=92, lh='trem', rh='oct')
II.tempo(120, 10)
play(II, FALL, vs=(80, 36), lvs=(60, 24), lh='bell')

# =========================== III. Угасание ===========================
III = Movement('III. Угасание', 4, 'Gm', 54, seed=3)
SIGH = [('Gm', 'G5:1.5 F#5:.5 D5:1 _:1'), ('Eb', 'G5:1.5 F5:.5 Eb5:1 _:1'), ('Cm', 'C6:1.5 Bb5:.5 G5:1 _:1'),
        ('D', 'A5:1.5 F#5:.5 D5:2'), ('Gm', 'Bb5:1.5 A5:.5 G5:1 D5:1'), ('Ab', 'C6:1.5 Bb5:.5 Ab5:1 G5:1'),
        ('D7', 'A5:1 C6:1 Eb6:2'), ('Gm', 'D6:3 _:1')]
MEMORY = [('G', 'B5:1 D6:1 G6:1'), ('G', 'F#6:1.5 E6:.5 D6:1'), ('C', 'E6:1 G6:1 C7:1'), ('Cm', 'Eb6:1 _:2')]
AGONY = [('Cm', 'C6:2 Bb5:1 Ab5:1'), ('Fm', 'Ab5:2 G5:1 F5:1'), ('Bdim7', 'F6:1.5 Eb6:.5 D6:1 C6:1'), ('D7', 'Bb6:3 A6:1'),
         ('Gm', 'G6:2 D6:2'), ('Ab', 'Ab6:2 Eb6:2'), ('D7', 'A5:1 F#5:1 D5:1 _:1'), ('Gm', 'G5:4')]
LAST = [('Gm', 'D5:2 _:2'), ('Gm', 'D5:1 _:3'), ('Gm', 'G4:1 _:3'), ('Gm', '_:4')]
play(III, SIGH, vs=(52, 58), lv=42, lh='pulse', deep=True, rub=.04)
play(III, MEMORY, vs=(46, 34), lv=26, lh='bell', deep=True, bpb=3, rub=.05)
III.tempo(66, 8)
play(III, AGONY[:4], vs=(88, 112), lvs=(80, 96), lh='trem', rh='oct', rub=.02)
play(III, AGONY[4:6], v=112, lv=96, lh='trem', rh='oct')
III.tempo(44, 12)
play(III, AGONY[6:], vs=(80, 44), lvs=(70, 36), lh='pulse', deep=True)
III.tempo(30, 14)
play(III, LAST[:3], vs=(44, 32), lvs=(40, 30), lh='pulse', deep=True, rub=.06)
III.tempo(24, 4)
play(III, LAST[3:], v=26, lv=28, lh='bell', deep=True)

# =========================== IV. Тишина ===========================
IV = Movement('IV. Тишина', 3, 'G', 46, seed=4)
BOX = [('G', '_:3'), ('G', '_:3'), ('G', 'B5:1 D6:1 G6:1'), ('G', 'F#6:2 _:1'), ('C', 'E6:1 G6:1 C7:1'), ('D7', 'B6:2 _:1'),
       ('G', 'B5:1 D6:1 G6:1'), ('Em', 'G6:1.5 F#6:.5 E6:1'), ('Am D7', 'C7:1 B6:.5 A6:.5 F#6:1'), ('G', 'G6:3')]
LULLABY = [('Gmaj7', 'D5:1 G5:1 B5:1'), ('Em7', 'G5:2 E5:1'), ('Cmaj7', 'E5:1 G5:1 C6:1'), ('D', 'F#5:2 _:1'),
           ('Gmaj7', 'B5:1 D6:1 G6:1'), ('Em7', 'F#6:2 E6:1'), ('Am7 D', 'C6:1 B5:.5 A5:.5 F#5:1'), ('G', 'G5:3')]
play(IV, BOX, v=72, lv=52, lh='drone', deep=True, rub=.05)
play(IV, LULLABY, vs=(68, 58), lv=48, lh='drone', deep=True, rub=.06)
IV.tempo(36, 6)
play(IV, [('G', 'G5+D6:3')], v=56, lv=40, lh='bell', deep=True)
play(IV, [('G', '_:3')], v=1, lv=1, lh='none')

if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'concerto')
    os.makedirs(out, exist_ok=True)
    marks = write_midi([I, II, III, IV], os.path.join(out, 'fragile_day_nocturne_concerto.mid'), gap=3.0)
    for n, t in marks: print('%5.0f s  %s' % (t, n))
