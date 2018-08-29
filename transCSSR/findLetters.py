def getOutputAlphabet(filename):
	s = set()

	with open(filename) as f:
		while True:
			c = f.read(1)
			if not c:
				break
			s.add(c)

	myList = list(s)
	myList.sort()
	print myList
	print "ye"
	return myList

