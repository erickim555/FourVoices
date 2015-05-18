'''
Created on Jan 4, 2010

@author: Sforzando
'''
home_dir = None

staff_pos_x = 40
staff_pos_y = 40

"""
selected_singer can be (0, 1, 2, or 3), which corresponds to
(soprano, alto, tenor, bass)
"""
selected_singer = 0

"""
A dict mapping singer-features to values
(only for appearance)
"""
note_config = { "soprano" : \
                  { "color" : "black", "stem_dir" : "up" }, \
                "alto" : \
                  { "color" : "black", "stem_dir" : "down" }, \
                "tenor" : \
                  { "color" : "black", "stem_dir" : "up" }, \
                "bass" : \
                  { "color" : "black", "stem_dir" : "down" }, }

"""
accidental can be (-1, 0, 1), which corresponds to
(Flat, None, Sharp)
"""
accidental = 0

""" A variable used by solver_frame_aux.py to remember the last-used time step """
last_time = 0

solver_frame_aux = None

singer_frame = None

chord_modifiers = [ "dim", "dim7", "m7(b5)", "7", "min7", "maj7", "min", "Maj" ]
