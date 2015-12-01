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

	App = QtGui.QApplication(sys.argv)

	Midi.startup()

	globals = GlobalSettings()

	TPlayer = Player(globals)
	TWidget = Widget(TPlayer,globals)
	TPanel = TWidget.panel

	TPlayer.set_panel(TPanel)

	if len(TPlayer.behaviournames) <= 0:
		print "Hey!?  No behaviours in %s !?" % globals.settings_dir(settingsname)
		sys.exit(1)

	bn = TPlayer.behaviournames[0]
	TPanel.change_behaviour(bn, True)

	TPanel.write_file_onchange = True

	oscmon = OscMonitor("127.0.0.1", globals.tuioport)
	oscmon.setcallback(TPlayer.mycallback, "")

	TWidget.show_and_raise()

	r = App.exec_()

	# leapcontrol.remove_listener(leapmon)

	Midi.shutdown()

	sys.exit(r)
