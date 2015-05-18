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

import time

import Core_Tree.Note
from Core_Tree.Note import Chord
import Core_Tree.harmony_solver_tree
import Core_Tree.init_problem
from Core_Tree.init_problem import addHarmony, addHarmonyRules, specify_voice
import Core_Tree.config

import Core_Tree.constraint

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


# Test 1: ii6 V7 I
def simpleTest(harm):
    dmin = Chord("D", ["min"], 0, "F")
    G = Chord("G", ["7"], 1, "G")
    C = Chord("C", None, 2, "C")
    addHarmony(dmin, "ii6")
    addHarmony(G, "V7")
    addHarmony(C, "I")
    addHarmonyRules()
    run_test(harm)

# Test 2: iii V43/ii ii V43 I
def sequenceTest(harm):
    emin = Chord("E", ["min"], 0, "E")
    A7 = Chord("A", ["7"], 1, "E")
    dmin = Chord("D", ["min"], 2, "D")
    G7 = Chord("G", ["7"], 3, "D")
    C = Chord("C", None, 4, "C")
    addHarmony(emin, "iii")
    addHarmony(A7, "V43/ii")
    addHarmony(dmin, "ii")
    addHarmony(G7, "V43")
    addHarmony(C, "I")
    addHarmonyRules()
    run_test(harm)

def simplestTest(harm):
    G7 = Chord("G", ["7"], 0, "G")
    C = Chord("C", None, 1, "C")
    addHarmony(G7, "V7")
    addHarmony(C, "I")
    addHarmonyRules()
    run_test(harm)

# Too long!
# Edit: Efficiency is better (pruned variable domains), but still failure
#   I suspect that this is just impossible to harmonize correctly
def test2(harm):
    # F Major
    F = Chord("F", None, 0, "F")
    A7 = Chord("A", ["7"], 1, "A")
    dmin = Chord("D", ["min"], 2, "D")
    F_C = Chord("F", None, 3, "C")
    C7 = Chord("C", ["7"], 4, "C")
    dmin2 = Chord("D", ["min"], 5, "D")
    F_C2 = Chord("F", None, 6, "C")
    Bb = Chord("Bb", None, 7, "Bb")
    gmin7 = Chord("G", ["min", "7"], 8, "Bb")
    C72 = Chord("C", ["7"], 9, "C")
    F_end = Chord("F", None, 10, "F")

    addHarmony(F, "I")
    addHarmony(A7, "V7/vi")
    addHarmony(dmin, "vi")
    addHarmony(F_C, "I64")
    addHarmony(C7, "V7")
    addHarmony(dmin2, "vi")
    addHarmony(F_C2, "I64")
    addHarmony(Bb, "IV")
    addHarmony(gmin7, "ii65")
    addHarmony(C72, "V7")
    addHarmony(F_end, "I")
    addHarmonyRules()
    run_test(harm)

def test2_relaxed(harm):
    # F Major
    F = Chord("F", None, 0, "F")
    A7 = Chord("A", ["7"], 1, "A")
    dmin = Chord("D", ["min"], 2)
    F_C = Chord("F", None, 3, "C")
    C7 = Chord("C", ["7"], 4, "C")
    dmin2 = Chord("D", ["min"], 5, "D")
    F_C2 = Chord("F", None, 6, "C")
    Bb = Chord("Bb", None, 7, "Bb")
    gmin7 = Chord("G", ["min", "7"], 8, "Bb")
    C72 = Chord("C", ["7"], 9, "C")
    F_end = Chord("F", None, 10, "F")

    addHarmony(F, "I")
    addHarmony(A7, "V7/vi")
    addHarmony(dmin, "vi")
    addHarmony(F_C, "I64")
    addHarmony(C7, "V7")
    addHarmony(dmin2, "vi")
    addHarmony(F_C2, "I64")
    addHarmony(Bb, "IV")
    addHarmony(gmin7, "ii65")
    addHarmony(C72, "V7")
    addHarmony(F_end, "I")
    addHarmonyRules()
    run_test(harm)


def test3(harm):
    addHarmony(Chord("F", None, 0, "F"), "I")
    addHarmony(Chord("A", ["7"], 1, "G"), "V42/vi")
    addHarmony(Chord("D", ["min", "7"], 2, "F"), "vi65")
    addHarmony(Chord("C", ["7"], 3, "E"), "V65")
    addHarmony(Chord("F", None, 4, "F"), "I")
    addHarmonyRules()
    run_test(harm)

def test4(harm):
    # D: ii6, V, I, V42/IV, IV6, iv6, V64, V7, I
    addHarmony(Chord("E", ["min"], 0, "G"), "ii6")
    addHarmony(Chord("A", None, 1, "A"), "V")
    addHarmony(Chord("D", None, 2, "D"), "I")
    addHarmony(Chord("D", ["7"], 3, "C"), "V42/IV")
    addHarmony(Chord("G", None, 4, "B"), "IV6")
    addHarmony(Chord("G", ["min"], 5, "Bb"), "iv6")
    addHarmony(Chord("D", None, 6, "A"), "I64")
    addHarmony(Chord("A", ["7"], 7, "A"), "V7")
    addHarmony(Chord("D", None, 8, "D"), "I")
    addHarmonyRules()
    run_test(harm)


# Exercise 1_cadences.1b
# From San Francisco Conservatory of Music Figured Harmony Exercises
def test5(harm):
    addHarmony(Chord("C", None, 0, "C"), "I")
    addHarmony(Chord("G", None, 1, "G"), "V")
    addHarmony(Chord("A", ["min"], 2, "A"), "vi")
    addHarmony(Chord("E", ["min"], 3, "E"), "iii")
    addHarmony(Chord("F", None, 4, "F"), "IV")
    addHarmony(Chord("C", None, 5, "C"), "I")
    addHarmony(Chord("D", ["min"], 6, "D"), "ii")
    addHarmony(Chord("G", None, 7, "G"), "V")
    addHarmony(Chord("C", None, 8, "C"), "I")
    addHarmonyRules()
    run_test(harm)

# Db: I V42/IV IV6 I64 V7 vi V42/V V6 I V64 I6 V64 I
def test6(harm):
    addHarmony(Chord("Db", None, 0, "Db"), "I")
    addHarmony(Chord("Db", ["7"], 1, "Cb"), "V42/IV")
    addHarmony(Chord("Gb", None, 2, "Bb"), "IV6")
    addHarmony(Chord("Db", None, 3, "Ab"), "I64")
    addHarmony(Chord("Ab", ["7"], 4, "Ab"), "V7")
    addHarmony(Chord("Bb", ["min"], 5, "Bb"), "vi")
    addHarmony(Chord("Eb", ["7"], 6, "Db"), "V42/V")
    addHarmony(Chord("Ab", None, 7, "C"), "V6")
    addHarmony(Chord("Db", None, 8, "Db"), "I")
    addHarmony(Chord("Ab", None, 9, "Eb"), "V64")
    addHarmony(Chord("Db", None, 10, "F"), "I6")
    addHarmony(Chord("Ab", None, 11, "Eb"), "V64")
    addHarmony(Chord("Db", None, 12, "Db"), "I")
    addHarmonyRules()
    run_test(harm)

# Db: I V42/IV IV6
def test7(harm):
    addHarmony(Chord("Db", None, 0, "Db"), "I")
    addHarmony(Chord("Db", ["7"], 1, "Cb"), "V42/IV")
    addHarmony(Chord("Gb", None, 2, "Bb"), "IV6")
    addHarmonyRules()
    run_test(harm)

# A: I vi V I
# Note: This version leaves the bass free, but specifies the soprano voice
def test8(harm):
    addHarmony(Chord("A", None, 0), "I")
    addHarmony(Chord("F#", ["min"], 1), "vi")
    addHarmony(Chord("E", None, 2), "V")
    addHarmony(Chord("A", None, 3), "I")
    addHarmonyRules()
    A5 = Core_Tree.Note.pitchToNum_absolute("A5")
    soprano_notes = [A5 + 4, A5, A5 + 2, A5]
    specify_voice(harm, "s", soprano_notes)
    run_test(harm)


# Takes a LOOONG time, even though there aren't that many solutions. Interesting.
def test9(harm):
    for i in range(8):
        addHarmony(Chord("G", None, i), "I")
    addHarmonyRules()
    run_test(harm)

def test9_stricter(harm):
    for i in range(5):
        addHarmony(Chord("G", None, i, "G"), "I")
    addHarmonyRules()
    run_test(harm)

def test10(harm):
    counter = 0
    for i in range(100):
        addHarmony(Chord("A", ["min"], counter), "ii")
        addHarmony(Chord("D", ["7"], counter + 1), "V7")
        addHarmony(Chord("G", None, counter + 2), "I")
        counter += 3
    addHarmonyRules()
    run_test(harm)

def test10_n(harm, n):
    counter = 0
    for i in range(n):
        addHarmony(Chord("A", ["min"], counter), "ii")
        addHarmony(Chord("D", ["7"], counter + 1), "V7")
        addHarmony(Chord("G", None, counter + 2), "I")
        counter += 3
    addHarmonyRules()
    run_test(harm)

def test10_n_stricter(harm, n):
    counter = 0
    for i in range(n):
        addHarmony(Chord("A", ["min"], counter, "C"), "ii")
        addHarmony(Chord("D", ["7"], counter + 1, "D"), "V7")
        addHarmony(Chord("G", None, counter + 2, "G"), "I")
        counter += 3
    addHarmonyRules()
    run_test(harm)

def test10_suite(harm):
    for i in range(1, 20):
        time1 = time.time()
        print "======== Running iteration i =", i
        test10_n_stricter(Core_Tree.constraint_unmodified.Problem(), i)
        print "TIME required to solve iteration", i, "was: ", time.time() - time1

def test10_stricter(harm):
    counter = 0
    for i in range(2):
        addHarmony(Chord("A", ["min"], counter, "C"), "ii")
        addHarmony(Chord("D", ["7"], counter + 1, "D"), "V7")
        addHarmony(Chord("G", None, counter + 2, "G"), "I")
        counter += 3
    addHarmonyRules()
    run_test(harm)

def t1(harm):
    addHarmony(Chord("D", ["min"], 0, "F"), "ii6")
    addHarmony(Chord("G", ["7"], 1, "G"), "V")
    addHarmonyRules()
    run_test(harm)

def _convertToShowFormat(dict):
    result = []
    for key in dict.keys():
        for var in key:
            result.append( (var, dict[key][var]) )
    return result

def run_test(harm):
    #if Core_Tree.config.debug == 1:
    #  Core_Tree.harmony_solver_tree.solveProblem_debug(harm)
    #else:
    #  Core_Tree.harmony_solver_tree.solveProblem(harm)
    iter = Core_Tree.harmony_solver_tree.solve(Core_Tree.init_problem.subproblems)
    solution = iter.next()
    number_solutions = 0
    for sol in iter:
        number_solutions += 1
        print number_solutions
        converted = _convertToShowFormat(sol)
        converted.sort(lambda a, b : myComparator(a[0], b[0]))
    print "== Total number solutions: ", number_solutions

    print solution
    if Core_Tree.config.debugging_options["show_results"] == 1:
        converted = _convertToShowFormat(solution)
        converted.sort(lambda a, b : myComparator(a[0], b[0]))
