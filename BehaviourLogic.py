import time

from Scale import *
from Quant import *
from Key import *
from Attribute import *
from nosuch.midiutil import *
from nosuch.midipypm import *

class BehaviourLogic(object):    # inherit from object, make it a newstyle class

	def __init__(self, player,settings):
		self.player = player
		self.sidstate = None
		self.lasttime = -1
		self.first = True
		self.settings = settings
		self.scalenotes = None

	def update_scalenotes(self):
		keyindex = Key.names.index(self.settings.key)
		self.scalenotes = Scale.make_scalenotes(self.settings.scale,keyindex)

	def updateSidState(self,newstate):

		if not self.settings.enabled:
			return

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
		
	def dragevent(self, newval):
		pass

	def diffSignificant(self, dv):
		threshval = (self.settings.threshold / 100.0)
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

	def playnote(self,pitch,velocity):

		if self.player == None:
			print "Behaviour.playnote called with player==None?"
			return

		s = self.settings
		if s.isscaled:
			if self.scalenotes == None:
				print "Hey, scalenotes is None?"
				return
			pitch = self.scalenotes[pitch]

		now = time.time()
		tm = self.nextquant(now, s.quant)
		if tm <= self.lasttime:
			# don't play two notes at the same time
			return
		self.lasttime = tm

		dur = Quant.vals[s.duration]
		ch = s.channel
		vel = s.velocity

		durclocks = Midi.clocks_per_second * dur
		n = SequencedNote(pitch=pitch, duration=durclocks, channel=ch, velocity=vel)
		if self.player.midiout:
			self.player.midiout.schedule(n, time=tm)
		else:
			print("No MIDI output, trying to play pitch=%d channel=%d velocity=%d" % (n.pitch, n.channel, n.velocity))

		if self.player.verbose > 0:
			print "playnote pitch=",pitch," dur=",dur," chan=",ch," tm=",(tm-self.player.time0)

	def playcontroller(self,value,ctrl):

		if self.player == None:
			print "Behaviour.playcontroller called with player==None?"
			return

		s = self.settings

		now = time.time()
		ch = s.channel

		msg = Controller( controller=ctrl, channel=ch, value=value)
		n = SequencedMidiMsg(msg)
		if self.player.midiout:
			self.player.midiout.schedule(n, time=now)
		else:
			print("No MIDI output, trying to play controller=%d value=%d chan=%d" % (ctrl,value,ch))

		if self.player.verbose > 0:
			print "playcontroller ctrl=",ctrl," val=",value," chan=",ch," now=",(now-self.player.time0)


class AttributeBehaviour(BehaviourLogic):

	def __init__(self, player, settings):
		BehaviourLogic.__init__(self,player,settings)

	def getVal(self, state):
		attrname = Attribute.names[self.settings.attribute]
		if attrname.startswith("getVal"):
			f = getattr(self,attrname)
			v = f(state)
		else:
			v = getattr(state,attrname)

		if self.player.verbose > 1:
			print "Value of %s is %.3f" % (self.settings.attribute,v)

		return v

	def getValTop(self,state):
		return state.y + (state.h/2.0)

	def getValBottom(self,state):
		return state.y - (state.h/2.0)

	def getValRight(self,state):
		return state.x + (state.w/2.0)

	def getValLeft(self,state):
		return state.x - (state.w/2.0)

	def getValDepth(self,state):
		return state.z

	def doAction(self):

		s = self.settings

		amin = s.activemin / 100.0
		amax = s.activemax / 100.0
		val = self.getVal(self.sidstate)
		# See if we're in an active part
		if val < amin:
			return
		if val > amax:
			return

		dval = s.valuemax - s.valuemin
		value = s.valuemin + dval * (val - amin) / (amax - amin)
		value = int(value) # should this be rounded?

		a = self.settings.actiontype
		if a == "Note":
			self.playnote(value,self.settings.velocity)
		elif a == "Note (Velocity=Depth)":
			self.playnote(value,self.settings.z)
		elif a.find("Controller ") == 0:
			ctrl = int(a[11:])
			self.playcontroller(value,ctrl)
		else:
			print "Unknown actiontype=",self.settings.actiontype