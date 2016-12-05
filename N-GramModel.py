

class N_Gram_Model():

    #this class will build n-gram models from 1 through the specified number
    #for n > 1, it will handle unseen values with backoff, for n = 1 it will use laplace smoothing

    def __init__(self, n):

        if n < 1:
            print("N_Gram_Model: n must be greater than or equal to 1")
            exit(1)

        self.n = n
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


    def train(self, sequence):

        self.sequences.append(sequence)
        for i in self.gram_lengths:
            self.total_grams[i] += len(sequence) - (i - 1)

        for i in range(len(sequence)):
            for j in self.gram_lengths:
                if i + j < len(sequence):
                    #construct the current n-length sequence, starting from sequence[i]
                    gram = self.sequence[i]
                    for k in range(j-1):
                        gram += "^" + self.sequence[i+k]

                    if gram in self.n_grams.keys[j].keys():
                        c = self.n_grams[j][gram]
                        self.n_grams[j][gram] = c + 1
                    else:
                        self.n_grams[j][gram] = 1
                        c = self.unique_grams[j]
                        self.unique_grams[j] = c + 1

    def decrease_gram(self, n_gram):
        for i in range(len(n_gram)):
            if n_gram[len(n_gram)-i-1] == "^":
                return n_gram[:len(n_gram)-i-1]
        print("N_Gram_Model: You called decrease_gram on a unigram")
        exit(1)


def main():

    n = N_Gram_Model([1,2,3,4,5], 6)
    print (n.decrease_gram(n.decrease_gram("he")))

main()