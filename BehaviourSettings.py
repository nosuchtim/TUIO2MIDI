import time
import json

from Scale import *
from nosuch.midiutil import *
from nosuch.midipypm import *

class BehaviourSettings(object):    # inherit from object, make it a newstyle class

	def __init__(self, j=None, fname=None):
		if fname:
			try:
				f = open(fname)
				lines = f.readlines()
				s = ""
				for ln in lines:
					s += str(ln.strip())
				j = json.loads(s)
				f.close()
			except:
				print "Error reading '%s': %s" % (fname,format_exc())
				j = None

		if j:
			self.enabled = j["enabled"]
			self.activemin = j["activemin"]
			self.activemax = j["activemax"]
			self.pitchmin = j["pitchmin"]
			self.pitchmax = j["pitchmax"]
			self.threshold = j["threshold"]
			self.scale = j["scale"]
			self.isscaled = j["isscaled"]
			self.key = j["key"]
			self.channel = j["channel"]
			self.duration = j["duration"]
			self.quant = j["quant"]
			self.velocity = j["velocity"]

	def write_file(self,fname):
		try:
			f = open(fname,"w")
			if not f:
				print "Unable to open ",fname," for writing!?"
				return
			f.write("{\n")
			f.write("\"enabled\":%d,\n" % self.enabled)
			f.write("\"activemin\":%d,\n" % self.activemin)
			f.write("\"activemax\":%d,\n" % self.activemax)
			f.write("\"pitchmin\":%d,\n" % self.pitchmin)
			f.write("\"pitchmax\":%d,\n" % self.pitchmax)
			f.write("\"threshold\":%f,\n" % self.threshold)
			f.write("\"scale\":\"%s\",\n" % self.scale)
			f.write("\"isscaled\":%d,\n" % self.isscaled)
			f.write("\"key\":\"%s\",\n" % self.key)
			f.write("\"channel\":%d,\n" % self.channel)
			f.write("\"duration\":\"%s\",\n" % self.duration)
			f.write("\"quant\":\"%s\",\n" % self.quant)
			f.write("\"velocity\":%d\n" % self.velocity)
			f.write("}\n")
			f.close()
		except:
			print "Error writing '%s': %s" % (fname,format_exc())
