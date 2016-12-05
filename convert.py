
from music21 import *

class Converter:

	def __init__(self, file):
		self.file = file
		self.chords = []
		self.bass = []

	def convert(self):
		#get list of pieces
		piece = converter.parse(self.file)
		key = piece.analyze('key')
		chords = piece.chordify()
		#romanizing the chords
		for chord in chords.recurse().getElementsByClass('Chord'):
			self.chords.append(roman.romanNumeralFromChord(chord, key).figure)
		#figured bass line
		harmonies = figuredBass.checker.extractHarmonies(piece)
		for (offsets, notes) in sorted(harmonies.items()):
			addList = []
			for i in range(0, len(notes)):
				if (notes[i].isNote):
					addList.append(interval.Interval(note.Note(key.tonic), notes[i]).chromatic.semitones)
				elif (notes[i].isRest):
					addList.append(notes[i])
			self.bass.append(addList)
	def getBass(self):
		return self.bass
	def getChords(self):
		return self.chords	


