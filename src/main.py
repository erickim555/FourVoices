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

import os
from Tkinter import *

import gui.config
from gui.staff import Staff
from gui.singer_frame import SingerFrame
from gui.solver_frame_aux import SolverFrameAux
from gui.solver_frame import SolverFrame

root = Tk()
root.title("Automatic Four-Part Harmony Solver")

"""
This is where the magic happens!!!
"""
gui.config.home_dir = os.path.abspath(os.path.curdir)

root.config(background="Gray")

music_canvas = Staff(root, width=1000, height=300, borderwidth=5, relief=GROOVE, background="White")
music_canvas.init()
music_canvas.grid(row=0, column=0, columnspan=5, rowspan=3, sticky=NW)

singer_frame = SingerFrame(root, width=200, height=300, borderwidth=2, relief=GROOVE)
singer_frame.init_frame(music_canvas)
singer_frame.grid(row=3, column=3, rowspan=1, sticky=NW)

solver_frame = SolverFrame(root, width=200, height=300, borderwidth=2, relief=GROOVE)
solver_frame.init_frame(music_canvas)
solver_frame.grid(row=3, column=4, sticky=NW)

aux_solver_frame = SolverFrameAux(root, width=200, height=300, borderwidth=2, relief=GROOVE)
aux_solver_frame.init_frame(solver_frame)
aux_solver_frame.grid(row=3, column=1, sticky=NW)

menu = Menu(root)
root.config(menu=menu)
file_menu = Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Save...", command=None)
file_menu.add_command(label="Open...", command=None)

help_menu = Menu(menu)
menu.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About..." , command=None)

"""  Adding Hotkeys  """

root.bind("<BackSpace>", singer_frame._delete_last_hotkey)
root.bind("<Control-z>", singer_frame._undo_hotkey)
root.bind("s", singer_frame._select_singer_hotkey)
root.bind("a", singer_frame._select_singer_hotkey)
root.bind("t", singer_frame._select_singer_hotkey)
root.bind("b", singer_frame._select_singer_hotkey)

"""
End magic!!!
"""
root.mainloop()
