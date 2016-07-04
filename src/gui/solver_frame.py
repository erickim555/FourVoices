'''
Created on Jan 4, 2010

@author: Sforzando
'''
#from Tkinter import *
import pdb
from util.mtTkinter import *
import tkFont
import tkMessageBox
import tkSimpleDialog
import core.solver
import gui.config
import util.SolutionToMidi
import playback.playSolution
import util.constants
from Data_Structures.dataStructs import TimeList

class SolveThread(threading.Thread):

    def __init__ (self, harmonySolver, solverframe):
        threading.Thread.__init__(self)
        self.harmonySolver = harmonySolver
        self.problem = harmonySolver.problem
        self.solverframe = solverframe

    def run(self):
        solverframe = self.solverframe
        solverframe.haltButton.flash()
        solutions = self.harmonySolver.solveProblem()
        if solutions == None:
            tkMessageBox.showwarning("No solutions", \
                                     "The solver didn't find any solutions! Try rechecking your harmony \
                                     or make sure your specified lines aren't wrong.")
            solverframe.haltButton.config(state=DISABLED)
            return
        print "Number sol's: ", len(solutions)
        """
        Retrieve first solution from solutions and display it
        """
        firstSolution_tuple = solutions[0]
        firstSolution_grade, firstSolution = firstSolution_tuple
        solverframe.display_solution(firstSolution, firstSolution_grade)
        solverframe.openSolutionsResultWindow()
        solverframe.haltButton.config(state=DISABLED)

class SolverFrame(Frame):
    """ Keep a list of all solutions examined by the user """
    sol_index = 0
    staff = None
    harmonySolver = None
    solve_b = None
    reset_prob_b = None
    sol_control = None
    haltButton = None

    def init_frame(self, staff):
        self.staff = staff

        my_font = tkFont.Font(size=14, weight="bold", family="Times New Roman")
        label = Label(self, text="Solve Controls", font=my_font)
        label.pack(pady=10, anchor=CENTER)
        self.solve_b = Button(self, text="Solve...", width=12, height=2, command=self.solve)
        self.solve_b.pack(side=BOTTOM, anchor=CENTER)

        self.reset_prob_b = Button(self, text="Delete Everything!", width=14, height=2, command=self.reset_prob)
        self.reset_prob_b.pack(side=BOTTOM, anchor=CENTER)

        self.sol_control = Button(self, text="Solution Controls...", width=15, height=2, command=self.openSolutionsResultWindow)
        self.sol_control.pack(side=BOTTOM, anchor=CENTER)

        self.haltButton = Button(self, text="Interrupt Solver", width=15, height=2, command=self.haltSolver, state=DISABLED)
        self.haltButton.config(activebackground="BLACK", activeforeground="RED")
        self.haltButton.pack(side=BOTTOM, anchor=CENTER)

        self.harmonySolver = core.solver.HarmonySolver()

    def openSolutionsResultWindow(self):
        result_window = SolutionsResultWindow(self)
        result_window.init_self()

    def haltSolver(self):
        self.harmonySolver.halt()

    def solve(self):
        self.haltButton.config(state=NORMAL)
        self.sol_index = 0
        num_time_steps = len(self.harmonySolver.chords)
        """
        Check to see if user actually put anything to be solved
        """
        if num_time_steps == 0:
            tkMessageBox.showwarning("No problem specified",\
                                     "You didn't add any chords! Please do so, and I'll stop yelling.")
            return None
        harmonySolver = self.harmonySolver
        #harmonySolver.problem._constraints = []     # Must reset the constraints, or else I'll have duplicate constraints when I call addHarmonyRules()
        # Hm - it doesn't seem to be duplicating the constraints.
        harmonySolver.addHarmonyRules()
        """ Add any specified lines (if the user did so) """
        specified_notes = self.staff.notes
        for i in ("soprano" , "alto" , "tenor" , "bass"):
            harmonySolver.specify_voice(i, specified_notes[i])
        solveThread = SolveThread(harmonySolver, self)
        solveThread.start()

    def reset_prob(self):
        gui.config.solver_frame_aux.remove_all_routine()  # Remove all chord labels
        gui.config.singer_frame.reset_staff()             # Remove all noteheads
        self.harmonySolver.removeAll()                    # Reset the Harmony Solver
        gui.config.last_time = 0
        if (len(self.harmonySolver.chords) != 0) and len(self.harmonySolver.harmonies) != 0:
            print "=== ERROR in solver_frame.py : reset_prob() didn't quite work right, as "+\
                  "harmonySolver.chords or harmonySolver.harmonies are NOT empty."
            exit(1)

# Unused?
    def display_solutions(self, solutions):
        self.staff.draw_solutions(solutions)

    def display_solution(self, solution, grade):
        self.staff.draw_solution(solution)


class SolutionsResultWindow(Toplevel):
    solverFrame = None

    def init_self(self):
        self.solverFrame = self.master

        my_font = tkFont.Font(size=11)
        label = Label(self, text="Browse solutions...", font=my_font)
        label.pack(pady=15, padx=20)
        self.nextButton = Button(self, text="Next solution...", command=self.next_solution)
        self.nextButton.pack(pady=2)
        self.prevButton = Button(self, text="Previous solution...", command=self.prev_solution)
        self.prevButton.pack(pady=2)
        self.playButton = Button(self, text="Play solution", command=self.playSolution)
        self.playButton.pack(pady=2)

        label2 = Label(self, text="Solution statistics", font=my_font)
        label2.pack(pady=5, padx=20)
        numSolutions_label = Label(self, text="Number of solutions:", font=my_font)
        numSolutions_label.pack(pady=5, padx=20)


    def next_solution(self):
        harmonySolver = self.solverFrame.harmonySolver
        if len(harmonySolver.solutions) == 0:
            return
        self.solverFrame.sol_index += 1
        try:
            next_sol_tuple = harmonySolver.solutions[self.solverFrame.sol_index]
        except IndexError:
            print "==== Looping in the solution history"
            self.solverFrame.sol_index = 0
            next_sol_tuple = harmonySolver.solutions[self.solverFrame.sol_index]
        next_grade = next_sol_tuple[0]
        next_sol = next_sol_tuple[1]
        self.solverFrame.display_solution(next_sol, next_grade)

    def prev_solution(self):
        harmonySolver = self.solverFrame.harmonySolver
        if len(harmonySolver.solutions) == 0:
            return
        self.solverFrame.sol_index -= 1
        try:
            next_sol_tuple = harmonySolver.solutions[self.solverFrame.sol_index]
        except IndexError:
            print "==== Looping in the solutions (from prev_solution())"
            self.solverFrame.sol_index = -1
            next_sol_tuple = harmonySolver.solutions[self.solverFrame.sol_index]
        next_grade = next_sol_tuple[0]
        next_sol = next_sol_tuple[1]
        self.solverFrame.display_solution(next_sol, next_grade)

    def playSolution(self):
        harmonySolver = self.solverFrame.harmonySolver
        if len(harmonySolver.solutions) == 0:
            return
        grade, solution = harmonySolver.solutions[self.solverFrame.sol_index]
        # solution is a list: list notes
        #   where notes[i] is: ["<singer><time>", int pitchnum]
        display_solution(solution)
        status = playback.playSolution.playSolution(solution)
        #status = util.SolutionToMidi.playSolution(solution)
        if not status:
            tkMessageBox.showwarning("MIDI playback not supported.",
                                     "MIDI playback not supported. Please check prerequisites.")

def display_solution(sol):
    """
    INPUT:
      list sol:
        sol[i] -> ["<singer><time>", int pitchnum]
    """
    if not type(sol) is dict:
        # First convert to dict repr
        soldict = {}
        for (k,v) in sol:
            dictkey = k[0] + "_" + k[1:]
            soldict[dictkey] = v
    else:
        soldict = dict
    # Output in nice way
    T = len(sol) / 4
    for t in xrange(T):
        print "[t={0}/{1}]".format(t+1, T)
        for singer in util.constants.VOICE_PREFIXES:
            k = core.solver.make_var(singer, t)
            num = soldict[k]
            print "  {0}: {1} ({2})".format(singer, core.Note.numToPitch_absolute(num), num)

