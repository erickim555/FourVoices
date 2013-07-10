'''
Created on May 25, 2010

@author: Sforzando
'''

mus_range = range(0, 87)
soprano_range = range(51, 66)     # C4 -> C5
alto_range = range(46, 66)        # G3 -> F5
tenor_range =  range(39, 51)      # C3 -> A4
bass_range = range(32, 51)        # F2 -> E4

TONIC = "tonic"
SUBDOMINANT = "subdominant"
PREDOMINANT = SUBDOMINANT
DOMINANT = "dominant"

MOD_MAJOR = ("major", "maj")
MOD_MINOR = ("minor", "min")
MOD_MAJOR_SEVENTH = ("major7", "maj7")
MOD_MINOR_SEVENTH = ("minor7", "min7", "m7")
MOD_DOMINANT_SEVENTH = ("7",)
MOD_DIM_HALF = ("m7(b5)",)
MOD_DIM_FULL = ("dim",)
MOD_DIM_FULL_SEVENTH = ("dim7",)

VOICE_PREFIXES = ("s", "a", "t", "b")
