'''
Created on Jan 4, 2010

@author: Sforzando
'''
from Tkinter import *
import tkFont
import tkSimpleDialog
import tkMessageBox
import gui.config
import core.Note

from util.constants import *

class SolverFrameAux(Frame):
  
  def init_frame(self, solverFrame):
    gui.config.solver_frame_aux = self
    self.solverFrame = solverFrame
    self.harmonySolver = solverFrame.harmonySolver
    
    my_font = tkFont.Font(size=11, weight="bold", family="Verdana")
    
    label = Label(self, text="Specify the problem...", font=my_font)
    label.grid(row=0, column=0)
    
    add_chord = Button(self, text="Add Chord", width=14, height=2, command=self.add_chord_routine)
    add_chord.grid(row=1, column=0)
    
    remove_chord = Button(self, text="Remove Chord", width=14, height=2, command=self.remove_chord_routine)
    remove_chord.grid(row=2, column=0)
    
    remove_all_chords = Button(self, text="Remove ALL Chords!", width=17, height=2, command=self.remove_all_routine)
    remove_all_chords.grid(row=3, column=0)
  
  """
  This method will add variables/domains to the CSP.
    1.) Create a Chord instance at time t
    2.) Associate a harmonic-function to the Chord instance
        (i.e "C Major" -> "I", or "G7" -> "V7")
  """
  def add_chord_routine(self):
    chord_dialog = AddChordDialog(self, self.harmonySolver)

  def remove_chord_routine(self):
    remove_chord_dialog = RemoveChordDialog(self, self.harmonySolver)
  
  def remove_all_routine(self):
    for t in self.harmonySolver.chords.get_times():
      self._remove_chord_label(t)       # Updates GUI
      self.harmonySolver.removeChord(t)   # Updates HarmonySolver Instance
      self.harmonySolver.removeHarmony(t) # ''
    """ Update gui.config.last_time """
    gui.config.last_time = 0
  
  def _remove_chord_label(self, time):
    self.solverFrame.staff.remove_chord_label(time)
    
class AddChordDialog(tkSimpleDialog.Dialog):
  chord_type = None
  seventh_type = None
  
  def __init__(self, parent, harmonySolver):
    self.harmonySolver = harmonySolver
    tkSimpleDialog.Dialog.__init__(self, parent)
  
  def _open_modifier_window(self):
    mod_dialog = AddModifierDialog(self)
    chord_type = mod_dialog.chord_type.get()
    seventh_type = mod_dialog.seventh_type.get()
    self.e3.delete(0, END)
    if (seventh_type == "None"):
      self.e3.insert(0, chord_type)
    else:
      self.e3.insert(0, chord_type+", "+seventh_type)
  
  def body(self, master):
    Label(master, text="Time: (i.e 0, 1, 2, ...)").grid(row=0)
    Label(master, text="Chord Root: (i.e C, Bb...)").grid(row=1)
    Label(master, text="Modifiers:").grid(row=2)
    Label(master, text="Harmonic Function: (i.e ii, V7/IV, etc...)").grid(row=3)
    
    self.e1 = Entry(master)
    self.e1.insert(0, str(gui.config.last_time))  # Default value
    self.e2 = Entry(master)
    self.e3 = Entry(master)
    self.add_mod_button = Button(master, text="Insert Modifier...", command=self._open_modifier_window)
    self.e4 = Entry(master)
    self.add_function_button = Button(master, text="Insert Function...", command=self._open_function_window)
    
    self.e1.grid(row=0, column=1)
    self.e2.grid(row=1, column=1)
    self.e3.grid(row=2, column=1)
    self.add_mod_button.grid(row=2, column=2)
    self.e4.grid(row=3, column=1)
    self.add_function_button.grid(row=3, column=2)
    return self.e2 # initial focus
  
  def _open_function_window(self):
    funct_dialog = AddFunctionDialog(self)
    self.e4.delete(0, END)
    self.e4.insert(0, funct_dialog.function)
    
  def apply(self):
    time = int(self.e1.get())
    root = self.e2.get()
    modifiers = self.e3.get()
    if (modifiers != None) and (modifiers != ''):
      modifiers = modifiers.split(", ")
    else:
      if (self.chord_type == None) and (self.seventh_type == None):
        modifiers = None
      else:
        ### Get data from add_modifier_window
        modifiers = self._clean_modifiers( [ self.chord_type , self.seventh_type ] )
    
    function = self.e4.get()
    chord = core.Note.Chord(root, modifiers, time)
    self.harmonySolver.addChord(chord, time)
    self.harmonySolver.addHarmony(function, time)
    """
    Now to reflect the new Chord on the GUI...
    """
    canvas = self.master.solverFrame.staff
    canvas.add_chord_label(chord, time)
    """ Update gui.config.last_time """
    gui.config.last_time = time + 1

  def _clean_modifiers(self, modifiers):
    for modifier in modifiers:
      if (modifier == "None") or (modifier == ''):
        modifiers.remove(modifier)
    return modifiers
  def validate(self):
    time = self.e1.get()
    root = self.e2.get()
    modifiers = self.e3.get()
    harmony = self.e4.get()
    try:
      time = int(time)
    except ValueError:
      tkMessageBox.showwarning("Invalid input.", \
                               "Please check your time input and try again.")
      return 0
    if time in self.harmonySolver.chords.get_times():
      tkMessageBox.showwarning("Add Chord Error.", "Warning - you're trying to add a chord to an already " +\
                               "occupied space! Remove it first before adding to it.")
      return 0
    if (len(root) > 2) or (root == '') or (harmony == ''):
      tkMessageBox.showwarning("Error.", "Warning - please recheck your inputs.")
      return 0
    if (root[0] not in ('A','B','C','D','E','F','G')) and (root[0] not in ('a','b','c','d','e','f','g')):
      tkMessageBox.showwarning("Error.", "Warning - please recheck your root input.")
      return 0
    if (len(root) == 2) and (root[1] not in ("#", "b")):
      tkMessageBox.showwarning("Error.", "Warning - please recheck your root input.")
      return 0
    return 1
    
class RemoveChordDialog(tkSimpleDialog.Dialog):
  
  def __init__(self, parent, harmonySolver):
    self.harmonySolver = harmonySolver
    tkSimpleDialog.Dialog.__init__(self, parent)
  
  def body(self, master):
    Label(master, text="Remove chord at time:").grid(row=0)  
    self.e1 = Entry(master)
    self.e1.grid(row=0, column=1)
    return self.e1 # initial focus

  def apply(self):
    time = int(self.e1.get())
    self.harmonySolver.removeChord(time)
    self.harmonySolver.removeHarmony(time)
    """ Now to reflect the change on the GUI """
    self.master.solverFrame.staff.remove_chord_label(time)
    """ Update gui.config.last_time """
    gui.config.last_time = time
        
  def validate(self):
    time = self.e1.get()
    try:
      time = int(time)
    except ValueError:
      tkMessageBox.showwarning("Invalid input.", \
                               "Please check your input and try again.")
      return 0
    if time not in self.harmonySolver.chords.get_times():
      tkMessageBox.showwarning("No chord at specified time found.",\
                         "Hm - you tried to delete a chord that doesn't " + \
                         "exist yet. Please try again?" )
      return 0
    return 1
    


"""
Types of modifiers:
  1.) Major/Minor/Diminished
  2.) Seventh-modifiers
      - maj7
      - min7
      - 7
"""
  
class AddModifierDialog(tkSimpleDialog.Dialog):
  chord_type = None # i.e major/minor/dim?
  seventh_type = None # i.e maj7/min7/7/None?
  
  def body(self, master):
    Label(master, text="Please select a modifier!").grid(row=0)
    width = 3
    self.chord_type = StringVar()
    self.seventh_type = StringVar()
    
    """ Major/Minor/Diminished group """
    self.e1 = Radiobutton(master, text="Major", variable=self.chord_type, value="Maj", indicatoron=0, width=15)
    self.e2 = Radiobutton(master, text="minor", variable=self.chord_type, value="min", indicatoron=0, width=15)
    self.e3 = Radiobutton(master, text="dim", variable=self.chord_type, value="dim", indicatoron=0, width=15)
    
    """ Seventh Type group """
    Label(master, text="Select the appropriate seventh modifier").grid(row=4)
    
    self.e4 = Radiobutton(master, text="None", variable=self.seventh_type, value="None", indicatoron=0, width=15)
    self.e5 = Radiobutton(master, text="maj7", variable=self.seventh_type, value="maj7", indicatoron=0, width=15)
    self.e6 = Radiobutton(master, text="7", variable=self.seventh_type, value="7", indicatoron=0, width=15)
    
    self.e1.grid(row=1, column=0)
    self.e2.grid(row=2, column=0)
    self.e3.grid(row=3, column=0)
    self.e4.grid(row=5, column=0)
    self.e5.grid(row=6, column=0)
    self.e6.grid(row=7, column=0)
    return self.e1 # initial focus

  def apply(self):
    if self.seventh_type.get() == '':
      self.seventh_type.set("None")
    if self.chord_type.get() == '':
      self.chord_type.set("Maj")
    pass
      
  def validate(self):
    chord_type = self.chord_type.get()
    seventh_type = self.seventh_type.get()
    return 1

class AddFunctionDialog(tkSimpleDialog.Dialog):
  
  def body(self, master):
    self.function = StringVar()
    
    self.tonic = Radiobutton(master, text="Tonic", variable=self.function, value=TONIC, indicatoron=0, width=15)
    self.predominant = Radiobutton(master, text="Predominant", variable=self.function, value=PREDOMINANT, indicatoron=0, width=15)
    self.dominant = Radiobutton(master, text="Dominant", variable=self.function, value=DOMINANT, indicator=0, width=15)
    
    self.tonic.grid(row=0, column=0)
    self.predominant.grid(row=1, column=0)
    self.dominant.grid(row=2, column=0)
    
  def apply(self):
    self.function = self.function.get()
  def validate(self):
    return 1