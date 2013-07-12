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
import sys

from core.Note import Chord
from core.solver import addHarmony, addHarmonyRules, solveProblem, specify_voice
import core.config

# Test 1: ii6 V7 I
def simpleTest(harm):
  dmin = Chord("D", ["min"], 0, "F")
  G = Chord("G", ["7"], 1, "G")
  C = Chord("C", None, 2, "C")  
  addHarmony(harm, dmin, "ii6")
  addHarmony(harm, G, "V7")
  addHarmony(harm, C, "I")          
  addHarmonyRules(harm)
  run_test(harm)
  
# Test 2: iii V43/ii ii V43 I  
def sequenceTest(harm):
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
  run_test(harm)



def simplestTest(harm):
  G7 = Chord("G", ["7"], 0, "G")
  C = Chord("C", None, 1, "C")
  addHarmony(harm, G7, "V7")
  addHarmony(harm, C, "I")
  addHarmonyRules(harm)
  run_test(harm)

def oneTest(harm):
  C = Chord("C", None, 0)
  addHarmony(harm, C, "I")
  addHarmonyRules(harm)
  run_test(harm)

def twoTest(harm):
  addHarmony(harm, Chord("C", None, 0), "I")
  addHarmony(harm, Chord("G", None, 1), "V")
  addHarmonyRules(harm)
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
  
  addHarmony(harm, F, "I")
  addHarmony(harm, A7, "V7/vi")
  addHarmony(harm, dmin, "vi")
  addHarmony(harm, F_C, "I64")
  addHarmony(harm, C7, "V7")
  addHarmony(harm, dmin2, "vi")
  addHarmony(harm, F_C2, "I64")
  addHarmony(harm, Bb, "IV")
  addHarmony(harm, gmin7, "ii65")
  addHarmony(harm, C72, "V7")
  addHarmony(harm, F_end, "I")
  addHarmonyRules(harm)
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
  
  addHarmony(harm, F, "I")
  addHarmony(harm, A7, "V7/vi")
  addHarmony(harm, dmin, "vi")
  addHarmony(harm, F_C, "I64")
  addHarmony(harm, C7, "V7")
  addHarmony(harm, dmin2, "vi")
  addHarmony(harm, F_C2, "I64")
  addHarmony(harm, Bb, "IV")
  addHarmony(harm, gmin7, "ii65")
  addHarmony(harm, C72, "V7")
  addHarmony(harm, F_end, "I")
  addHarmonyRules(harm)
  run_test(harm)


def test3(harm):
  addHarmony(harm, Chord("F", None, 0, "F"), "I")
  addHarmony(harm, Chord("A", ["7"], 1, "G"), "V42/vi")
  addHarmony(harm, Chord("D", ["min", "7"], 2, "F"), "vi65")
  addHarmony(harm, Chord("C", ["7"], 3, "E"), "V65")
  addHarmony(harm, Chord("F", None, 4, "F"), "I")
  addHarmonyRules(harm)
  run_test(harm)

def test4(harm):
  # D: ii6, V, I, V42/IV, IV6, iv6, V64, V7, I
  addHarmony(harm, Chord("E", ["min"], 0, "G"), "ii6")
  addHarmony(harm, Chord("A", None, 1, "A"), "V")
  addHarmony(harm, Chord("D", None, 2, "D"), "I")
  addHarmony(harm, Chord("D", ["7"], 3, "C"), "V42/IV")
  addHarmony(harm, Chord("G", None, 4, "B"), "IV6")
  addHarmony(harm, Chord("G", ["min"], 5, "Bb"), "iv6")
  addHarmony(harm, Chord("D", None, 6, "A"), "I64")
  addHarmony(harm, Chord("A", ["7"], 7, "A"), "V7")
  addHarmony(harm, Chord("D", None, 8, "D"), "I")
  addHarmonyRules(harm)
  run_test(harm)


# Exercise 1_cadences.1b
# From San Francisco Conservatory of Music Figured Harmony Exercises
def test5(harm):
  addHarmony(harm, Chord("C", None, 0, "C"), "I")
  addHarmony(harm, Chord("G", None, 1, "G"), "V")
  addHarmony(harm, Chord("A", ["min"], 2, "A"), "vi")
  addHarmony(harm, Chord("E", ["min"], 3, "E"), "iii")
  addHarmony(harm, Chord("F", None, 4, "F"), "IV")
  addHarmony(harm, Chord("C", None, 5, "C"), "I")
  addHarmony(harm, Chord("D", ["min"], 6, "D"), "ii")
  addHarmony(harm, Chord("G", None, 7, "G"), "V")
  addHarmony(harm, Chord("C", None, 8, "C"), "I")
  addHarmonyRules(harm)
  run_test(harm)

# Db: I V42/IV IV6 I64 V7 vi V42/V V6 I V64 I6 V64 I 
def test6(harm):
  addHarmony(harm, Chord("Db", None, 0, "Db"), "I")
  addHarmony(harm, Chord("Db", ["7"], 1, "Cb"), "V42/IV")
  addHarmony(harm, Chord("Gb", None, 2, "Bb"), "IV6")
  addHarmony(harm, Chord("Db", None, 3, "Ab"), "I64")
  addHarmony(harm, Chord("Ab", ["7"], 4, "Ab"), "V7")
  addHarmony(harm, Chord("Bb", ["min"], 5, "Bb"), "vi")
  addHarmony(harm, Chord("Eb", ["7"], 6, "Db"), "V42/V")
  addHarmony(harm, Chord("Ab", None, 7, "C"), "V6")
  addHarmony(harm, Chord("Db", None, 8, "Db"), "I")
  addHarmony(harm, Chord("Ab", None, 9, "Eb"), "V64")
  addHarmony(harm, Chord("Db", None, 10, "F"), "I6")
  addHarmony(harm, Chord("Ab", None, 11, "Eb"), "V64")
  addHarmony(harm, Chord("Db", None, 12, "Db"), "I")
  addHarmonyRules(harm)
  run_test(harm)

# Db: I V42/IV IV6 
def test7(harm):
  addHarmony(harm, Chord("Db", None, 0, "Db"), "I")
  addHarmony(harm, Chord("Db", ["7"], 1, "Cb"), "V42/IV")
  addHarmony(harm, Chord("Gb", None, 2, "Bb"), "IV6")
  addHarmonyRules(harm)
  run_test(harm)

# A: I vi V I
# Note: This version leaves the bass free, but specifies the soprano voice
def test8(harm):
  addHarmony(harm, Chord("A", None, 0), "I")
  addHarmony(harm, Chord("F#", ["min"], 1), "vi")
  addHarmony(harm, Chord("E", None, 2), "V")
  addHarmony(harm, Chord("A", None, 3), "I")
  addHarmonyRules(harm)
  A5 = core.Note.pitchToNum_absolute("A5")
  soprano_notes = [A5 + 4, A5, A5 + 2, A5]
  specify_voice(harm, "s", soprano_notes)
  run_test(harm)


# Takes a LOOONG time, even though there aren't that many solutions. Interesting.
def test9(harm):
  for i in range(8):
    addHarmony(harm, Chord("G", None, i), "I")
  addHarmonyRules(harm)
  run_test(harm)

def test9_stricter(harm):
  for i in range(5):
    addHarmony(harm, Chord("G", None, i, "G"), "I")
  addHarmonyRules(harm)
  run_test(harm)

def test10(harm):
  counter = 0
  for i in range(300):
    addHarmony(harm, Chord("A", ["min"], counter), "ii")
    addHarmony(harm, Chord("D", ["7"], counter + 1), "V7")
    addHarmony(harm, Chord("G", None, counter + 2), "I")
    counter += 3
  addHarmonyRules(harm)
  run_test(harm)

def test10_n(harm, n):
  counter = 0
  for i in range(n):
    addHarmony(harm, Chord("A", ["min"], counter), "ii")
    addHarmony(harm, Chord("D", ["7"], counter + 1), "V7")
    addHarmony(harm, Chord("G", None, counter + 2), "I")
    counter += 3
  addHarmonyRules(harm)
  run_test(harm)

def test10_n_stricter(harm, n):
  counter = 0
  for i in range(n):
    addHarmony(harm, Chord("A", ["min"], counter, "C"), "ii")
    addHarmony(harm, Chord("D", ["7"], counter + 1, "D"), "V7")
    addHarmony(harm, Chord("G", None, counter + 2, "G"), "I")
    counter += 3
  addHarmonyRules(harm)
  run_test(harm)

def test10_suite(harm):
  for i in range(1, 20):
    time1 = time.time()
    print "======== Running iteration i =", i
    test10_n_stricter(core.constraint.Problem(), i)
    print "TIME required to solve iteration", i, "was: ", time.time() - time1

def test10_stricter(harm):
  counter = 0
  for i in range(2):
    addHarmony(harm, Chord("A", ["min"], counter, "C"), "ii")
    addHarmony(harm, Chord("D", ["7"], counter + 1, "D"), "V7")
    addHarmony(harm, Chord("G", None, counter + 2, "G"), "I")
    counter += 3
  addHarmonyRules(harm)
  run_test(harm)

def t1(harm):
  addHarmony(harm, Chord("D", ["min"], 0, "F"), "ii6")
  addHarmonyRules(harm)
  run_test(harm)

def t2(harm):
  addHarmony(harm, Chord("G", ["7"], 0, "G"), "V")
  addHarmonyRules(harm)
  run_test(harm)

def run_test(harm):
  solveProblem(harm)

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
  arg_handle(sys.argv)
  problem = core.solver.createProblem()
  if core.config.test_name != None:
    print "====== Running Test: ", core.config.test_name
    exec(core.config.test_name + "(problem)")
  else:
    oneTest(problem)

