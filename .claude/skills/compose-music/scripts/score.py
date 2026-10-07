"""MIDI -> piano score PDF (via music21 + LilyPond).
usage: python score.py in.mid out.pdf "Title" [beats_per_bar=4] [grid_per_beat=4] [--lh-treble] [--key-flats N]
--key-flats N: key signature with N flats (2 = G minor) and flat spelling.
--lh-treble: left hand in treble clef with an 8 below (reads like treble, sounds an octave lower).
Notes are quantized to the grid, split between hands at middle C, and written legato
(each onset lasts until the next onset in the same hand)."""
import os, sys, subprocess, tempfile
import pretty_midi as pm
from music21 import stream, note, chord, meter, tempo, clef, metadata, key


def build(mid, title, bpb=4, grid=4, lh_treble=False, flats=0):
    m = pm.PrettyMIDI(mid)
    times, tempi = m.get_tempo_changes()
    bpm = tempi[0]
    q = lambda sec: m.time_to_tick(sec) / m.resolution     # position in quarter notes (follows tempo changes)
    hands = {'rh': {}, 'lh': {}}
    two = len(m.instruments) > 1   # instrument 0 = right hand, 1 = left hand; otherwise split at middle C
    for k, inst in enumerate(m.instruments[:2]):
        for n in inst.notes:
            pos = round(q(n.start) * grid) / grid
            h = ('rh' if k == 0 else 'lh') if two else ('rh' if n.pitch >= 60 else 'lh')
            hands[h].setdefault(pos, set()).add(n.pitch)
    end = max(max(h) for h in hands.values() if h) + 1
    sc = stream.Score(); sc.metadata = metadata.Metadata(title=title, composer='Claude')
    for name, cl in (('rh', clef.TrebleClef()), ('lh', clef.Treble8vbClef() if lh_treble else clef.BassClef())):
        part = stream.Part(); part.insert(0, cl)
        if flats: part.insert(0, key.KeySignature(-flats))
        part.insert(0, meter.TimeSignature('%d/4' % bpb))
        for ts, tp in zip(times, tempi):
            if name == 'rh': part.insert(round(q(ts) * grid) / grid, tempo.MetronomeMark(number=round(tp)))
        offs = sorted(hands[name]); 
        for i, o in enumerate(offs):
            nxt = offs[i + 1] if i + 1 < len(offs) else end
            ps = sorted(hands[name][o])
            el = note.Note(ps[0]) if len(ps) == 1 else chord.Chord(ps)
            if flats:     # G minor etc.: spell black keys as flats, except F# (leading tone)
                for pt in el.pitches:
                    if pt.accidental is not None and pt.accidental.name == 'sharp' and pt.name != 'F#': pt.getEnharmonic(inPlace=True)
            el.quarterLength = min(nxt - o, bpb * 2)
            part.insert(o, el)
        part.makeRests(fillGaps=True, inPlace=True)
        part = part.makeMeasures(); part.makeTies(inPlace=True)
        sc.insert(0, part)
    return sc


if __name__ == '__main__':
    lh_treble = '--lh-treble' in sys.argv
    flats = int(sys.argv[sys.argv.index('--key-flats') + 1]) if '--key-flats' in sys.argv else 0
    args = [a for i, a in enumerate(sys.argv) if a not in ('--lh-treble', '--key-flats') and not (i and sys.argv[i - 1] == '--key-flats')]
    mid, out, title = args[1:4]
    sc = build(mid, title, int(args[4]) if len(args) > 4 else 4, int(args[5]) if len(args) > 5 else 4, lh_treble, flats)
    d = tempfile.mkdtemp(); xml = os.path.join(d, 's.musicxml'); sc.write('musicxml', fp=xml)
    # musicxml2ly repeats the title as a subtitle
    subprocess.run(['musicxml2ly', '-o', os.path.join(d, 's.ly'), xml], check=True, capture_output=True)
    ly = open(os.path.join(d, 's.ly')).read()
    import re; open(os.path.join(d, 's.ly'), 'w').write(re.sub(r'\n\s*subtitle = [^\n]*', '', ly))
    subprocess.run(['lilypond', '-o', os.path.join(d, 's'), os.path.join(d, 's.ly')], check=True, capture_output=True)
    os.replace(os.path.join(d, 's.pdf'), out)
