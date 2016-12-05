from music21 import *

def main():
	#get list of pieces
	piece = corpus.parse("bwv66.6")
	key = piece.analyze('key')
	chords = piece.chordify()
	
	timeList = []
	print(len(piece))
	#romanizing the chords
	for chord in chords.recurse().getElementsByClass('Chord'):
		print(chord.measureNumber, chord.beatStr, roman.romanNumeralFromChord(chord, key))
	#figured bass line
	harmonies = figuredBass.checker.extractHarmonies(piece)
	for (offsets, notes) in sorted(harmonies.items()):
		print("{0!s:15}[{1!s:23}{2!s:23}{3!s:22}]".format(offsets, notes[0], notes[1], notes[2]))
main() 
