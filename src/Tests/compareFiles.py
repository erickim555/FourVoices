'''
Created on Feb 1, 2010

@author: Sforzando
'''

import os

"""
Returns a list of all lines in file2 NOT FOUND in file1
"""
def compare(file1, file2):
  list = []
  file1_lines = []
  for line in file1:
    file1_lines.append(line)
  for line in file2:
    if line not in file1_lines:
      list.append(line)
  return list
  
# File: readline-example-5.py
if __name__ == '__main__':
  curdir = os.path.abspath(os.path.curdir)
  file1_path = os.path.normpath(curdir + "/guiResult.txt")
  file2_path = os.path.normpath(curdir + "/testResult.txt")
  file1 = open(file1_path)
  file2 = open(file2_path)
  
  result = compare(file1, file2)
  
  print len(result)
  for line in result:
    print line