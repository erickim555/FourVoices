# FourVoices

## Table of Contents
1. About
2. GitHub
3. Prerequisites
4. How to Run
5. Contact
6. History
7. Acknowledgements

## 1. About

FourVoices automatically generates correct four-part harmonizations
(Soprano, alto, tenor, bass) for any harmonic chord progression.
May be particularly useful for music theory students, eg for four-part
writing homework assignments.

Features:
- Automatic generation of correct four-part harmonizations
- Specify lines for each singer, eg provide the soprano line, and have the FourVoices fill in the rest of the voices.
- Chord modifiers: major/minor, seventh chords, diminished.
- User interface, as well as a command-line interface
- Audio playback (see prerequisites)
- Export vocal parts to PDF (Coming soon...)

FourVoices (as of v.0.23) uses the GNU GPL (ver3) license.

## 2. GitHub

Since v0.23, FourVoices has been living on GitHub at:
    
[http://erickim555.github.com/FourVoices/](http://erickim555.github.com/FourVoices/)
    
Feel free to clone the repository, make pull requests, etc.

## 3. Prerequisites

(Tentative, as of v0.23)

Only tested on Windows 7, Ubuntu (12.04).

- Minimums:
    - Python 2.6.4/2.7.2

- Optional:
    - pygame
        - Used for MIDI playback. Homepage at:
            - [Pygame](http://www.pygame.org/)
    - mxm Python MIDI Package
        - Used to construct MIDI files for playback. Homepage at:
            - [mxm Python Midi Package](http://www.mxm.dk/products/public/pythonmidi)

Note: A design goal is to achieve playback without having to do a
      round-about approach. Currently, the codebase converts the 
      vocal parts into a MIDI file (using the mxm_Python_MIDI 
      library), saves it to a temporary midi file, then plays back
      that midi file using pygame. Questionable, at best!
      
## 4. How to Run

If you're in Windows, double-click the `main.py` file.

If you're in Unix, simply do:
```
python main.py
```

There is also a command-line interface (CLI) available in the `core/`
subdirectory:

```
cd core/
python solver.py PROBLEM
```

PROBLEM is the path to a harmonic problem - see `core/tests/TEMPLATE`
for an explanation on the file format.
Additionally, `core/tests/` contains example harmonic problems.

## 5. Contact

You can reach erickim555 either by messaging me via GitHub:

    https://github.com/erickim555
    
Or by e-mailing me at:

    erickim555@gmail.com

## 6. History

The code base was originally written by Eric back in Winter of
2009, while he was an undergraduate at the University of California, 
Berkeley. 
An avid musician and composer, he was inspired to merge his love for
music with his passion for computer science after taking an
Artificial Intelligence course (cs188).
Recognizing that the rules of four-part writing can be easily
expressed as a constraint satisfaction problem, Eric spent a winter
break hacking up a four-part generator with a crude user interface.

## 7. Acknowledgements
    
As of v0.23, FourVoice is powered by a wonderful Constraint 
Satisfaction Problem (CSP) library written by Gustavo Niemeyer:

[Python Constraint](http://labix.org/python-constraint)
