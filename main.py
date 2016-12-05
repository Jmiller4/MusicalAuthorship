#from music21 import * maybe need this maybe not
import NGramModel
import convert
import piece
import os
import NGLearner



def train(n):
	learners = {} #{composer name: NGLearner object}

	currdir = os.path.dirname(__file__) #the absolute filepath to the directory containing main.py
	folderpath = "mxl_files" #the subdirectory containing our training data
	finalPath = os.path.join(currdir, folderpath) #concatenate the two paths for use

	for composer in os.listdir(finalPath): #mxl_files is full of folders corresponding to composers; inside is all pieces of theirs to train with
		nextPath = os.path.join(finalPath, composer) #the path to this composer folder

		composerFB = NGramModel.N_Gram_Model(n, True) #the learner for figured bass
		composerChords = NGramModel.N_Gram_Model(n, False) #the learner for chords

		if (os.path.isdir(nextPath)): #if this is a folder
			for piece in os.listdir(nextPath): #loop through all pieces by the corresponding composer
			    if piece.endswith(".mxl"): #if the file is .mxl format (it should be)
			    	piecePath = os.path.join(nextPath, piece)
			    	C = convert.Converter(piecePath)
			    	C.convert() #convert the file

			    	composerFB.train(C.getBass()) #train on this piece's figured bass for this composer
			    	composerChords.train(C.getChords()) #train on this piece's chords for this composer
		toAdd = NGLearner.learner(composerFB, composerChords)
		learners[composer] = toAdd

	return learners

def main():
	pieceToPredict = input("Please specify the filepath to a .mxl score: ")
	n = eval(input("What length n-gram model? "))

	learners = train(n) #list of piece objects to train on

	print (learners)

main()

#TODO: figure out how to get composer name from .mxl metadata, use this as a 'label.'
#To predict given a new .mxl file, run a converter on it, then loop through all n-gram objects and find which one returns the highest probability; 
#this is our predicted composer label (experiment with n-grams that represent styles instead of composers;
#also, experiment with a main that after making a prediction, adds the predicted piece to that n-gram's training data, semi evolutionary algorithm)