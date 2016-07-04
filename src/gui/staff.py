'''
Created on Jan 4, 2010

@author: Sforzando
'''

import os, pdb, string
from Tkinter import *
import tkMessageBox
import gui.config
import core.Note
from Data_Structures.dataStructs import *

"""
Only deals with Visual aspects
"""

class Staff(Canvas):
    """
    Visual-related Parameters
    """
    first_note_x = 120
    note_step_x = 60

    ledger_gap = 20
    ledger_len = 800

    treble_clef_start_x = 40
    treble_clef_start_y = 60 # Location of F5

    bass_clef_start_x = 40
    bass_clef_start_y = treble_clef_start_y + ( 6 * ledger_gap )

    first_delimiter_x = 150
    first_delimiter_y = treble_clef_start_y - ledger_gap
    delimiter_step_x = 60

    first_text_x = first_note_x
    first_text_y = 285

    """
    Music-related Parameters
    """
    solutions = []
    """
    notes is a data structure used by the solver in order
    to specify a voice's line prior to harmonizing it.
    [ <soprano> , <alto> , <tenor> , <bass> ]
    """
    notes = { "soprano" : TimeList() , "alto" : TimeList() , "tenor" : TimeList() , "bass" : TimeList() }
    """
    singer_history is a variable used by the "Undo" feature
    in order to determine which singer was last updated.
    """
    singer_history = []
    images = ImageStructure()
    times = {"soprano" : 0 , "alto" : 0 , "tenor" : 0 , "bass" : 0}
    chord_label_ids = TimeList()

    ### Fields that govern which voice is selected at which time
    selectedSinger = "soprano"

    def init(self):
        self.show_staves()
        self.draw_aux_ledgers()
        self.bind("<Button-1>", self.add_note)
        self.bind("<Button-3>", self.remove_note)
        self.bind("<Shift-Button-1>", self.remove_note)
        self.add_delimiters()
        self.images.append(self._get_cursor_gif())

    def show_staves(self):
        self._draw_treble()
        self._draw_bass()

    def add_delimiters(self):
        initial_x = self.first_delimiter_x
        initial_y = self.first_delimiter_y
        step_x = self.delimiter_step_x
        for i in range(10):
            self.create_line(initial_x + ( i * step_x ), initial_y, \
                             initial_x + ( i * step_x ), initial_y + 220, \
                             fill="red", width=1.8 )

    def add_note(self, event):
        x = event.x
        y = event.y
        note_head = None
        accidental = None
        singer = self.selectedSinger
        self.singer_history.append(singer)
        note_head = self._get_notehead_gif(singer)
        new_x, new_y = self._interpret_mouse(x, y)

        """
        actually, this is more complicated - i need to
        generalize the step distances, it's not just by
        2's (whole steps vs. half steps, accidentals, etc)
        """
        time = self._calc_time(new_x)
        note_value = self._translate_to_val(new_y)
        print "note_value: ", note_value, core.Note.numToPitch_absolute(note_value)
        if self.notes[singer].get(time) == None:    # If there isn't a note in the spot time
            self.notes[singer].add( time, note_value )
            self.create_image(new_x, new_y, image=note_head)
            """
            Add the accidental to the staff if necessary
            """
            if ( gui.config.accidental != 0 ):
                accidental = self._get_accidental_gif(gui.config.accidental)
                self.create_image(new_x - 15, new_y, image=accidental)

            """
            Add the images to a data structure so that we don't 'lose'
            a reference to the image.
            """
            self.images[singer].add( time , ( note_head, accidental ) )
        else:
            """ We are replacing a note at the specified time with another note """
            self.images[singer].remove(time)
            self.notes[singer].remove(time)
            self.notes[singer].add( time, note_value )
            self.create_image(new_x, new_y, image=note_head)
            """
            Add the accidental to the staff if necessary
            """
            if ( gui.config.accidental != 0 ):
                accidental = self._get_accidental_gif(gui.config.accidental)
                self.create_image(new_x - 15, new_y, image=accidental)

            """
            Add the images to a data structure so that we don't 'lose'
            a reference to the image.
            """
            self.images[singer].add( time , ( note_head, accidental ) )

    def remove_note(self, event):
        x = event.x
        y = event.y
        singer = self.selectedSinger
        new_x, new_y = self._interpret_mouse(x, y)
        """
        actually, this is more complicated - i need to
        generalize the step distances, it's not just by
        2's (whole steps vs. half steps, accidentals, etc)
        """
        time = self._calc_time(new_x)
        self.images[singer].remove(time)
        self.notes[singer].remove(time)

    def _get_accidental_gif(self, val):
        curdir_compat = os.path.normpath(gui.config.home_dir)
        tag = "sharp"
        if val == -1:
            tag = "flat"
        img_path = os.path.normpath(curdir_compat + "/gui/images/" + tag + "_gif.gif")
        return PhotoImage(file=img_path)

    def _calc_time(self, x):
        range = self.delimiter_step_x
        time_step = ( (x - self.first_delimiter_x) / range ) + 1
        return time_step

    """
    This helper method takes the y-cord, step_offset from the GUI, and translates
    it to the note_value used by the solver.
    """
    def _translate_to_val(self, y):
        offset = y - 90   # offset from C5_y
        step_offset = offset / 10
        c_major_steps_upwards =   [2, 2, 1, 2, 2, 2, 1]
        c_major_steps_downwards = [1, 2, 2, 2, 1, 2, 2]
        note_val = 72 # C5
        for i in range( abs(step_offset) ):
            if step_offset < 0:
                note_val += c_major_steps_upwards[i%7]
            else:
                note_val -= c_major_steps_downwards[i%7]
        accidental = gui.config.accidental
        return (note_val + accidental)

    def _get_notehead_gif(self, singer):
        curdir_compat = os.path.normpath(gui.config.home_dir)
        color = gui.config.note_config[singer]["color"]
        stem_dir = gui.config.note_config[singer]["stem_dir"]
        img_path = os.path.normpath(curdir_compat + "/gui/images/note_head_gif_"+color+"_"+stem_dir+".gif")
        return PhotoImage(file=img_path)

    def _get_cursor_gif(self):
        curdir_compat = os.path.normpath(gui.config.home_dir)
        img_path = os.path.normpath(curdir_compat + "/gui/images/note_head_gif.gif")
        return PhotoImage(file=img_path)
    """
    This helper method takes the (x, y) coordinates of where
    the user clicked, and "interprets" it to be what note
    to add to the staff.
    There should definitely be "wiggle" room to add any note,
    which is why each note has a little "cloud" in which the user
    can click in order to add that note.

    Returns the "canonical" ( x , y ) coordinates of where to
    actually place the note, and it also adds that note to
    our solver-data-structure.
    """
    def _interpret_mouse(self, x, y):
        new_x = self._calc_x_coord(x)
        new_y = self._calc_y_coord(y)
        return ( new_x , new_y )

    def _calc_x_coord(self, mouse_x):
        range = self.delimiter_step_x
        cell_x = ( (mouse_x - self.first_delimiter_x) / range ) + 1
        return self.first_note_x + (cell_x * self.note_step_x)
    def _calc_y_coord(self, mouse_y):
        ones_digit = int(str(mouse_y)[-1])
        new_y = ( mouse_y / 10 ) * 10   # "pseudo-round", i.e 88 -> 80, 62 -> 60
        if ( ones_digit > 5 ):
            new_y += 10
        return new_y

    def _draw_treble(self):
        start_x = self.treble_clef_start_x
        start_y = self.treble_clef_start_y
        line_len = self.ledger_len
        spine_len = 4 * self.ledger_gap
        self.create_line(start_x, start_y, \
                         start_x, start_y + spine_len, \
                         fill="black", width=4)
        for i in range(5):
            self.create_line(start_x, start_y + (self.ledger_gap * i), \
                             start_x + line_len, start_y + ( self.ledger_gap * i ), \
                             fill="black", width=2.3)
        cur_dir_compat = os.path.normpath(gui.config.home_dir)
        img_path = os.path.normpath(cur_dir_compat + "/gui/images/treble-clef_gif_r.gif")

        treble_clef = PhotoImage(file=img_path)
        self.images.append(treble_clef)
        self.create_image(start_x + 30, start_y + 50, image=treble_clef)

    def _draw_bass(self):
        start_x = self.bass_clef_start_x
        start_y = self.bass_clef_start_y
        line_len = self.ledger_len
        spine_len = 4 * self.ledger_gap
        self.create_line(start_x, start_y, \
                         start_x, start_y + spine_len, \
                         fill="black", width=4)

        for i in range(5):
            self.create_line(start_x, start_y + (self.ledger_gap * i), \
                             start_x + line_len, start_y + ( self.ledger_gap * i ), \
                             fill="black", width=2.3)
        cur_dir_compat = os.path.normpath(gui.config.home_dir)
        img_path = os.path.normpath(cur_dir_compat + "/gui/images/bass-clef_r.gif")
        bass_clef = PhotoImage(file=img_path)
        self.images.append(bass_clef)
        self.create_image(start_x + 30, start_y + 30, image=bass_clef)

    def draw_aux_ledgers(self):
        start_x = self.treble_clef_start_x
        start_y = self.treble_clef_start_y - self.ledger_gap
        line_len = self.ledger_len
        #for i in (0, 6):
        for i in (6,):
            self.create_line(start_x, start_y + (self.ledger_gap * i), \
                           start_x + line_len, start_y + ( self.ledger_gap * i ), \
                           fill="black", width=1)

    """
    Adds a text-label to the bottom of the staff in order to reflect
    what chord is there.
    """
    def add_chord_label(self, chord, time):
        """ Optional error check - this should be taken care of in the validate() call of the add_chord dialogue box """
        if self._find_chord_label_id(time) != None:
            tkMessageBox.showwarning("Add Chord Error.", "Warning - you're trying to add a chord to an already " +\
                                     "occupied space! Remove it first before adding to it.")
            return
        else:
            textLabel = self._createTextLabel(chord)
            if chord.modifiers != None:
                for modifier in chord.modifiers:
                    textLabel = textLabel + modifier
            x = self.first_text_x + (time * 60)
            y = self.first_text_y
            """ tuple := (< time_id > , < chord_label_id > ) """
            time_label_id = self.create_text( x , y + 15, text=time)
            chord_label_id = self.create_text( x , y , text=textLabel)
            tuple = (time_label_id , chord_label_id)
            self.chord_label_ids.add(time, tuple)

    def _createTextLabel(self, chord):
        root = string.upper( chord.root )
        modifiers = chord.modifiers
        return chord.root

    """
    A helper method for add/remove_chord_label() that returns the element at time t, or None
    if it's not present.
    """
    def _find_chord_label_id(self, time):
        found = None
        for t in self.chord_label_ids.get_times():
            if t == time:
                found = self.chord_label_ids.get(t)
                break
        return found

    def remove_chord_label(self, time):
        """ Optional error check - this should be taken care of in the validate() call of the remove_chord dialogue box """
        found = self._find_chord_label_id(time)
        if found == None:
            tkMessageBox.showwarning("No chord at specified time found.",\
                                     "Hm - you tried to delete a chord that doesn't " + \
                                     "exist yet. Please try again?" )
            return
        else:
            self.chord_label_ids.remove(time)
            time_label_id = found[0]
            chord_label_id = found[1]
            self.delete(time_label_id)
            self.delete(chord_label_id)

    ### Unused...?
    def draw_solutions(self, solutions):
        self.solutions = [x for x in solutions]
        first_sol = self.solutions[0][1]
        length = len(first_sol) / 4
        for singer in ("s", "a", "t", "b"):
            for t in range(length):
                tag = singer+str(t)
                pitch = self._find_tuple(tag, first_sol)
                self.add_solution_note(singer, pitch, t)

    def draw_solution(self, solution):
        """ First clear the staff """
        self.reset_staff()

        length = len(solution) / 4
        for singer in ("s", "a", "t", "b"):
            for t in range(length):
                tag = singer+str(t)
                pitch = self._find_tuple(tag, solution)
                self.add_solution_note(singer, pitch, t)

    def _find_tuple(self, tag, list):
        for tuple in list:
            if tuple[0] == tag:
                return tuple[1]
        print "=== Error in Staff._find_tuple(): Couldn't \
              find the tuple. Hm."
        exit()

    def add_solution_note(self, singer, pitch, time):
        accidental = None
        """ We want to represent singer as (soprano,alto,tenor,bass), not (s,a,t,b) or (0,1,2,3)"""
        singer = self._convertToCanonical(singer)
        self.singer_history.append(singer)
        note_head = self._get_notehead_gif(singer)
        x, y = self._get_note_coords(pitch, time)
        if self.notes[singer].get(time) != pitch:
            #self.notes[singer].add(self.times[singer], pitch)
            self.notes[singer].add( time, pitch )
            self.create_image(x, y, image=note_head)
            """
            Add the accidental to the staff if necessary
            """
            if ( self._is_accidental(pitch) ):
                """ Another instance of assuming sharps below (self._get_accidental_gif(1)) """
                accidental = self._get_accidental_gif(1)
                self.create_image(x - 15, y, image=accidental)

            """
            Add the images to a data structure so that we don't 'lose'
            a reference to the image.
            """
            #self.images[singer].add(self.times[singer] , ( note_head, accidental ) )
            self.images[singer].add( time , ( note_head, accidental ) )
            #self.times[singer] += 1

    def _get_note_coords(self, pitchnum, time):
        """
        INPUT:
          int pitch:
          int time:
        """
        #pitchnum = core.Note.pitchToNum_absolute("B3")
        STEP = 10 # 10px is spacing between each note, ie C -> D
                  # 20px is spacing btwn each ledger line
        # self.treble_clef_start_y is location of C
        coord_C6 = self.treble_clef_start_y - (STEP*4) # The coords of C6
        pitch = core.Note.numToPitch_absolute(pitchnum)
        note,octave = core.Note.pitchInfo(pitch)
        dict_ = {"C": 0, "D": -STEP, "E": -STEP*2, "F": -STEP*3, "G": -STEP*4, "A": -STEP*5, "B": -STEP*6}
        coord_offset = dict_[note[0]] + ((6 - octave)*(STEP*7))
        ycoord = coord_C6 + coord_offset
        return (self.first_note_x + (time * self.note_step_x),
                ycoord )

    def _is_accidental(self, pitch):
        c_major = ["C", "D", "E", "F", "G", "A", "B"]
        c_major_nums = [core.Note.pitchToNum(x) for x in c_major]
        return (pitch % 12) not in c_major_nums

    def delete_last(self, singer):
        singer = self._convertToCanonical(singer)
        num_notes = 0
        for voice in ("soprano" , "alto" , "tenor" , "bass"):
            num_notes += len(self.images[voice].get_times())
        if ( num_notes > 0) :
            if len(self.notes[singer].get_times()) > 0:
                self.images[singer].pop()
                self.times[singer] -= 1
                self.notes[singer].pop()

    def undo(self):
        num_notes = 0
        for i in ("soprano" , "alto" , "tenor" , "bass"):
            num_notes += len(self.images[i].get_times())
        if ( num_notes > 0) :
            while(True):
                if len(self.singer_history) > 0:
                    singer = self.singer_history.pop()
                    if len(self.notes[singer].get_times()) > 0:
                        self.images[singer].pop()
                        self.times[singer] -= 1
                        self.notes[singer].pop()
                        return

    def reset_staff(self):
        for i in ("soprano", "alto", "tenor", "bass"):
            self.notes[i] = TimeList()
            self.images[i] = TimeList()
            self.times[i] = 0
            self.singer_history = []

    def selectSinger(self, singer):
        if (type(singer) == str):
            self.selectedSinger = singer.lower()
        if (type(singer) == int):
            try:
                singer = {0 : "soprano" , 1 : "alto" , 2 : "tenor" , 3 : "bass"}[singer]
                self.selectedSinger = singer
            except KeyError:
                print "Error in Staff.selectSinger(): argument was outside bounds of our dict"
                raise

    # Takes in singer, and converts it to something in ("soprano","alto","tenor","bass")
    # i.e, we don't want (0,1,2,3) or (s,a,t,b) representations floating around.
    def _convertToCanonical(self, singer):
        if type(singer) == int:
            singer = {0 : "soprano" , 1 : "alto", 2 : "tenor" , 3 : "bass"}[singer]
        if singer not in ("soprano" , "alto" , "tenor" , "bass"):
            try:
                singer = {"s" : "soprano" , "a" : "alto" , "t" : "tenor" , "b" : "bass"}[singer]
            except ValueError:
                raise ValueError , "ValueError : In Staff.convertToCanonical(), 'singer' was NOT a valid argument: %s" % singer
        return singer
