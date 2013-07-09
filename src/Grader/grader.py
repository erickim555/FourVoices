from core.Note import *
import copy
# =============== Legend ==============
# =====================================
# leap_type1 := it is bad to leap up to a leading tone, since it resolves in the same direction as the leap
# leap_type2 := it is also bad to leap down to a seventh, since it also resolves downward 
# cm_* := Contrary motion between the two specified voices
# =====================================
# =====================================

feature_weights = {"cm_s_a" : .3, "cm_s_t" : .3, "cm_s_b" : .5, "cm_a_t" : .2, \
                   "cm_a_b" : .25, "cm_t_b" : .35, "doubled_root" : .3, \
                   "leap_type1" : -.8, "leap_type2" : -.8}
feature_counts = {}

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


### NOTE: IN THE MIDST OF MAKING THIS ACCEPT A DICT, CONVERT TO AN ORDERED LIST IN THE FORM OF result
# Input: solution  :=  dict
# Output: A 4-tuple, where each tuple is for each voice (s,a,t,b)
def _regroup_solution(solution):
  result = [[], [], [], []]   # One list for each voice: S, A, T, B
  orderedSol = list()
  for key in solution.keys():
    orderedSol.append([key, solution[key]])
  orderedSol.sort(lambda x, y: myComparator(x[0], y[0]))
  for tuple in orderedSol:
    singer = tuple[0][0]
    num = tuple[1]
    if singer == 's':
      result[0].append(num)
    elif singer == 'a':
      result[1].append(num)
    elif singer == 't':
      result[2].append(num)
    else:   # Bass, 'b'
      result[3].append(num)
  return result

def _numToVoice(num):
  return {0: "s",\
          1: "a",\
          2: "t",\
          3: "b"}[num]

def _init_counts():
  for key in feature_weights.keys():
    feature_counts[key] = 0

# tuple looks like:
# ( ( <voice_1> , <note_0> , <note_1> )  ,  ( <voice_2> , <note_1> , <note_2> ) )  
def isContraryMotion(tuple):
  a_0 = tuple[0][1]
  a_1 = tuple[0][2]
  b_0 = tuple[1][1]
  b_1 = tuple[1][2]
  dist_a = a_0 - a_1
  dist_b = b_0 - b_1
  return ( (dist_a > 0) and (dist_b < 0) ) or ( (dist_a < 0) and (dist_b > 0) )
  

def grade_solutions(ordered_solutions):
  sorted_result = []
  for solution in ordered_solutions:
    sorted_result.append( (grade(solution), solution) )
  sorted_result.sort(lambda x, y : _myCmp(x, y))
  return sorted_result

def grade_solution(solution):
  return ( grade(solution), solution )

def _myCmp(x, y):
  x = x[0]
  y = y[0]
  if x < y: return -1
  if x > y: return 1
  return 0

# solution is a dict mapping variables to values - in this case, voices to notes
def grade(solution, chords, harmonies):
  
  _init_counts()
  solution = _regroup_solution(solution)
  length = len(solution[0])
  # Check for doubled roots, which are generally a good thing
  for t in range(length):
    chord = chords.get(t)
    chord_tones = chord.getChordTones_nums()
    if (chord.getSeventh__() == None): #and (harmony[t][0:3] != "vii"):
      root = chord_tones[0]
      notes = [(x[t]% 12) for x in solution]    # A list of the notes that each voice has at time step t
      if notes.count(root) >= 2:
        feature_counts["doubled_root"] += 1
    if t < (length - 1):
      # Check for contrary motion *what a doozy*
      singer_array = []
      history = []
      for index in range(len(solution)):
        for index2 in range(len(solution)):
          if (index!= index2) and ((index, index2) not in history):
            singer_array.append(((_numToVoice(index), solution[index][t], solution[index][t+1]), \
                                 (_numToVoice(index2), solution[index2][t], solution[index2][t+1])))
            history.append((index2, index))
      for tuple in singer_array:
        if isContraryMotion(tuple):
          tag = "cm_"+tuple[0][0]+"_"+tuple[1][0]
          feature_counts[tag] += 1
      # Mark down for bad leaps to a tendency tone (both sevenths and leading tones)
      chord_2 = chords.get(t+1)
      harmony_2 = harmonies.get(t+1)
      chord_tones_2 = chord_2.getChordTones_nums()
      for voice in solution:
        if harmony_2[0] == "V":
          leading_tone = chord_tones_2[1]
          if (voice[t+1] % 12) == leading_tone:
            note1 = voice[t]
            note2 = voice[t+1]
            dist = note1 - note2
            if (dist < 0) and (abs(dist) > 2):   # If approaching the leading tone from the below, it is best to do so by step
              feature_counts["leap_type1"] += 1
        seventh = chord_2.getSeventh__()
        if seventh != None:
          note1 = voice[t]
          note2 = voice[t+1]
          dist = note1 - note2
          if (dist > 0) and (dist > 2):
            feature_counts["leap_type2"] += 1
  
  utility = 0
  for key in feature_weights.keys():
    utility += feature_weights[key] * feature_counts[key]      
  return utility

def grade_debug(solution, chords, harmonies):
  
  _init_counts()
  solution = _regroup_solution(solution)
  length = len(solution[0])
  # Check for doubled roots, which are generally a good thing
  for t in range(length):
    chord = chords.get(t)
    chord_tones = chord.getChordTones_nums()
    if (chord.getSeventh__() == None): #and (harmony[t][0:3] != "vii"):
      root = chord_tones[0]
      notes = [(x[t]% 12) for x in solution]    # A list of the notes that each voice has at time step t
      if notes.count(root) >= 2:
        feature_counts["doubled_root"] += 1
        
    if t < (length - 1):
      # Check for contrary motion *what a doozy*
      singer_array = []
      history = []
      for index in range(len(solution)):
        for index2 in range(len(solution)):
          if (index!= index2) and ((index, index2) not in history):
            singer_array.append(((_numToVoice(index), solution[index][t], solution[index][t+1]), \
                                 (_numToVoice(index2), solution[index2][t], solution[index2][t+1])))
            history.append((index2, index))
      for tuple in singer_array:
        if isContraryMotion(tuple):
          tag = "cm_"+tuple[0][0]+"_"+tuple[1][0]
          feature_counts[tag] += 1
      
      # Mark down for bad leaps to a tendency tone (both sevenths and leading tones)    
      chord_2 = chords.get(t+1)
      harmony_2 = harmonies.get(t+1)
      chord_2_tones = chord_2.getChordTones_nums()
      for voice in solution:
        if harmony_2[0] == "V":
          leading_tone = chord_2_tones[1]
          if (voice[t+1] % 12) == leading_tone:
            note1 = voice[t]
            note2 = voice[t+1]
            dist = note1 - note2
            if (dist < 0) and (abs(dist) > 2):   # If approaching the leading tone from the below, it is best to do so by step
              feature_counts["leap_type1"] += 1
        seventh = chord_2.getSeventh__()
        if seventh != None:
          note1 = voice[t]
          note2 = voice[t+1]
          dist = note1 - note2
          if (dist > 0) and (dist > 2):
            feature_counts["leap_type2"] += 1
        
  # Mark down for many leaps in similar motion
  
  # Mark down for incomplete chords
  
  
          
  utility = 0
  for key in feature_weights.keys():
    utility += feature_weights[key] * feature_counts[key]      
  return (utility, copy.copy(feature_counts))


# A heuristic used by constraint.py in order to prune the solution space
# partial_assignments := a dictionary mapping variables to its value
# Note: If there aren't enough values assigned to the problem in order to make
# a sensible judgement (i.e if the soprano voice hasn't been filled in yet), then
# return None.
def partial_grade(partial_assignments, chords, harmonies):
  _init_counts()
  solution = _regroup_solution(partial_assignments)
  for list in solution:
    if len(list) == 0:
      return None
  length = min([len(x) for x in solution])
  # Check for doubled roots, which are generally a good thing
  for t in range(length):
    chord = chords.get(t)
    harmony = harmonies.get(t)
    chord_tones = chord.getChordTones_nums()
    if (chord.getSeventh__() == None): #and (harmony[t][0:3] != "vii"):
      root = chord_tones[0]
      notes = [(x[t]% 12) for x in solution]    # A list of the notes that each voice has at time step t
      #print root, "notes: ", notes
      if notes.count(root) >= 2:
        feature_counts["doubled_root"] += 1
  
  # Check for contrary motion *what a doozy*
  for t in range(length - 1):
    singer_array = []
    history = []
    for index in range(len(solution)):
      for index2 in range(len(solution)):
        if (index!= index2) and ((index, index2) not in history):
          singer_array.append(((_numToVoice(index), solution[index][t], solution[index][t+1]), \
                               (_numToVoice(index2), solution[index2][t], solution[index2][t+1])))
          history.append((index2, index))
    for tuple in singer_array:
      if isContraryMotion(tuple):
        tag = "cm_"+tuple[0][0]+"_"+tuple[1][0]
        feature_counts[tag] += 1
  # Mark down for bad leaps to a tendency tone (both sevenths and leading tones)
  for t in range(length - 1):
    chord = chords.get(t+1)
    harmony = harmonies.get(t+1)
    chord_tones = chord.getChordTones_nums()
    for voice in solution:
      if harmony[0] == "V":
        leading_tone = chord_tones[1]
        if (voice[t+1] % 12) == leading_tone:
          note1 = voice[t]
          note2 = voice[t+1]
          dist = note1 - note2
          if (dist < 0) and (abs(dist) > 2):   # If approaching the leading tone from the below, it is best to do so by step
            feature_counts["leap_type1"] += 1
      seventh = chord.getSeventh__()
      if seventh != None:
        note1 = voice[t]
        note2 = voice[t+1]
        dist = note1 - note2
        if (dist > 0) and (dist > 2):
          feature_counts["leap_type2"] += 1
  utility = 0
  for key in feature_weights.keys():
    utility += feature_weights[key] * feature_counts[key]      
  return utility