from music21 import MusicXMLImportException
import NGramModel
import convert
import piece
import os
import NGLearner
import math

def predict(piece, learners, n, chord_FB_split):
	bestMatch = ""
	bestProb = -99999999

	totalChordGrams = 0
	totalBassGrams = 0
	for learner in learners.keys():
		totalChordGrams += learners[learner].getChords().total_grams[1]
		totalBassGrams += learners[learner].getFB().total_grams[1]

	for learner in learners.keys(): #check function/variable names here; it's a little long-winded
		thisBassProb = learners[learner].FB.giveProbabilityOfSequence(piece.getFBList(), n, totalBassGrams, True)
		thisChordProb = learners[learner].chords.giveProbabilityOfSequence(piece.getChordList(), n, totalChordGrams, True)

		if (chord_FB_split > 1.0) | (chord_FB_split < 0.0):
			print("WARNING: illegal chord_FB_split of", chord_FB_split)
			print("reverting to 0.5")
			chord_FB_split = 0.5

		chordWeight = chord_FB_split
		FBWeight = 1.0 - chord_FB_split

		thisProb = (chordWeight * thisChordProb) + (FBWeight * thisBassProb) #gets a weighted average of n-gram probabilities of figured bass & chords for this piece and composer

		if (thisProb > bestProb):
			bestProb = thisProb
			bestMatch = learner

	return bestMatch


def processTestSet():
	testPieces = {} #{composer name: piece object}

	currdir = os.path.dirname(__file__) #the absolute filepath to the directory containing main.py
	folderpath = "test_set" #the subdirectory containing our training data
	finalPath = os.path.join(currdir, folderpath) #concatenate the two paths for use

	for composer in os.listdir(finalPath): #test_set is full of folders corresponding to composers; inside is all pieces of theirs to train with
		testPieces[composer] = []
		if (composer != ".DS_Store"):
			nextPath = os.path.join(finalPath, composer) #the path to this composer folder
			if (os.path.isdir(nextPath)): #if this is a folder
				for testPiece in os.listdir(nextPath): #loop through all pieces by the corresponding composer
					if testPiece.endswith(".mxl"): #if the file is .mxl format (it should be)
						piecePath = os.path.join(nextPath, testPiece)
						C = convert.Converter(piecePath)
						C.convert() #convert the file
						toAdd = piece.Piece(C.getBass(), C.getChords())
						testPieces[composer].append(toAdd)
	return testPieces


#the error we were getting is:  music21.musicxml.xmlToM21.MusicXMLImportException
#you might just be able to reference it as music21.MusicXMLImportException

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
				    	try:
				    		C.convert() #convert the file
				    	except MusicXMLImportException:
				    		continue

				    	composerFB.train(C.getBass()) #train on this piece's figured bass for this composer
				    	composerChords.train(C.getChords()) #train on this piece's chords for this composer

			print("creating learner object for composer", composer)
			
			toAdd = NGLearner.learner(composerFB, composerChords) #create the learner object
			print("adding learner")
			learners[composer] = toAdd #add it to the learners dictionary
		
	return learners

#this function runs a set of N-gram models on testing data, given some hyperparameters
#it returns a list with lots of information about how testing went
def testWithParameters(testing, learners, n, backoff, chord_FB_split):

	infoDict = {}
	infoDict["n"] = str(n)
	infoDict["backoff"] = str(backoff)
	infoDict["chord_FB_split"] = str(chord_FB_split)
	infoDict["filename"] = "NGramModel_N"+str(n)+"_backoff"+str(backoff)+"_ChordBassSplit"+str(chord_FB_split)+".csv"

	total = 0
	correct = 0
	matrix = {} #the confusion matrix. It's indexed by predicted label, actual label

	labelList = list(learners.keys())
	for l1 in labelList:
		matrix[l1] = {}
		for l2 in labelList:
			matrix[l1][l2] = 0

	for composer in testing.keys():
		for piece in testing[composer]:

			bestGuess = predict(piece, learners, n, chord_FB_split) #return the best guess prediction

			if composer == bestGuess:
				correct += 1
			total += 1
			matrix[bestGuess][composer] += 1

	#Making the confusion matrix as a string
	confusionMatrix = ""
	strTop = ""
	for l in range(len(labelList)):
		strTop = strTop + labelList[l]
		if l + 1 != len(labelList):
			strTop = strTop + ","
	confusionMatrix += strTop + "\n"
	for i in range(len(labelList)):
		strLine = ""
		for j in range(len(labelList)):
			strLine += str(matrix[labelList[j]][labelList[i]])
			strLine += ","
		strLine += labelList[i]
		confusionMatrix += strLine + "\n"

	infoDict["matrix"] = confusionMatrix

	return list([infoDict, correct, total, (float(correct) / total), matrix]) #this last item in the list, "matrix", is the dictionary of the confusion matrix, rather than the string of the confusion matrix

def main2():
	toPredict = ""

	n = 10

	learners = train(n) #list of piece objects to train on

	print (learners) #to test, for now

	testing = processTestSet()

	resultsDict = {}
	for backoff in [True, False]:
		resultsDict[backoff] = {}
		for split in [0.0, 0.25, 0.5, 0.75, 1.0]:
			resultsDict[backoff][split] = {}
			for n_toUse in range(n+1)[1:]:
				resultsDict[backoff][split][n_toUse] = testWithParameters(testing, learners, n_toUse, backoff, split)

	tableTop = "\\begin{center}\n    \\begin{tabular}{| l | l | l | l | l | l |}\n    \\hline\n"
	tableTop += " & 0.0 & 0.25 & 0.5 & 0.75 & 1.0 \\\\ \\hline\n"

	table1 = tableTop
	for n_used in range(n+1)[1:]:
		table1 += "   " + str(n_used)
		for split in [0.0, 0.25, 0.5, 0.75, 1.0]:
			acc = resultsDict[True][split][n_used][3]
			acc_s = "%.4f"%(acc)
			table1 += " & " + acc_s
		table1 += " \\\\ \\hline\n"

	table1 += "    \\end{tabular}\nWith Backoff\n\\end{center}\n"

	table2 = tableTop 

	for n_used in range(n+1)[1:]:
		table2 += "   " + str(n_used)
		for split in [0.0, 0.25, 0.5, 0.75, 1.0]:
			acc = resultsDict[False][split][n_used][3]
			acc_s = "%.4f"%(acc)
			table2 += " & " + acc_s
		table2 += " \\\\ \\hline\n"

	table2 += "    \\end{tabular}\nWithout Backoff\n\\end{center}\n"

	fileObject = open("RESULTS.txt", 'w')
	fileObject.write(table1)
	fileObject.write(table2)
	fileObject.write(str(resultsDict))
	fileObject.close()
	print("wrote to file: RESULTS. see ya.")

def main():
	toPredict = ""
	while (toPredict != 'exit'): #TODO: only relearn if n is different
		#toPredict = input("Please specify the filepath to a .mxl score to predict, or type 'exit' to quit: ")
		n = eval(input("What length n-gram model? "))

		backoff = bool(input("Enter True to use backoff, False to not use backoff:"))

		split = float(input("What weight do you want chords to have, vs figured bass? Enter 1.0 to have prediction entirely based on chords. Enter 0.0 to have prediction entirely based on figured bass:"))

		writingBool = bool(input("Enter True to write these results to a file, enter False not to."))

		learners = train(n) #list of piece objects to train on

		print (learners) #to test, for now

		#x = os.path.dirname(__file__) #get filepath to input file
		#testPath = os.path.join(x, toPredict)

		#PC = convert.Converter(testPath) #piece converter initialization
		#PC.convert() #convert the piece
		#pieceToPredict = piece.Piece(PC.getBass(), PC.getChords()) #create the piece python object
		testing = processTestSet()

		results = testWithParameters(testing, learners, n, backoff, split)

		print("finished testing!")

		print("accuracy:", results[3])
		print(results[0]["matrix"])

		if writingBool:
			fileObject = open(results[0]["filename"], 'w')
			fileObject.write(results[0]["matrix"])
			fileObject.close()
			print("wrote to file. see ya.")


main2()

#TODO: experiment with a main that after making a prediction, adds the predicted piece to that n-gram's training data; 
#sort of a semi evolutionary algorithm