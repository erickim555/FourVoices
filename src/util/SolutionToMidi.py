'''
Created on May 22, 2010

@author: Sforzando
'''
import core.Note

try:
    import pygame
except ImportError:
    print "Unable to import pygame. MIDI playback will not be supported."
try:
    from mxm_Python_MIDI import MidiWrapper
except ImportError:
    print "Unable to import mxm_Python_MIDI. MIDI playback will not be supported."

def normalizeSolutionOutput(solution):
    solution.sort(cmp=lambda x,y : int.__cmp__( int(x[0][1]) , int(y[0][1])))
    pitches = [core.Note.numToPitch_absolute(x[1]) for x in solution]
    return pitches

# Solution := [ [<voice>_0, x] , [<voice>_1, y}, ... ]
def playSolution(solution):
    try:
        pitches = normalizeSolutionOutput(solution)
        m = MidiWrapper.MidiWrapper()
        m.createFile("tempfile.mid")
        time = 0
        i = 0
        for pitch in pitches:
            octave = int(pitch[-1])
            time = 300 * (i / 4)
            m.addNote(pitch[0:-1], octave, time, 300)
            i += 1
        m.finalize()

        pygame.init()
        pygame.mixer.init()
        pygame.mixer.music.load("tempfile.mid")
        pygame.mixer.music.play()
    except:
        print "SolutionToMidi.playSolution(1) failed. Aborting playback."
