import music21 as m2

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

    def catchFiguredBass(self, list, isFiguredBass):
        if isFiguredBass:
            try:
                s = ""
                for i in list:
                    s += str(i)
                return s
            except TypeError:
                return "REST"
        return list

    def decrease_gram(self, n_gram):
        for i in range(len(n_gram)):
            if n_gram[len(n_gram)-i-1] == "^":
                return n_gram[:len(n_gram)-i-1]
        return ""

    #gives the probablility of a specific n gram occurring
    def giveProbablility(self, n_gram, n):

        if n == 0:
            print("wow, not even a unigram matched this one")
            return 1

        if n_gram in self.n_grams[n]:
            return float(self.n_grams[n][n_gram]) / self.total_grams[n]
        else:
            return self.giveProbability(self, self.decrease_gram(n_gram), n-1)



    #this method takes in an n, which is the max n the model will look at.
    #so for example if you built a 10-gram model but wanted to see how a 4-gram model would do on the data,
    #you could call this function with n=4
    def giveProbabilityOfSequence(self, sequence, n):

        if n > self.n:
            print("requested n is greater than this model's n(", self.n,")... decreasing to", self.n)
            n = self.n

        prob = 1.0

        for i in range(len(sequence)):
            if i + n < len(sequence):
                prob *= self.giveProbability(self.convertToNGram(sequence[i:(i+n)]))

        return prob