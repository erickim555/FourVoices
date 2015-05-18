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
import cProfile
import sys
import time
import Core_Tree.constraint
import Core_Tree.constraint_unmodified
from Note import *
from Core_Tree.harmony_rules import *
import Examples_Tree.harmonytests
from Grader.grader import grade, grade_debug
import Core_Tree.config
import Core_Tree.tree_decomp_solver
from mega_constraints import *

###
# First Parallel Fifth caught! 2:39 AM, 11-23-09 :)

mus_range = range(0, 87)
soprano_range = range(51, 66)     # C4 -> C5
alto_range = range(46, 68)        # G3 -> F5
tenor_range =  range(39, 51)      # C3 -> A4
bass_range = range(32, 55)        # F2 -> E4

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

# Adds a mega-constraint to two mega-variables, storing the result in a dict
def addMegaConstraint(var1, var2, constraint, dict):
    var1 = tuple(var1)
    var2 = tuple(var2)
    if dict.has_key( (var1, var2) ):
        list = dict[ (var1, var2) ]
        list.append(constraint)
    else:
        dict[ (var1, var2) ] = [constraint,]

# mega_constraints := a dict mapping mega-variables to mega-constraints
def getMegaConstraints(subproblems_list):
    mega_constraints = {}
    for t in range(len(subproblems_list) - 1):
        var1 = subproblems_list[t][0].keys()
        var2 = subproblems_list[t+1][0].keys()
        var1.sort(lambda x, y : myComparator(x, y))
        var2.sort(lambda x, y : myComparator(x, y))
        addMegaConstraint(var1, var2, lambda a, b : noParallelFifth_mega(a, b), mega_constraints)
        addMegaConstraint(var1, var2, lambda a, b: noParallelOctave_mega(a, b), mega_constraints)
        addMegaConstraint(var1, var2, lambda a, b : biggestLeap_mega(a, b), mega_constraints)
        if Core_Tree.config.chords[t].getSeventh__() != None:
            addMegaConstraint(var1, var2, handleSevenths_mega(Core_Tree.config.chords[t]), mega_constraints)
        if Core_Tree.config.harmonies[t][0] == "V":
            addMegaConstraint(var1, var2, handleLeadingTone_mega(Core_Tree.config.chords[t]), mega_constraints)
        addMegaConstraint(var1, var2, lambda a, b : handleHidden_outer_mega(a, b), mega_constraints)
        addMegaConstraint(var1, var2, lambda a, b : handle_temporal_overlap_mega(a, b), mega_constraints)
    return mega_constraints

# Main interface to the tree_decomposed CSP solver.
# Each subproblem is the < s, a, t, b > at each time step.
# So, the mega-constraints are the constraints in between each chord.
def solve(subproblems_list):
    subproblems = []
    for tuple in subproblems_list:
        var_dict = tuple[0]
        const_dict = tuple[1]
        subproblem = Core_Tree.constraint_unmodified.Problem()
        for var in var_dict.keys():
            subproblem.addVariable(var, var_dict[var])
        for var in const_dict.keys():
            for constraint in const_dict[var]:
                subproblem.addConstraint(constraint, var)
        subproblems.append(subproblem)
    mega_constraints = getMegaConstraints(subproblems_list)
    return Core_Tree.tree_decomp_solver.solve_iter(subproblems, mega_constraints)

def profile_test(harm):
    cProfile.run('examples.harmonytests.test4(harm)')

def arg_handle(argv):
    for arg in argv:
        if (len(arg) > 5) and (arg[0:5] == "test="):
            Core_Tree.config.test_name = arg[5:]
        if (len(arg) > 2) and (arg[0:2] == "n="):
            Core_Tree.config.num_solutions = int(arg[2:])
        if (arg == "-d") or (arg == "-debug") : Core_Tree.config.debug = 1
        if Core_Tree.config.debugging_options.has_key(arg):
            Core_Tree.config.debugging_options[arg] = 1

if __name__ == '__main__':
    time1 = time.time()
    arg_handle(sys.argv)
    if Core_Tree.config.debugging_options["old_constraint"] == 1:
        harm = Core_Tree.constraint_unmodified.Problem()
    else:
        harm = Core_Tree.constraint.Problem()
    if Core_Tree.config.test_name != None:
        print "====== Running Test: ", Core_Tree.config.test_name
        exec("Examples_Tree.harmonytests." + Core_Tree.config.test_name + "(harm)")
    else:
        Examples_Tree.harmonytests.test4(harm)
    print "Time (in seconds) to perform test: ", time.time() - time1
