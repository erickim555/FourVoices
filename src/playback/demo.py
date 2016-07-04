import time
PATH_SOUNDFONT = "./TimGM6mb.sf2"

from mingus.midi import fluidsynth
fluidsynth.init(PATH_SOUNDFONT, "pulseaudio")
time.sleep(1)

from mingus.containers import Note, Track
#fluidsynth.play_Note(Note("C-5"))

track = Track()
track.add_notes(["A-5", "D-5"], 2)
track.add_notes(["B-5", "E-5"], 2)

fluidsynth.play_Track(track)

time.sleep(5)
