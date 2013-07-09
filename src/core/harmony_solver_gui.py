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
import constraint_noPruning as constraint
from harmony_rules import *
from Grader.grader import grade, grade_debug
import core.config
from Data_Structures.dataStructs import TimeList
from util.constants import *

###
# First Parallel Fifth caught! 2:39 AM, 11-23-09 :)

#chords = []    ## A data structure to keep track of what chords
              ## are at what time steps.
              ## i.e chords[3] is the chord at time step 3
#harmonies = []  ## A data structure to keep track of the harmony at
      ## Different time steps.
      ## i.e harmony[3] is the harmony at time step 3, like "ii6" or "V42"

class HarmonySolver():
  
  def __init__(self):
    self.problem = constraint.Problem()
    self._halt = 0
    self.chords = TimeList()
    self.harmonies = TimeList()
    self.num_solutions = 100000
    self.solutions = []

  # x = "S, A, T, B"
  # y = "S, A, T, B"
  # Order by "s3, s2, s1, a3, ..., t3, ..., b3, ..."
  def myComparator(self, x, y):
    x1 = self.__voiceToNum__(x)
    y1= self.__voiceToNum__(y)
    if x1 > y1: return 1
    if x1 == y1:
      x_num = int(x[1:])
      y_num = int(y[1:])
      return x_num.__cmp__(y_num)
    # x1 < y1
    return -1
  
  def halt(self):
    self._halt = 1
  
  # translates "S, A, T, B" to "0, 1, 2, 3"
  def __voiceToNum__(self, voice):
    lowerCase = voice.lower() # Just in case we get something like "S3" versus "s3"
    return {"s": 0,
            "a": 1,
            "t": 2,
            "b": 3}[lowerCase[0]] # Grab first letter
  
  
  # Returns True if the harmony at the specified time-step is Dominant (i.e a "V") or not.
  def isDominant(self, time):
    harmony = self.harmonies.get(time)
    return (harmony[0] == "V") or (harmony == "Dominant")
  
  # In an attempt to prune the domain-space of each variable, I will do preprocessing to
  # decrease the domain, rather than enforcing it with constraints.
  def getSingerDomain(self, voice, chord):
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
  
  def createNewProblem(self):
    """ Reset chords/harmonies database """
    self.problem = constraint.Problem()
    self._halt = 0
  
  # If the user wishes to specify any voice, then he/she can do so here. Should overwrite any previous 
  # specified notes (for the specified voice). 
  # voice := Either "soprano", "alto", "tenor", "bass"
  # notes := a Timelist() of numbers that represents the EXACT note that the singer sings
  #          at each time step.
  def specify_voice(self, voice, notes):
    voice = self._convertToConstraintForm(voice)
    if notes.is_empty():  # We don't need to specify the voice, so just use the original chord domain.
      for t in self.chords.get_times():
        chord = self.chords[t]
        var = voice+str(t)
        if var in self.problem._variables:
          self.problem.replaceVariable(var, self.getSingerDomain(voice, chord))
        else:
          raise RuntimeError, "Error in HarmonySolver.specify_voice() - var wasn't in self.problem._variables, \
                                  , where var is: %s" % var
    else:                 # Restrict the variable's domain to the exact note specified
      for t in notes.get_times():
        if notes[t] != None:
          var = voice+str(t)
          if var in self.problem._variables:
            self.problem.replaceVariable(var, (notes[t],))
          else:
            raise RuntimeError, "Error in HarmonySolver.specify_voice() - var wasn't in self.problem._variables, \
                                  , where var is: %s" % var  
  # This method, used by the user to initialize the CSP, will
  # add variables to the CSP (4 variables for each voice: SATB) for the
  # various time steps.
  #  problem := CSP Problem
  #  chord   := Chord object, created by user
  #  time    := time step, i.e 0, 1, 2, 3, ...
  def addChord(self, chord, time):
    problem = self.problem
    self.chords.add(time, chord)  # Update our chord database
    # Now let's update our Problem() instance's variable list
    singers = ("s"+str(time), "a"+str(time), "t"+str(time), "b"+str(time))
    problem.addVariable(singers[0], self.getSingerDomain("s", chord))
    problem.addVariable(singers[1], self.getSingerDomain("a", chord))
    problem.addVariable(singers[2], self.getSingerDomain("t", chord))
    problem.addVariable(singers[3], self.getSingerDomain("b", chord))
    
    problem.addConstraint(SpecifyChordConstraint(chord, self.harmonies) , tuple(singers))
    if chord.bassNote != None:
      problem.addConstraint(SetBassConstraint(chord), ["b"+str(time)])
    ### BIG QUESTION: Why can't I say:
    #problem.addConstraint(setBass(chord), list(singers[3]))
    # ??????????????????????? :/
  
  def removeChord(self, time):
    self.chords.remove(time)
    singers = ("s"+str(time), "a"+str(time), "t"+str(time), "b"+str(time))
    for var in singers:
      self.problem.removeVariable(var)
  
  def addHarmony(self, harmony, time):
    self.harmonies.add(time, harmony)
  
  def removeHarmony(self, time):
    self.harmonies.remove(time)
    
  def removeAll(self):
    times = self.chords.get_times()
    for t in times:
      self.removeChord(t)
      self.removeHarmony(t)
    if (not self.chords.is_empty()) or (not self.harmonies.is_empty()):
      raise RuntimeError, "Either self.chords or self.harmonies was not empty, despite calling HarmonySolver.removeAll()"
      exit(1)
    self.solutions = []

  def addHarmonyRules(self):
    problem = self.problem  
    numTimeSteps = len(self.chords.get_times())
    for t in range(numTimeSteps):
      # Make sure that voices are at most an octave away from each other
      problem.addConstraint(SpacingConstraint(), ["s"+str(t), "a"+str(t)])
      problem.addConstraint(SpacingConstraint(), ["a"+str(t), "t"+str(t)])
      problem.addConstraint(SpacingConstraint(), ["t"+str(t), "b"+str(t)])
      # Make sure that voices don't cross each other
      problem.addConstraint(CrossoverConstraint(), ["s"+str(t), "a"+str(t), "t"+str(t), "b"+str(t)])
      if t < (numTimeSteps - 1):    # Mainly, if t != numTimeSteps    
        # Check Leaps
        for singer in ("s", "a", "t", "b"):
          singer2 = singer+str(t+1)
          problem.addConstraint(LeapConstraint(), [singer+str(t), singer2])
        # Make sure that there are no temporal overlaps
        problem.addConstraint(TemporalOverlapConstraint(), \
                           ["s"+str(t), "s"+str(t+1), "a"+str(t), "a"+str(t+1)])
        problem.addConstraint(TemporalOverlapConstraint(), \
                           ["a"+str(t), "a"+str(t+1), "t"+str(t), "t"+str(t+1)])
        problem.addConstraint(TemporalOverlapConstraint(), \
                           ["t"+str(t), "t"+str(t+1), "b"+str(t), "b"+str(t+1)])
        chord = self.chords.get(t)
        # Add parallel fifth/octave handling
        singer_array = []
        history = []
        for singer in ("s", "a", "t", "b"):
          for singer2 in ("s", "a", "t", "b"):
            if (singer != singer2) and ((singer, singer2) not in history):
              singer_array.append((singer+str(t), singer+str(t+1), singer2+str(t), singer2+str(t+1)))
              history.append((singer2, singer))
        for i in range(len(singer_array)):
          problem.addConstraint(ParallelFifthConstraint(), singer_array[i])
          problem.addConstraint(ParallelOctaveConstraint(), singer_array[i])
        # Add behavior for soprano/bass relationship (i.e no hidden 5th, hidden octave)
        ### Note: singer_array[2] contains the tuple ( <s0>, <s1>, <b0>, <b1> ), which is what we want
        problem.addConstraint(HiddenMotionOuterConstraint(), singer_array[2])        
        # Add behavior for sevenths
        if chord.getSeventh__() != None:
          for singer in ("s", "a", "t", "b"):
            problem.addConstraint(SeventhConstraint(chord), [singer+str(t), singer+str(t+1)])
        # Add behavior for leading tones of dominant chords)
        if self.isDominant(t):
          for singer in ("s", "a", "t", "b"):
            problem.addConstraint(LeadingToneConstraint(chord), [singer+str(t), singer+str(t+1)])
        # Add behavior for diminished fifths of diminished chords
        if ("dim" in chord.modifiers) or ("dim7" in chord.modifiers):
          for singer in ("s", "a", "t", "b"):
            problem.addConstraint(DiminishedFifthConstraint(chord), [singer+str(t), singer+str(t+1)])
    
  """
  Returns n solutions, where n = core.config.num_solutions
  """  
  def unhalt(self):
    self._halt = 0
  
  def isHalt(self):
    return self._halt == 1
  
  def solveProblem(self):
    self.unhalt()    
    solutionIter = self.problem.getSolutionIter()
    numberSolutions = 0
    solutions_graded = []
    
    bestGradeSoFar = -1000000000
    
    for solution in solutionIter:
      
      if self.isHalt() or (numberSolutions == self.num_solutions):
        break  
      
      if solution != None:
        orderedSol = list()
        numberSolutions += 1
        for key in solution.keys():
          orderedSol.append([key, solution[key]])
        orderedSol.sort(lambda x, y: self.myComparator(x[0], y[0]))
        sol_grade = grade(solution, self.chords, self.harmonies)
  #      if (bestGradeSoFar > sol_grade) and (core.config.debugging_options["old_constraint"] == 0):
  #        print "Uh oh, there seems to be a problem in my understanding of what grade_debug() does."
  #        print "=== bestGradeSoFar: ", bestGradeSoFar, "sol_grade_tuple[0]: ", sol_grade
  #        print "Apparently, constraint.py didn't return a 'bestsofar' solution. Hm."
        bestGradeSoFar = sol_grade
        solutions_graded.append( (sol_grade, orderedSol) )
      else:
        print "No solution reported."
        return None  
    print "Number of solutions: ", numberSolutions
    if numberSolutions == 0:
      print "No solution reported."
      return None
    # Now to choose the solution from solutions_graded with the highest grade
    solutions_graded.sort(lambda x, y : self._solution_cmp(x, y))
    best_sol = solutions_graded[0]
    worst_sol = solutions_graded[len(solutions_graded) - 1]
    #print "Best solution: ", best_sol
    #print "Worst solution: ", worst_sol
    self.solutions = solutions_graded
    return solutions_graded
  
  
  """
  Returns n solutions, where n = core.config.num_solutions. NOTE: Not used at the moment....
  """  
  def solveProblem_iter(self):
    self.unhalt()
    solutionIter = self.problem.getSolutionIter()
    numberSolutions = 0
    solutions_graded = []
    
    bestGradeSoFar = -1000000000
    
    for solution in solutionIter:
      if numberSolutions == self.num_solutions:
        break  
      if solution != None:
        orderedSol = list()
        numberSolutions += 1
        for key in solution.keys():
          orderedSol.append([key, solution[key]])
        orderedSol.sort(lambda x, y: self.myComparator(x[0], y[0]))
        sol_grade = grade(solution, self.chords, self.harmonies)
        if (bestGradeSoFar > sol_grade) and (core.config.debugging_options["old_constraint"] == 0):
          print "Uh oh, there seems to be a problem in my understanding of what grade_debug() does."
          print "=== bestGradeSoFar: ", bestGradeSoFar, "sol_grade_tuple[0]: ", sol_grade
          print "Apparently, constraint.py didn't return a 'bestsofar' solution. Hm."
        bestGradeSoFar = sol_grade
        solutions_graded.append( (sol_grade, orderedSol) )
      else:
        print "No solution reported."
        #return None  
    print "Number of solutions: ", numberSolutions
    if numberSolutions == 0:
      print "No solution reported."
      #return None
    # Now to choose the solution from solutions_graded with the highest grade
    solutions_graded.sort(lambda x, y : self._solution_cmp(x, y))
    best_sol = solutions_graded[0]
    worst_sol = solutions_graded[len(solutions_graded) - 1]
    print "Best solution: ", best_sol
    print "Worst solution: ", worst_sol
    #converter.convertToAbjad(best_sol[1:][0])
    #converter.convertToAbjad(worst_sol[1:][0])
    self.solutions = solutions_graded
    for sol in solutions_graded:
      yield sol
  
  # x, y := tuple of the form: ( <grade>, <orderedSol list of lists> )     
  def _solution_cmp(self, x, y):
    grade_0 = x[0]
    grade_1 = y[0]
    if grade_0 < grade_1: return 1
    if grade_0 > grade_1: return -1
    return 0

  # Converts (soprano,alto,tenor,bass) to (s,a,t,b), since constraint.py's variables are of the form:
  # s0, b4, etc...
  def _convertToConstraintForm(self, voice):
    if (type(voice) == int):
      voice = {0:"s",1:"a",2:"t",3:"b"}[voice]
    if voice not in ("s","a","t","b"):
      try:
        voice = {"soprano":"s" , "alto":"a" , "tenor":"t" , "bass":"b"}[voice]
      except ValueError:
        raise ValueError , "Error in HarmonySolver._convertToConstraintForm() , %s" % voice
    return voice
#def arg_handle(argv):
#  for arg in argv:
#    if (len(arg) > 5) and (arg[0:5] == "test="):
#      core.config.test_name = arg[5:]
#    if (len(arg) > 2) and (arg[0:2] == "n="):
#      core.config.num_solutions = int(arg[2:])
#    if (arg == "-d") or (arg == "-debug") : core.config.debug = 1
#    if core.config.debugging_options.has_key(arg):
#      core.config.debugging_options[arg] = 1
#
#if __name__ == '__main__':
#  time1 = time.time()
#  arg_handle(sys.argv)
#  harm = createProblem()
#  if core.config.test_name != None:
#    print "====== Running Test: ", core.config.test_name
#    exec("examples.harmonytests." + core.config.test_name + "(harm)")
#  else:
#    examples.harmonytests.test4(harm)
#  print "Time (in seconds) to perform test: ", time.time() - time1