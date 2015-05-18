'''
Created on Jan 4, 2010

@author: Sforzando
'''

import os

from Tkinter import *
import tkFont
import gui.config
from Data_Structures.dataStructs import TimeList

class SingerFrame(Frame):
    v = None
    a = 0
    staff = None

    def set_voice(self):
        self.staff.selectSinger( self.v.get() )

    def set_accidental(self):
        gui.config.accidental = self.a.get()

    def init_frame(self, staff):
        self.staff = staff
        gui.config.singer_frame = self

        my_font = tkFont.Font(size=12, weight="bold", family="Helvetica")

        label = Label(self, text="Specify a line...", font=my_font)
        label.grid(row=0, column=0, pady=10)

        self.v = IntVar()
        s = Radiobutton(self, text="Soprano", variable=self.v, value=0, indicatoron=0, width=10, command=self.set_voice)
        s.grid(row=1, column=0)
        a = Radiobutton(self, text="Alto", variable=self.v, value=1, indicatoron=0, width=10, command=self.set_voice)
        a.grid(row=2, column=0)
        t = Radiobutton(self, text="Tenor", variable=self.v, value=2, indicatoron=0, width=10, command=self.set_voice)
        t.grid(row=3, column=0)
        b = Radiobutton(self, text="Bass", variable=self.v, value=3, indicatoron=0, width=10, command=self.set_voice)
        b.grid(row=4, column=0)

        self.singer_radio_buttons = (s, a, t, b)

        label = Label(self, text="Accidentals...", font=my_font)
        label.grid(row=5, column=0, pady=10)

        self.a = IntVar()

        sharp_icon = self._get_sharp_icon()
        flat_icon = self._get_flat_icon()

        no_accidental = Radiobutton(self, text="None", variable=self.a, value=0, indicatoron=0, width=10, command=self.set_accidental)
        no_accidental.grid(row=6, column=0)
        sharp_accidental = Radiobutton(self, text="Sharp", variable=self.a, value=1, indicatoron=0, width=10, command=self.set_accidental)
        sharp_accidental.grid(row=7, column=0)
        flat_accidental = Radiobutton(self, text="Flat", variable=self.a, value=-1, indicatoron=0, width=10, command=self.set_accidental)
        flat_accidental.grid(row=8, column=0)

        label_edit = Label(self, text="Editing...", font=my_font)
        label_edit.grid(row=0, column=1, pady=10)

        delete_last = Button(self, text="Delete last note \n (of sel. singer)", width=15, command=self.delete_last)
        delete_last.grid(row=1, column=1)

        undo = Button(self, text="Undo", command=self.undo, width=10)
        undo.grid(row=2, column=1)

        reset_staff = Button(self, text="Delete All Notes!", command=self.reset_staff, width=12)
        reset_staff.grid(row=3, column=1)

    def _get_sharp_icon(self):
        curdir = os.path.normpath(gui.config.home_dir)
        img_path = os.path.normpath(curdir + "/gui/images/sharp_gif.gif")
        return PhotoImage(file=img_path)
    def _get_flat_icon(self):
        curdir = os.path.normpath(gui.config.home_dir)
        img_path = os.path.normpath(curdir + "/gui/images/flat_gif.gif")
        return PhotoImage(file=img_path)

    def delete_last(self):
        singer = self.v.get()
        self.staff.delete_last(singer)

    def undo(self):
        self.staff.undo()

    def reset_staff(self):
        self.staff.reset_staff()

    def _delete_last_hotkey(self, event):
        self.delete_last()
    def _undo_hotkey(self, event):
        self.undo()
    def _select_singer_hotkey(self, event):
        singer = {"s":0, "a":1, "t":2, "b":3}[event.char]
        self.singer_radio_buttons[singer].invoke()
