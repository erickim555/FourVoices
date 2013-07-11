"""
FourVoices -- A music generator. 
Copyright (C) 2012 Eric Kim <erickim555@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, string, pdb
sys.path.append('..')

from util.constants import *

# ============= Under the covers implementation of Pitch/Octave =============
# noteValue is a number from 0 to 87 (corresponding to the 88 keys in a piano)
# noteValue  = 0 :  A0
# noteValue  = 1 :  A#0
# ...  
# noteValue  = 86 :  B8
# noteValue  = 87 :  C8
# =========================================================================

# pitch := " < Letter > < Octave > "
# Example: pitchToNum("A5") = 60 
def pitchToNum_absolute(pitch):
  octave = int(pitch[-1])
  pitch = string.upper( pitch[0] )
  if pitch == "A":
    return 0 + (12 * octave)
  if (pitch == "A#") or (pitch == "Bb"):
    return 1 + (12 * octave)
  if (pitch == "B") or (pitch == "Cb"):
    return 2 + (12 * octave)
  if (pitch == "C"):
    return 3 + (12 * octave)
  if (pitch == "C#") or (pitch == "Db"):
    return 4 + (12 * octave)
  if (pitch == "D"):
    return 5 + (12 * octave)
  if (pitch == "D#") or (pitch == "Eb"):
    return 6 + (12 * octave)
  if (pitch == "E") or (pitch == "Fb"):
    return 7 + (12 * octave)
  if (pitch == "F"):
    return 8 + (12 * octave)
  if (pitch == "F#") or (pitch == "Gb"):
    return 9 + (12 * octave)
  if (pitch == "G"):
    return 10 + (12 * octave)
  if (pitch == "G#") or (pitch == "Ab"):
    return 11 + (12 * octave)
  else:
    print "Error - invalid pitch passed, returning 0"
    return 0

# pitch := <letter>
def pitchToNum(pitch):
  pitch = string.upper( pitch )
  if pitch == "A":
    return 0
  if (pitch == "A#") or (pitch == "Bb"):
    return 1
  if (pitch == "B") or (pitch == "Cb"):
    return 2
  if (pitch == "C"):
    return 3
  if (pitch == "C#") or (pitch == "Db"):
    return 4
  if (pitch == "D"):
    return 5
  if (pitch == "D#") or (pitch == "Eb"):
    return 6
  if (pitch == "E") or (pitch == "Fb"):
    return 7
  if (pitch == "F"):
    return 8
  if (pitch == "F#") or (pitch == "Gb"):
    return 9
  if (pitch == "G"):
    return 10
  if (pitch == "G#") or (pitch == "Ab"):
    return 11
  else:
    print "Error - invalid pitch passed, returning 0"
    return 0

# num := number representing ABSOLUTE pitch
# i.e  numToPitch(13) = A#1
def numToPitch_absolute(num):
  octave = num / 12
  num = num % 12
  
  if num == 0:
    return "A"+str(octave)
  if (num == 1):
    return "A#"+str(octave)
  if (num == 2):
    return "B"+str(octave)
  if (num == 3):
    return "C"+str(octave)
  if (num == 4):
    return "C#"+str(octave)
  if (num == 5):
    return "D"+str(octave)
  if (num == 6):
    return "D#"+str(octave)
  if (num == 7):
    return "E"+str(octave)
  if (num == 8):
    return "F"+str(octave)
  if (num == 9):
    return "F#"+str(octave)
  if (num == 10):
    return "G"+str(octave)
  if (num == 11):
    return "G#"+str(octave)
  else:
    print "Error - invalid num passed, returning A."
    return "A0"

# num := number representing pitch
# i.e  numToPitch(13) = A#
def numToPitch (num):
  num = num % 12
  if num == 0:
    return "A"
  if (num == 1):
    return "A#"
  if (num == 2):
    return "B"
  if (num == 3):
    return "C"
  if (num == 4):
    return "C#"
  if (num == 5):
    return "D"
  if (num == 6):
    return "D#"
  if (num == 7):
    return "E"
  if (num == 8):
    return "F"
  if (num == 9):
    return "F#"
  if (num == 10):
    return "G"
  if (num == 11):
    return "G#"
  else:
    print "Error - invalid num passed, returning A."
    return "A0"

#  Class Chord
#
#    root
#      The root of the chord (i.e for "C/E", "C" is the root).
#      Note that major/minor is implied here: "C" is C MAJOR, while "c" is C MINOR.
# ============= Correction: major/minor is NOT implied by C versus c.
# =============
#    bass_note
#      The actual bass note of the chord (i.e for "D/C", "C" is the bass note)
#    modifiers
#      A tuple of modifiers to the chord. Modifiers are defined as things like:
#      "dim", "7", "6", etc
#    time
#      A number representing at which time this chord is playing.

# ================== Implementation Details of Harmonies ====================
# ===========================================================================
# How do you quickly and efficiently extract numbers from a chord?
# If I am given an input, say, A7 (i.e A dominant 7th chord), I should be able to
# decompose this into several facts.
#
#    a.) The root is "A" - which has a noteValue of 0.
#    b.) Because "A" is uppercase, I know we want a Major chord. // NOPE
#    c.) Since no root-indicator was specified, I can assume that the bass_note is "A".
#    d.) There is a modifier of "7", which means "Dominant 7th".
#
# These preliminary facts aren't enough: I still don't have an explicit/implicit definition
# of WHAT a chord precisely is. I should be able to determine if, given a collection of
# notes, the notes represent a C Major chord or not. 
# Idea: Have everything relative to the noteValue of the ROOT.
# So, Major indicates that the domain of the Chord's notes MUST include the note that is
# a major-3rd away from the root (i.e 4 away from the the noteValue(root)).
#
# UPDATE:
# Actually, having uppercase roots encode Major/Minor is a BAD idea. Instead, the user needs
# to explicitly express whether or not the chord is major or minor in the MODIFIERS field.
# However, if the user does NOT specify Major/Minor, let us assume that the user wished
# to input a MAJOR chord (this way, less hard-crashes can happen! Happy code = Happy Eric)
# 
# UPDATE 2: A Chord() instance can either have a bass note specified, OR not. This effects 
# the solution-process, as a chord WITH a bass note will have that constraint created. A chord
# WITHOUT a bass note will NOT have a constraint created.

class Chord(object):
  # I.e Cmaj7/G = Chord("C", ["maj7"], 0, "G")
  # dmin = Chord("D", ["min"], 0)
  def __init__(self, root, modifiers, time, bassNote=None, role=None): 
    """
    Input:
        str ROOT:
        list MODIFIERS:
        int TIME:
        str BASSNOTE:
        str ROLE:
            Harmonic function. One of: TONIC, SUBDOMINANT, or DOMINANT
    """
    self.root = root
    self.bassNote = bassNote
    self.modifiers = []
    if modifiers != None:
      self.modifiers = modifiers
    self.time = time
    if bassNote != None:
      self.bassNum = pitchToNum(bassNote)
    else:
      self.bassNum = None
    self.rootNum = pitchToNum(root)
    self.role = role
    
    #self.chordTones = self.getChordTones()
    self.triad = getTriadTones(self.root)
  
  def getRoot(self):
    return self.root
  def getBassNote(self):
    return self.bassNote
  def getModifiers(self):
    return self.modifiers
  def getTime(self):
    return self.time
  
  def getThird__(self):
    return self.getChordTones_nums()[1]
  
  def getFifth__(self):
    return self.getChordTones_nums()[2]
  
  # Returns the NUMBER value of the seventh, or None if the chord
  # doesn't have a seventh
  def getSeventh__(self):
    seventh = None
    chordTones__ = self.getChordTones_nums()
    if len(chordTones__) > 3:
      seventh = chordTones__[3]
    return seventh

  # Return a tuple of noteValues that can possibly correspond to the given bass_note
  # i.e, if bass_note = "A", then the tuple [0, 12, 24, 36, 48, 60, 72, 84] should be returned.
  def getBassRange(self):
    return [x for x in range(0, 87) if ((x % 12) == self.bassNum)]
  def getRootRange(self):
    return [x for x in range(0, 87) if ((x % 12) == self.rootNum)]
  
  # Return a tuple of notes that correspond to the notes that must be present for the given
  # chord. So, A7 should be: ("A", "C#", "E", "G")
  def getChordTones(self):
    chordTones = list()
    chordTones.extend(self.triad)
    if ("dim" in self.modifiers) and ("7" in self.modifiers):
      self.modifiers.remove("dim")
      self.modifiers.remove("7")
      self.modifiers.append("dim7")
    if self.modifiers != None:
      for modifier in self.modifiers:
        chordTones = self.applyModifier(modifier, chordTones)
    return tuple(chordTones)
  
  def is_dominant(self):
    """ Return True if this chord's role is a Dominant role. """
    if self.role:
        return self.role[0] == "V" or self.role == DOMINANT
    return False

  def is_dim(self):
    """ Is this chord diminished (all variants)? """
    return (len(set(self.modifiers).intersection(MOD_DIM)) >= 1 or
            self.is_dim_full() or self.is_dim_half())

  def is_dim_full(self):
    """ Return True if this chord is FULLY diminished. """
    return len(set(self.modifiers).intersection(MOD_DIM_FULL)) >= 1
  def is_dim_half(self):
    """ Return True if this chord is HALF diminished. """
    return len(set(self.modifiers).intersection(MOD_DIM_HALF)) >= 1
  
  # Return a tuple of a list of numbers that correspond to the noteNums that need to be
  # present in the chord, as specified by the modifiers. 
  # So, for a C Major chord, if the specifier is "7" [dominant seventh], then this method
  # should return:
  # ( [<note ranges for "C">], [<note ranges for "E">], [<note ranges for "G">], [<note ranges for "Bb"])     
  def getChordTones_nums(self):
    chordTone_nums = list()
    for chordTone in self.getChordTones():
      chordTone_nums.append(pitchToNum(chordTone))
    return chordTone_nums
    
    
    #for chordTone in self.getChordTones():
    #  toneRange = [x for x in range(0, 87) if (x % 12) == pitchToNum(chordTone)]
    #  chordTone_nums.append(toneRange)
    #return tuple(chordTone_nums)
    
  def applyModifier(self, modifier, chordTones):
    modifier = modifier.lower()
    newChordTones = list(chordTones)
    if modifier in MOD_MAJOR:
      return newChordTones
    if modifier in MOD_MINOR:
      newChordTones[1] = numToPitch(pitchToNum(newChordTones[1]) - 1)
      return newChordTones
    if modifier in MOD_MAJOR_SEVENTH:
      newChordTones.append(numToPitch(self.rootNum - 1))
      return newChordTones
    if modifier in MOD_MINOR_SEVENTH:
      newChordTones[1] = numToPitch(pitchToNum(newChordTones[1]) - 1)
      newChordTones.append(numToPitch(self.rootNum - 2))
      return newChordTones
    if modifier in MOD_DOMINANT_SEVENTH:
      newChordTones.append(numToPitch(self.rootNum - 2))
      return newChordTones
    if modifier in MOD_DIM_HALF:  # i.e half-diminished
      newChordTones[1] = numToPitch(pitchToNum(newChordTones[1]) - 1)
      newChordTones[2] = numToPitch(pitchToNum(newChordTones[2]) - 1)
      newChordTones.append(numToPitch(self.rootNum - 2))
      return newChordTones
    if modifier in MOD_DIM:     # i.e diminished
      newChordTones[1] = numToPitch(pitchToNum(newChordTones[1]) - 1)
      newChordTones[2] = numToPitch(pitchToNum(newChordTones[2]) - 1)
      return newChordTones
    if modifier in MOD_DIM_FULL: # fully diminished
      newChordTones[1] = numToPitch(pitchToNum(newChordTones[1]) - 1)
      newChordTones[2] = numToPitch(pitchToNum(newChordTones[2]) - 1)
      #newChordTones.append(numToPitch(pitchToNum(newChordTones[2]) + 3))
      newChordTones.append(numToPitch(self.rootNum - 3))
      return newChordTones
      
  def __str__(self):
    return "Chord({0},{1},{2},bassNote={3},role={4})".format(self.root, self.modifiers, self.time, self.bassNum, self.role)
  def __repr__(self):
    return "Chord({0},{1},{2},bassNote={3},role={4})".format(self.root, self.modifiers, self.time, self.bassNum, self.role)
    
# Return the triad (Root, Third, and Fifth).
# Note that we initially assume that all chord start off as Major Triads - the modifiers
# will make appropriate changes to the chordTones to make the chord minor/diminished/etc.     
def getTriadTones(root):
  triad = []
  rootNum = pitchToNum(root)
  triad.append(root)
  triad.append(numToPitch(rootNum + 4))   # The Third
  triad.append(numToPitch(rootNum + 7))         # The Fifth
  return triad
