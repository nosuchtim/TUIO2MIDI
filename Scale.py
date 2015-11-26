class Scale:

	list = {
		"Ionian": [0, 2, 4, 5, 7, 9, 11],
		"Dorian": [0, 2, 3, 5, 7, 9, 10],
		"Phrygian": [0, 1, 3, 5, 7, 8, 10],
		"Lydian": [0, 2, 4, 6, 7, 9, 11],
		"Mixolydian": [0, 2, 4, 5, 7, 9, 10],
		"Aeolian": [0, 2, 3, 5, 7, 8, 10],
		"Locrian": [0, 1, 3, 5, 6, 8, 10],
		"Newage": [0, 3, 5, 7, 10],
		"Fifths": [0, 7],
		"Octaves": [0],
		"Harminor": [0, 2, 3, 5, 7, 8, 11],
		"Melminor": [0, 2, 3, 5, 7, 9, 11],
		"Chromatic": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
		}

	@staticmethod
	def make_scalenotes(scalename,keyindex):

		# Construct an array of 128 elements with the mapped
		# pitch of each note to a given scale of notes
		sc = Scale.list[scalename]

		# Adjust the incoming scale to the current key
		realscale = []
		for i in range(len(sc)):
			realscale.append((sc[i] + keyindex) % 12)

		scalenotes = []
		# Make an array mapping each pitch to the closest scale note.
		# This code is brute-force, it starts at the pitch and
		# goes incrementally up/down from it until it hits a pitch
		# that's on the scale.
		for pitch in range(128):
			scalenotes.append(pitch)
			inc = 1
			sign = 1
			cnt = 0
			p = pitch
			# the cnt is just-in-case, to prevent an infinite loop
			while cnt < 100:
				if p >= 0 and p <= 127 and ((p % 12) in realscale):
					break
				cnt += 1
				p += (sign * inc)
				inc += 1
				sign = -sign
			if cnt >= 100:
				print "Something's amiss in set_scale!?"
				p = pitch
			scalenotes[pitch] = p

		print "make_scalenotes = ",scalenotes
		return scalenotes
