class Piece():
	def __init__(self, FB, chords):
		self.FBList = FB
		self.chordList = chords

	def setFBList(self, FB):
		self.FBList = FB

	def setChordList(self, chords):
		self.chordList = chords

	def getFBList(self):
		return self.FBList

	def getChordList(self):
		return self.chordList