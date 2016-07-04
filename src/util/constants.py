'''
Created on May 25, 2010

@author: Sforzando
'''

mus_range = range(0, 87)
# ranges from:
#   https://en.wikipedia.org/wiki/Vocal_range
soprano_range = range(60, 84)     # C4 -> C6
alto_range = range(57, 81)        # A3 -> A5
tenor_range =  range(48, 72)      # C3 -> C5
bass_range = range(40, 64)        # E2 -> E4

TONIC = "tonic"
SUBDOMINANT = "subdominant"
PREDOMINANT = SUBDOMINANT
DOMINANT = "dominant"

MOD_MAJOR = ("major", "maj")
MOD_MINOR = ("minor", "min")
MOD_MAJOR_SEVENTH = ("major7", "maj7")
MOD_MINOR_SEVENTH = ("minor7", "min7", "m7")
MOD_DOMINANT_SEVENTH = ("7",)
MOD_DIM = ("dim",)
MOD_DIM_HALF = ("min7(b5)", "m7(b5)", "halfdim")
MOD_DIM_FULL = ("dim7",)

VOICE_PREFIXES = ("s", "a", "t", "b")

NOTES = ("a", "b", "c", "d", "e", "f", "g",
         "A", "B", "C", "D", "E", "F", "G")
