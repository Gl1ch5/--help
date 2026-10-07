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
- **Vivaldi / Baroque**: see `scripts/vivaldi_concerto_allegro.py` (ritornello + episodes, terraced dynamics, driving 8th bass, 16th arpeggio and scale-run sequences, no pedal). Keep it playable: single-line right hand, single-note bass, no hand span over an octave. For readers who dislike bass clef, score with `--lh-treble`.
- **Hip-hop / Eminem-style piano**: see `scripts/eminem_style_piano.py` (G minor, 88 bpm, 16th ostinato in the right hand, left hand only single bass notes or fifths, octave hook). Default score is bass clef; prefer it unless the user asks for `--lh-treble`.
- **Rachmaninoff-style in G minor**: see `scripts/rachmaninoff_g_minor.py` (i-iv-V7-i, VI, III; left hand bass octaves + chords, right hand chords and octaves, lyrical middle section). Use it when the user wants chord-based left hand in a key they improvise in.
- **Mixed Mozart + Chopin + Rachmaninoff**: see `scripts/fantasy_g_minor.py` (Mozart period with runs, Chopin ornamented nocturne with turns and rubato, Rachmaninoff climax; left hand only bass + chords).
- **Tango (Piazzolla spirit)**: see `scripts/tango_g_minor.py` built on `scripts/engine.py` (shared two-hand helpers: left hand bass + chords, right hand melody/chords/octaves/runs; 3+3+2 accents, chromatic fire section).
- **Two-part nocturne (slow + fast)**: see `scripts/nocturne_two_parts.py` (two Engines at different tempi merged into one MIDI with a tempo change via `mido`; `score.py` follows tempo changes). Unusual-melody devices: Dorian raised sixth, 7th leap, Neapolitan Ab chord, chromatic sighs.
- **Improvisation material** (lead sheet + development ladder + backing track): see `scripts/improvisation_ladder.py` (melody and chord symbols are the single source for both the LilyPond lead sheet and the audio; `embellish()` ornaments the melody; `--key-flats 2` in score.py for G minor).
- **Programmatic concert / story piece** (tempo curves, any key, several movements): see `scripts/dsl_piano.py` (text DSL: chords, melody tokens, runs, trills, left-hand patterns, accelerando/ritardando) and `scripts/nocturne_concerto.py` ("Fragile Day", one theme transformed across four movements). Check per-movement loudness: sampled pianos are very quiet at low velocity, so soft movements need higher velocities.
- **Shostakovich**/: minor keys with ironic major-key shifts (A minor -> F major -> E7), waltz oom-pah-pah (`accomp='oompah'`, 3 beats per bar), tritone jumps, clipped dry accompaniment, accents on beat 1, tempo ~150.

## Sheet music

`python scripts/score.py piece.mid score.pdf "Title" [beats_per_bar]` makes a piano score PDF (needs `apt-get install -y lilypond` and `pip install music21`). With two MIDI instruments (right hand first, left hand second) the staves split by hand; otherwise at middle C. The score is auto-quantized, so treat it as a readable draft.

## Honesty notes

Output is an original piece "in the style of", not a copy, and quality depends on the SoundFont. Tell the user how to play MIDI on Android (Piano MIDI Player, Midi Voyager) and that the MP3 plays everywhere.
