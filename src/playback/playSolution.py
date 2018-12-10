"""
Functionality to playback a solution.
Uses mingus fluidsynth.
"""
import sys, pdb, time, os
sys.path.append("..")

from util.constants import *
from core.Note import numToPitch_absolute, pitchToNum_absolute
from core.solver import make_var

# Try to initialize playback
curfiledir = os.path.split(os.path.abspath(os.path.realpath(__file__)))[0]
PATH_SOUNDFONT = os.path.join(curfiledir, "./TimGM6mb.sf2")
try:
    from mingus.midi import fluidsynth
    import mingus.containers
    canPlayback = fluidsynth.init(PATH_SOUNDFONT, "pulseaudio")
except ImportError:
    print "Warning: Could not import mingus. Playback is not supported."
    canPlayback = False
if not canPlayback:
    print "Warning: Playback is not supported!"
else:
    print "Playback supported!"

def playSolution(solution):
    """ Plays back a given solution.
    INPUT:
      dict solution:
        NOTE: GUI passes in a list of the form:
          [["<singer><time>", int pitchnum], ...]
        Command-line interface uses a different representation than
        the GUI code. So, this function handles both cases until I 
        update the GUI code to follow the CLI style.
    OUTPUT:
      True if playback is successful, False otherwise.
    """
    # TODO(erickim)[2018-12-09] Not fond of using global canPlayback
    if not canPlayback:
        print "Warning: midi playback not supported. Did you install mingus?"
        return False
    if type(solution) is dict:
        track = sol2fluidsynth(solution)
    elif type(solution) is list:
        # Convert list-repr to dict repr
        soldict = {}
        for (key,pitchnum) in solution:
            dictkey = key[0]+"_"+key[1:]
            soldict[dictkey] = pitchnum
        track = sol2fluidsynth(soldict)
    else:
        raise ValueError("Unexpected type: {0}".format(type(solution)))
    try:
        fluidsynth.play_Track(track)
        fluidsynth.main_volume(1, 127)
    except Exception as e:
        print e
        return False
    return True

def sol2fluidsynth(solution, dur=2):
    """ Converts my note representation into mingus form.
    INPUT:
      dict solution:
      int dur: [2]
        Duration to play notes.
    OUTPUT:
      mingus.containers.Track
    """
    T = len(solution) / 4 # nb time steps
    track = mingus.containers.Track()
    for t in xrange(T):
        chord = []
        for v in VOICE_PREFIXES:
            key = make_var(v, t)
            pitchnum = solution[key]
            pitch = numToPitch_absolute(pitchnum, delim='-')
            chord.append(pitch)
        track.add_notes(chord, duration=dur)
    return track

def testit():
    p2n = pitchToNum_absolute
    solution = {'s_0': p2n("B4"), 'a_0': p2n("G3"), 't_0': p2n("D3"), 'b_0': p2n("G2"),
                's_1': p2n("C5"), 'a_1': p2n("G3"), 't_1': p2n("E3"), 'b_1': p2n("C2")}
    playSolution(solution)
    time.sleep(2)

def testit_lst():
    p2n = pitchToNum_absolute
    solution = [['s0', p2n("B4")], ['a0', p2n("G3")], ['t0', p2n("D3")], ['b0', p2n("G2")],
                ['s1', p2n("C5")], ['a1', p2n("G3")], ['t1', p2n("E3")], ['b1', p2n("C2")]]
    playSolution(solution)
    time.sleep(2)

if __name__ == '__main__':
    #testit()
    testit_lst()
