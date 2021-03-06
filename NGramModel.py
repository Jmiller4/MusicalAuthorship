import music21 as m2
import math as m

class N_Gram_Model():

    #this class will build n-gram models from 1 through the specified number
    #for n > 1, it will handle unseen values with backoff

    #the n-grams used by this model look like "item1^item2^...^itemN"   -- so its a string of the sequence, with each item separated by a "^"

    def __init__(self, n, isFiguredBass):

        self.n = n
        if self.n < 1:
            print("N_Gram_Model: n must be greater than or equal to 1... setting n = 1")
            self.n = 1

        self.n_grams = {}
        self.unique_grams = {}
        self.total_grams = {}
        self.sequences = []
        self.gram_lengths = []
        for i in range(self.n):
            self.n_grams[i+1] = {}
            self.gram_lengths.append(i+1)
            self.unique_grams[i+1] = 0
            self.total_grams[i+1] = 0

        self.isFiguredBass = isFiguredBass

    #updates the dictionary of n-gram counts according to the new training sequence
    def train(self, sequence):

        self.sequences.append(sequence)
        for i in self.gram_lengths:
            self.total_grams[i] += len(sequence) - (i - 1)

        for i in range(len(sequence)):
            for j in self.gram_lengths:
                if i + j < len(sequence):
                    #find the current n-length sequence, starting from sequence[i]

                    gram = self.convertToNGram(sequence[i:(i+j)])

                    #update dictionaries to reflect this newly seen gram
                    if gram in self.n_grams[j].keys():
                        c = self.n_grams[j][gram]
                        self.n_grams[j][gram] = c + 1
                    else:
                        self.n_grams[j][gram] = 1
                        c = self.unique_grams[j]
                        self.unique_grams[j] = c + 1


    #converts lists to n-grams, which are strings in this case
    def convertToNGram(self, list):
        gram = self.catchFiguredBass(list[0])
        for k in list[1:]:
            gram += "^" + self.catchFiguredBass(k)
        return gram

    #this function makes sure that everything that gets added to an individual n-gram is a string
    def catchFiguredBass(self, list):
        if self.isFiguredBass:
            try:
                s = ""
                for i in list:
                    s += str(i)
                return s
            except TypeError:
                return "REST"
        return list

    #this function takes in an n-gram and finds the corresponding (n-1)-gram, i.e. that n-gram with the last thing chopped off
    def decrease_gram(self, n_gram):
        for i in range(len(n_gram)):
            if n_gram[len(n_gram)-i-1] == "^":
                return n_gram[:len(n_gram)-i-1]
        return ""

    #this function gives the probablility of a specific n gram occurring, and it recursively uses backoff...
    #I'm actually not sure that using backoff is a good idea overall...
    #b is the psuedocount for the denominator
    def giveProbability(self, n_gram, n, b, backoff):

        if n == 0:
            #print("wow, not even a unigram matched this one")
            return m.log(1.0 / (self.total_grams[1] + b))

        if n_gram in self.n_grams[n]:
            return m.log(float(self.n_grams[n][n_gram] + 1) / (self.total_grams[n] + b))
        else:
            if backoff:
                return self.giveProbability(self.decrease_gram(n_gram), n-1, b, backoff)
            else:
                return m.log(1.0 / self.total_grams[n] + b)

    #this method takes in an n, which is the max n the model will look at.
    #so for example if you built a 10-gram model but wanted to see how a 4-gram model would do on the data,
    #you could call this function with n=4
    #backoff is a Boolean that's true if you want the model to handle unseen values with backoff to a n-1 gram model, if its false the model will use psuedocounts to handle unseen values
    #(even if backoff is enabled, the model will still use psuedocounts at n = 1)
    def giveProbabilityOfSequence(self, sequence, n, total, backoff):

        if self.total_grams[1] == 0:
            print("Oy... looks like this model has never been trained. So it can't really give a probability...")
            return 0

        if n > self.n:
            print("requested n is greater than this model's n(", self.n,")... decreasing to", self.n)
            n = self.n

        prob = 0.0

        for i in range(len(sequence)):
            if i + n < len(sequence):
                prob += self.giveProbability(self.convertToNGram(sequence[i:(i+n)]), n, len(sequence), backoff)

        prob += m.log(self.total_grams[1] / total)

        return prob
