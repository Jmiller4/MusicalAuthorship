#from music21 import * maybe need this maybe not
import NGramModel
import convert
import piece
import os
import NGLearner
import math

def predict(piece, learners, n):
	bestMatch = ""
	bestProb = -9999999

	totalChordGrams = 0
	totalBassGrams = 0
	for learner in learners.keys():
		totalChordGrams += learners[learner].getChords().total_grams[1]
		totalBassGrams += learners[learner].getFB().total_grams[1]

	for learner in learners.keys(): #check function/variable names here; it's a little long-winded
		thisBassProb = learners[learner].FB.giveProbabilityOfSequence(piece.getFBList(), n, totalBassGrams)
		thisChordProb = learners[learner].chords.giveProbabilityOfSequence(piece.getChordList(), n, totalChordGrams)
		thisProb = ((thisBassProb+thisChordProb)/2) #gets average of n-gram probabilities of figured bass & chords for this piece and composer

		if (thisProb > bestProb):
			bestProb = thisProb
			bestMatch = learner

	return bestMatch


def train(n):
	learners = {} #{composer name: NGLearner object}

	currdir = os.path.dirname(__file__) #the absolute filepath to the directory containing main.py
	folderpath = "mxl_files" #the subdirectory containing our training data
	finalPath = os.path.join(currdir, folderpath) #concatenate the two paths for use

	for composer in os.listdir(finalPath): #mxl_files is full of folders corresponding to composers; inside is all pieces of theirs to train with
		if (composer != ".DS_Store"): 
			print("checking composer ", composer)
			nextPath = os.path.join(finalPath, composer) #the path to this composer folder

			composerFB = NGramModel.N_Gram_Model(n, True) #the learner for figured bass
			composerChords = NGramModel.N_Gram_Model(n, False) #the learner for chords

			if (os.path.isdir(nextPath)): #if this is a folder
				print("in folder")
				for piece in os.listdir(nextPath): #loop through all pieces by the corresponding composer
				    print("checking piece", piece)
				    if piece.endswith(".mxl"): #if the file is .mxl format (it should be)
				    	piecePath = os.path.join(nextPath, piece)
				    	C = convert.Converter(piecePath)
				    	C.convert() #convert the file

				    	composerFB.train(C.getBass()) #train on this piece's figured bass for this composer
				    	composerChords.train(C.getChords()) #train on this piece's chords for this composer

			print("creating learner object for composer", composer)
			
			toAdd = NGLearner.learner(composerFB, composerChords) #create the learner object
			print("adding learner")
			learners[composer] = toAdd #add it to the learners dictionary
		
	return learners

def main():
	toPredict = ""
	while (toPredict != 'exit'): #TODO: only relearn if n is different
		toPredict = input("Please specify the filepath to a .mxl score to predict, or type 'exit' to quit: ")
		n = eval(input("What length n-gram model? "))

		learners = train(n) #list of piece objects to train on

		print (learners) #to test, for now

		x = os.path.dirname(__file__) #get filepath to input file
		testPath = os.path.join(x, toPredict)

		PC = convert.Converter(testPath) #piece converter initialization
		PC.convert() #convert the piece
		pieceToPredict = piece.Piece(PC.getBass(), PC.getChords()) #create the piece python object

		bestGuess = predict(pieceToPredict, learners, n) #return the best guess prediction

		print("I'm pretty sure that", toPredict, "was composed by", bestGuess)

main()

#TODO: experiment with a main that after making a prediction, adds the predicted piece to that n-gram's training data; 
#sort of a semi evolutionary algorithm
