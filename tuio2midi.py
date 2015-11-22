#!/usr/bin/env python
#
# TuioPlayer
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

import sys

try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

class HelpPopup(QtGui.QWidget):

	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setWindowTitle("TUIO2MIDI Help")

		self.help = QtGui.QTextEdit(self)
		
		qd = QtGui.QTextDocument()
		qd.setHtml(self.helptext())
		self.help.setDocument(qd)

		layout = QtGui.QGridLayout()
		layout.addWidget(self.help,0,0,1,1)
		self.setLayout(layout)

	def helptext(self):
		return (
		"<h2>TUIO2MIDI</h2>"
		"This program uses the Leap Motion device to "
		"translate your finger movement into MIDI.  "
		"<p>"
		"To get started, you need to set "
		"<b>MIDI Output</b> to the device you "
		"want to use.  On Windows, you can use "
		"the <i>Microsoft GS WaveTable Synth</i> if you don't "
		"have anything else.  You should then be able "
		"to wave your hand above the Leap Motion device "
		"and hear notes being played.  "
		"<p>"
		"The pitch of the MIDI notes is determined by "
		"the horizontal (left/right) position of your "
		"fingers.  "
		"The velocity of the MIDI notes (which usually "
		"controls the volume) is determined by the "
		"depth (in/out) of your fingers.  "
		"<p>"
		"The <b>Quantization</b> value controls the timing "
		"of the notes.  If you select <i>Height-based</i>, the "
		"height (up/down) of your fingers will determine the "
		"quantization amount."
		"<p>"
		"The <b>Duration</b> value controls how long the notes "
		"will play.  If you select <i>Height-based</i>, the "
		"height (up/down) of your fingers will determine the "
		"note duration."
		"<p>"
		"The <b>Movement Threshold</b> value is the distance that "
		"your finger must move before a new MIDI note "
		"is triggered.  "
		"If you set this value to 0.0, MIDI notes will be "
		"triggered continuously, as long as the Leap device "
		"sees your fingers."
		"<p>"
		"The <b>Scale</b> value controls how the notes are "
		"adjusted to fall on particular musical scales.  "
		"You can optionally set the notes of the scale by specifying "
		"a <b>MIDI Input</b> device - typically a MIDI keyboard "
		"controller.  If you play a chord of notes on the "
		"MIDI input device, those notes will be used as the scale "
		"of notes that you are playing with your Leap.  "
		"You don't have to hold the chord notes down - they "
		"will be remembered and used until you play a new chord.  "
		"You can change the chord/scale in realtime, so "
		"a common scenario would be to use one hand on the MIDI "
		"keyboard to control the chord/scale and one hand above "
		"the Leap to play notes."
		"<p>"
		"by Tim Thompson "
		"(me@timthompson.com, http://timthompson.com)"
		)

class ControlPanel(QtGui.QGroupBox):

	# valueChanged = QtCore.Signal(int)

	def just_label(self,s):
		# in case the label Alignment needs to be changed
		label = QtGui.QLabel(s)
		return label

	def __init__(self, parent, midiinputs, midioutputs, scales, keynames):
		super(ControlPanel, self).__init__("",parent)

		self.parent = parent
		self.midiinputs = midiinputs
		self.midioutputs = midioutputs
		self.helpwindow = None

		self.label_top = self.just_label("")

		self.label_message = QtGui.QLabel("")

		self.label_title = QtGui.QLabel(" TUIO2MIDI")
		f = self.label_title.font()
		f.setPointSize(20)
		self.label_title.setFont(f)
		self.label_title.setAlignment(QtCore.Qt.AlignHCenter)
		# self.label_title.setAlignment(QtCore.Qt.AlignVCenter)

		self.label_scale = self.just_label("Scale")
		self.combo_scale = QtGui.QComboBox()
		for s in scales:
			self.combo_scale.addItem(s)
		self.combo_scale.addItem("Using Chord from MIDI Input")
		self.combo_scale.activated[str].connect(self.change_scale)

		self.label_key = self.just_label("Key")
		self.combo_key = QtGui.QComboBox()
		for i in range(len(keynames)):
			self.combo_key.addItem(keynames[i])
		self.combo_key.activated[str].connect(self.change_key)

		self.label_midiin = self.just_label("Midi Input")
		self.combo_midiin = QtGui.QComboBox()
		for s in midiinputs:
			self.combo_midiin.addItem(s)
		self.combo_midiin.addItem("None")
		self.combo_midiin.activated[str].connect(self.change_midiin)

		self.label_midiout = self.just_label("Midi Output")
		self.combo_midiout = QtGui.QComboBox()
		for s in midioutputs:
			self.combo_midiout.addItem(s)
		self.combo_midiout.addItem("None")
		self.combo_midiout.activated[str].connect(self.change_midiout)

		self.label_thresh = self.just_label("Movement Threshold")
		self.spinbox_thresh = QtGui.QDoubleSpinBox()
		self.spinbox_thresh.setRange(0.0,0.1)
		self.spinbox_thresh.setSingleStep(0.01)
		self.spinbox_thresh.setDecimals(2)

		self.spinbox_thresh.valueChanged[float].connect(self.change_threshold)

		self.label_sideheader = {}

		self.label_channel = {}
		self.spinbox_channel = {}
		self.change_channel = {
				"KINECT0" : self.change_left_channel,
				"KINECT1" : self.change_right_channel
				}

		self.label_scaleit = {}
		self.spinbox_scaleit = {}
		self.change_scaleit = {
				"KINECT0" : self.change_left_scaleit,
				"KINECT1" : self.change_right_scaleit
				}

		self.label_program = {}
		self.spinbox_program = {}
		self.change_program = {
				"KINECT0" : self.change_left_program,
				"KINECT1" : self.change_right_program
				}

		self.label_minpitch = {}
		self.spinbox_minpitch = {}
		self.change_minpitch = {
				"KINECT0" : self.change_left_minpitch,
				"KINECT1" : self.change_right_minpitch
				}

		self.label_maxpitch = {}
		self.spinbox_maxpitch = {}
		self.change_maxpitch = {
				"KINECT0" : self.change_left_maxpitch,
				"KINECT1" : self.change_right_maxpitch
				}

		for side in ["KINECT0","KINECT1"]:

			self.label_sideheader[side] = self.just_label("")

			self.label_channel[side] = self.just_label(side+" Channel")
			self.spinbox_channel[side] = QtGui.QSpinBox()
			self.spinbox_channel[side].setRange(1,17)
			self.spinbox_channel[side].setSingleStep(1)

			self.spinbox_channel[side].valueChanged[int].connect(self.change_channel[side])

			self.label_scaleit[side] = self.just_label(side+" Scaleable?")
			self.spinbox_scaleit[side] = QtGui.QSpinBox()
			self.spinbox_scaleit[side].setRange(0,2)
			self.spinbox_scaleit[side].setSingleStep(1)

			self.spinbox_scaleit[side].valueChanged[int].connect(self.change_scaleit[side])

			self.label_program[side] = self.just_label(side+" Program Change")
			self.spinbox_program[side] = QtGui.QSpinBox()
			self.spinbox_program[side].setRange(1,129)
			self.spinbox_program[side].setSingleStep(1)

			self.spinbox_program[side].valueChanged[int].connect(self.change_program[side])

			self.label_minpitch[side] = self.just_label(side+" Min Pitch")
			self.spinbox_minpitch[side] = QtGui.QSpinBox()
			self.spinbox_minpitch[side].setRange(0,64)
			self.spinbox_minpitch[side].setSingleStep(1)

			self.spinbox_minpitch[side].valueChanged[int].connect(self.change_minpitch[side])

			self.label_maxpitch[side] = self.just_label(side+" Max Pitch")
			self.spinbox_maxpitch[side] = QtGui.QSpinBox()
			self.spinbox_maxpitch[side].setRange(64,128)
			self.spinbox_maxpitch[side].setSingleStep(1)

			self.spinbox_maxpitch[side].valueChanged[int].connect(self.change_maxpitch[side])

		layout = QtGui.QGridLayout()

		ncols = 4

		row = 0
		layout.addWidget(self.label_title,row,0,1,ncols)

		self.help_button = QtGui.QPushButton("Help")
		self.help_button.clicked.connect(self.do_help)
		layout.addWidget(self.help_button,row,3,1,1)

		row += 1
		layout.addWidget(self.createQuantGroup(),row,0,1,ncols)

		row += 1
		layout.addWidget(self.createDurationGroup(),row,0,1,ncols)

		row += 1
		layout.addWidget(self.label_top,row,0,1,ncols)

		row += 1
		layout.addWidget(self.label_scale,row,1,1,1)
		layout.addWidget(self.combo_scale,row,2,1,1)

		row += 1
		layout.addWidget(self.label_key,row,1,1,1)
		layout.addWidget(self.combo_key,row,2,1,1)

		# ETC...
		row += 1
		layout.addWidget(self.label_thresh,row,1,1,1)
		layout.addWidget(self.spinbox_thresh,row,2,1,1)

		row += 1
		layout.addWidget(self.label_midiin,row,1,1,1)
		layout.addWidget(self.combo_midiin,row,2,1,1)

		row += 1
		layout.addWidget(self.label_midiout,row,1,1,1)
		layout.addWidget(self.combo_midiout,row,2,1,1)

		for side in ["KINECT0", "KINECT1"]:

			row += 1
			layout.addWidget(self.label_sideheader[side],row,0,1,ncols)

			row += 1
			layout.addWidget(self.label_channel[side],row,1,1,1)
			layout.addWidget(self.spinbox_channel[side],row,2,1,1)

			row += 1
			layout.addWidget(self.label_scaleit[side],row,1,1,1)
			layout.addWidget(self.spinbox_scaleit[side],row,2,1,1)

			row += 1
			layout.addWidget(self.label_minpitch[side],row,1,1,1)
			layout.addWidget(self.spinbox_minpitch[side],row,2,1,1)

			row += 1
			layout.addWidget(self.label_maxpitch[side],row,1,1,1)
			layout.addWidget(self.spinbox_maxpitch[side],row,2,1,1)

			row += 1
			layout.addWidget(self.label_program[side],row,1,1,1)
			layout.addWidget(self.spinbox_program[side],row,2,1,1)

		row += 1
		layout.addWidget(self.label_message,row,0,1,ncols)

		self.setLayout(layout)

	def do_help(self):
		self.helpwindow = HelpPopup()
		self.helpwindow.setGeometry(QtCore.QRect(100,100,400,550))
		self.helpwindow.show()

	def close_help(self):
		if self.helpwindow:
			self.helpwindow.close()

	def change_quant(self,checked):
		if checked:
			button = self.sender()
			for nm in self.quantbuttons:
				if self.quantbuttons[nm] == button:
					self.parent.set_quant(nm)

	def change_dur(self,checked):
		if checked:
			button = self.sender()
			for nm in self.durbuttons:
				if self.durbuttons[nm] == button:
					self.parent.set_duration(nm)


	def createQuantGroup(self):

		group = QtGui.QGroupBox("Quantization")

		layout = QtGui.QHBoxLayout()

		self.quantbuttons = {}
		qnames = self.parent.quantnames
		for q in range(len(qnames)):
			nm = qnames[q]
			self.quantbuttons[nm] = QtGui.QRadioButton(nm)
			self.quantbuttons[nm].toggled[bool].connect(self.change_quant)
			layout.addWidget(self.quantbuttons[nm])

		group.setLayout(layout)    
		return group

	def createDurationGroup(self):

		group = QtGui.QGroupBox("Duration")

		layout = QtGui.QHBoxLayout()

		self.durbuttons = {}
		names = self.parent.durationnames
		for q in range(len(names)):
			nm = names[q]
			self.durbuttons[nm] = QtGui.QRadioButton(nm)
			self.durbuttons[nm].toggled[bool].connect(self.change_dur)
			layout.addWidget(self.durbuttons[nm])

		group.setLayout(layout)    
		return group

	def select_quant(self,quantname):
		self.quantbuttons[quantname].setChecked(True)

	def select_duration(self,durname):
		self.durbuttons[durname].setChecked(True)

	def set_message(self,msg):
		self.label_message.setText(msg)

	def set_key_by_index(self,ix):
		self.combo_key.setCurrentIndex(ix)

	def set_scale_by_name(self,nm):
		for ix in range(0,self.combo_scale.count()):
			if nm == self.combo_scale.itemText(ix):
				self.combo_scale.setCurrentIndex(ix)
				break

	def change_scale(self,val):
		self.parent.set_scale_by_name(val)

	def change_key(self,val):
		self.parent.set_key(val)

	def change_midiin(self,val):
		if not self.parent.open_midiin(val):
			self.combo_midiin.setCurrentIndex(self.indexof_midiin("None"))
		else:
			i = self.indexof_midiin(val)
			self.combo_midiin.setCurrentIndex(i)

	def change_midiout(self,val):
		if not self.parent.open_midiout(val):
			self.combo_midiout.setCurrentIndex(self.indexof_midiout("None"))
		else:
			i = self.indexof_midiout(val)
			self.combo_midiout.setCurrentIndex(i)

	def change_tuioport(self,val):
		print "CHANGE tuioport = ",val

	def indexof_midiin(self,name):
		# Assumes that None is after all midiinputs
		if name == "None":
			return len(self.midiinputs)
		return self.midiinputs.index(name)

	def indexof_midiout(self,name):
		# Assumes that None is after all midioutputs
		if name == "None":
			return len(self.midioutputs)
		return self.midioutputs.index(name)

	def change_threshold(self,val):
		self.parent.set_threshold(val)

	def set_threshold(self,v):
	 	self.spinbox_thresh.setValue(v)

	# XXX - Eventually I should figure out how to parameterize these change_* things

	### Channel

	def change_left_channel(self,val):
		self.parent.set_channel(val,"KINECT0")

	def change_right_channel(self,val):
		self.parent.set_channel(val,"KINECT1")

	def set_channel(self,v,side):
	 	self.spinbox_channel[side].setValue(v)

	### Scaleit

	def change_left_scaleit(self,val):
		print "CHANGE_KINECT0_SCALEIT! val=",val
		self.parent.set_scaleit(val,"KINECT0")

	def change_right_scaleit(self,val):
		print "CHANGE_KINECT1_SCALEIT! val=",val
		self.parent.set_scaleit(val,"KINECT1")

	def set_scaleit(self,v,side):
		print "SET_SCALEIT! val=",v," side=",side
	 	self.spinbox_scaleit[side].setValue(v)

	### Program

	def change_left_program(self,val):
		self.parent.set_program(val,"KINECT0")

	def change_right_program(self,val):
		self.parent.set_program(val,"KINECT1")

	def set_program(self,v,side):
	 	self.spinbox_program[side].setValue(v)

	### Minpitch

	def change_left_minpitch(self,val):
		self.parent.set_minpitch(val,"KINECT0")

	def change_right_minpitch(self,val):
		self.parent.set_minpitch(val,"KINECT1")

	def set_minpitch(self,v,side):
	 	self.spinbox_minpitch[side].setValue(v)

	### Maxpitch

	def change_left_maxpitch(self,val):
		self.parent.set_maxpitch(val,"KINECT0")

	def change_right_maxpitch(self,val):
		self.parent.set_maxpitch(val,"KINECT1")

	def set_maxpitch(self,v,side):
	 	self.spinbox_maxpitch[side].setValue(v)

def sideof(x):
	if x < 0.5:
		return "KINECT0"
	else:
		return "KINECT1"

class TuioPlayer(QtGui.QWidget):

	def __init__(self):
		super(TuioPlayer, self).__init__()
		
		# a -1 quantval means height-based
		self.quantvals = [ 0.0, 0.03125, 0.0625, 0.125, 0.25, -1 ]
		self.quantnames = [ "None", "1/32", "1/16",
					"1/8", "1/4", "Height-based" ]
		self.quantkeys = { "0":0, "1":1, "2":2, "3":3, "4":4 }


		self.durationnames = [ "1/32", "1/16", "1/8", "1/4",
					"1/2", "1", "2", "Height-based" ]
		# duration values are in clocks
		cps = Midi.clocks_per_second
		self.durationvals = [ 0.03125*cps, 0.0625*cps, 0.125*cps,
				0.25*cps, 0.5*cps, 1.0*cps, 2.0*cps, -1.0 ]

		self.savequant = ""
		self.debug = 2
		self.midinotesdown = 0

		# These are not the defaults
		self.channel = { "KINECT0":0, "KINECT1":0 }
		self.program = { "KINECT0":0, "KINECT1":0 }
		self.minpitch = { "KINECT0":0, "KINECT1":0 }
		self.maxpitch = { "KINECT0":0, "KINECT1":0 }
		self.scaleit = { "KINECT0":0, "KINECT1":0 }

		self.scales = {
			"Ionian": [0,2,4,5,7,9,11],
			"Dorian": [0,2,3,5,7,9,10],
			"Phrygian": [0,1,3,5,7,8,10],
			"Lydian": [0,2,4,6,7,9,11],
			"Mixolydian": [0,2,4,5,7,9,10],
			"Aeolian": [0,2,3,5,7,8,10],
			"Locrian": [0,1,3,5,6,8,10],
			"Newage": [0,3,5,7,10],
			"Fifths": [0,7],
			"Octaves": [0],
			"Harminor": [0,2,3,5,7,8,11],
			"Melminor": [0,2,3,5,7,9,11],
			"Chromatic": [0,1,2,3,4,5,6,7,8,9,10,11]
			}
		self.keynames = [
			"C", "C#", "D", "D#", "E",
			"F", "F#", "G", "G#", "A", "A#", "B" ]
		self.keyindex = 0    # in keynames, also used as pitch offset

		self.sids = {}

		Midi.startup()
		self.midi = MidiPypmHardware()
		midiinputs = self.midi.input_devices()
		midioutputs = self.midi.output_devices()
		self.midiin = None
		self.midiout = None

		Midi.callback(self.midicallback,"")

		x, y, w, h = 500, 200, 100, 100
		self.setGeometry(x, y, w, h)

		self.panel = ControlPanel(self,midiinputs,midioutputs,
				self.scales,self.keynames)

		self.layout = QtGui.QHBoxLayout()
		self.layout.addWidget(self.panel)
		self.setLayout(self.layout)

		self.setWindowTitle("TUIO2MIDI")

		#########################################
		# This is where default values get set
		#########################################
		self.set_threshold(0.04)
		self.set_scale_by_name("Newage")

		# self.set_quant("1/8")
		self.set_quant("Height-based")

		self.set_key("F")
		self.set_duration("Height-based")

		self.set_channel(10,"KINECT0")
		self.set_scaleit(0,"KINECT0")
		self.set_program(1,"KINECT0")
		self.set_minpitch(37,"KINECT0")
		self.set_maxpitch(59,"KINECT0")

		self.set_channel(1,"KINECT1")
		self.set_scaleit(1,"KINECT1")
		self.set_program(1,"KINECT1")
		self.set_minpitch(40,"KINECT1")
		self.set_maxpitch(100,"KINECT1")

	def set_message(self,msg):
		self.panel.set_message(msg)
	
	def send_testnote(self):
		# Send a test note to see if MIDI output is alive
		nt = SequencedNote(pitch=60,duration=12,channel=1,velocity=100)
		self.midiout.schedule(nt)

	def send_program(self,ch,prog):
		if self.midiout and ch > 0 and prog > 0:
			p = Program(channel=ch,program=prog)
			self.midiout.schedule(p)

	def set_tuioport(self,port):
		self.panel.change_tuioport(port)

	def set_midiout(self,name):
		self.panel.change_midiout(name)

	def set_midiin(self,name):
		self.panel.change_midiin(name)

	def set_threshold(self,v):
		self.threshold = v
		self.panel.set_threshold(v)

	def set_channel(self,v,side):
		self.channel[side] = v
		self.panel.set_channel(v,side)
		self.send_program(self.channel[side],self.program[side])

	def set_scaleit(self,v,side):
		print "PARENT set_scaleit v=",v," side=",side
		self.scaleit[side] = v
		self.panel.set_scaleit(v,side)

	def set_program(self,v,side):
		self.program[side] = v
		self.panel.set_program(v,side)
		self.send_program(self.channel[side],self.program[side])

	def set_minpitch(self,v,side):
		self.minpitch[side] = v
		self.panel.set_minpitch(v,side)

	def set_maxpitch(self,v,side):
		self.maxpitch[side] = v
		self.panel.set_maxpitch(v,side)

	def set_duration(self,durname):
		i = self.durationnames.index(durname)
		self.duration = self.durationvals[i]
		self.panel.select_duration(durname)

	def set_quant(self,quantname):
		i = self.quantnames.index(quantname)
		self.quant = self.quantvals[i]
		self.panel.select_quant(quantname)

	def set_key(self,keyname):
		self.keyindex = self.keynames.index(keyname)
		self.panel.set_key_by_index(self.keyindex)
		self.make_scalenotes()

	def set_scale_by_name(self,scalename):
		if not (scalename in self.scales):
			print "No such scale: ",scalename
			return
		self.scalecurrent = self.scales[scalename]
		self.panel.set_scale_by_name(scalename)
		self.make_scalenotes()

	def make_scalenotes(self):
		# Construct an array of 128 elements with the mapped
		# pitch of each note to a given scale of notes
		scale = self.scalecurrent

		# Adjust the incoming scale to the current key
		realscale = []
		for i in range(len(scale)):
			realscale.append((scale[i] + self.keyindex) % 12)

		scalenotes = []
		# Make an array mapping each pitch to the closest scale note.
		# This code is brute-force, it starts at the pitch and
		# goes incrementally up/down from it until it hits a pitch
		# that's on the scale.
		for pitch in range(128):
			scalenotes.append(pitch)
			inc = 1
			sign = 1
			cnt = 0
			p = pitch
			# the cnt is just-in-case, to prevent an infinite loop
			while cnt < 100:
				if p >=0 and p <= 127 and ((p%12) in realscale):
					break
				cnt += 1
				p += (sign * inc)
				inc += 1
				sign = -sign
			if cnt >= 100:
				print "Something's amiss in set_scale!?"
				p = pitch
			scalenotes[pitch] = p
		self.scalenotes = scalenotes

	def open_midiin(self,name):
		if self.midiin:
			tmp = self.midiin
			self.midiin = None
			tmp.close()
		try:
			# if name is "None", we leave self.midiin as None
			if name != "None":
				self.midiin = self.midi.get_input(name)
				self.midiin.open()
			# self.set_message("MIDI input set to: %s" % name)
			self.set_message("")
		except:
			self.set_message("Unable to open MIDI input: %s" % name)
			print("Error opening MIDI input: %s, exception: %s" % (name,format_exc()))
			self.midiin = None
			return False;

		return True

	def open_midiout(self,name):
		if self.midiout:
			tmp = self.midiout
			self.midiout = None
			tmp.close()
		try:
			# if name is "None", we leave self.midiout as None
			if name != "None":
				tmp = self.midi.get_output(name)
				tmp.open()
				self.midiout = tmp
			# self.set_message("MIDI output set to: %s" % name)
			self.set_message("")
		except:
			self.set_message("Unable to open MIDI output: %s" % name)
			print("Error opening MIDI output: %s, exception: %s" % (name,format_exc()))
			self.midiout = None
			return False;

		return True

	def show_and_raise(self):
		self.show()
		self.raise_()

	def keyPressEvent(self, evt):
		key = evt.key()
		unikey = evt.text()
		modifier = evt.modifiers()
		# print "keyPressEvent! key=",key," unikey=",unikey," ord=",ord(unikey)
		if unikey in self.quantkeys:
			q = self.quantkeys[unikey]
			qname = self.quantnames[q]
			self.set_quant(qname)
			self.savequant = qname

		# elif unikey == "Q" or unikey == "\033":
		# 	global App
		# 	App.quit()

	def keyReleaseEvent(self, evt):
		key = evt.key()
		unikey = evt.text()
		modifier = evt.modifiers()
		# print "keyReleaseEvent! key=",key," unikey=",unikey," ord=",ord(unikey)
		if self.savequant != "":
			self.set_quant(self.savequant)
			self.savequant = ""

	def closeEvent(self, evt):
		self.panel.close_help()

	def midicallback(self,msg,data):
		if self.debug > 0:
			print("MIDI INPUT = %s" % str(msg))
		m = msg.midimsg

		if isinstance(m,NoteOn):
			self.midinotesdown += 1
			if self.midinotesdown == 1:
				self.currentchord = [m.pitch]
				self.panel.set_scale_by_name("Using Chord from MIDI Input")
			else:
				self.currentchord.append(m.pitch)
			self.scalecurrent = self.currentchord
			self.make_scalenotes()

		elif isinstance(m,NoteOff):
			self.midinotesdown -= 1

		elif isinstance(m,Controller):
			if self.midiout:
				self.midiout.schedule(m)

	def playnote(self,tm,sid,pitch,dur,ch,vel):
		n = SequencedNote(pitch=pitch,duration=dur,channel=ch,velocity=vel)
		if self.midiout:
			self.midiout.schedule(n,time=tm)
		else:
			print("No MIDI output, trying to play pitch=%d channel=%d velocity=%d" % (n.pitch,n.channel,n.velocity))

	def nextquant(self,tm,q):
		# We assume values are in terms of seconds
		if q <= 0:
			return tm
		q1000 = int(q * 1000)
		tm1000 = int(tm * 1000)
		tmq = tm1000 % q1000
		dq = (tmq/1000.0)
		nextq = tm + (q-dq)
		# print "nextquant tm=%f q=%f tmq=%d dq=%f nextq=%f" % (tm,q,tmq,dq,nextq)
		return nextq

	def cursorDrag(self,state):

		x = state.x
		y = state.y
		z = state.z
		sid = state.sid

		if sid in self.sids:
			s = self.sids[sid]
			lasttime = s["lasttime"]
			lastx = s["lastx"]
			lasty = s["lasty"]
			lastz = s["lastz"]
		else:
			lasttime = 0
			lastx = 999.0
			lasty = 999.0
			lastz = 999.0

		now = time.time()

		if self.debug > 1:
			print "cursormove sid = %d xyz = %.3f %.3f %.3f" % (sid,x,y,z)

		dx = (x - lastx)
		dy = (y - lasty)
		dz = (z - lastz)
		dist = math.sqrt(dx*dx+dy*dy+dz*dz)
		if dist <= self.threshold:
			if self.debug > 1:
				print("dist=%f ignoring" % dist)
			return

		side = sideof(x)

		if self.debug > 1:
			print "==== sid=%d dist=%.3f xy=%.3f %.3f lastxy=%.3f,%.3f" % (sid,dist,x,y,lastx,lasty)

		pitch = self.pitchof(state)
		vel = self.velocityof(state)
		ch = self.channel[side]

		if self.duration < 0:
			# it's height-based
			dur = self.durationof(pos)
		else:
			dur = self.duration

		if self.quant < 0:
			# it's height-based
			q = self.quantof(pos)
		else:
			q = self.quant
		if self.debug > 1:
			print "pos y=%.3f q=%.3f" % (pos[1],q)
		tm = self.nextquant(now,q)

		if tm <= lasttime:
			# print "sid=",sid," too soon, tm=",tm," lasttime=",lasttime
			return

		self.playnote(tm,sid,pitch,dur,ch,vel)

		if self.debug > 0:
			print("playnote ch=%d pitch=%d q=%.3f dur=%.3f vel=%.3f" % (ch,pitch,q,dur,vel))

		# if self.debug > 0:
		# 	print "Playing sid=%d now=%.4f quant=%.4f tm=%.4f" % (sid,now,self.quant,tm)
		self.sids[sid] = {"lasttime":tm, "lastx":x, "lasty":y, "lastz":z}

	def pitchof(self,state):
		x = state.x
		# Make x go from 0.0 to 1.0 for each side
		side = state.side
		if side == "KINECT0":
			x = x * 2.0
		else:
			x = (x - 0.5) * 2.0
		if x < 0.0:
			x = 0.0
		if x > 1.0:
			x = 1.0
		dp = self.maxpitch[side] - self.minpitch[side]
		rawp = self.minpitch[side] + int(dp * x)
		if self.scaleit[side]:
			p = self.scalenotes[rawp]
		else:
			p = rawp
		if self.debug > 1:
			print "PITCHOF side%s x=%.3f p=%d   dp=%.3f int(dp*x)=%d" % (side,x,p,dp,int(dp*x))
		return p

	def velocityof(self,state):
		return int(self.z * 128.0)

	def channelof(self,state):
		# y = pos[1]
		# return 1 + (int(y * 16.0) % 16)
		return 1

	def quantof(self,state):
		# returns quantization in seconds
		y = state.y
		# if y < 0.05:
		# 	return 0
		# if y < 0.05:
		# 	return 0.03125
		if y < 0.2:
			return 0.0625
		if y < 0.45:
			return 0.125
		if y < 0.7:
			return 0.250
		return 0.5

	def durationof(self,pos):
		# Returns duration in clocks.
		y = pos[1]
		# The higher you are, the longer the duration.
		b = Midi.clocks_per_second
		if y < 0.1:
			return 1
		if y < 0.2:
			return b/16
		if y < 0.4:
			return b/8
		if y < 0.6:
			return b/4
		if y < 0.75:
			return b
		return b*2

	def cursorDown(self,state):
		self.cursorDrag(state)

# 		# print "DOWN sid=",state.sid," x=",state.x," y=",state.y," z=",state.z
# 		p = self.pitchof(state.x)
# 		p = self.pitchofh(state.h)
# 		ch = self.chanof(state.x)
# 		v = self.velocityof(state.z)
# 		v = self.velocityofx(state.x)
# 		d = 0.0625 * Midi.clocks_per_second
# 		d = 1.0 * Midi.clocks_per_second
# 		m = SequencedNote(pitch=p,duration=d,channel=ch,velocity=v)
# 		print "    M = ",m
# 		tm = time.time()
# 		q = quantof(state.y)
# 		q = quantofh(state.h)
# 		tm = nextquant(tm,q)
# 		MidiOut.schedule(m,tm)
# 	
# 	def cursorDrag(self,state):
# 		# print "DRAG sid=",state.sid," x=",state.x," y=",state.y," z=",state.z
# 		self.cursorMove(state)
	
	def cursorUp(self,state):
		# print "Up sid=",state.sid," x=",state.x," y=",state.y," z=",state.z
		# self.cursorUpdate(state)
		pass

	def mycallback(self,ev,d):
		# print "TuioPlayer.mycallback!"

		source = ""
		fseq = 0

		# Seems silly to have to scan them all to get the fseq first...
		# While I'm doing it, I might as well grab source up front, too.
		for m in ev.oscmsg:
			if len(m) >= 3 and m[0] == "/tuio/25Dblb":
				if m[2] == "fseq":
					fseq = m[3]
					# print "FSEQ ",fseq," ",source
					continue
				if m[2] == "source":
					source = m[3]
					# print "SOURCE = ",source
					continue

		for m in ev.oscmsg:
			lenm = len(m)
			if m[0] != "/tuio/25Dblb":
				continue
			if lenm < 3:
				continue
			if m[2] == "alive":
				for i in range(3,len(m)):
					sid = m[i]
					# print "alive sid=",sid
				continue
			if m[2] == "set":
				sid = m[3]
				x = m[4]
				y = m[5]
				z = m[6]
				w = m[8]
				h = m[9]
				print "Source=",source," Fseq=",fseq," set sid=",sid," w=",w," h=",h
				continue

class CursorState:
	def __init__(self,fseq,sid):
		self.fseq = fseq
		self.sid = sid
		self.isdown = False

# def mycallback(ev,player):
# 	global Fseq, Sids
# 	for m in ev.oscmsg:
# 		lenm = len(m)
# 		if m[0] != "/tuio/25Dblb":
# 			pass
# 		if lenm >= 3 and m[2] == "alive":
# 			for i in range(3,len(m)):
# 				sid = m[i]
# 				if sid in Sids:
# 					Sids[sid].fseq = Fseq
# 				else:
# 					Sids[sid] = CursorState(Fseq,sid)
# 			toremove = []
# 			for k in Sids:
# 				if Sids[k].fseq != Fseq:
# 					toremove.append(k)
# 			for k in toremove:
# 				player.cursorUp(Fseq,toremove[k])
# 				del Sids[k]
# 		elif lenm >= 3 and m[2] == "fseq":
# 			Fseq = m[3]
# 		elif lenm >= 3 and m[2] == "set":
# 			# print m
# 			sid = m[3]
# 			x = m[4]
# 			y = m[5]
# 			z = m[6]
# 			w = m[8]
# 			h = m[9]
# 			print "w=",w," h=",h
# 			if sid in Sids:
# 				state = Sids[sid]
# 				state.x = x
# 				state.y = y
# 				state.z = z
# 				state.w = w
# 				state.h = h
# 				# print "updated sid = ",state.x," ",state.y," ",state.z
# 				if state.isdown:
# 					player.cursorDrag(state)
# 				else:
# 					player.cursorDown(state)
# 					state.isdown = True
# 			else:
# 				print "sid ",sid," isn't in Sids!?"

def bound_it(v):
	if v < 0.0:
		return 0.0
	if v > 1.0:
		return 1.0
	return v

# def scale_leap_pos(pos):
# 	x = bound_it((pos.x + 250.0) / 500.0)
# 	y = bound_it((pos.y - 50.0) / 500.0)
# 	z = bound_it((pos.z + 250.0) / 500.0)
# 	z = 1.0 - z
# 	return (x,y,z)
# 
# def leapcallback(frame,parent):
# 	if len(frame.fingers) > 0:
# 		for f in frame.fingers:
# 			pos = f.tip_position
# 			scaledpos = scale_leap_pos(pos)
# 			# print "LEAP f=%d h=%d wid=%.3f length=%.3f valid=%s isfing=%s pos=%.3f,%.3f,%.3f" % (
# 			# 	f.id,f.hand.id,f.width,f.length,f.is_valid,f.is_finger,pos[0],pos[1],pos[2])
# 			parent.cursormove(f.id,scaledpos)
# 
# class LeapMonitor(Leap.Listener):
# 
#     def __init__(self,callback,data):
# 	super(LeapMonitor, self).__init__()
# 	self.callback = callback
# 	self.callback_data = data
# 
#     # def on_init(self, controller):
#     #     print "LeapMonitor Initialized"
# 
#     # def on_connect(self, controller):
#     #     print "LeapMonitor Connected"
# 
#     # def on_disconnect(self, controller):
#     #     print "LeapMonitor Disconnected"
# 
#     # def on_exit(self, controller):
#     #     print "LeapMonitor Exited"
# 
#     def on_frame(self, controller):
#         frame = controller.frame()
# 	if self.callback:
# 		self.callback(frame,self.callback_data)
# 	return

if __name__ == "__main__":

	args = sys.argv

	if len(args) < 3:
		print "Usage: tuio2midi {tuio-port} {midi-output-name} [{midi-input-name}]"
		sys.exit(1)

	tuioport = int(args[1])
	midioutputname = args[2]
	if len(args) > 3:
		midiinputname = args[3]
	else:
		midiinputname = "None"

	# global Sids, Fseq
	# Sids = {}
	# Fseq = 0

	App = QtGui.QApplication(sys.argv)

	TP = TuioPlayer()
	TP.set_tuioport(tuioport)
	TP.set_midiout(midioutputname)
	TP.set_midiin(midiinputname)

	oscmon = OscMonitor("127.0.0.1",tuioport)
	oscmon.setcallback(TP.mycallback,"")

	# leapmon = LeapMonitor(leapcallback,TP)
	# leapcontrol = Leap.Controller()
	# leapcontrol.add_listener(leapmon)

	TP.show_and_raise()

	r = App.exec_()

	# leapcontrol.remove_listener(leapmon)

	Midi.shutdown()

	sys.exit(r)
