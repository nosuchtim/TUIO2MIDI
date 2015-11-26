from nosuch.midiutil import *
from nosuch.midipypm import *
from Sid import *
from BehaviourLogic import *
from BehaviourSettings import *
from Quant import *
from Scale import *
from Key import *
from Duration import *

import json

class Player():

	def __init__(self):

		self.sids = {}   # index is sid name, value is SidInstance

		self.panel = None
		self.debug = 2
		self.midinotesdown = 0

# 		# These are not the defaults
# 		self.channel = 0
# 		self.pitchmin = 40
# 		self.pitchmax = 100
# 		self.activemin = 10
# 		self.activemax = 90
# 		self.isscaled = True

		self.keyindex = 0    # in keynames, also used as pitch offset

		self.midi = MidiPypmHardware()
		self.midiinputs = self.midi.input_devices()
		self.midioutputs = self.midi.output_devices()
		self.midiout = None
		self.midiin = None

		Midi.callback(self.midicallback, "")

		self.behaviours = {}
		for b in Behaviours:
			# load settings from file
			fn = "%s.json" % b
			bs = BehaviourSettings(fname=fn)
			self.behaviours[b] = Behaviours[b](self,bs)

		# x, y, w, h = 500, 200, 100, 100
		# self.setGeometry(x, y, w, h)

		# self.panel = Panel(self, midiinputs, midioutputs, self.keynames)
		# self.layout = QtGui.QHBoxLayout()
		# self.layout.addWidget(self.panel)
		# self.setLayout(self.layout)
		# self.setWindowTitle("TUIO2MIDI")
		
	def set_message(self, msg):
		self.panel.set_message(msg)

	def set_panel(self,panel):
		self.panel = panel
	
	def send_testnote(self):
		# Send a test note to see if MIDI output is alive
		nt = SequencedNote(pitch=60, duration=12, channel=1, velocity=100)
		self.midiout.schedule(nt)

	def send_program(self, ch, prog):
		if self.midiout and ch > 0 and prog > 0:
			p = Program(channel=ch, program=prog)
			self.midiout.schedule(p)

	def set_tuioport(self, port):
		print "Player.set_tuioport ",port
		# self.panel.change_tuioport(port)

	def set_midiout(self, name):
		print "Player.set_midiout needs work?"

	def set_midiin(self, name):
		print "Player.set_midiin needs work?"

	def set_threshold(self, v):
		print "Player.set_threshold ", v
		self.threshold = v

	def set_velocity(self, v):
		print "Player.set_velocity ", v
		self.velocity = v

	def set_enabled(self, b):
		print "Player.set_enabled ", b
		self.enabled = b

	def set_channel(self, v):
		print "Player.set_channel ", v
		self.channel = v

	def set_isscaled(self, v):
		print "Player.set_isscaled ", v
		self.isscaled = v

	def set_pitchmin(self, v):
		print "Player.set_pitchmin ", v
		self.pitchmin = v

	def set_pitchmax(self, v):
		print "Player.set_pitchmax ", v
		self.pitchmax = v

	def set_activemin(self, v):
		print "Player.set_activemin ", v
		self.activemin = v

	def set_activemax(self, v):
		print "Player.set_activemax ", v
		self.activemax = v

	def set_duration(self, nm):
		if not (nm in Duration.vals):
			print "No such duration: ", nm
			return
		print "Player.set_duration=", nm
		self.duration = Duration.vals[nm]

	def set_quant(self, nm):
		if not (nm in Quant.vals):
			print "No such quant: ", nm
			return
		self.quant = Quant.vals[nm]
		print "Player.set_quant=",nm

	def set_key(self, nm):
		if not (nm in Key.names):
			print "No such key: ", nm
			return
		print "Player.set_key=", nm
		self.keyindex = Key.names.index(nm)
		self.scalenotes = Scale.make_scalenotes(self.scale,self.keyindex)

	def set_scale(self,nm):
		print "Player.set_scale nm=",nm
		self.scale = nm
		self.scalenotes = Scale.make_scalenotes(self.scale,self.keyindex)

	def open_midiin(self, name):
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
			print("Error opening MIDI input: %s, exception: %s" % (name, format_exc()))
			self.midiin = None
			return False;

		return True

	def open_midiout(self, name):
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
			print("Error opening MIDI output: %s, exception: %s" % (name, format_exc()))
			self.midiout = None
			return False;

		return True

	# def show_and_raise(self):
	# 	self.show()
	# 	self.raise_()

	# def closeEvent(self, evt):
	# 	self.panel.close_help()

	def midicallback(self, msg, data):
		if self.debug > 0:
			print("MIDI INPUT = %s" % str(msg))
		m = msg.midimsg

		if isinstance(m, NoteOn):
			self.midinotesdown += 1
			if self.midinotesdown == 1:
				self.currentchord = [m.pitch]
			else:
				self.currentchord.append(m.pitch)
			print "currentchord = ",self.currentchord

		elif isinstance(m, NoteOff):
			self.midinotesdown -= 1

		elif isinstance(m, Controller):
			if self.midiout:
				self.midiout.schedule(m)

	def updateSidState(self, sid, fseq, newstate):

		if not sid in self.sids:
			self.sids[sid] = SidInstance(self)
			
		for b in self.behaviours:
			bl = self.behaviours[b]
			bl.updateSidState(newstate)

	def pitchof(self, state):
		x = state.x
		# Make sure x is from 0 to 1
		if x < 0.0:
			x = 0.0
		if x > 1.0:
			x = 1.0
		dp = self.pitchmax - self.pitchmin
		rawp = self.pitchmin + int(dp * x)
		if self.isscaled:
			p = self.scalenotes[rawp]
		else:
			p = rawp
		if self.debug > 1:
			print "PITCHOF x=%.3f p=%d   dp=%.3f int(dp*x)=%d" % (x, p, dp, int(dp * x))
		return p

	def velocityof(self, state):
		return int(self.z * 128.0)

	def channelof(self, state):
		# y = pos[1]
		# return 1 + (int(y * 16.0) % 16)
		return 1

	def quantof(self, state):
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

	def durationof(self, pos):
		# Returns duration in clocks.
		y = pos[1]
		# The higher you are, the longer the duration.
		b = Midi.clocks_per_second
		if y < 0.1:
			return 1
		if y < 0.2:
			return b / 16
		if y < 0.4:
			return b / 8
		if y < 0.6:
			return b / 4
		if y < 0.75:
			return b
		return b * 2

	def cursorDown(self, state):
		self.cursorDrag(state)

	def cursorUp(self, state):
		# print "Up sid=",state.sid," x=",state.x," y=",state.y," z=",state.z
		# self.cursorUpdate(state)
		pass

	def fullsid(self, sid, source):
		return "%d-%s" % (int(sid), source)

	def mycallback(self, ev, d):
		# print "Player.mycallback!"

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

		alive = {}
		for m in ev.oscmsg:
			lenm = len(m)
			if m[0] != "/tuio/25Dblb":
				continue
			if lenm < 3:
				continue
			if m[2] == "alive":
				for i in range(3, len(m)):
					fullsid = self.fullsid(m[i], source)
					alive[fullsid] = 1
				continue
			if m[2] == "set":
				fullsid = self.fullsid(m[3], source)
				newstate = SidState(fullsid, fseq)
				newstate.x = m[4]
				newstate.y = m[5]
				newstate.z = m[6]
				newstate.w = m[8]
				newstate.h = m[9]
				# print "Source=", source, " Fseq=", fseq, " set fullsid=", fullsid, " h=", newstate.h
				self.updateSidState(fullsid, fseq, newstate)
				continue

