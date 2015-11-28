class Attribute:
	names = {
		"CenterX" : "x",
		"CenterY" : "y",
		"Top" : "getValTop",
		"Bottom" : "getValBottom",
		"Right" : "getValRight",
		"Left" : "getValLeft",
		"Depth" : "getValDepth",
		}

	order = []
	for i in names:
		order.append(i)
	order.sort()

	@staticmethod
	def getorder():
		return order
