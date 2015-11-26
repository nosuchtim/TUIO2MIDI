from nosuch.midiutil import *

class Duration:

		# duration values are in clocks
		cps = Midi.clocks_per_second
		order = [ "1/32", "1/16", "1/8", "1/4", "1/2", "1", "2", "Variable" ]
		vals = {
				"1/32": 0.03125 * cps,
				"1/16": 0.0625 * cps,
				"1/8": 0.125 * cps,
				"1/4": 0.25 * cps,
				"1/2": 0.5 * cps,
				"1": 1.0 * cps,
				"2": 2.0 * cps,
				"Variable":-1.0
				}
