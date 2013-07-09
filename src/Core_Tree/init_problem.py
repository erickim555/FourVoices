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

from Core_Tree.harmony_rules import *
import Core_Tree.config

mus_range = range(0, 87)
soprano_range = range(51, 66)     # C4 -> C5
alto_range = range(46, 68)        # G3 -> F5
tenor_range =  range(39, 51)      # C3 -> A4
bass_range = range(32, 55)        # F2 -> E4

"""
subproblems is a list of subproblems, where a subproblem is a list of the form:
subproblem := [ < variables/domains dict > , < variables/constraints dict > ] 
"""
subproblems = []

# In an attempt to prune the domain-space of each variable, I will do preprocessing to
# decrease the domain, rather than enforcing it with constraints.
def getSingerDomain(voice, chord):
  domain = []
  voice_range = {"s": soprano_range,
                 "a": alto_range,
                 "t": tenor_range,
                 "b": bass_range}[voice]
  chordTones__= chord.getChordTones_nums()
  for note in chordTones__:
    for note2 in voice_range:
      if (note2 % 12) == note:
        domain.append(note2)
  return domain

# Returns True if the harmony at the specified time-step is Dominant (i.e a "V") or not.
def isDominant(time):
  harmony = Core_Tree.config.harmonies[time][0]
  return (harmony == "V")


# This method, used by the user to initialize the CSP, will
# add variables to the CSP (4 variables for each voice: SATB) for the
# various time steps.
#  problem := CSP Problem
#  chord   := Chord object, created by user
#  time    := time step, i.e 0, 1, 2, 3, ...
def addChord(chord, time):
  Core_Tree.config.chords.insert(time, chord)  # Update our chord database

  singers = ("s"+str(time), "a"+str(time), "t"+str(time), "b"+str(time))
  var_value_dict = {}
  for singer in singers:
    var_value_dict[singer] = getSingerDomain(singer[0], chord)
  var_const_dict = {}
  var_const_dict[tuple(singers)] = [specifyChord(chord, Core_Tree.config.harmonies),]
  if chord.bassNote != None:
    var_const_dict[("b"+str(time)),] = [setBass(chord),]
  subproblems.append( [var_value_dict, var_const_dict ] )

def addHarmony(chord, harmony):
  addChord(chord, chord.time)
  Core_Tree.config.harmonies.insert(chord.time, harmony)

# If the user wishes to specify any voice, then he/she can do so here.
# problem := Problem() instance
# voice := Either "s", "a", "t", "b"
# notes := a list of numbers that represents the EXACT note that the singer sings
#          at each time step.
def specify_voice(voice, notes):
  for t in range(len(notes)):
    if notes[t] != None:
      var = voice+str(t)
      subproblem_vars = subproblems[t][0]
      subproblem_vars[var] = notes[t] 

def addConstraint(vars, constraint, t):
  dict = subproblems[t][1]
  if type(vars) != type(()):
    vars = tuple(vars)
  if dict.has_key(vars):
    constraints = dict[vars]
    constraints.append(constraint)
  else:
    dict[vars] = [constraint,]

def addHarmonyRules():  
  #numTimeSteps = len(subproblems[0][0].keys()) / 4
  numSubProblems = len(subproblems)
  for t in range(numSubProblems):
    # Make sure that voices are at most an octave away from each other
    addConstraint(["s"+str(t), "a"+str(t)], lambda a, b : handleSpacing(a, b) , t)
    addConstraint(["a"+str(t), "t"+str(t)], lambda a, b : handleSpacing(a, b) , t)
    addConstraint(["t"+str(t), "b"+str(t)], lambda a, b : handleSpacing(a, b) , t)
    
    # Make sure that voices don't cross each other
    addConstraint(["s"+str(t), "a"+str(t), "t"+str(t), "b"+str(t)], lambda s, a, t, b : checkCrossOver(s, a, t, b), t)