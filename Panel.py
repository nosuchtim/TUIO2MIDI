try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

from Scale import *
from BehaviourLogic import *
from BehaviourSettings import *
from Key import *
from Quant import *
from Duration import *

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

class Panel(QtGui.QGroupBox):

	def __init__(self,player):
		super(Panel, self).__init__("")

		self.settings = BehaviourSettings()
		self.player = player
		self.helpwindow = None

		self.label_top = self.just_label("")

		self.label_message = QtGui.QLabel("")

		self.label_title = QtGui.QLabel(" TUIO2MIDI")
		f = self.label_title.font()
		f.setPointSize(20)
		self.label_title.setFont(f)
		self.label_title.setAlignment(QtCore.Qt.AlignHCenter)
		# self.label_title.setAlignment(QtCore.Qt.AlignVCenter)

		self.label_tuioport = self.just_label("TUIO Port")
		self.spinbox_tuioport = QtGui.QSpinBox()
		self.spinbox_tuioport.setRange(3333, 9999)
		self.spinbox_tuioport.setSingleStep(1)
		self.spinbox_tuioport.valueChanged[int].connect(self.change_tuioport)

		self.label_scale = self.just_label("Scale")
		self.combo_scale = QtGui.QComboBox()
		for s in Scale.list:
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
		for i in Behaviours:
			self.combo_behaviour.addItem(i)
		self.combo_behaviour.activated[str].connect(self.change_behaviour)

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

		self.label_thresh = self.just_label("Threshold")
		self.spinbox_thresh = QtGui.QDoubleSpinBox()
		self.spinbox_thresh.setRange(0.0, 0.1)
		self.spinbox_thresh.setSingleStep(0.01)
		self.spinbox_thresh.setDecimals(2)
		self.spinbox_thresh.valueChanged[float].connect(self.change_threshold)

		self.label_velocity = self.just_label("Velocity")
		self.spinbox_velocity = QtGui.QSpinBox()
		self.spinbox_velocity.setRange(1, 127)
		self.spinbox_velocity.setSingleStep(1)
		self.spinbox_velocity.valueChanged.connect(self.change_velocity)

		self.label_blankheader = self.just_label("")

		self.label_enabled = self.just_label("Enabled")
		self.checkbox_enabled = QtGui.QCheckBox()
		self.checkbox_enabled.stateChanged[int].connect(self.change_enabled)
		
		self.label_channel = self.just_label("Channel")
		self.spinbox_channel = QtGui.QSpinBox()
		self.spinbox_channel.setRange(1, 17)
		self.spinbox_channel.setSingleStep(1)
		self.spinbox_channel.valueChanged.connect(self.change_channel)

		self.label_isscaled = self.just_label("Scaled")
		self.checkbox_isscaled = QtGui.QCheckBox()
		self.checkbox_isscaled.stateChanged[int].connect(self.change_isscaled)

		self.label_pitchmin = self.just_label("Pitch Min")
		self.spinbox_pitchmin = QtGui.QSpinBox()
		self.spinbox_pitchmin.setRange(0, 120)
		self.spinbox_pitchmin.setSingleStep(1)
		self.spinbox_pitchmin.valueChanged[int].connect(self.change_pitchmin)
		# self.spinbox_pitchmin.valueChanged.connect(self.change_pitchmin)

		self.label_pitchmax = self.just_label("Pitch Max")
		self.spinbox_pitchmax = QtGui.QSpinBox()
		self.spinbox_pitchmax.setRange(10, 128)
		self.spinbox_pitchmax.setSingleStep(1)
		self.spinbox_pitchmax.valueChanged[int].connect(self.change_pitchmax)

		self.label_activemin = self.just_label("Active Min")
		self.spinbox_activemin = QtGui.QSpinBox()
		self.spinbox_activemin.setRange(0, 90)
		self.spinbox_activemin.setSingleStep(1)
		# self.spinbox_activemin.valueChanged[int].connect(self.change_activemin)
		self.spinbox_activemin.valueChanged.connect(self.change_activemin)

		self.label_activemax = self.just_label("Active Max")
		self.spinbox_activemax = QtGui.QSpinBox()
		self.spinbox_activemax.setRange(10, 100)
		self.spinbox_activemax.setSingleStep(1)
		self.spinbox_activemax.valueChanged[int].connect(self.change_activemax)

		layout = QtGui.QGridLayout()

		ncols = 4

		row = 0
		layout.addWidget(self.label_title, row, 0, 1, ncols)

		self.help_button = QtGui.QPushButton("Help")
		self.help_button.clicked.connect(self.do_help)
		layout.addWidget(self.help_button, row, 3, 1, 1)

		# row += 1
		# layout.addWidget(self.createQuantGroup(),row,0,1,ncols)

		# row += 1
		# layout.addWidget(self.createDurationGroup(),row,0,1,ncols)

		row += 1
		layout.addWidget(self.label_top, row, 0, 1, ncols)

		row += 1

		layout.addWidget(self.label_tuioport, row, 1, 1, 1)
		layout.addWidget(self.spinbox_tuioport, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_midiin, row, 1, 1, 1)
		layout.addWidget(self.combo_midiin, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_midiout, row, 1, 1, 1)
		layout.addWidget(self.combo_midiout, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_blankheader, row, 0, 1, ncols)

		row += 1
		layout.addWidget(self.label_behaviour, row, 1, 1, 1)
		layout.addWidget(self.combo_behaviour, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_enabled, row, 1, 1, 1)
		layout.addWidget(self.checkbox_enabled, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_channel, row, 1, 1, 1)
		layout.addWidget(self.spinbox_channel, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_isscaled, row, 1, 1, 1)
		layout.addWidget(self.checkbox_isscaled, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_activemin, row, 1, 1, 1)
		layout.addWidget(self.spinbox_activemin, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_activemax, row, 1, 1, 1)
		layout.addWidget(self.spinbox_activemax, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_pitchmin, row, 1, 1, 1)
		layout.addWidget(self.spinbox_pitchmin, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_pitchmax, row, 1, 1, 1)
		layout.addWidget(self.spinbox_pitchmax, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_scale, row, 1, 1, 1)
		layout.addWidget(self.combo_scale, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_key, row, 1, 1, 1)
		layout.addWidget(self.combo_key, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_quant, row, 1, 1, 1)
		layout.addWidget(self.combo_quant, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_duration, row, 1, 1, 1)
		layout.addWidget(self.combo_duration, row, 2, 1, 1)

		# ETC...
		row += 1
		layout.addWidget(self.label_thresh, row, 1, 1, 1)
		layout.addWidget(self.spinbox_thresh, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_velocity, row, 1, 1, 1)
		layout.addWidget(self.spinbox_velocity, row, 2, 1, 1)

		row += 1
		layout.addWidget(self.label_message, row, 0, 1, ncols)

		self.setLayout(layout)

	def just_label(self, s):
		# in case the label Alignment needs to be changed
		label = QtGui.QLabel(s)
		return label

	def set_player(self,player):
		self.player = player

	def do_help(self):
		self.helpwindow = HelpPopup()
		self.helpwindow.setGeometry(QtCore.QRect(100, 100, 400, 550))
		self.helpwindow.show()

	def close_help(self):
		if self.helpwindow:
			self.helpwindow.close()

	def set_message(self, msg):
		self.label_message.setText(msg)

	def change_tuioport(self, val):
		print "Panel.change_tuioport val=",val
		self.spinbox_tuioport.setValue(val)
		self.player.set_tuioport(val)

	####### Behaviour

	def change_behaviour(self, val, gui=True):
		print "Panel.change_behaviour=",val," gui=",gui
		fn = "%s.json" % val
		self.settings = BehaviourSettings(fname=fn)
		self.applySettings(self.settings,gui=gui)
		if gui:
			for ix in range(0, self.combo_behaviour.count()):
				if val == self.combo_behaviour.itemText(ix):
					print "Found behaviour ix=",ix," val=",val
					self.combo_behaviour.setCurrentIndex(ix)
					break
		self.currbehaviour = val

	def write_settings(self):
		bn = self.combo_behaviour.currentText()
		fn = "%s.json" % bn
		self.settings.write_file(fn)

	def applySettings(self,s,gui):
		self.change_activemin(s.activemin,gui)
		self.change_activemax(s.activemax,gui)
		self.change_pitchmin(s.pitchmin,gui)
		self.change_pitchmax(s.pitchmax,gui)
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
		self.player.set_duration(str(val))
		self.settings.duration = str(val)
		if gui:
			for ix in range(0, self.combo_duration.count()):
				if val == self.combo_duration.itemText(ix):
					self.combo_duration.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Quant

	def change_quant(self, val, gui=True):
		self.player.set_quant(str(val))
		self.settings.quant = str(val)
		if gui:
			for ix in range(0, self.combo_quant.count()):
				if val == self.combo_quant.itemText(ix):
					self.combo_quant.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Scale

	def change_scale(self, val, gui=True):
		self.player.set_scale(str(val))
		self.settings.scale = str(val)
		if gui:
			for ix in range(0, self.combo_scale.count()):
				if val == self.combo_scale.itemText(ix):
					self.combo_scale.setCurrentIndex(ix)
					self.write_settings()
					break

	####### Key

	def change_key(self, val, gui=True):
		self.player.set_key(val)
		self.settings.key = val
		if gui:
			ix = Key.names.index(val)
			self.combo_key.setCurrentIndex(ix)
			self.write_settings()

	####### Threshold

	def change_threshold(self, val, gui=True):
		self.player.set_threshold(val)
		self.settings.threshold = val
		if gui:
			self.spinbox_thresh.setValue(val)
			self.write_settings()

	####### Velocity

	def change_velocity(self, val, gui=True):
		self.player.set_velocity(val)
		self.settings.velocity = val
		if gui:
			self.spinbox_velocity.setValue(val)
			self.write_settings()

	####### Enabled

	def change_enabled(self, val, gui=True):
		self.player.set_enabled(val)
		self.settings.enabled = val
		if gui:
			self.checkbox_enabled.setChecked(val)
			self.write_settings()

	####### Channel

	def change_channel(self, val, gui=True):
		self.player.set_channel(val)
		self.settings.channel = val
		if gui:
		  self.spinbox_channel.setValue(val)
		  self.write_settings()

	####### Scaleit

	def change_isscaled(self, val, gui=True):
		self.player.set_isscaled(val)
		self.settings.isscaled = val
		if gui:
			self.checkbox_isscaled.setChecked(val)
			self.write_settings()

	####### Pitchmin

	def change_pitchmin(self, val, gui=True):
		self.player.set_pitchmin(val)
		self.settings.pitchmin = val
		if gui:
			self.spinbox_pitchmin.setValue(val)
			self.write_settings()

	####### Pitchmax

	def change_pitchmax(self, val, gui=True):
		self.player.set_pitchmax(val)
		self.settings.pitchmax = val
		if gui:
			self.spinbox_pitchmax.setValue(val)
			self.write_settings()

	####### activemin

	def change_activemin(self, val, gui=True):
		self.player.set_activemin(val)
		self.settings.activemin = val
		if gui:
			self.spinbox_activemin.setValue(val)
			self.write_settings()

	####### activemax

	def change_activemax(self, val, gui=True):
		self.player.set_activemax(val)
		self.settings.activemax = val
		if gui:
			self.spinbox_activemax.setValue(val)
			self.write_settings()
