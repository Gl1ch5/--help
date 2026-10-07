"""A small text DSL for writing piano pieces beat by beat (free tempo curves, any key).

Movement(name, beats_per_bar, key, bpm).bar(chords, melody, lh=..., rh=...)
  chords : "G"  or  "Am D7"  or  "Am D7@2"   (chord names: C, Am, D7, Bdim7, Ebmaj7, G/B, ...)
  melody : space separated tokens, durations in beats (0.5, 1.5, 1/3 ...)
     F#5:1      note            _:1         rest           G4+B4+D5:2   chord
     ~E5:2      trill           gE5         grace note before the next note
     >C6-F5:.25 scale run (stepwise from the first to the last note, in the bar's key; key 'chrom' = chromatic)
     v70        set velocity from here
  lh   : waltz | noct | n12 | hurry | trem | pulse | drone | bell | none
  rh   : solo | oct | chord | oct+   (doubling of the melody)
Tempo: m.tempo(bpm, ramp_beats) at the current position (accelerando / ritardando).
"""
import math, random, re
from fractions import Fraction
import pretty_midi as pm

PCS = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
ACC = {'#': 1, 'b': -1, '': 0}
NOTE_RE = re.compile(r'([A-G])([#b]?)(-?\d)')
SHARPS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
QUAL = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'm7': [0, 3, 7, 10], 'maj7': [0, 4, 7, 11], 'dim': [0, 3, 6],
        'dim7': [0, 3, 6, 9], 'm7b5': [0, 3, 6, 10], 'aug': [0, 4, 8], 'sus4': [0, 5, 7], '7sus4': [0, 5, 7, 10],
        '6': [0, 4, 7, 9], 'add9': [0, 4, 7, 2], '7b9': [0, 4, 7, 10, 1], 'm6': [0, 3, 7, 9], 'm9': [0, 3, 7, 10, 2]}


def nn(name):
    m = NOTE_RE.fullmatch(name)
    if not m: raise ValueError('bad note ' + name)
    L, a, o = m.groups()
    return 12 * (int(o) + 1) + PCS[L] + ACC[a]


def name_of(m): return SHARPS[m % 12] + str(m // 12 - 1)


def dur(s): return float(Fraction(s))


def chord_info(name):
    base, _, slash = name.partition('/')
    m = re.fullmatch(r'([A-G][#b]?)(.*)', base)
    root, q = m.groups()
    r = (PCS[root[0]] + ACC[root[1:]]) % 12
    pcs = [(r + i) % 12 for i in QUAL[q]]
    bass = (PCS[slash[0]] + ACC[slash[1:]]) % 12 if slash else r
    return r, pcs, bass


def voicing(name, lo=50):
    r, pcs, _ = chord_info(name)
    use = pcs[1:4] if len(pcs) >= 4 else pcs        # shell voicing for 7th chords (root is in the bass)
    return [m for m in range(lo, lo + 20) if m % 12 in use][:3]


def bass_note(name, deep=False):
    _, _, b = chord_info(name)
    m = next(x for x in range(38, 50) if x % 12 == b)
    return m - 12 if deep else m


def scale_pcs(key):
    if key == 'chrom': return list(range(12))
    minor = key.endswith('m') or key.endswith('h')
    r = (PCS[key[0]] + ACC[key[1] if len(key) > 1 and key[1] in '#b' else '']) % 12
    iv = [0, 2, 3, 5, 7, 8, 10] if key.endswith('m') else [0, 2, 3, 5, 7, 8, 11] if key.endswith('h') else [0, 2, 4, 5, 7, 9, 11]
    return [(r + i) % 12 for i in iv]


def run_notes(a, b, key):
    pcs = scale_pcs(key); d = 1 if b > a else -1
    out = [a]; m = a
    while m != b and len(out) < 40:
        m += d
        while m % 12 not in pcs: m += d
        if (d > 0 and m > b) or (d < 0 and m < b): break
        out.append(m)
    return out


def upper_neighbor(m, key):
    pcs = scale_pcs(key); m += 1
    while m % 12 not in pcs: m += 1
    return m


def shift_mel(mel, semis):
    def f(mo):
        return name_of(nn(mo.group(0)) + semis)
    return NOTE_RE.sub(f, mel)


class Movement:
    def __init__(self, name, bpb=3, key='G', bpm=100, seed=0):
        self.name, self.bpb, self.key = name, bpb, key
        self.ev, self.ped, self.pos = [], [], 0.0
        self.tp = [(0.0, float(bpm))]
        self.rng = random.Random(seed)

    # ---- tempo curve ----
    def bpm_at(self, b):
        tp = self.tp
        if b <= tp[0][0]: return tp[0][1]
        for (b0, t0), (b1, t1) in zip(tp, tp[1:]):
            if b <= b1: return t0 + (t1 - t0) * (b - b0) / (b1 - b0) if b1 > b0 else t1
        return tp[-1][1]

    def tempo(self, bpm, ramp=0.0):
        cur = self.bpm_at(self.pos)
        self.tp.append((self.pos, cur)); self.tp.append((self.pos + max(ramp, 1e-6), float(bpm)))

    def sec(self, b):
        tp, total, prev = self.tp, 0.0, self.tp[0]
        def seg(b0, t0, b1, t1):
            db = b1 - b0
            return 60 * db / t0 if abs(t1 - t0) < 1e-9 else 60 * db / (t1 - t0) * math.log(t1 / t0)
        for p in tp[1:]:
            if p[0] <= prev[0]: prev = p; continue
            if b <= p[0]: return total + seg(prev[0], prev[1], b, self.bpm_at(b))
            total += seg(prev[0], prev[1], p[0], p[1]); prev = p
        return total + 60 * (b - prev[0]) / prev[1]

    # ---- events ----
    def _ev(self, b0, b1, pitch, vel, late=0.0):
        self.ev.append((b0, b1, int(pitch), int(max(1, min(120, vel + self.rng.randint(-3, 3)))), late + self.rng.uniform(0, .008)))

    def _chords(self, spec, bpb):
        items = spec.split(); names, starts = [], []
        for i, it in enumerate(items):
            n, _, at = it.partition('@')
            names.append(n); starts.append(float(at) if at else round(i * bpb / len(items) + 1e-9))
        ends = starts[1:] + [bpb]
        return list(zip(names, starts, ends))

    def bar(self, chords, mel='', lh='waltz', rh='solo', v=80, v2=None, lv=None, ped=True, rub=0.0, stac=1.0,
            key=None, bpb=None, deep=False):
        bpb = bpb or self.bpb; key = key or self.key; v2 = v if v2 is None else v2
        lv = lv if lv is not None else max(20, v - 26)
        t0 = self.pos
        segs = self._chords(chords, bpb)
        # ---- left hand ----
        for name, s, e in segs:
            self._lh(name, t0 + s, t0 + e, lh, lv, stac, deep)
        # ---- right hand ----
        x, vel, total = 0.0, None, 0.0
        def chord_at(t):
            for name, s, e in segs:
                if s <= t < e: return name
            return segs[-1][0]
        for tok in mel.split():
            if re.fullmatch(r'v\d+', tok): vel = int(tok[1:]); continue
            if tok.startswith('g') and NOTE_RE.fullmatch(tok[1:]):
                self._ev(t0 + x - .12, t0 + x, nn(tok[1:]), (vel or v) - 8); continue
            body, _, d = tok.partition(':'); d = dur(d)
            base = vel if vel is not None else v + (v2 - v) * x / bpb + (5 if x % 1 == 0 else 0)
            late = self.rng.uniform(0, rub) if (rub and d >= .5) else 0
            if body == '_': pass
            elif body.startswith('>'):
                a, b = body[1:].split('-'); notes = run_notes(nn(a), nn(b), key)
                for i, m in enumerate(notes): self._ev(t0 + x + i * d, t0 + x + (i + 1) * d * 1.1, m, base + (4 if i % 4 == 0 else 0), late)
                d = d * len(notes)
            elif body.startswith('~'):
                m = nn(body[1:]); u = upper_neighbor(m, key); n = int(d / .125)
                for i in range(n): self._ev(t0 + x + i * .125, t0 + x + (i + 1) * .125 * 1.2, m if i % 2 == 0 or i == n - 1 else u, base - 6, late)
            else:
                ms = [nn(p) for p in body.split('+')]
                dd = d * (.95 if stac >= 1 else stac)
                for m in ms:
                    self._ev(t0 + x, t0 + x + dd, m, base, late)
                    if rh in ('oct', 'oct+'): self._ev(t0 + x, t0 + x + dd, m - 12, base - 8, late)
                    if rh in ('chord', 'oct+') and len(ms) == 1:
                        _, pcs, _ = chord_info(chord_at(x)); k = 0
                        for q in range(m - 1, m - 13, -1):
                            if q % 12 in pcs and m - q >= 3 and k < (2 if rh == 'chord' else 1):
                                self._ev(t0 + x, t0 + x + dd, q, base - 14, late); k += 1; m = q
            x += d; total += d
        assert abs(total - bpb) < 1e-6, (self.name, chords, mel, total, bpb)
        if ped == 'seg':
            for _, s, e in segs: self.ped += [(t0 + s + .02, 127), (t0 + e - .06, 0)]
        elif ped:
            self.ped += [(t0 + .02, 127), (t0 + bpb - .06, 0)]
        self.pos += bpb

    def _lh(self, name, a, b, pat, v, stac, deep):
        if pat == 'none': return
        bn, vo, L = bass_note(name, deep), voicing(name), b - a
        sh = lambda s: stac if stac < 1 else s
        if pat == 'waltz':
            self._ev(a, a + min(L, 1) * sh(.9), bn, v + 10)
            for i in range(1, int(L)):
                for m in vo: self._ev(a + i, a + i + sh(.85), m, v)
        elif pat == 'n12':       # 12/8 nocturne rocking: per dotted quarter group, bass then two chord tones
            vo2 = voicing(name, 55)
            for g in range(int(L // 1.5)):
                t = a + 1.5 * g; pr = (vo2[0], vo2[1]) if g % 2 == 0 else (vo2[1], vo2[2])
                self._ev(t, t + 1.45, bn, v + 8)
                self._ev(t + .5, t + 1.4, pr[0], v - 6); self._ev(t + 1.0, t + 1.5, pr[1], v - 6)
        elif pat == 'noct':
            seq = [bn, vo[0], vo[1], vo[2], vo[1], vo[0]]
            for i in range(int(L * 2)): self._ev(a + i * .5, a + i * .5 + .95, seq[i % 6], v + (8 if i == 0 else 0))
        elif pat == 'hurry':
            for i in range(int(L * 2)):
                if i == 0: self._ev(a, a + .45, bn, v + 12); self._ev(a, a + .45, bn + 12, v + 4)
                else:
                    for m in vo: self._ev(a + i * .5, a + i * .5 + .4, m, v + (6 if i % 2 == 0 else -4))
        elif pat == 'trem':
            for i in range(int(L * 4)): self._ev(a + i * .25, a + i * .25 + .3, bn + (12 if i % 2 else 0), v + (8 if i % 4 == 0 else 0))
            for m in vo: self._ev(a, a + L * .9, m, v - 18)
        elif pat == 'pulse':
            for i in range(int(L)):
                self._ev(a + i, a + i + .4, bn, v); self._ev(a + i + .35, a + i + .7, bn, v - 14)
        elif pat == 'drone':
            self._ev(a, b, bn, v); self._ev(a, b, bn + 7, v - 6)
        elif pat == 'bell':
            self._ev(a, b, bn, v + 6)
            for m in vo[:2]: self._ev(a + .02, b, m, v - 12)

    def rest(self, beats): self.pos += beats


def write_midi(movements, path, gap=3.0):
    midi = pm.PrettyMIDI(); inst = pm.Instrument(0, name='Piano'); midi.instruments.append(inst)
    off, marks = 0.0, []
    for m in movements:
        marks.append((m.name, round(off, 1)))
        for b0, b1, pitch, vel, late in m.ev:
            s = off + m.sec(b0) + late; e = max(s + .03, off + m.sec(b1) + late)
            inst.notes.append(pm.Note(vel, pitch, s, e))
        for b, val in m.ped: inst.control_changes.append(pm.ControlChange(64, val, off + m.sec(b)))
        off += m.sec(m.pos) + gap
    midi.write(path)
    return marks
