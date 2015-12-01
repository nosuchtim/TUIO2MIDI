import sys
import os

try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

from Attribute import *
from Duration import *
from Scale import *
from BehaviourLogic import *
from BehaviourSettings import *
from Key import *
from Quant import *

class HelpPopup(QtGui.QWidget):

	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.setWindowTitle("TUIO2MIDI Help")

		self.help = QtGui.QTextEdit(self)
		
		qd = QtGui.QTextDocument()
		qd.setHtml(self.helptext())
		self.help.setDocument(qd)

		layout = QtGui.QGridLayout()
		layout.addWidget(self.help, 0, 0, 1, 1)
		self.setLayout(layout)

	def helptext(self):
		return (
		"<h2>TUIO2MIDI</h2>"
		"This program converts TUIO messages "
		"(using the 25D profile) into MIDI.  "
		"It is intended for use with the "
		"MMTT software that uses 3D cameras "
		"(like the Kinect) to track body "
		"movement and send out TUIO messages."
		"<p>"
		"by Tim Thompson "
		"(me@timthompson.com, http://timthompson.com)"
		)

class Panel(QtGui.QGroupBox):

	def __init__(self,player,settingsname):
		super(Panel, self).__init__("")

		self.write_file_onchange = False
		self.currbehaviour = None
		self.panelsettings = BehaviourSettings()
		self.player = player
		self.helpwindow = None
		self.settingsname = settingsname

		self.label_message = QtGui.QLabel("")

		self.label_title = QtGui.QLabel("TUIO2MIDI  ")
		f = self.label_title.font()
		f.setPointSize(20)
		self.label_title.setFont(f)
		self.label_title.setAlignment(QtCore.Qt.AlignLeft)

		self.label_settingsname = self.just_label("Settings")
		self.combo_settingsname = QtGui.QComboBox()
		self.combo_settingsname.activated[str].connect(self.change_settingsname)
		self.init_combo_settingsname()

		# self.label_settingsname = self.just_label("Settings")
		# self.spinbox_settingsname = QtGui.QLineEdit()
		# self.spinbox_settingsname.returnPressed.connect(self.change_settingsname)
		# self.spinbox_settingsname.setText(settingsname)

		self.label_tuioport = self.just_label("TUIO Port")
		self.spinbox_tuioport = QtGui.QSpinBox()
		self.spinbox_tuioport.setRange(3333, 9999)
		self.spinbox_tuioport.setSingleStep(1)
		self.spinbox_tuioport.valueChanged[int].connect(self.change_tuioport)

		self.label_source = self.just_label("Source")
		self.text_source = QtGui.QLineEdit()
		self.text_source.textChanged.connect(self.change_source)

		self.label_attribute = self.just_label("Attribute")
		self.combo_attribute = QtGui.QComboBox()
		for s in Attribute.order:
			self.combo_attribute.addItem(s)
		self.combo_attribute.activated[str].connect(self.change_attribute)

		self.label_actiontype = self.just_label("Action")
		self.combo_actiontype = QtGui.QComboBox()
		self.combo_actiontype.addItem("Note")
		# self.combo_actiontype.addItem("Note (Velocity=Depth)")
		for i in range(0,128):
			self.combo_actiontype.addItem("Controller %d" % i)
		self.combo_actiontype.activated[str].connect(self.change_actiontype)

		self.label_scale = self.just_label("Scale")
		self.combo_scale = QtGui.QComboBox()
		for s in Scale.order:
			self.combo_scale.addItem(s)
		self.combo_scale.activated[str].connect(self.change_scale)

		self.label_key = self.just_label("Key")
		self.combo_key = QtGui.QComboBox()
		for i in range(len(Key.names)):
			self.combo_key.addItem(Key.names[i])
		self.combo_key.activated[str].connect(self.change_key)

		self.label_quant = self.just_label("Quantization")
		self.combo_quant = QtGui.QComboBox()
		for i in Quant.order:
			self.combo_quant.addItem(i)
		self.combo_quant.activated[str].connect(self.change_quant)

		self.label_duration = self.just_label("Duration")
		self.combo_duration = QtGui.QComboBox()
		for i in Duration.order:
			self.combo_duration.addItem(i)
		self.combo_duration.activated[str].connect(self.change_duration)

		self.label_behaviour = self.just_label("Behaviour")
		self.combo_behaviour = QtGui.QComboBox()
		self.init_combo_behaviour()

		self.label_midiin = self.just_label("Midi Input")
		self.combo_midiin = QtGui.QComboBox()
		for s in self.player.midiinputs:
			self.combo_midiin.addItem(s)
		self.combo_midiin.addItem("None")
		self.combo_midiin.activated[str].connect(self.change_midiin)

		self.label_midiout = self.just_label("Midi Output")
		self.combo_midiout = QtGui.QComboBox()
		for s in self.player.midioutputs:
			self.combo_midiout.addItem(s)
		self.combo_midiout.addItem("None")
		self.combo_midiout.activated[str].connect(self.change_midiout)

		self.label_thresh = self.just_label("Active Move%")
		self.spinbox_thresh = QtGui.QSpinBox()
		self.spinbox_thresh.setRange(0, 100)
		self.spinbox_thresh.setSingleStep(1)
		self.spinbox_thresh.valueChanged.connect(self.change_threshold)

		self.label_velocity = self.just_label("Velocity")
		self.spinbox_velocity = QtGui.QSpinBox()
		self.spinbox_velocity.setRange(1, 127)
		self.spinbox_velocity.setSingleStep(1)
		self.spinbox_velocity.valueChanged.connect(self.change_velocity)

		self.label_enabled = self.just_label("Enabled")
		self.checkbox_enabled = QtGui.QCheckBox()
		self.checkbox_enabled.stateChanged[int].connect(self.change_enabled)
		
		self.label_verbose = self.just_label("Verboseness")
		self.spinbox_verbose = QtGui.QSpinBox()
		self.spinbox_verbose.setRange(0, 2)
		self.spinbox_verbose.setSingleStep(1)
		self.spinbox_verbose.valueChanged[int].connect(self.change_verbose)
		
		self.label_channel = self.just_label("Channel")
		self.spinbox_channel = QtGui.QSpinBox()
		self.spinbox_channel.setRange(1, 17)
		self.spinbox_channel.setSingleStep(1)
		self.spinbox_channel.valueChanged.connect(self.change_channel)

		self.label_isscaled = self.just_label("Scaled")
		self.checkbox_isscaled = QtGui.QCheckBox()
		self.checkbox_isscaled.stateChanged[int].connect(self.change_isscaled)

		self.label_pitchmin = self.just_label("Pitch/Val Min")
		self.spinbox_pitchmin = QtGui.QSpinBox()
		self.spinbox_pitchmin.setRange(0, 120)
		self.spinbox_pitchmin.setSingleStep(1)
		self.spinbox_pitchmin.valueChanged[int].connect(self.change_pitchmin)
		# self.spinbox_pitchmin.valueChanged.connect(self.change_pitchmin)

		self.label_pitchmax = self.just_label("Pitch/Val Max")
		self.spinbox_pitchmax = QtGui.QSpinBox()
		self.spinbox_pitchmax.setRange(10, 128)
		self.spinbox_pitchmax.setSingleStep(1)
		self.spinbox_pitchmax.valueChanged[int].connect(self.change_pitchmax)

		self.label_activemin = self.just_label("Active Min%")
		self.spinbox_activemin = QtGui.QSpinBox()
		self.spinbox_activemin.setRange(0, 90)
		self.spinbox_activemin.setSingleStep(1)
		# self.spinbox_activemin.valueChanged[int].connect(self.change_activemin)
		self.spinbox_activemin.valueChanged.connect(self.change_activemin)

		self.label_activemax = self.just_label("Active Max%")
		self.spinbox_activemax = QtGui.QSpinBox()
		self.spinbox_activemax.setRange(10, 100)
		self.spinbox_activemax.setSingleStep(1)
		self.spinbox_activemax.valueChanged[int].connect(self.change_activemax)

		layout_master = QtGui.QGridLayout()
		layout_title = QtGui.QGridLayout()
		layout_globals = QtGui.QGridLayout()
		layout_settings = QtGui.QGridLayout()

		#######################################

		layout_title.addWidget(self.label_title, 0, 0, 1, 1)

		self.open_button = QtGui.QPushButton("Open Settings Directory")
		self.open_button.clicked.connect(self.do_open)
		# layout_title.addWidget(self.open_button, 0, 2, 1, 1)

		# self.help_button = QtGui.QPushButton("Help")
		# self.help_button.clicked.connect(self.do_help)
		# layout.addWidget(self.help_button, row, 3, 1, 1)

		#######################################

		row = 0
		ncols = 4

		row += 1
		layout_globals.addWidget(self.just_label(" "), row, 0, 1, ncols)

		row += 1
		layout_globals.addWidget(self.open_button, row, 1, 1, 2)

		row += 1
		layout_globals.addWidget(self.just_label(" "), row, 0, 1, ncols)

		row += 1
		layout_globals.addWidget(self.label_settingsname, row, 1, 1, 1, QtCore.Qt.AlignTop)
		layout_globals.addWidget(self.combo_settingsname, row, 2, 1, 1, QtCore.Qt.AlignTop)

		row += 1

		layout_globals.addWidget(self.label_tuioport, row, 1, 1, 1, QtCore.Qt.AlignTop)
		layout_globals.addWidget(self.spinbox_tuioport, row, 2, 1, 1, QtCore.Qt.AlignTop)

		row += 1
		layout_globals.addWidget(self.label_midiin, row, 1, 1, 1, QtCore.Qt.AlignTop)
		layout_globals.addWidget(self.combo_midiin, row, 2, 1, 1, QtCore.Qt.AlignTop)

		row += 1
		layout_globals.addWidget(self.label_midiout, row, 1, 1, 1, QtCore.Qt.AlignTop)
		layout_globals.addWidget(self.combo_midiout, row, 2, 1, 1, QtCore.Qt.AlignTop)

		row += 1
		layout_globals.addWidget(self.label_verbose, row, 1, 1, 1, QtCore.Qt.AlignTop)
		layout_globals.addWidget(self.spinbox_verbose, row, 2, 1, 1, QtCore.Qt.AlignTop)

		#######################################

		row += 1
		layout_settings.addWidget(self.label_behaviour, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_behaviour, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_enabled, row, 1, 1, 1)
		layout_settings.addWidget(self.checkbox_enabled, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_source, row, 1, 1, 1)
		layout_settings.addWidget(self.text_source, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_actiontype, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_actiontype, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_attribute, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_attribute, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_activemin, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_activemin, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_activemax, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_activemax, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_thresh, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_thresh, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_channel, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_channel, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_pitchmin, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_pitchmin, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_pitchmax, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_pitchmax, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_isscaled, row, 1, 1, 1)
		layout_settings.addWidget(self.checkbox_isscaled, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_scale, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_scale, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_key, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_key, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_quant, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_quant, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_duration, row, 1, 1, 1)
		layout_settings.addWidget(self.combo_duration, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_velocity, row, 1, 1, 1)
		layout_settings.addWidget(self.spinbox_velocity, row, 2, 1, 1)

		row += 1
		layout_settings.addWidget(self.label_message, row, 0, 1, ncols)

		#########################################

		layout_master.addLayout(layout_title, 0, 0, 1, 1)
		layout_master.addLayout(layout_globals, 1, 0, 1, 1)

		layout_master.addWidget(self.just_label("       "), 0, 1, 1, 1)

		layout_master.addLayout(layout_settings, 0, 2, 3, 1)
		layout_master.setAlignment(layout_settings, QtCore.Qt.AlignTop)

		self.setLayout(layout_master)

	def init_combo_behaviour(self):
		self.combo_behaviour.clear()
		for i in self.player.behaviournames:
			if self.currbehaviour == None:
				self.currbehaviour = i
			self.combo_behaviour.addItem(i)
		self.combo_behaviour.activated[str].connect(self.change_behaviour)

	def init_combo_settingsname(self):
		self.combo_settingsname.clear()
		dir = BehaviourSettings.settings_parentdir()
		settingsnames = [f.replace(".json","") for f in os.listdir(dir) if os.path.isdir(os.path.join(dir,f)) ]
		settingsnames.sort()
		ix = 0
		for i in settingsnames:
			self.combo_settingsname.addItem(i)
			if i == "current":
				current_ix = ix
			ix += 1
		self.combo_settingsname.activated[str].connect(self.change_settingsname)
		self.settingsname = "current"
		self.combo_settingsname.setCurrentIndex(current_ix)

	def just_label(self, s):
		# in case the label Alignment needs to be changed
		label = QtGui.QLabel(s)
		return label

	def set_player(self,player):
		self.player = player

	def do_help(self):
		self.helpwindow = HelpPopup()
		self.helpwindow.setGeometry(QtCore.QRect(300, 100, 400, 150))
		self.helpwindow.show()

	def do_open(self):
		os.system("start %s" % BehaviourSettings.settings_parentdir())

	def close_help(self):
		if self.helpwindow:
			self.helpwindow.close()

	def set_message(self, msg):
		self.label_message.setText(msg)

	def change_settingsname(self):
		self.settingsname = str(self.combo_settingsname.currentText())
		self.player.init_settings(self.settingsname)
		self.currbehaviour = None
		self.init_combo_behaviour()
		if self.currbehaviour:
			self.change_behaviour(self.currbehaviour, True)

	def change_tuioport(self, val):
		# print "Panel.change_tuioport val=",val
		self.spinbox_tuioport.setValue(val)
		self.player.set_tuioport(val)

	####### Behaviour

	def change_behaviour(self, val, gui=True):
		# print "Panel.change_behaviour=",val," gui=",gui
		val = str(val)
		self.currbehaviour = val
		fname = BehaviourSettings.behaviour_filename(self.settingsname,val)
		self.panelsettings = BehaviourSettings(fname)
		self.applySettings(self.panelsettings,gui=gui)
		self.player.behaviours[val].settings = self.panelsettings

		if gui:
			for ix in range(0, self.combo_behaviour.count()):
				if val == self.combo_behaviour.itemText(ix):
					# print "Found behaviour ix=",ix," val=",val
					self.combo_behaviour.setCurrentIndex(ix)
					break

	def write_settings(self):
		# we want to write self.panelsettings
		if not self.write_file_onchange:
			return
		bn = str(self.combo_behaviour.currentText())
		self.player.behaviours[bn].settings = self.panelsettings
		self.panelsettings.write_behaviour(self.settingsname,bn)

	def applySettings(self,s,gui):
		self.change_attribute(s.attribute,gui)
		self.change_actiontype(s.actiontype,gui)
		self.change_source(s.source,gui)
		self.change_activemin(s.activemin,gui)
		self.change_activemax(s.activemax,gui)
		self.change_pitchmin(s.valuemin,gui)
		self.change_pitchmax(s.valuemax,gui)
		self.change_threshold(s.threshold,gui)
		self.change_isscaled(s.isscaled,gui)
		self.change_channel(s.channel,gui)
		self.change_duration(s.duration,gui)
		self.change_enabled(s.enabled,gui)
		self.change_quant(s.quant,gui)
		self.change_scale(s.scale,gui)
		self.change_key(s.key,gui)
		self.change_velocity(s.velocity,gui)

	####### Midi Input

	def change_midiin(self, val):
		if not self.player.open_midiin(val):
			self.combo_midiin.setCurrentIndex(self.indexof_midiin("None"))
		else:
			i = self.indexof_midiin(val)
			self.combo_midiin.setCurrentIndex(i)

	def indexof_midiin(self, name):
		# Assumes that None is after all midiinputs
		if name == "None":
			return len(self.player.midiinputs)
		return self.player.midiinputs.index(name)

	####### Midi Output

	def change_midiout(self, val):
		if not self.player.open_midiout(val):
			self.combo_midiout.setCurrentIndex(self.indexof_midiout("None"))
		else:
			i = self.indexof_midiout(val)
			self.combo_midiout.setCurrentIndex(i)

	def indexof_midiout(self, name):
		# Assumes that None is after all midioutputs
		if name == "None":
			return len(self.player.midioutputs)
		return self.player.midioutputs.index(name)

	####### Duration

	def change_duration(self, val, gui=True):
		val = str(val)
		self.player.set_duration(val)
		self.panelsettings.duration = val
		if gui:
			for ix in range(0, self.combo_duration.count()):
				if val == self.combo_duration.itemText(ix):
					self.combo_duration.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Quant

	def change_quant(self, val, gui=True):
		val = str(val)
		self.player.set_quant(val)
		self.panelsettings.quant = val
		if gui:
			for ix in range(0, self.combo_quant.count()):
				if val == self.combo_quant.itemText(ix):
					self.combo_quant.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Scale

	def update_scalenotes(self):
		self.player.behaviours[self.currbehaviour].update_scalenotes()

	def change_scale(self, val, gui=True):
		val = str(val)
		self.player.set_scale(val)
		self.panelsettings.scale = val
		self.update_scalenotes()
		if gui:
			for ix in range(0, self.combo_scale.count()):
				if val == self.combo_scale.itemText(ix):
					self.combo_scale.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Key

	def change_key(self, val, gui=True):
		val = str(val)
		self.player.set_key(val)
		self.panelsettings.key = val
		self.update_scalenotes()
		if gui:
			ix = Key.names.index(val)
			self.combo_key.setCurrentIndex(ix)
			self.write_settings()

	####### Source

	def change_source(self, val, gui=True):
		val = str(val)
		self.player.set_source(val)
		self.panelsettings.source = val
		if self.currbehaviour:
			self.player.behaviours[self.currbehaviour].settings = self.panelsettings
		if gui:
			self.text_source.setText(val)
			self.write_settings()

	####### Attribute

	def change_attribute(self, val, gui=True):
		val = str(val)
		self.player.set_attribute(val)
		self.panelsettings.attribute = val
		if self.currbehaviour:
			self.player.behaviours[self.currbehaviour].settings = self.panelsettings
		if gui:
			for ix in range(0, self.combo_attribute.count()):
				if val == self.combo_attribute.itemText(ix):
					self.combo_attribute.setCurrentIndex(ix)
					self.write_settings()

	####### ActionType

	def change_actiontype(self, val, gui=True):
		val = str(val)
		self.player.set_actiontype(val)
		self.panelsettings.actiontype = val
		if self.currbehaviour:
			self.player.behaviours[self.currbehaviour].settings = self.panelsettings
		if gui:
			for ix in range(0, self.combo_actiontype.count()):
				if val == self.combo_actiontype.itemText(ix):
					self.combo_actiontype.setCurrentIndex(ix)
					self.write_settings()

	####### Threshold

	def change_threshold(self, val, gui=True):
		self.player.set_threshold(val)
		self.panelsettings.threshold = val
		if gui:
			self.spinbox_thresh.setValue(val)
			self.write_settings()

	####### Velocity

	def change_velocity(self, val, gui=True):
		self.player.set_velocity(val)
		self.panelsettings.velocity = val
		if gui:
			self.spinbox_velocity.setValue(val)
			self.write_settings()

	####### Enabled

	def change_enabled(self, val, gui=True):
		self.player.set_enabled(val)
		self.panelsettings.enabled = val
		if gui:
			self.checkbox_enabled.setChecked(val)
			self.write_settings()

	####### Verbose

	def change_verbose(self, val, gui=True):
		self.player.verbose = val
		if gui:
			self.spinbox_verbose.setValue(val)

	####### Channel

	def change_channel(self, val, gui=True):
		self.player.set_channel(val)
		self.panelsettings.channel = val
		if gui:
		  self.spinbox_channel.setValue(val)
		  self.write_settings()

	####### Scaleit

	def change_isscaled(self, val, gui=True):
		self.player.set_isscaled(val)
		self.panelsettings.isscaled = val
		if gui:
			self.checkbox_isscaled.setChecked(val)
			self.write_settings()

	####### Pitchmin

	def change_pitchmin(self, val, gui=True):
		self.player.set_pitchmin(val)
		self.panelsettings.valuemin = val
		if gui:
			self.spinbox_pitchmin.setValue(val)
			self.write_settings()

	####### Pitchmax

	def change_pitchmax(self, val, gui=True):
		self.player.set_pitchmax(val)
		self.panelsettings.valuemax = val
		if gui:
			self.spinbox_pitchmax.setValue(val)
			self.write_settings()

	####### activemin

	def change_activemin(self, val, gui=True):
		self.player.set_activemin(val)
		self.panelsettings.activemin = val
		if gui:
			self.spinbox_activemin.setValue(val)
			self.write_settings()

	####### activemax

	def change_activemax(self, val, gui=True):
		self.player.set_activemax(val)
		self.panelsettings.activemax = val
		if gui:
			self.spinbox_activemax.setValue(val)
			self.write_settings()
