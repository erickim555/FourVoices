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
  ./src/core/solver.py

Contains the main routines that actually solves the harmonization
problem. Involves:
    - Creation of problem instances
    - Solving problem instances

Main functions:
  init_problem()
  solve()

Also defines a command-line interface (CLI).
'''

import sys, os, time, pdb, traceback, argparse, itertools

import config, Note
from harmony_rules import *

sys.path.append("..")
from constraint import constraint
from Grader.grader import grade, grade_debug
from Data_Structures.dataStructs import TimeList
from util.constants import *

def solve(problem):
    """ Solves an input harmonization problem.
    INPUT:
      Problem problem
    Output:
        SOLUTIONS_ITER
    """
    solutions_iter = problem.getSolutionIter()
    return solutions_iter

def init_problem(problem, chords, figures):
    """ Initializes the CSP Problem by adding all constraints
    introduced by specified chords, harmonies, and optional provided
    lines.
    Input:
        Problem PROBLEM:
        list CHORDS:
        list FIGURES:
    Output:
        Problem PROBLEM.
    """
    '''
    (1) Add simple chord constraints (unary)
      Each chord enforces that the voices (satb) must cover the chord
      tones (ie root, third, fifth, etc).
    '''
    chords = sorted(chords, key=lambda c: c.time)
    for chord in chords:
        # Generate CSP vars and constraints for this chord
        t = chord.time
        vars_toadd = [make_var(voice, t) for voice in VOICE_PREFIXES]
        # At time t, create CSP vars for S,A,T,B
        for i, var in enumerate(vars_toadd):
            voice = VOICE_PREFIXES[i]
            domain = get_singer_domain(voice, chord)
            problem.addVariable(var, domain)
        # Create CSP constraint for satb
        problem.addConstraint(SpecifyChordConstraint(chord), vars_toadd)
        if chord.bassNote != None:
            # Bass *must* cover this note
            problem.addConstraint(SetBassConstraint(chord), [make_var("b", t)])

    '''
    (2) Add relational harmonic constraints (2+ vars)
      Defines rules that govern interactions between voices, ie
      - voice spacing, no crossing, leaps, no-parallel-fifths, etc.
    '''
    num_time_steps = len(chords)
    for t, chord in enumerate(chords):
        # Voices are at most an octave away from each other
        problem.addConstraint(SpacingConstraint(), [make_var("s", t), make_var("a", t)])
        problem.addConstraint(SpacingConstraint(), [make_var("a", t), make_var("t", t)])
        problem.addConstraint(SpacingConstraint(), [make_var("t", t), make_var("b", t)])
        # Voices don't cross each other
        problem.addConstraint(CrossoverConstraint(),
                              [make_var(v, t) for v in VOICE_PREFIXES])
        if t < (num_time_steps - 1):    # Mainly, if t != numTimeSteps
        # Check Leaps
            for voice in VOICE_PREFIXES:
                var0, var1 = make_var(voice, t), make_var(voice, t+1)
                problem.addConstraint(LeapConstraint(), [var0, var1])
            # Make sure that there are no temporal overlaps
            problem.addConstraint(TemporalOverlapConstraint(),
                                  [make_var("s", t), make_var("s", t+1),
                                   make_var("a", t), make_var("a", t+1)])
            problem.addConstraint(TemporalOverlapConstraint(),
                                  [make_var("a", t), make_var("a", t+1),
                                   make_var("t", t), make_var("t", t+1)])
            problem.addConstraint(TemporalOverlapConstraint(),
                                  [make_var("t", t), make_var("t", t+1),
                                   make_var("b", t), make_var("b", t+1)])
            # Add parallel fifth/octave handling
            voice_pairs = []
            singer_array = []
            history = []
            for v1 in VOICE_PREFIXES:
                for v2 in VOICE_PREFIXES:
                    if (v1 != v2) and ((v1, v2) not in history):
                        singer_array.append(
                            (make_var(v1,t),make_var(v1,t+1),
                             make_var(v2,t),make_var(v2,t+1)))
                        history.append((v2, v1))
            for i in xrange(len(singer_array)):
                problem.addConstraint(ParallelFifthConstraint(), singer_array[i])
                problem.addConstraint(ParallelOctaveConstraint(), singer_array[i])
            # Add behavior for soprano/bass relationship (i.e no hidden 5th, hidden octave)
            problem.addConstraint(HiddenMotionOuterConstraint(),
                                  (make_var("s", t), make_var("s", t+1),
                                   make_var("b", t), make_var("b", t+1)))
            # Add behavior for sevenths
            if chord.getSeventh__() != None:
                for voice in VOICE_PREFIXES:
                    problem.addConstraint(SeventhConstraint(chord),
                                          [make_var(voice, t), make_var(voice, t+1)])
            # Add behavior for leading tones of dominant chords
            if chord.is_dominant():
                for voice in VOICE_PREFIXES:
                    problem.addConstraint(LeadingToneConstraint(chord),
                                          [make_var(voice, t), make_var(voice, t+1)])
            # Add behavior for diminished fifths of diminished chords
            if chord.is_dim():
                for voice in VOICE_PREFIXES:
                    problem.addConstraint(DiminishedFifthConstraint(chord),
                                         [make_var(voice, t), make_var(voice, t+1)])
            # For fully-dim chords, the root should always resolve upwards
            if chord.is_dim_full():
                for voice in VOICE_PREFIXES:
                    problem.addConstraint(FullDiminishedRootConstraint(chord),
                                          [make_var(voice, t), make_var(voice, t+1)])
    # 3.) Add any specified notes
    problem = add_figure_constraints(problem, figures)
    return problem

def add_figure_constraints(problem, figures):
    """ Adds CSP constraints to the Problem instance to handle any
    specified notes.
    Input:
        Problem PROBLEM:
        list FIGURES: [(int time, str voice, str note, int octave/None), ...]
    Output:
        Problem PROBLEM.
    """
    def get_singer_range(voice):
        return {'s': soprano_range,
                'a': alto_range,
                't': tenor_range,
                'b': bass_range}[voice]
    for (time, voice, note, octave) in figures:
        var = make_var(voice, time)
        if var not in problem._variables:
            raise RuntimeError("(add_figure_constraints) Var {0} wasn't in problem._variables".format(var))
        domain_new = []
        note_num = pitchToNum(note)
        if octave == None:
            for pitch in get_singer_range(voice):
                if pitch % 12 == note_num:
                    domain_new.append(pitch)
        else:
            domain_new.append(note_num * octave)
        problem.replaceVariable(var, domain_new)
    return problem

def make_var(voice, time):
    """ Creates a CSP Variable for singer VOICE at time TIME. """
    # CSP vars are strings of the form:
    #     "<voice>_<time>"
    # i.e. "s_0"
    return "{0}_{1}".format(voice, time)

def get_singer_domain(voice, chord):
    """ Returns a list of valid possible pitches for VOICE to sing on
    CHORD.
    Input:
        str VOICE: "s", "a", "t", or "b"
        Chord CHORD:
    Output:
        list PITCHES: [int pitch0, ...]
    """
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

class HarmonySolver():
    """
  Class that UI uses. Sort of a wraper class for constraint.Problem().
  UI does this:
    As user adds chords/voices, the HarmonySolver's internal datastructs
    are updated. Then, when user clicks "solve", the HarmonySolver its
    chords and harmonies lists, adds the relevant vars/constraints to
    its constraint.Problem(), then runs the solver.

  This is basically a complete rewrite of the above code that creates a
  problem instance from the CLI.

  TODO: Refactor this class to only have this functionality:
      add_chord()
      add_note()
      solve()
          This calls init_problem() and solve().
    """
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
        return (harmony[0] == "V") or (harmony == DOMINANT)

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

        problem.addConstraint(SpecifyChordConstraint(chord) , tuple(singers))
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
        self.chords[time].role = harmony

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

def parse_problemfile(problemfile):
    """ Parses an input file containing a Harmony problem.
    See the template file for information about the expected
    file format.
    Input:
        str PROBLEMFILE:
    Output:
        (list CHORDS, list FIGURES)
    CHORDS: [Chord c, ...]
    FIGURES: [(int t, str voice, str note, int octave/None), ...]
    """
    try:
        f = open(problemfile, 'r')
    except IOError as e:
        print "  Error opening harmony file: {0}".format(problemfile)
        return None
    is_chord, is_figures = False, False
    BEGIN_CHORD, BEGIN_FIGURES = "[Chords]", "[Figures]"
    chords, figures = [], []
    for line in f.readlines():
        if not line: continue
        line = line.strip()
        if not line or line.startswith("#"): continue
        if line.startswith(BEGIN_CHORD):
            is_chord, is_figures = True, False
        elif line.startswith(BEGIN_FIGURES):
            is_chord, is_figures = False, True
        elif is_chord:
            chord = parse_chord(line)
            if chord != None:
                chords.append(chord)
        elif is_figures:
            # list FIGURE: (str voice, [(str voice, int octave/None)/None, ...])
            figure_tup = parse_figure(line)
            if figure_tup != None:
                voice, notes = figure_tup
                figure_ = []
                for time, entry in enumerate(notes):
                    if entry != None:
                        note, octave = entry
                        figure_.append((time, voice, note, octave))
                figures.extend(figure_)
    return chords, figures

def parse_chord(line):
    """ Parses a line from the [Chords] section. Returns None if
    the parsing fails.
    """
    try:
        s = line.split(",")
        time, root, role, bassnote = s[:4]
        time, root, role, bassnote = int(time), root.strip().upper(), role.strip().lower(), bassnote.strip().upper()
        if root in ("", "NONE", " "):
            root = None
        if role in ("", "none", " "):
            role = None
        if bassnote in ("", "NONE", " "):
            bassnote = None
        mods = [w.lower().strip() for w in s[4:]]
        mods = [m for m in mods if m.lower() not in ('', 'none', ' ')]
        chord = Chord(root, mods, time, bassNote=bassnote, role=role)
        return chord
    except:
        return None

def parse_figure(line):
    """ Parses a line from the [Figures] section. Returns None if
    the parsing fails.
    Output:
    (str VOICE, tuple FIGURE)
        VOICE: one of 's', 'a', 't', 'b'
        FIGURE: ((str note, int octave/None)/None, ...)

    Example:
    >>> parse_figure("s: A4, None, C")
    ('s', [('A', 4), None, ('C', None)])
    """
    try:
        voice = line[0].lower()
        figure = []
        if voice not in VOICE_PREFIXES:
            raise Exception("Not a valid voice: {0}".format(voice))
        line_ = line[2:].strip()
        entries = [wd.strip().lower() for wd in line_.split(",")]
        for entry in entries:
            if entry.lower() == "none":    # Can be anything
                figure.append(None)
            else:
                note = entry[0]
                try:
                    octave = int(entry[1:])
                except ValueError:
                    octave = None
                if note not in NOTES:
                    raise Exception("Not a valid note: {0}".format(note))
                if octave != None and (octave < 0 or octave > 8):
                    raise Exception("Octave too low/high: {0}{1}".format(note, octave))
                figure.append((note.upper(), octave))
        return voice, figure
    except Exception:
        traceback.print_exc()
        return None

def run_tests():
    pass

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("problem", help="Path to problem instance.")
    parser.add_argument("--run_tests", action="store_true",
                        help="Runs the solver on a suite of built-in \
problem instances.")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.run_tests:
        return run_tests()
    # list FIGURES: [(str voice, [(str note, int octave/None)/None, ...]), ...]
    pair = parse_problemfile(args.problem)
    if not pair:
        print "  Exiting."
        return 1
    chords = pair[0]
    figures = pair[1]
    print "(Info) Initializing harmony problem..."
    t = time.time()
    problem = init_problem(constraint.Problem(), chords, figures)
    print "(Info) Finished initialization ({0:.4f}s)".format(time.time() - t)
    print "(Info) Solving Harmony Problem"
    t = time.time()
    solutions_iter = solve(problem)
    dur = time.time() - t
    print "(Info) Done Solving ({0:.4f}s)".format(dur)
    print "  Displaying solutions:"
    flag_continue = False
    solutions = []
    for sol in solutions_iter:
        solutions.append(sol)
    print "    {0} Solutions Total.".format(len(solutions))
    for i, solution in enumerate(solutions):
        if flag_continue:
            continue
        tmax = len(solution) / 4
        for t in xrange(tmax):
            print "Time={0}:    [{1}]".format(t, chords[t])
            for voice in VOICE_PREFIXES:
                var = make_var(voice, t)
                pitchnum = solution[var]
                print "    {0}: {1}".format(voice, Note.numToPitch_absolute(pitchnum))
        s = raw_input("({0}/{1}) Press enter to continue, 'c' to skip, or 'q' to exit.".format(i, len(solutions) - 1))
        if s == 'c':
            flag_continue = True
        elif s == 'q':
            break

if __name__ == '__main__':
    main()
