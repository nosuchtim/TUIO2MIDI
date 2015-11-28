class Attribute:
	names = {
		"Center X" : "x",
		"Center Y" : "y",
		"Top" : "getValTop",
		"Bottom" : "getValBottom",
		"Right" : "getValRight",
		"Left" : "getValLeft",
		}

	order = []
	for i in names:
		order.append(i)
	order.sort()

	@staticmethod
	def getorder():
		return order
