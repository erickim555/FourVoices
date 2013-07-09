'''
Created on Feb 1, 2010

@author: Sforzando
'''

from core.Note import *

print "Type -1 to exit"
while(1):
  num = raw_input("Enter a number: ")
  if num == '-1':
    exit(0)
  print "Pitch is: ", numToPitch_absolute(int(num))