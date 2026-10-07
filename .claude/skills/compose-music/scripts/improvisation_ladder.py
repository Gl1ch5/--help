"""Chopin-style melody in G minor as a lead sheet + an 'improvisation ladder' showing how to develop it.

Outputs (folder improv/): lead sheet PDF (melody, chord symbols, bass notes, chord chart, tips),
theme MIDI, backing track (left hand only, 4 choruses to improvise over), and the ladder MIDI:
  0 theme -> 1 left hand comes alive -> 2 ornament the melody -> 3 richer harmony
  -> 4 free improvisation (runs, octaves, cadenza).
Melody and chords are one source of truth for both the audio and the LilyPond lead sheet."""
import os, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))
from engine import *

T = None
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', 'improv')
os.makedirs(OUT, exist_ok=True)
BPM = 66

# ---------------- the theme: 16 bars, 4/4, chords (c1, c2) per half bar ----------------
THEME = [('Gm', 'Gm', [('D5', 1.5), ('G5', .5), ('A#5', 1), ('A5', .5), ('G5', .5)]),
         ('Gm', 'Gm', [('F#5', 1), ('G5', .5), ('A5', .5), ('A#5', 2)]),
         ('Cm', 'Cm', [('C6', 1.5), ('A#5', .5), ('G#5', .5), ('G5', .5), ('D#5', 1)]),
         ('D7', 'D7', [('D5', 1), ('F#5', .5), ('A5', .5), ('C6', 1.5), ('A#5', .5)]),
         ('Gm', 'Gm', [('A5', 1.5), ('G5', .5), ('D5', 1), ('A#4', 1)]),
         ('Eb', 'Eb', [('A#4', 1), ('D#5', 1), ('G5', 1.5), ('F5', .5)]),
         ('Cm', 'D7', [('D#5', 1), ('G5', .5), ('C6', .5), ('A5', 1), ('F#5', 1)]),
         ('Gm', 'Gm', [('G5', 3), (T, 1)]),
         ('Bb', 'Bb', [('F5', 1), ('A#5', 1.5), ('A5', .5), ('G5', 1)]),
         ('F', 'F', [('A5', 1.5), ('G5', .5), ('F5', 1), ('C5', 1)]),
         ('Eb', 'Eb', [('G5', 1), ('A#5', 1), ('D#6', 1.5), ('D6', .5)]),
         ('Cm', 'Cm', [('C6', 1), ('A#5', .5), ('G#5', .5), ('G5', 1), ('D#5', 1)]),
         ('Gm', 'Gm', [('D5', 1), ('G5', 1), ('A#5', 1.5), ('A5', .5)]),
         ('Ab', 'Ab', [('G#5', 1.5), ('G5', .5), ('D#5', 1), ('C5', 1)]),
         ('Cm', 'D7', [('D#6', 1), ('D6', 1), ('C6', .5), ('A5', .5), ('F#5', 1)]),
         ('Gm', 'Gm', [('G5', 4)])]
RICH = [('Gm', 'Gm'), ('Gm', 'Gm'), ('Cm7', 'Cm7'), ('D7b9', 'D7b9'), ('Gm', 'Gm7'), ('Ebmaj7', 'Ebmaj7'), ('Cm7', 'D7b9'), ('Gm', 'Gm'),
        ('Bbmaj7', 'Bbmaj7'), ('F7', 'F7'), ('Ebmaj7', 'Ebmaj7'), ('Cm7', 'Cm7'), ('Gm7', 'Gm7'), ('Abmaj7', 'Abmaj7'), ('Cm7', 'D7b9'), ('Gm', 'Gm')]


# ---------------- ornamenting ----------------
def steps_between(m, n, ch):
    d = 1 if n > m else -1; cur = m
    for k in range(1, 5):
        cur = step(cur, d, ch)
        if cur == n: return k
        if (d > 0 and cur > n) or (d < 0 and cur < n): return None
    return None


def next_pitch(bars, bi, ei):
    for b in range(bi, len(bars)):
        for e, (n, d) in enumerate(bars[b][2]):
            if (b, e) > (bi, ei) and n is not None: return midi(n)
    return None


def flourish(m, d, nxt, ch):
    n = 5 if d < 3 else 8
    dr = 1 if (nxt is not None and nxt > m) else -1
    cur, seq = m, []
    for _ in range(n):
        if (dr > 0 and cur > 84) or (dr < 0 and cur < 62): dr = -dr
        cur = step(cur, dr, ch); seq.append((cur, .25))
    return [(m, d - .25 * n)] + seq


def embellish(bars, level):
    out = []
    for bi, (c1, c2, mel) in enumerate(bars):
        new, x = [], 0
        for ei, (n, d) in enumerate(mel):
            ch = c1 if x < 2 - 1e-9 else c2
            if n is None: new.append((n, d))
            else:
                m, nxt = midi(n), next_pitch(bars, bi, ei)
                if level >= 4 and d >= 2: new += flourish(m, d, nxt, ch)
                elif d >= 2: new += turn(m, d, ch)
                elif d == 1.5: new += [(m, 1), (step(m, 1, ch), .25), (m, .25)]
                elif d == 1 and nxt is not None and steps_between(m, nxt, ch) == 2: new += [(m, .5), (step(m, 1 if nxt > m else -1, ch), .5)]
                else: new.append((m, d))
            x += d
        out.append((c1, c2, new))
    return out


# ---------------- LilyPond lead sheet ----------------
FLAT = ['c', 'des', 'd', 'ees', 'e', 'f', 'fis', 'g', 'aes', 'a', 'bes', 'b']
DUR = {4: '1', 3: '2.', 2: '2', 1.5: '4.', 1: '4', .75: '8.', .5: '8', .25: '16'}
SYM = {'Gm': 'g:m', 'Gm7': 'g:m7', 'Cm': 'c:m', 'Cm7': 'c:m7', 'D7': 'd:7', 'D7b9': 'd:7.9-', 'Eb': 'ees', 'Bb': 'bes', 'F': 'f',
       'Ab': 'aes', 'Ebmaj7': 'ees:maj7', 'Bbmaj7': 'bes:maj7', 'F7': 'f:7', 'Abmaj7': 'aes:maj7', 'C': 'c'}
RU = ['до', 'ре♭', 'ре', 'ми♭', 'ми', 'фа', 'фа♯', 'соль', 'ля♭', 'ля', 'си♭', 'си']


def ly_note(m, d):
    o = m // 12 - 1
    return FLAT[m % 12] + ("'" * (o - 3) if o >= 3 else "," * (3 - o)) + DUR[d]


def lead_sheet(path_ly):
    mel, bass, chords = [], [], []
    for c1, c2, m in THEME:
        for n, d in m: mel.append('r' + DUR[d] if n is None else ly_note(midi(n), d))
        if c1 == c2:
            bass.append(ly_note(lh_bass(c1), 4)); chords.append(SYM[c1] if False else SYM[c1].replace(':', '1:', 1) if ':' in SYM[c1] else SYM[c1] + '1')
        else:
            for c in (c1, c2):
                bass.append(ly_note(lh_bass(c), 2)); chords.append(SYM[c].replace(':', '2:', 1) if ':' in SYM[c] else SYM[c] + '2')
    allc = []
    for c1, c2, _ in THEME + [(a, b, 0) for a, b in RICH]:
        for c in (c1, c2):
            if c not in allc: allc.append(c)
    rows = []
    for c in sorted(allc, key=lambda c: (CH[c][0] - 7) % 12):
        notes = ' – '.join(RU[(pc)] for pc in CH[c])
        bn = RU[CH[c][0]]
        rows.append('\\line { \\bold "%s"  —  %s   (бас: %s) }' % (c, notes, bn))
    tips = [
        "Как пользоваться: сыграй тему (аудио theme), потом играй левой рукой аккорды из таблицы, а правой — свою версию.",
        "Ступень 1: оживи левую руку — арпеджио (бас, потом три ноты аккорда).",
        "Ступень 2: украшай мелодию — форшлаги, трели, «проходящие» ноты между скачками, мордент на длинных нотах.",
        "Ступень 3: обогащай гармонию — септаккорды (Cm7, Gm7), Ebmaj7, D7♭9 вместо D7, F7 вместо F; мелодия остаётся.",
        "Ступень 4: свободно — быстрые пассажи на длинных нотах, октавы в части B, каденция в конце, рубато и педаль.",
        "Секрет: длинные ноты темы — самое удобное место для украшений; сильные доли держи на нотах аккорда."]
    doc = r'''\version "2.24.3"
#(set-global-staff-size 19)
\paper { #(define fonts (set-global-fonts #:roman "DejaVu Serif" #:sans "DejaVu Sans" #:typewriter "DejaVu Sans Mono")) }
\header { title = "Мелодия для импровизации" subtitle = "в стиле Шопена, соль минор" composer = "Claude" tagline = ##f }
global = { \key g \minor \time 4/4 \tempo "Andante cantabile" 4 = %d }
\score {
  << \new ChordNames { \set chordChanges = ##f \chordmode { %s } }
     \new Staff { \global \clef treble { %s } }
     \new Staff { \global \clef bass { %s } } >>
  \layout { }
}
\markup \vspace #1
\markup \bold "Аккорды: ноты и бас (названия нот по-русски)"
\markup \column { %s }
\markup \vspace #1
\markup \bold "Лестница импровизации"
\markup \column { %s }
''' % (BPM, ' '.join(chords), ' '.join(mel), ' '.join(bass), '\n'.join(rows),
       '\n'.join('\\wordwrap { %s }' % t for t in tips))
    open(path_ly, 'w').write(doc)


# ---------------- audio ----------------
def build():
    stages = []
    # theme alone (2 choruses) -----------------------------------------------------------
    et = Engine(BPM, 71)
    for _ in range(2): et.section(THEME, 'solo', 'noct', 80, 56, ped=True)
    et.final_chord(4, 100)
    et.save('improv', 'chopin_theme.mid')
    # backing track: left hand only, 4 choruses -------------------------------------------
    eb = Engine(BPM, 72)
    rests = [(c1, c2, [(T, 4)]) for c1, c2, _ in THEME]
    for _ in range(4): eb.section(rests, 'solo', 'wave', 0, 60, ped=True)
    eb.final_chord(4, 90)
    eb.save('improv', 'chopin_backing_track.mid')
    # ladder -------------------------------------------------------------------------------
    e = Engine(BPM, 73)
    gap = lambda: setattr(e.p, 't', e.p.t + 2 * e.B)
    stage = lambda name: stages.append((name, round(e.p.t, 1)))
    rich = lambda bars: [(r[0], r[1], b[2]) for r, b in zip(RICH, bars)]
    orn = embellish(THEME, 2)
    free = embellish(THEME, 4)
    stage('0. Тема'); e.section(THEME, 'solo', 'noct', 80, 56, ped=True); gap()
    stage('1. Левая рука оживает (арпеджио)'); e.section(THEME, 'solo', 'wave', 82, 58, ped=True); gap()
    stage('2. Украшаем мелодию'); e.section(orn, 'solo', 'wave', 84, 60, ped=True, rub=.04); gap()
    stage('3. Богаче гармония'); e.section(rich(orn), 'sing', 'wave', 86, 62, ped=True, rub=.04); gap()
    stage('4. Свободная импровизация')
    e.section(rich(free)[:8], 'sing', 'wave', 90, 66, ped=True, rub=.05)
    e.section(rich(free)[8:], 'oct', 'tango_big', 100, 84, ped=True, rub=.03)
    e.section([('Gm', 'D7', arp(['G4', 'A#4', 'D5', 'G5', 'A#5', 'D6', 'A#5', 'G5']) + run('D7', 'D6', 8, -1)),
               ('Gm', 'Gm', [('G5', 4)])], 'oct', 'tango_big', 104, 88, ped=True)
    e.final_chord(6, 108)
    e.save('improv', 'chopin_improvisation_ladder.mid')
    return stages


if __name__ == '__main__':
    st = build()
    for n, t in st: print('%6.1f s  %s' % (t, n))
    lead_sheet(os.path.join(OUT, 'chopin_theme_leadsheet.ly'))
    subprocess.run(['lilypond', '-o', os.path.join(OUT, 'chopin_theme_leadsheet'), os.path.join(OUT, 'chopin_theme_leadsheet.ly')],
                   check=True, capture_output=True)
    os.remove(os.path.join(OUT, 'chopin_theme_leadsheet.ly'))
