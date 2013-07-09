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
Created on May 26, 2010

@author: Sforzando
'''

class TimeList:
  def __init__(self):
    self.items = []
  
  """
  thing is either a Chord() instance, or a "Harmonic-Function" string
  This Data Structure keeps its list sorted by time (0, 1, ...)
  """
  def add(self, time, thing):
    if type(4) != type(time):
      raise ValueError, "First argument must be an integer, but instead was: %s" % repr(time) 
    if len(self.items) == 0:    
      self.items.append( (time, thing) )
    else:
      for item in self.items:
        if time < item[0]:
          self.items.insert( self.items.index(item), (time, thing) )
          return
      """ If we get here, then our thing belongs at the end """
      self.items.append( (time, thing) )
  
  """
  Returns True if removal was successful, and Returns
  False if the item wasn't there.
  """
  def remove(self, time):
    for item in self.items:
      if item[0] == time:
        self.items.remove(item)
        return True
    return False
  
  
  def get(self, time):
    for item in self.items:
      if item[0] == time:
        return item[1]
    return None
  
  def get_times(self):
    return [x[0] for x in self.items]

  """ 
  Returns True if there is absolutely NOTHING inside the TimeList.
  Note that isEmpty() != (__len__(self) == 0)!!!!
  """
  def is_empty(self):
    return len(self.items) == 0
    
  """
  Return (and remove) the element with greatest time
  """
  def pop(self):
    x = max([x[0] for x in self.items])
    el = self.get(x)
    if self.remove(x) != True:
      print "=== Error in TimeList() : self.remove(x) didn't work correctly... "
      exit(1)
    return el
  
  """
  The length of this data structure is the length of the first
  contiguous set of chords (beginning at t=0)
  """
  def __len__(self):
    """ Base cases """
    if (len(self.items) == 0):
      return 0
    if self.items[0][0] != 0:
      return 0
    
    length = 1
    for item in self.items:
      if self.items.index(item) == 0:
        continue
      if item[0] != length:
        return length
      else:
        length += 1
    return length
      
  def __iter__(self):
    times = self.get_times()
    temp = []
    for i in times:
      temp.append(self.get(i))
    return iter(temp)
  
  def __getitem__(self, i):
    return self.get(i)

class ImageStructure(dict):
  def __init__(self):
    self["soprano"] = TimeList()
    self["alto"] = TimeList()
    self["tenor"] = TimeList()
    self["bass"] = TimeList()
    self["others"] = []
    dict.__init__(self)
   
  def append(self, object):
    if "others" not in self:
      print "WARNING : Uh oh, we got to a bad part in ImageStructure.append()."
      self["others"] = []
    self["others"].append(object)

if __name__ == '__main__':
  x = ImageStructure()
  x["soprano"] = 0
  x["alto"] = 1
  x["tenor"] = 2
  x["bass"] = 3
  x.append(4)
  x.append(5)
  y = [ ("soprano" , 0) , ("alto" , 1) , ("tenor" , 2) , ("bass" , 3) , ("others" , [4, 5]) ]
  if x.items() != y:
    raise Exception , "Test didn't pass! %s" % x.items()

