'''
Created on Jan 6, 2010

@author: Sforzando
'''

from Data_Structures.timelist import TimeList

def empty_test():
    tlist = TimeList()
    return 0 == len(tlist)

def insert_test():
    tlist = TimeList()
    tlist.add(0, "a")
    if len(tlist) != 1:
        print "1, ", tlist.items, len(tlist)
        return False
    tlist.add(1, "b")
    if len(tlist) != 2:
        print "2, ", tlist.items, len(tlist)
        return False
    tlist.add(100, "way out there")
    return len(tlist) == 2

def remove_test():
    tlist = TimeList()
    tlist.add(0, "a")
    tlist.remove(0)
    if len(tlist) != 0:
        return False
    if (tlist.remove(0) != False) and (tlist.remove(1003) != False):
        return False
    tlist.add(3, "c")
    tlist.add(1, "a")
    tlist.add(2, "b")
    if len(tlist) != 0:
        return False
    tlist.add(0, "-a")
    if len(tlist) != 4:
        return False
    tlist.remove(0)
    if len(tlist) != 0:
        return False

print "========= Running TimeList Tests ==========="
print "=== Running empty_test() ==="
if empty_test() == False:
    print "= Failure reported."
print "=== Running insert_test() ==="
if insert_test() == False:
    print "= Failure reported."
print "=== Running remove_test() ==="
if remove_test() == False:
    print "= Failure reported."
