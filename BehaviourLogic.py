import time

from Scale import *
from Quant import *
from nosuch.midiutil import *
from nosuch.midipypm import *

class BehaviourLogic(object):    # inherit from object, make it a newstyle class

	def __init__(self, player,settings):
		self.name = ""
		self.player = player
		self.sidstate = None
		self.lastaction = -1
		self.first = True
		self.settings = settings

	def updateSidState(self,newstate):

		if self.first:
			self.first = False
			self.setSidState(newstate)
			return

		dv = self.diffState(newstate)
		if self.diffSignificant(dv):
			self.setSidState(newstate)
			self.doAction()
		else:
			# Don't update state, so next diff is cumulative
			pass
		
#	def set_scale(self, nm):
#		print "Behaviour",self.name," set_scale=",nm
#		if not (nm in Scale.list):
#			print "No such scale: ", nm
#			return
#		self.scale = nm;
#		if self.player:
#			self.scalenotes = Scale.make_scalenotes(nm,0)
#		else:
#			self.scalenotes = None

	def dragevent(self, newval):
		pass

	def diffSignificant(self, dv):
		threshval = self.settings.threshold / 100.0
		# print "threshval=",threshval," dv=",dv
		if dv >= threshval:
			return True
		else:
			return False

	def nextquant(self, tm, qnm):
		# We assume values are in terms of seconds
		q = Quant.vals[qnm]
		if q <= 0:
			return tm
		q1000 = int(q * 1000)
		tm1000 = int(tm * 1000)
		tmq = tm1000 % q1000
		dq = (tmq / 1000.0)
		nextq = tm + (q - dq)
		return nextq

	def setSidState(self,sidstate):
		self.sidstate = sidstate

	def diffState(self, state1):
		d = abs(self.getVal(state1) - self.getVal(self.sidstate))
		return d

	def computeTime(self):
		now = time.time()
		tm = self.nextquant(now, self.settings.quant)
		if tm <= self.lastaction:
			# print "tm <= lastaction!?  too soon"
			return
		return tm


	def computePitch(self):
		settings = self.settings
		dpitch = settings.pitchmax - settings.pitchmin
		rawrange = 1.0
		amin = settings.activemin * rawrange / 100.0
		amax = settings.activemax * rawrange / 100.0
		# print "amin=",amin," amax=",amax

		v = self.getVal(self.sidstate)
		print "computePitch getVal=",v
		if v < amin:
			v = amin
		if v > amax:
			v = amax
		pitch = settings.pitchmin + dpitch * (v - amin) / (amax - amin)

		# should this be rounded?
		pitch = int(pitch)

		# print "new v = ",v," pitch=",pitch
		
		if settings.isscaled:
			pitch = self.player.scalenotes[pitch]
		return pitch

	def playnote(self):

		if self.player == None:
			print "Behaviour.playnote called with player==None?"
			return

		pitch = self.computePitch()
		tm = self.computeTime()
		dur = Quant.vals[self.settings.duration]
		ch = self.settings.channel
		vel = self.settings.velocity

		self.lastaction = tm
		n = SequencedNote(pitch=pitch, duration=dur, channel=ch, velocity=vel)
		if self.player.midiout:
			self.player.midiout.schedule(n, time=tm)
		else:
			print("No MIDI output, trying to play pitch=%d channel=%d velocity=%d" % (n.pitch, n.channel, n.velocity))

		print "playnote pitch=",pitch," dur=",dur," chan=",ch


class CenterYBehaviour(BehaviourLogic):

	def __init__(self, player,settings):
		BehaviourLogic.__init__(self,player,settings)
		self.name = "Center_Y"

	def getVal(self, state):
		return state.y

	def setVal(self, state, v):
		state.y = v

	def doAction(self):
		self.playnote()

class CenterXBehaviour(BehaviourLogic):

	def __init__(self, player, settings):
		BehaviourLogic.__init__(self,player,settings)
		self.name = "Center_X"

	def getVal(self, state):
		return state.x

	def setVal(self, state, v):
		state.x = v

	def doAction(self):
		self.playnote()


Behaviours = {
		"Center_Y": CenterYBehaviour,
		"Center_X": CenterXBehaviour
		}
