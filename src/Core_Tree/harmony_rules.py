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

'''
Created on Nov 22, 2009

@author: Sforzando
'''
from Core_Tree.Note import *

# Need to make sure that the correct notes of the chord are hit.
# This just makes sure that every note of the chord is present, it doesn't check for
# doubled-thirds/fifths/etc.
# Note that, for a tonic chord, the fifth may be omitted
def specifyChord(chord, harmonies):
  return (lambda a, b, c, d: __allNotes__(a, b, c, d, chord, harmonies))
  
def __allNotes__(a, b, c, d, chord, harmonies):
  history = []
  chordTones = chord.getChordTones_nums()
  for x in (a, b, c, d):
    if (x % 12) not in chordTones:
      return False
    else:
      if ((x % 12) in chordTones) and ((x % 12) not in history):
        history.append(x % 12)
  # For tonic chord, fifth is optional
  if (harmonies[chord.getTime()] == "I") or (harmonies[chord.getTime()] == "i"):
    fifth = chord.getFifth__()
    if fifth not in history: 
      return (len(history) + 1) == len(chordTones)
    else:
      return len(history) == len(chordTones)
  else:    
    return len(history) == len(chordTones)

def setBass(chord):
  bassNum = pitchToNum(chord.getBassNote())
  return lambda x : (x % 12) == bassNum

# We assume that the first argument is one time-step ahead from the second argument
# addConstraint(noParallelFifth(), ["s0", "s1", "a0", "a1"]
# A Parallel Fifth is when two voices start as perfect fifths and END as perfect fifths.
# Note: A perfect fifth distance is 7.
def noParallelFifth(x0, x1, y0, y1):  
  if ((x0 - y0) % 12 == 7):
    return ((x1 - y1) % 12) != 7
  else:
    return True
def noParallelOctave(x0, x1, y0, y1):
  if ((x0 - y0) % 12 == 0):
    return ((x1 - y1) % 12) != 0
  else:
    return True  

# A singer should never have to leap more than a major seventh (distance of 11)
# x0 = note that singer 'x' is singing at time t
# x1 = note that singer 'x' is singing at time (t + 1)
def biggestLeap(x0, x1):
  return abs(x0 - x1) <= 11

# Singers should not cross over, i.e the tenor should never go below the bass
# However, voices may be in unison
# s, a, t, b := pitch that singer s is singing at a particular time
def checkCrossOver(s, a, t, b):
  return (s >= a) and (s >= t) and (s >= b) and \
         (a >= t) and (a >= b) and \
         (t >= b)



# Makes sure that the seventh (if present within a chord) resolves correctly
# All sevenths must either resolve downward, or stay as a suspension
# note1: the seventh, at time interval "t"
# note2: the next note following note1, at time interval "t + 1"
# NOTE: This is slightly tricky, because the definition of "resolving down a step'
# changes depending on what chords are at "t0" and "t1," in addition to the current
# key.
# For instance, in C Major, a the seventh of a dmin7 chord will resolve down a half-step
# to a B (or remain on C). But, in c minor, the seventh of a G7 chord will resolve a
# whole-step from F->Eb (or remain on F).
# So, I feel like we need to analyze: chords, current key, notes.
## Maybe I'll just say that a "step" is EITHER a half-step or a whole-step 
def handleSevenths(chord):
  seventh = chord.getSeventh__()
  return lambda x, y : __seventh__(x, y, seventh)

def __seventh__(x, y, seventh):
  if (x%12) == seventh:
    return ((x - y) == 1) or ((x - y) == 2) or ((x - y) == 0)
  else:
    return True     # Voice x doesn't have the seventh 

# Makes sure that the leading tone of a Dominant (V) chord resolves correctly
# (i.e leading tones need to resolve up a half step, or stay constant)
def handleLeadingTone(chord):
  leadingTone = chord.getThird__()
  return lambda x, y : __leadingTone__(x, y, leadingTone)

def __leadingTone__(x, y, leadingTone):
  if ((x%12) == leadingTone):
    return ((y - x) == 1) or ((y - x) == 0)
  else:
    return True

def handleSpacing(a, b):
  return abs(a - b) <= 12

# Make sure that the soprano/bass don't have hidden 5ths/octaves
#####  Pseudocode
###  if <similar motion between soprano and bass> :
###    return not( dist(soprano, bass) == <fifth> OR dist(soprano, bass) == <octave> )
def handleHidden_outer(s0, s1, b0, b1):
  if isSimilarMotion(s0, s1, b0, b1):
    dist = (s1 - b1) % 12
    return (dist != 7) and (dist != 0)
  else:
    return True

def isSimilarMotion(s0, s1, b0, b1):
  dist_s = s0 - s1
  dist_b = b0 - b1
  if dist_s != 0 and dist_b != 0:
    return ( (dist_s < 0) and (dist_b < 0) ) or ( (dist_s > 0) and (dist_b > 0) )
  else:
    return False

# Constraint that disallows the possibility of voice overlap. An example:
# Say the Bass is singing a G, and the Tenor is singing a B above the G.
# The bass is NOT allowed to go up to the C, because then the Bass would
# be singing a note that is higher than what the Tenor was singing previously.
# x0, x1: Upper voice
# y0, y1: Lower voice
def handle_temporal_overlap(x0, x1, y0, y1):
  return (x0 > y1) and (x1 > y0)
