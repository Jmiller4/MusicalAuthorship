class learner():

	def __init__(self, FBLearner, chordLearner):
		self.FB = FBLearner
		self.chords = chordLearner

	def getFB(self):
		return self.FB

	def getChords(self):
		return self.chords