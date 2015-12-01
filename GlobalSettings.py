import time
import json
import os
import sys
from traceback import *

class GlobalSettings(object):    # inherit from object, make it a newstyle class

	def __init__(self):
		self.first =  True
		self.read()

	def settings_dir(self, settingsname=None):
		root = os.getenv("TUIO2MIDI")
		if not root:
			root = "c:\\Users\\Public\\Documents\\Nosuch Media\\TUIO2MIDI"
		dir = os.path.join(root,"Settings")
		if self.first:
			print "Settings directory = ",dir
			self.first = False
		if settingsname:
			dir = os.path.join(dir,settingsname)
		return dir

	def global_filename(self):
		return os.path.join(self.settings_dir(),"global.json")

	def read(self):
		fname = self.global_filename()
		try:
			f = open(fname)
			s = f.read()
			j = json.loads(s)
			f.close()
			if j:
				self.tuioport = int(j["tuioport"])
				self.midiin = j["midiinput"]
				self.midiout = j["midioutput"]
				self.settingsname = j["settings"]
				self.depthmult = float(j["depthmult"])
				self.verbose = int(j["verboseness"])
		except:
			print "Error reading '%s': %s" % (fname,format_exc())

	def write(self):
		fname = self.global_filename()
		try:
		    f = open(fname,"w")
		    f.write("{\n")
		    f.write("\"tuioport\":%d,\n" % self.tuioport)
		    f.write("\"midiinput\":\"%s\",\n" % self.midiin)
		    f.write("\"midioutput\":\"%s\",\n" % self.midiout)
		    f.write("\"settings\":\"%s\",\n" % self.settingsname)
		    f.write("\"depthmult\":\"%f\",\n" % self.depthmult)
		    f.write("\"verboseness\":%d\n" % self.verbose)
		    f.write("}\n")
		    f.close()
		except:
			print "Error writing '%s': %s" % (fname,format_exc())

