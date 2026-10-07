"""Tiny helper for writing piano pieces bar by bar and saving them as MIDI."""
import random
import pretty_midi as pm

N = pm.note_name_to_number
R = None  # rest

# chord name -> (bass note, triad/7th tones for the accompaniment, low to high)
CHORDS = {
    'C': ('C2', ['C3', 'E3', 'G3']), 'G': ('G1', ['G2', 'B2', 'D3']),
    'G7': ('G1', ['G2', 'B2', 'F3']), 'F': ('F1', ['F2', 'A2', 'C3']),
    'D7': ('D2', ['D3', 'F#3', 'C4']), 'D': ('D2', ['D3', 'F#3', 'A3']),
    'Dm': ('D2', ['D3', 'F3', 'A3']), 'Am': ('A1', ['A2', 'C3', 'E3']),
    'Em': ('E2', ['E3', 'G3', 'B3']), 'E7': ('E2', ['E3', 'G#3', 'D4']),
    'Bb': ('A#1', ['A#2', 'D3', 'F3']),
}


class Piece:
    def __init__(self, bpm=120, beats_per_bar=4, seed=1):
        self.bpm, self.bpb = bpm, beats_per_bar
        self.beat = 60 / bpm
        self.t = 0.0
        self.rng = random.Random(seed)
        self.midi = pm.PrettyMIDI(initial_tempo=bpm)
        self.inst = pm.Instrument(0, name='Piano')
        self.midi.instruments.append(self.inst)

    def _add(self, pitch, start, end, vel):
        vel = max(1, min(120, vel + self.rng.randint(-4, 4)))
        self.inst.notes.append(pm.Note(vel, N(pitch) if isinstance(pitch, str) else pitch,
                                       start + self.rng.uniform(0, .008), end))

    def bar(self, chord, melody, accomp='alberti', accent=84, soft=52, pedal=False):
        """melody: list of (note|None, beats). accomp: 'alberti' | 'oompah' | 'block' | None."""
        bass, tri = CHORDS[chord]
        b, t0 = self.beat, self.t
        if accomp == 'alberti':      # low-high-mid-high eighths, played lightly and short
            lo, mid, hi = tri
            for i in range(self.bpb * 2):
                self._add([lo, hi, mid, hi][i % 4], t0 + i * b / 2, t0 + i * b / 2 + b * .45, soft + (6 if i % 4 == 0 else 0))
        elif accomp == 'oompah':     # bass on 1, chord on the other beats (waltz)
            self._add(bass, t0, t0 + b * .95, soft + 30)
            for k in range(1, self.bpb):
                for n in tri:
                    self._add(n, t0 + k * b, t0 + (k + .75) * b, soft - 6)
        elif accomp == 'block':
            for n in [bass] + tri:
                self._add(n, t0, t0 + self.bpb * b * .95, soft + 10)
        x = t0
        for note, d in melody:
            if note:
                self._add(note, x, x + d * b * (.97 if d < 2 else 1.0), accent if x == t0 else accent - 10)
            x += d * b
        if pedal:
            cc = pm.ControlChange
            self.inst.control_changes += [cc(64, 127, t0 + .02), cc(64, 0, t0 + self.bpb * b - .05)]
        self.t += self.bpb * b

    def save(self, path):
        self.midi.write(path)
