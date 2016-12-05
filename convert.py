from music21 import *

class Convert:

	def __init__(self, file):
		self.file = file
		self.chords = []
		self.bass = []
	def convert(self):
		#get list of pieces
		piece = corpus.parse(self.file)
		key = piece.analyze('key')
		chords = piece.chordify()
		#romanizing the chords
		for chord in chords.recurse().getElementsByClass('Chord'):
			self.chords.append(roman.romanNumeralFromChord(chord, key).figure)
		#figured bass line
		harmonies = figuredBass.checker.extractHarmonies(piece)
		for (offsets, notes) in sorted(harmonies.items()):
			self.bass.append([interval.Interval(note.Note(key.tonic), notes[0]).chromatic.semitones, interval.Interval(note.Note(key.tonic), notes[1]).chromatic.semitones, interval.Interval(note.Note(key.tonic),notes[2]).chromatic.semitones])
	def getBass(self):
		return self.bass
	def getChords(self):
		return self.chords	


