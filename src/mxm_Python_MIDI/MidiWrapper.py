import pygame, os
from MidiOutFile import MidiOutFile

class MidiWrapper:
  def __init__(self):
    self.file = None
    self.eventQueue = []
    
  def createFile(self, filename):
    self.file = MidiOutFile(filename)
    self.file.header()
    self.file.start_of_track()
  
  def addNote(self, pitch, octave, time, duration, channel=0):
    if not self.file:
      print "Error - outfile has not been created yet! Use MidiWrapper.createFile(1) to make the file first."
      return
    file = self.file
    octaveOffset = ((octave + 1) * 12) - 3  # Middle C (C4) is 0x3C = 60
    noteNum = self._pitchToHex(pitch) + octaveOffset
    self.eventQueue.append((time, "on", (noteNum, channel)))
    self.eventQueue.append((time+duration, "off", (noteNum, channel)))
    
  def _pitchToHex(self, pitch):
    choices = {"A": 0, "B": 2, "C":3, "D":5, "E":7, "F":8, "G":10}
    accidental = None
    if len(pitch) > 1:
      accidental = pitch[1]
      pitch = pitch[0]
    return choices[pitch] + (1 if accidental else 0)
    
  def finalize(self):
    if not self.file:
      print "Error - outfile has not been created yet! Use MidiWrapper.createFile(1) to make the file first."
      return
    self.eventQueue.sort(cmp=lambda x, y : int.__cmp__(x[0], y[0]))
    file = self.file
    for tuple in self.eventQueue:
      time, op, dataTuple = tuple
      file.update_time(time,0)
      if op == "on":
        file.update_time(time,0)
        noteNum, channel= dataTuple
        file.note_on(channel, noteNum)
      else:
        noteNum, channel = dataTuple
        file.note_off(channel, noteNum) 
    # non optional midi framework
    self.file.update_time(0)
    self.file.end_of_track() # not optional!

    self.file.eof()
    return self.file

if __name__ == '__main__':
  pygame.init()
  pygame.mixer.init()
  
  print "============ Testing MidiWrapper ==========="
  print " Test 1: Middle C for 200 clicks"
  test1 = MidiWrapper()
  test1.createFile("midiout/m1.mid")
  test1.addNote("C", 4, 0, 200)
  test1.finalize()

  pygame.mixer.music.load("midiout/m1.mid")
  pygame.mixer.music.play()
  while(pygame.mixer.music.get_busy()):
    continue 
  
  print " Test 2: G Major Chord for 300 clicks "
  test2 = MidiWrapper()
  test2.createFile("midiout/m2.mid")
  test2.addNote("G", 4, 0, 300)
  test2.addNote("B", 4, 0, 300)
  test2.addNote("D", 5, 0, 300)
  test2.addNote("G", 5, 0, 300)
  test2.finalize()
  
  pygame.mixer.music.load("midiout/m2.mid")
  pygame.mixer.music.play()
  while(pygame.mixer.music.get_busy()):
    continue
  
  print " Test 3: ii - V - I in D major "
  test3 = MidiWrapper()
  test3.createFile("midiout/m3.mid")
  test3.addNote("E", 4, 0, 300)
  test3.addNote("G", 4, 0, 300)
  test3.addNote("B", 4, 0, 300)
  
  test3.addNote("E", 4, 350, 300)
  test3.addNote("A", 4, 350, 300)
  test3.addNote("C#", 5, 350, 300)
  
  test3.addNote("D", 4, 700, 300)
  test3.addNote("F#", 4, 700, 300)
  test3.addNote("D", 5, 700, 300)
  test3.finalize()  

  pygame.mixer.music.load("midiout/m3.mid")
  pygame.mixer.music.play()
  while(pygame.mixer.music.get_busy()):
    continue  