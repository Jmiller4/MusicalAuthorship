from music21 import *

def main():
        #get list of pieces
        piece = corpus.parse("bwv66.6")
        key = piece.analyze('key')
        chords = piece.chordify()
        chordList = []
        bassLine = []
        #romanizing the chords
        for chord in chords.recurse().getElementsByClass('Chord'):
                chordList.append(roman.romanNumeralFromChord(chord, key).figure)
        #figured bass line
        harmonies = figuredBass.checker.extractHarmonies(piece)
        for (offsets, notes) in sorted(harmonies.items()):
                bassLine.append([interval.Interval(note.Note(key.tonic), notes[0]).chromatic.semitones, interval.Interval(note.Note(key.tonic), notes[1]).chromatic.semitones, interval.Interval(note.Note(key.tonic),notes[2]).chromatic.semitones])
        print(chordList)
        print(bassLine)
        return chordList, bassLine
main()

