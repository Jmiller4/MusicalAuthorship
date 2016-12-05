from music21 import *
import N-GramModel
import convert
import piece


def fillTrainingList():
	return 0

def main():
	pieceToPredict = input("Please specify the filepath to a .mxl score: ")
	n = eval(input("What length n-gram model? "))

	for filename in os.listdir('/mxl files'):
	    if filename.endswith(".mxl"): 
	        print(os.path.join(directory, filename))
	        continue
	    else:
	        continue

	trainingPieces = fillTrainingList() #list of piece objects to train on

	converter = convert.Converter() #for-loop

	ngramFB = N-GramModel.N_Gram_Model(n, True) #the learner for figured bass
	ngramChords = N-GramModel.N_Gram_Model(n, False) #the learner for chords

	FB = converter.getFBList()
	chords = converter.getChordList()


	#loop these over all pieces in trainingPieces
	ngramFB.train(FB) #trains figured bass
	ngramChords.train(chords) #trains chords

	return 0

main()

#TODO: figure out how to get composer name from .mxl metadata, use this as a 'label.'
#To predict given a new .mxl file, run a converter on it, then loop through all n-gram objects and find which one returns the highest probability; 
#this is our predicted composer label (experiment with n-grams that represent styles instead of composers;
#also, experiment with a main that after making a prediction, adds the predicted piece to that n-gram's training data, semi evolutionary algorithm)