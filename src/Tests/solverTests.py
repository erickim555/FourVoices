'''
Created on Jan 31, 2010

@author: Sforzando
'''
import unittest
import core.config
from core.solver import createProblem, addHarmony, solveProblem, addHarmonyRules
from core.Note import Chord, pitchToNum, numToPitch
from Data_Structures.timelist import TimeList
"""
To create and set up a problem:

solver.py
    1.) Create a problem
        - createProblem() returns a Problem() instance (from constraint_unmodified)
    2.) Specify the problem
        - addHarmony(problem, chord, harmony), i.e addHarmony(prob, Chord() instance, "Tonic"/"I")
    3.) Add harmony rules (i.e constraints to problem)
        - addHarmonyRules(problem)
    3.) Solve the problem
        - solveProblem(problem) returns a list of solutions (of length dependent on core.config.num_solutions)
"""

class SolverTester(unittest.TestCase):

    def setUp(self):
        core.config.num_solutions = 100000000000000000000

    def testOne(self):
        core.config.chords = TimeList()
        core.config.harmonies = TimeList()
        harm = createProblem()  
        addHarmony(harm, Chord("C", None, 0), "I")
        addHarmonyRules(harm)
        solutions = solveProblem(harm)
        self.assertEqual(len(solutions), 42)
    
    def testTwo(self):
        core.config.chords = TimeList()
        core.config.harmonies = TimeList()
        harm = createProblem()
        addHarmony(harm, Chord("C", None, 0), "I")
        addHarmony(harm, Chord("G", None, 1), "V")
        addHarmonyRules(harm)
        solutions = solveProblem(harm)
        self.assertEqual(len(solutions), 438)
    
    def testSequence(self):
        core.config.chords = TimeList()
        core.config.harmonies = TimeList()
        harm = createProblem()
        emin = Chord("E", ["min"], 0, "E")
        A7 = Chord("A", ["7"], 1, "E")
        dmin = Chord("D", ["min"], 2, "D")
        G7 = Chord("G", ["7"], 3, "D")
        C = Chord("C", None, 4, "C")  
        addHarmony(harm, emin, "iii")
        addHarmony(harm, A7, "V43/ii")
        addHarmony(harm, dmin, "ii")
        addHarmony(harm, G7, "V43")
        addHarmony(harm, C, "I")
        addHarmonyRules(harm)
        solutions = solveProblem(harm)
        self.assertEqual(len(solutions), 128)


    def testDiminished(self):
        core.config.chords = TimeList()
        core.config.harmonies = TimeList()
        harm = createProblem()
        gsharpdim7 = Chord("G#", ["dim7"], 0, "G#")
        addHarmony(harm, gsharpdim7, "vii7")
        addHarmonyRules(harm)
        solutions = solveProblem(harm)
        firstSolution = solutions[0][1]
        firstSolution = [x[1] for x in firstSolution]
        self.assertTrue(self.solutionHasNotes(firstSolution, ["G#", "B", "D", "F"]))
    
    def solutionHasNotes(self, solution, notes):
        solution = [ numToPitch(x) for x in solution ]
        difference = [ x for x in notes if x not in solution ]
        print "MOOSE", solution, difference
        return (len(difference) == 0)
        
#    def testchoice(self):
#        element = random.choice(self.seq)
#        self.assert_(element in self.seq)

#    def testsample(self):
#        self.assertRaises(ValueError, random.sample, self.seq, 20)
#        for element in random.sample(self.seq, 5):
#            self.assert_(element in self.seq)

if __name__ == '__main__':
    unittest.main()
