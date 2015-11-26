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

from BehaviourLogic import *
from Player import *

import sys

try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

class SidInstance:

	def __init__(self,player):
		self.player = player

class SidState:
	def __init__(self, sid, fseq):
		self.sid = sid
		self.fseq = fseq
		self.isdown = False
