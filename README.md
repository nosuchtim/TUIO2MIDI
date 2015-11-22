This is MIDI Fingers, a python-based program that uses the
Leap Motion device to generate MIDI.  It has been developed
and only tested on Windows.  This version is a two-channel version,
which means that the left side of the space (in which you wave
your fingers) can control a different MIDI channel than the 
right side of the space.  Since there's no option in this version
to go back to the single-channel version, I'm uploading this to
githup as a seprate repository (midifingers2), so the original
version is still available.  At some point, multiple Leap Motion
devices will be supported simultaneously, which will probably
be a much better way of controlling multiple MIDI channels.

Ideally a single program would be able to support a variety
of configurations.  It would be nice for someone to start with
this version and make it more configurable.

RUNNING IT
----------
If you just want to run it, you should be able to unzip
the midifingers.zip file to create a midifingers directory,
which will contain everything needed to run it, including
the Python interpreter.  Just execute the midifingers.exe
file you'll find there.

CHANGING IT
-----------
If you want to modify the program, you will need to install:

    Python 2.7  http://www.python.org/download/
                Use python 2.7.3, 32-bit version.

    Pygame      http://pygame.org/download.shtml
                Use pygame 1.9.1, 32-bit version for python 2.7.

    PySide      http://qt-project.org/wiki/PySide_Binaries_Windows
                Use pyside 1.1.2, 32-bit version for python 2.7.

You also need the following files from the Leap SDK:

    Leap.dll
    Leap.py
    LeapPython.pyd

You may also need the following files:

    msvcp100.dll
    msvcr100.dll

by Tim Thompson, me@timthompson.com, http://timthompson.com
