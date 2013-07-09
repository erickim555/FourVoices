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

### A set of modified harmony rules that is designed to use mega-variables

# We assume that the first argument is one time-step ahead from the second argument
# addConstraint(noParallelFifth(), ["s0", "s1", "a0", "a1"]
# A Parallel Fifth is when two voices start as perfect fifths and END as perfect fifths.
# Note: A perfect fifth distance is 7.
# var1 := a dict mapping variables to its assigned value
# var2 := a dict mapping variables to its assigned value
# Note: This constraint only goes one way (i.e time(var1) < time(var2))
def noParallelFifth_mega(var1, var2):
  # Add parallel fifth
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  singer_array = []
  history = []
  for singer in ("s", "a", "t", "b"):
    for singer2 in ("s", "a", "t", "b"):
      if (singer != singer2) and ((singer, singer2) not in history):
        singer_array.append((singer+str(t), singer+str(t+1), singer2+str(t), singer2+str(t+1)))
        history.append((singer2, singer))
  for i in range(len(singer_array)):
    a, b, c, d = singer_array[i]
    x0 = var1[a]
    x1 = var2[b]
    y0 = var1[c]
    y1 = var2[d]
    if ((x0 - y0) % 12 == 7) and (((x1 - y1) % 12) == 7):
      return False
  return True
def noParallelOctave_mega(var1, var2):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  singer_array = []
  history = []
  for singer in ("s", "a", "t", "b"):
    for singer2 in ("s", "a", "t", "b"):
      if (singer != singer2) and ((singer, singer2) not in history):
        singer_array.append((singer+str(t), singer+str(t+1), singer2+str(t), singer2+str(t+1)))
        history.append((singer2, singer))
  for i in range(len(singer_array)):
    a, b, c, d = singer_array[i]
    x0 = var1[a]
    x1 = var2[b]
    y0 = var1[c]
    y1 = var2[d]
    if ((x0 - y0) % 12 == 0) and ((x1 - y1) % 12 == 0):
      return False
  return True

# A singer should never have to leap more than a major seventh (distance of 11)
# x0 = note that singer 'x' is singing at time t
# x1 = note that singer 'x' is singing at time (t + 1)
def biggestLeap_mega(var1, var2):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  for singer in ("s", "a", "t", "b"):
    singer2 = singer+str(t+1)
    x0 = var1[singer+str(t)]
    x1 = var2[singer2]
    if abs(x0 - x1) > 11:
      return False
  return True

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
def handleSevenths_mega(chord):
  seventh = chord.getSeventh__()
  return lambda x, y : __seventh__(x, y, seventh)

def __seventh__(var1, var2, seventh):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  for singer in ("s", "a", "t", "b"):
    x = var1[singer+str(t)]
    y = var2[singer+str(t+1)]
    if (x%12) == seventh and not(((x - y) == 1) or ((x - y) == 2) or ((x - y) == 0)):
      return False
  return True

# Makes sure that the leading tone of a Dominant (V) chord resolves correctly
# (i.e leading tones need to resolve up a half step, or stay constant)
def handleLeadingTone_mega(chord):
  leadingTone = chord.getThird__()
  return lambda x, y : __leadingTone__(x, y, leadingTone)

def __leadingTone__(var1, var2, leadingTone):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  for singer in ("s", "a", "t", "b"):
    x = var1[singer+str(t)]
    y = var2[singer+str(t+1)]
    if ((x%12) == leadingTone) and (not(((y - x) == 1) or ((y - x) == 0))):
      return False
  return True

# Make sure that the soprano/bass don't have hidden 5ths/octaves
#####  Pseudocode
###  if <similar motion between soprano and bass> :
###    return not( dist(soprano, bass) == <fifth> OR dist(soprano, bass) == <octave> )
def handleHidden_outer_mega(var1, var2):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  s0 = var1["s"+str(t)]
  s1 = var2["s"+str(t+1)]
  b0 = var1["b"+str(t)]
  b1 = var2["b"+str(t+1)] 
  if isSimilarMotion(s0, s1, b0, b1):
    dist = (s1 - b1) % 12
    if not((dist != 7) and (dist != 0)):
      return False
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
def handle_temporal_overlap_mega(var1, var2):
  t = int(var1.keys()[0][1:])
  t2 = int(var2.keys()[0][1:])
  if not(t < t2):
    return True
  tuple1 = ( var1["s"+str(t)], var2["s"+str(t+1)], var1["a"+str(t)], var2["a"+str(t+1)] )
  tuple2 = ( var1["a"+str(t)], var2["a"+str(t+1)], var1["t"+str(t)], var2["t"+str(t+1)] )
  tuple3 = ( var1["t"+str(t)], var2["t"+str(t+1)], var1["b"+str(t)], var2["b"+str(t+1)] )
  for tuple in (tuple1, tuple2, tuple3):
    x0, x1, y0, y1 = tuple
    if not((x0 > y1) and (x1 > y0)):
      return False
  return True
