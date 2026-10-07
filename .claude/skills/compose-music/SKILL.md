---
name: compose-music
description: Compose original piano music in the style of a classical composer (Mozart, Chopin, Shostakovich, ...) and deliver it as MIDI plus a realistic MP3 rendered with a sampled grand piano. Use when the user asks to write, compose or generate music, a waltz, nocturne, sonata, etc.
---

# Compose piano music

Claude cannot emit audio directly. The workflow is: write the notes as code -> save MIDI -> render MIDI with a sampled piano SoundFont -> send MP3 + MIDI to the user.

## Steps

1. **Pick form and style.** Ask only if missing (composer, form, mood). Default: short piece, 1-2 minutes.
2. **Write the piece** in a Python file using `scripts/music.py` (`Piece.bar(chord, melody, accomp=...)`). See `scripts/mozart_sonata_allegro.py` for a full example. Add new chords to `CHORDS` as needed.
3. **Save MIDI**, then render: `python scripts/render.py piece.mid piece.mp3`.
   - Needs `fluidsynth` and `ffmpeg` (`apt-get update && apt-get install -y fluidsynth fluid-soundfont-gm`) and `pip install pretty_midi`.
   - It downloads Salamander Grand Piano (~300 MB, CC-BY) once and caches it; falls back to FluidR3_GM.
4. **Check** the MP3 is not silent (`ffmpeg -i x.mp3 -af volumedetect -f null -`). Say honestly that the result was not listened to.
5. **Deliver** MP3 and MID with SendUserFile, commit them to the working branch. Do not commit the SoundFont.

## Style recipes

- **Mozart / Classical**: major keys, 4/4 or 2/4, 4+4 bar phrases (question/answer), Alberti bass (`accomp='alberti'`), scale runs in 16ths, tonic -> dominant -> tonic; B theme in the dominant (G major for C). No pedal, light touch, tempo 120-132.
- **Chopin / Romantic**: 3/4 or 4/4 (nocturne 12/8), singing right hand over arpeggiated left hand (broken chords spanning 2 octaves), chromatic passing tones, ornaments, rubato (vary note timing by a few ms to tens of ms), sustain pedal each bar (`pedal=True`), tempo 60-90.
- **Chopin Revolutionary-style etude**: see `scripts/revolutionary_etude.py` (non-stop 16th arpeggio LH, octave+chord RH, fff); render loud with `render.py in.mid out.mp3 "" -11`.
- **Shostakovich**: minor keys with ironic major-key shifts (A minor -> F major -> E7), waltz oom-pah-pah (`accomp='oompah'`, 3 beats per bar), tritone jumps, clipped dry accompaniment, accents on beat 1, tempo ~150.

## Sheet music

`python scripts/score.py piece.mid score.pdf "Title" [beats_per_bar]` makes a piano score PDF (needs `apt-get install -y lilypond` and `pip install music21`). With two MIDI instruments (right hand first, left hand second) the staves split by hand; otherwise at middle C. The score is auto-quantized, so treat it as a readable draft.

## Honesty notes

Output is an original piece "in the style of", not a copy, and quality depends on the SoundFont. Tell the user how to play MIDI on Android (Piano MIDI Player, Midi Voyager) and that the MP3 plays everywhere.
