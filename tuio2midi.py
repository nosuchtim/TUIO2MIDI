#!/usr/bin/env python
#
# TUIO2MIDI
#
# Translate Leap Motion into MIDI, using all 3 dimensions.
# Pitch is controlled by the X dimension.
#
# by Tim Thompson, me@timthompson.com, http://timthompson.com

import sys
import time
import math
from nosuch.midiutil import *
from nosuch.midipypm import *
from nosuch.oscutil import *

# from Behaviour import *
from Player import *
from Widget import *

import sys

try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

if __name__ == "__main__":

	args = sys.argv

	if len(args) < 4:
		# print "Usage: tuio2midi {tuio-port} {midi-output-name} {midi-input-name}"
		tuioport = 3333
		midioutputname = "01. Internal MIDI" 
		midiinputname = "None"
	else:
		tuioport = int(args[1])
		midioutputname = args[2]
		midiinputname = args[3]

	App = QtGui.QApplication(sys.argv)

	Midi.startup()

	TPlayer = Player()
	TWidget = Widget(TPlayer)
	TPanel = TWidget.panel

	TPlayer.set_panel(TPanel)

	TPanel.change_behaviour("Center_Y",True)
	TPanel.change_tuioport(tuioport)
	TPanel.change_midiout(midioutputname)
	TPanel.change_midiin(midiinputname)

	oscmon = OscMonitor("127.0.0.1", tuioport)
	oscmon.setcallback(TPlayer.mycallback, "")

	# leapmon = LeapMonitor(leapcallback,TP)
	# leapcontrol = Leap.Controller()
	# leapcontrol.add_listener(leapmon)

	TWidget.show_and_raise()

	r = App.exec_()

	# leapcontrol.remove_listener(leapmon)

	Midi.shutdown()

	sys.exit(r)
