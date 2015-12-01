import os
import shutil
import time
import json

from nosuch.midiutil import *
from nosuch.midipypm import *
from Sid import *
from BehaviourLogic import *
from BehaviourSettings import *
from Quant import *
from Scale import *
from Key import *
from Duration import *

class Player():

	def __init__(self,settingsname):

		self.sids = {}   # index is sid name, value is SidInstance

		self.panel = None
		self.verbose = 0
		self.midinotesdown = 0

		self.midi = MidiPypmHardware()
		self.midiinputs = self.midi.input_devices()
		self.midioutputs = self.midi.output_devices()
		self.midiout = None
		self.midiin = None

		self.time0 = time.time()

		Midi.callback(self.midicallback, "")

		self.init_settings(settingsname)

	def init_settings(self,settingsname):
		dir = BehaviourSettings.settings_dir(settingsname)
		try:
			os.stat(dir)
		except:
			# directory doesn't exist?
			os.makedirs(dir)
			# Copy stuff from "current" settings
			currentdir = BehaviourSettings.settings_dir("current")
			for fn in os.listdir(currentdir):
				src = os.path.join(currentdir,fn)
				dst = os.path.join(dir,fn)
				print "Copying %s to %s" % (src,dst)
				shutil.copyfile(src,dst)

		self.behaviournames = [f.replace(".json","") for f in os.listdir(dir) if os.path.isfile(os.path.join(dir,f)) and f.endswith(".json")]
		self.behaviournames.sort()

		self.behaviours = {}
		for b in self.behaviournames:
			fn = BehaviourSettings.behaviour_filename(settingsname,b)
			bs = BehaviourSettings(fn)     # load settings from file
			# print "Creating behaviour named '%s' in '%s' settings" % (b,settingsname)
			self.behaviours[b] = AttributeBehaviour(self,bs)

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
		# print "Player.set_tuioport ",port
		# self.panel.change_tuioport(port)
		pass

	def set_midiout(self, name):
		self.open_midiout(name)

	def set_midiin(self, name):
		self.open_midiin(name)

	def set_threshold(self, v):
		self.threshold = v

	def set_velocity(self, v):
		self.velocity = v

	def set_enabled(self, b):
		self.enabled = b

	def set_channel(self, v):
		self.channel = v

	def set_isscaled(self, v):
		self.isscaled = v

	def set_pitchmin(self, v):
		self.pitchmin = v

	def set_pitchmax(self, v):
		self.pitchmax = v

	def set_activemin(self, v):
		self.activemin = v

	def set_activemax(self, v):
		self.activemax = v

	def set_duration(self, nm):
		if not (nm in Duration.vals):
			print "No such duration: ", nm
			return
		self.duration = Duration.vals[nm]

	def set_quant(self, nm):
		if not (nm in Quant.vals):
			print "No such quant: ", nm
			return
		# self.quant = Quant.vals[nm]
		# print "Player.set_quant=",nm
		pass

	def set_source(self, nm):
		self.source = nm

	def set_attribute(self, nm):
		if not (nm in Attribute.names):
			print "No such attribute: ", nm
			return
		self.attribute = nm

	def set_actiontype(self, nm):
		self.actiontype = nm

	def set_key(self, nm):
		if not (nm in Key.names):
			print "No such key: ", nm
			return
		# print "Player.set_key=", nm
		pass

	def set_scale(self,nm):
		self.scale = nm

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
			print "MIDI input set to: %s" % name
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
			print "MIDI output set to: %s" % name
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
		if self.verbose:
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
			self.behaviours[b].updateSidState(newstate)

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
					if source.find(self.source) < 0:
						return
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

