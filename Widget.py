try:
	from PySide import QtCore, QtGui
except ImportError:
	from PyQt4 import QtCore, QtGui

from Panel import *

class Widget(QtGui.QWidget):

	def __init__(self,player,settingsname):

		super(Widget, self).__init__()
		
		self.debug = 2
		# self.midinotesdown = 0
		self.keyindex = 0    # in keynames, also used as pitch offset

		x, y, w, h = 500, 200, 100, 100
		self.setGeometry(x, y, w, h)

		self.panel = Panel(player,settingsname)

		self.layout = QtGui.QHBoxLayout()
		self.layout.addWidget(self.panel)
		self.setLayout(self.layout)

		self.setWindowTitle("TUIO2MIDI")

	def show_and_raise(self):
		self.show()
		self.raise_()

	def closeEvent(self, evt):
		self.panel.close_help()