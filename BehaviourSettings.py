import os
import time
import json

from Scale import *
from nosuch.midiutil import *
from nosuch.midipypm import *

class BehaviourSettings(object):    # inherit from object, make it a newstyle class

	def __init__(self, fname=None, j=None):
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
			self.attribute = j["attribute"]

			if not "source" in j:
				self.source = ""  # default, matches everything
			else:
				self.source = j["source"]

			if not "actiontype" in j:
				self.actiontype = "Note"  # default, matches everything
			else:
				self.actiontype = j["actiontype"]

			self.activemin = j["activemin"]
			self.activemax = j["activemax"]
			self.valuemin = j["valuemin"]
			self.valuemax = j["valuemax"]
			self.threshold = j["threshold"]
			self.scale = j["scale"]
			self.isscaled = j["isscaled"]
			self.key = j["key"]
			self.channel = j["channel"]
			self.duration = j["duration"]
			self.quant = j["quant"]
			self.velocity = j["velocity"]

	@staticmethod
	def settings_parentdir():
		return "Settings"

	@staticmethod
	def settings_dir(settingsname):
		return os.path.join(BehaviourSettings.settings_parentdir(),settingsname)

	@staticmethod
	def behaviour_filename(settingsname,behaviourname):
		return "%s/%s.json" % (BehaviourSettings.settings_dir(settingsname),behaviourname)

	def write_behaviour(self,settingsname,behaviourname):
		# Make sure directory exists
		dn = BehaviourSettings.settings_dir(settingsname)
		try:
			os.stat(dn)
		except:
			# directory doesn't exist, probably
			os.makedirs(dn)

		fname = self.behaviour_filename(settingsname,behaviourname)
		try:
			f = open(fname,"w")
			if not f:
				print "Unable to open ",fname," for writing!?"
				return
			f.write("{\n")
			f.write("\"enabled\":%d,\n" % self.enabled)
			f.write("\"attribute\":\"%s\",\n" % self.attribute)
			f.write("\"actiontype\":\"%s\",\n" % self.actiontype)
			f.write("\"source\":\"%s\",\n" % self.source)
			f.write("\"activemin\":%d,\n" % self.activemin)
			f.write("\"activemax\":%d,\n" % self.activemax)
			f.write("\"valuemin\":%d,\n" % self.valuemin)
			f.write("\"valuemax\":%d,\n" % self.valuemax)
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
