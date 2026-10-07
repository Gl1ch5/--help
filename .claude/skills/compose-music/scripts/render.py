"""Render a MIDI file to MP3 with FluidSynth + a piano SoundFont.

usage: python render.py in.mid out.mp3 [soundfont.sf2]
SoundFont lookup: argument, $PIANO_SF2, a cached Salamander Grand Piano
(downloaded once from freepats.zenvoid.org, CC-BY), then FluidR3_GM.
"""
import glob, os, subprocess, sys, tarfile, tempfile, urllib.request

SAL_URL = 'https://freepats.zenvoid.org/Piano/SalamanderGrandPiano/SalamanderGrandPiano-SF2-V3+20200602.tar.xz'
CACHE = os.path.expanduser('~/.cache/piano-sf2')


def find_sf2(arg=None):
    if arg: return arg
    if os.environ.get('PIANO_SF2'): return os.environ['PIANO_SF2']
    hit = glob.glob(CACHE + '/**/*.sf2', recursive=True)
    if hit: return hit[0]
    try:
        os.makedirs(CACHE, exist_ok=True)
        tmp = os.path.join(tempfile.mkdtemp(), 's.tar.xz')
        print('downloading Salamander Grand Piano (~300 MB)...')
        urllib.request.urlretrieve(SAL_URL, tmp)
        tarfile.open(tmp).extractall(CACHE)
        return glob.glob(CACHE + '/**/*.sf2', recursive=True)[0]
    except Exception as e:
        print('Salamander unavailable (%s), falling back to FluidR3_GM' % e)
        return '/usr/share/sounds/sf2/FluidR3_GM.sf2'  # apt install fluidsynth fluid-soundfont-gm


def render(mid, mp3, sf2=None):
    sf2 = find_sf2(sf2)
    wav = mp3.rsplit('.', 1)[0] + '.tmp.wav'
    subprocess.run(['fluidsynth', '-ni', '-g', '1.0', '-r', '44100', '-F', wav, sf2, mid], check=True)
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', wav, '-af', 'loudnorm=I=-16:TP=-1.5', '-b:a', '192k', mp3], check=True)
    os.remove(wav)


if __name__ == '__main__':
    render(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
