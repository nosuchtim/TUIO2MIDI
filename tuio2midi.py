#!/usr/bin/env python
#
# TUIO2MIDI
#
# Translate TUIO into MIDI, using all 3 dimensions in the 25D profile
#
# by Tim Thompson, me@timthompson.com, http://timthompson.com

import sys
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
		# print "Usage: tuio2midi {tuio-port} {midi-output-name} {midi-input-name} {settingsname}"
		tuioport = 3333
		midioutputname = "01. Internal MIDI" 
		midiinputname = "None"
		settingsname = "current"
	else:
		tuioport = int(args[1])
		midioutputname = args[2]
		midiinputname = args[3]
		settingsname = args[4]

	App = QtGui.QApplication(sys.argv)

	Midi.startup()

	TPlayer = Player(settingsname)
	TWidget = Widget(TPlayer,settingsname)
	TPanel = TWidget.panel

	TPlayer.set_panel(TPanel)

	if len(TPlayer.behaviournames) <= 0:
		print "Hey!?  No behaviours in %s !?" % BehaviourSettings.settings_dir(settingsname)
		sys.exit(1)

	bn = TPlayer.behaviournames[0]
	TPanel.change_behaviour(bn, True)
	TPanel.change_verbose(1, True)

	TPanel.change_tuioport(tuioport)
	TPanel.change_midiout(midioutputname)
	TPanel.change_midiin(midiinputname)

	TPanel.write_file_onchange = True

	oscmon = OscMonitor("127.0.0.1", tuioport)
	oscmon.setcallback(TPlayer.mycallback, "")

	TWidget.show_and_raise()

	r = App.exec_()

	# leapcontrol.remove_listener(leapmon)

	Midi.shutdown()

	sys.exit(r)
