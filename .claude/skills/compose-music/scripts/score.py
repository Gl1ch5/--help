"""MIDI -> piano score PDF (via music21 + LilyPond).
usage: python score.py in.mid out.pdf "Title" [beats_per_bar=4] [grid_per_beat=4]
Notes are quantized to the grid, split between hands at middle C, and written legato
(each onset lasts until the next onset in the same hand)."""
import os, sys, subprocess, tempfile
import pretty_midi as pm
from music21 import stream, note, chord, meter, tempo, clef, metadata, key


def build(mid, title, bpb=4, grid=4):
    m = pm.PrettyMIDI(mid)
    bpm = m.get_tempo_changes()[1][0]
    beat = 60 / bpm
    hands = {'rh': {}, 'lh': {}}
    two = len(m.instruments) > 1   # instrument 0 = right hand, 1 = left hand; otherwise split at middle C
    for k, inst in enumerate(m.instruments[:2]):
        for n in inst.notes:
            pos = round(n.start / beat * grid) / grid
            h = ('rh' if k == 0 else 'lh') if two else ('rh' if n.pitch >= 60 else 'lh')
            hands[h].setdefault(pos, set()).add(n.pitch)
    end = max(max(h) for h in hands.values() if h) + 1
    sc = stream.Score(); sc.metadata = metadata.Metadata(title=title, composer='Claude')
    for name, cl in (('rh', clef.TrebleClef()), ('lh', clef.BassClef())):
        part = stream.Part(); part.insert(0, cl); part.insert(0, meter.TimeSignature('%d/4' % bpb))
        part.insert(0, tempo.MetronomeMark(number=round(bpm)))
        offs = sorted(hands[name]); 
        for i, o in enumerate(offs):
            nxt = offs[i + 1] if i + 1 < len(offs) else end
            ps = sorted(hands[name][o])
            el = note.Note(ps[0]) if len(ps) == 1 else chord.Chord(ps)
            el.quarterLength = min(nxt - o, bpb * 2)
            part.insert(o, el)
        part.makeRests(fillGaps=True, inPlace=True)
        part = part.makeMeasures(); part.makeTies(inPlace=True)
        sc.insert(0, part)
    return sc


if __name__ == '__main__':
    mid, out, title = sys.argv[1:4]
    sc = build(mid, title, int(sys.argv[4]) if len(sys.argv) > 4 else 4, int(sys.argv[5]) if len(sys.argv) > 5 else 4)
    d = tempfile.mkdtemp(); xml = os.path.join(d, 's.musicxml'); sc.write('musicxml', fp=xml)
    # musicxml2ly repeats the title as a subtitle
    subprocess.run(['musicxml2ly', '-o', os.path.join(d, 's.ly'), xml], check=True, capture_output=True)
    ly = open(os.path.join(d, 's.ly')).read()
    import re; open(os.path.join(d, 's.ly'), 'w').write(re.sub(r'\n\s*subtitle = [^\n]*', '', ly))
    subprocess.run(['lilypond', '-o', os.path.join(d, 's'), os.path.join(d, 's.ly')], check=True, capture_output=True)
    os.replace(os.path.join(d, 's.pdf'), out)
