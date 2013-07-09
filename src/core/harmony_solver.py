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

# Note: This is sort of deprecated - sort of meant for a command-line-based interface?
# I feel like I don't need this anymore however. 

'''
Created on Nov 22, 2009

@author: Sforzando
'''
import os
import copy
import cProfile
import sys
import time
import constraint
import constraint_unmodified
from Note import *
from harmony_rules import *
import examples.harmonytests
from Grader.grader import grade, grade_debug
import core.config

###
# First Parallel Fifth caught! 2:39 AM, 11-23-09 :)

mus_range = range(0, 87)
soprano_range = range(51, 66)     # C4 -> C5
alto_range = range(46, 66)        # G3 -> F5
tenor_range =  range(39, 51)      # C3 -> A4
bass_range = range(32, 51)        # F2 -> E4

chords = []		## A data structure to keep track of what chords
              ## are at what time steps.
              ## i.e chords[3] is the chord at time step 3
harmonies = []  ## A data structure to keep track of the harmony at
      ## Different time steps.
      ## i.e harmony[3] is the harmony at time step 3, like "ii6" or "V42"

# x = "S, A, T, B"
# y = "S, A, T, B"
# Order by "s3, s2, s1, a3, ..., t3, ..., b3, ..."
def myComparator(x, y):
  x1 = __voiceToNum__(x)
  y1= __voiceToNum__(y)
  if x1 > y1: return 1
  if x1 == y1:
    x_num = int(x[1:])
    y_num = int(y[1:])
    return x_num.__cmp__(y_num)
  # x1 < y1
  return -1

# translates "S, A, T, B" to "0, 1, 2, 3"
def __voiceToNum__(voice):
  lowerCase = voice.lower() # Just in case we get something like "S3" versus "s3"
  return {"s": 0,
          "a": 1,
          "t": 2,
          "b": 3}[lowerCase[0]] # Grab first letter


# Returns True if the harmony at the specified time-step is Dominant (i.e a "V") or not.
def isDominant(time):
  harmony = harmonies[time][0]
  return (harmony == "V")

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

# This method, used by the user to initialize the CSP, will
# add variables to the CSP (4 variables for each voice: SATB) for the
# various time steps.
#  problem := CSP Problem
#  chord   := Chord object, created by user
#  time    := time step, i.e 0, 1, 2, 3, ...
def addChord(problem, chord, time):
  chords.insert(time, chord)	# Update our chord database

  singers = ("s"+str(time), "a"+str(time), "t"+str(time), "b"+str(time))
  problem.addVariable(singers[0], getSingerDomain("s", chord))
  problem.addVariable(singers[1], getSingerDomain("a", chord))
  problem.addVariable(singers[2], getSingerDomain("t", chord))
  problem.addVariable(singers[3], getSingerDomain("b", chord))
  
  problem.addConstraint(specifyChord(chord, harmonies), tuple(singers))
  if chord.bassNote != None:
    problem.addConstraint(setBass(chord), ["b"+str(time)])
  ### BIG QUESTION: Why can't I say:
  #problem.addConstraint(setBass(chord), list(singers[3]))
  # ??????????????????????? :/

def addHarmony(problem, chord, harmony):
  addChord(problem, chord, chord.time)
  harmonies.insert(chord.time, harmony)

# If the user wishes to specify any voice, then he/she can do so here.
# problem := Problem() instance
# voice := Either "s", "a", "t", "b"
# notes := a list of numbers that represents the EXACT note that the singer sings
#          at each time step.
def specify_voice(problem, voice, notes):
  for t in range(len(notes)):
    if notes[t] != None:
      var = voice+str(t)
      problem.replaceVariable(var, (notes[t],))

def addHarmonyRules(harm):  
  numTimeSteps = len(harm._variables) / 4
  for t in range(numTimeSteps):
    # Make sure that voices are at most an octave away from each other
    harm.addConstraint(lambda a, b : handleSpacing(a, b), ["s"+str(t), "a"+str(t)])
    harm.addConstraint(lambda a, b : handleSpacing(a, b), ["a"+str(t), "t"+str(t)])
    harm.addConstraint(lambda a, b : handleSpacing(a, b), ["t"+str(t), "b"+str(t)])
    
    # Make sure that voices don't cross each other
    harm.addConstraint(lambda s, a, t, b : checkCrossOver(s, a, t, b), ["s"+str(t), "a"+str(t), "t"+str(t), "b"+str(t)])
    
    if t < (numTimeSteps - 1):    # Mainly, if t != numTimeSteps    
      # Check Leaps
      for singer in ("s", "a", "t", "b"):
        singer2 = singer+str(t+1)
        harm.addConstraint(lambda a, b : biggestLeap(a, b), [singer+str(t), singer2])
    
      # Make sure that there are no temporal overlaps
      harm.addConstraint(lambda x0, x1, y0, y1 : handle_temporal_overlap(x0,x1,y0,y1), \
                         ["s"+str(t), "s"+str(t+1), "a"+str(t), "a"+str(t+1)])
      harm.addConstraint(lambda x0, x1, y0, y1 : handle_temporal_overlap(x0,x1,y0,y1), \
                         ["a"+str(t), "a"+str(t+1), "t"+str(t), "t"+str(t+1)])
      harm.addConstraint(lambda x0, x1, y0, y1 : handle_temporal_overlap(x0,x1,y0,y1), \
                         ["t"+str(t), "t"+str(t+1), "b"+str(t), "b"+str(t+1)])
      
      chord = chords[t]
      
      # Add parallel fifth/octave handling
      singer_array = []
      history = []
      for singer in ("s", "a", "t", "b"):
        for singer2 in ("s", "a", "t", "b"):
          if (singer != singer2) and ((singer, singer2) not in history):
            singer_array.append((singer+str(t), singer+str(t+1), singer2+str(t), singer2+str(t+1)))
            history.append((singer2, singer))
      for i in range(len(singer_array)):
        harm.addConstraint(lambda a, b, c, d : noParallelFifth(a, b, c, d), singer_array[i])
        harm.addConstraint(lambda a, b, c, d : noParallelOctave(a, b, c, d), singer_array[i])
      # Add behavior for soprano/bass relationship (i.e no hidden 5th, hidden octave)
      ### Note: singer_array[2] contains the tuple ( <s0>, <s1>, <b0>, <b1> ), which is what we want
      harm.addConstraint(lambda a, b, c, d : handleHidden_outer(a, b, c, d), singer_array[2])
      
      # Add behavior for sevenths
      if chord.getSeventh__() != None:
        for singer in ("s", "a", "t", "b"):
          harm.addConstraint(handleSevenths(chord), [singer+str(t), singer+str(t+1)])
      # Add behavior for leading tones of dominant chords)
      if isDominant(t):
        for singer in ("s", "a", "t", "b"):
          harm.addConstraint(handleLeadingTone(chord), [singer+str(t), singer+str(t+1)])
  
def solveProblem(harm):
  # numTimeSteps = len(harm._variables) / 4
  
  core.config.chords = chords
  core.config.harmonies = harmonies
  
  solutionIter = harm.getSolutionIter()
  #f = open('C:\Users\Sforzando\Desktop\cspOutput.txt', 'w')
  #f_p = open('C:\Users\Sforzando\Desktop\cspOutput_pickled.txt', 'w')
  numberSolutions = 0
  solutions_graded = []
  
  bestGradeSoFar = -1000000000
  
  for solution in solutionIter:
    if numberSolutions == core.config.num_solutions:
      break	
    if solution != None:
      orderedSol = list()
      numberSolutions += 1
      for key in solution.keys():
        orderedSol.append([key, solution[key]])
      orderedSol.sort(lambda x, y: myComparator(x[0], y[0]))
      sol_grade = grade(solution, chords, harmonies)
      if (bestGradeSoFar > sol_grade) and (core.config.debugging_options["old_constraint"] == 0):
        print "Uh oh, there seems to be a problem in my understanding of what grade_debug() does."
        print "=== bestGradeSoFar: ", bestGradeSoFar, "sol_grade_tuple[0]: ", sol_grade
        print "Apparently, constraint.py didn't return a 'bestsofar' solution. Hm."
      bestGradeSoFar = sol_grade
      solutions_graded.append( (sol_grade, orderedSol) )
#      counter = 0
#      f.write("Solution Number: " + str(numberSolutions) + "\t Grade: " + str(sol_grade))
#      f.write('\n\n')
#      for thing in orderedSol:
#        if counter == numTimeSteps:
#          counter = 0
#          f.write('\n\n')
#        f.write(str(thing))
#        counter += 1
#      f.write('\n\n\n')
  if numberSolutions == 0:
    print "No solution reported."
#    f.close()
#    f_p.close()
    return		    
#  f.close()
#  f_p.close() 
  print "Number of solutions: ", numberSolutions
  # Now to choose the solution from solutions_graded with the highest grade
  solutions_graded.sort(lambda x, y : _solution_cmp(x, y))
  best_sol = solutions_graded[0]
  worst_sol = solutions_graded[len(solutions_graded) - 1]
  print "Best solution: ", best_sol
  print "Worst solution: ", worst_sol
  converter.convertToAbjad(best_sol[1:][0])
  converter.convertToAbjad(worst_sol[1:][0])

def solveProblem_debug(harm):
  time1 = time.time()
  numTimeSteps = len(harm._variables) / 4
  
  core.config.chords = chords
  core.config.harmonies = harmonies
  
  solutionIter = harm.getSolutionIter()
  f = open('C:\Users\Sforzando\Desktop\cspOutput.txt', 'w')
  f_p = open('C:\Users\Sforzando\Desktop\cspOutput_pickled.txt', 'w')
  numberSolutions = 0
  solutions_graded = []
  bestGradeSoFar = -1000000000
  
  for solution in solutionIter:
    if numberSolutions == core.config.num_solutions:
      break  
    if solution != None:
      print "Solutions computed: ", numberSolutions
      orderedSol = list()
      numberSolutions += 1
      for key in solution.keys():
        orderedSol.append([key, solution[key]])
      orderedSol.sort(lambda x, y: myComparator(x[0], y[0]))
      sol_grade_tuple = grade_debug(solution, chords, harmonies)  # grade_debug() returns the tuple ( <grade> , <feature_counts> )
      if (bestGradeSoFar > sol_grade_tuple[0]) and (core.config.debugging_options["old_constraint"] == 0):
        print "Uh oh, there seems to be a problem in my understanding of what grade_debug() does."
        print "=== bestGradeSoFar: ", bestGradeSoFar, "sol_grade_tuple[0]: ", sol_grade_tuple[0]
        print "Apparently, constraint.py didn't return a 'bestsofar' solution. Hm." 
      bestGradeSoFar = sol_grade_tuple[0]
      if core.config.debugging_options["track_grade"] == 1:
        print " ===== DEBUG  - track_grade - ===== ", bestGradeSoFar
      solutions_graded.append( (sol_grade_tuple, orderedSol) )
      if core.config.debugging_options["write_file"] == 1:
        print " ===== DEBUG - write_file - ===== "
        counter = 0
        f.write("Solution Number: " + str(numberSolutions) + "\t Grade: " + str(sol_grade_tuple))
        f.write('\n\n')
        for thing in orderedSol:
          if counter == numTimeSteps:
            counter = 0
            f.write('\n\n')
          f.write(str(thing))
          counter += 1
        f.write('\n\n\n')
  if numberSolutions == 0:
    print "No solution reported."
    f.close()
    f_p.close()
    return        
  f.close()
  f_p.close()
  print "============================================"
  print "Time to generate solutions: ", time.time() - time1
  print "============================================" 
  print "Number of solutions: ", numberSolutions
  # Now to choose the solution from solutions_graded with the highest grade
  solutions_graded.sort(lambda x, y : _solution_cmp_debug(x, y))
  best_sol = solutions_graded[0]
  worst_sol = solutions_graded[len(solutions_graded) - 1]
  print "Best solution grade: ", best_sol[0][0]
  print "Best solution: ", best_sol[1]
  if core.config.debugging_options["show_features"] == 1:
    print ""
    print " ===== DEBUG - show_features - ===== Best solution feature_counts: ", best_sol[0][1]
    print ""
  print "Worst solution grade: ", worst_sol[0][0]
  print "Worst solution: ", worst_sol[1]
  if core.config.debugging_options["show_features"] == 1:
    print ""
    print " ===== DEBUG - show_features - ===== Worst solution feature_counts: ", worst_sol[0][1]
    print ""
  print "best_sol form: ", best_sol[1:][0]


# x, y := tuple of the form: ( <grade>, <orderedSol list of lists> )     
def _solution_cmp(x, y):
  grade_0 = x[0]
  grade_1 = y[0]
  if grade_0 < grade_1: return 1
  if grade_0 > grade_1: return -1
  return 0

# x, y := tuple of the form: ( ( <grade> , <dict of feature_counts> ) , [orderedSol list of lists] )
def _solution_cmp_debug(x, y):
  grade_0 = x[0][0]
  grade_1 = y[0][0]
  if grade_0 < grade_1: return 1
  if grade_0 > grade_1: return -1
  return 0

def profile_test(harm):
  cProfile.run('examples.harmonytests.test4(harm)')

def arg_handle(argv):
  for arg in argv:
    if (len(arg) > 5) and (arg[0:5] == "test="):
      core.config.test_name = arg[5:]
    if (len(arg) > 2) and (arg[0:2] == "n="):
      core.config.num_solutions = int(arg[2:])
    if (arg == "-d") or (arg == "-debug") : core.config.debug = 1
    if core.config.debugging_options.has_key(arg):
      core.config.debugging_options[arg] = 1

if __name__ == '__main__':
  time1 = time.time()
  arg_handle(sys.argv)
  if core.config.debugging_options["old_constraint"] == 1:
    harm = constraint_unmodified.Problem()
  else:
    harm = constraint.Problem()
  if core.config.test_name != None:
    print "====== Running Test: ", core.config.test_name
    exec("examples.harmonytests." + core.config.test_name + "(harm)")
  else:
    examples.harmonytests.test4(harm)
  print "Time (in seconds) to perform test: ", time.time() - time1