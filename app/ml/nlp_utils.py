import numpy as np
import nltk
from nltk.stem.porter import PorterStemmer

stemmer = PorterStemmer()


def tokenize(sentence):
    try:
        return nltk.word_tokenize(sentence)
    except Exception as e:
        print(f"Error in tokenization, using simple split: {e}")
        return sentence.lower().split()


def stem(word):
    try:
        return stemmer.stem(word.lower())
    except Exception as e:
        print(f"Error in stemming: {e}")
        return word.lower()


def bag_of_words(tokenized_sentence, words):
    try:
        sentence_words = [stem(word) for word in tokenized_sentence]
        bag = np.zeros(len(words), dtype=np.float32)

        for idx, w in enumerate(words):
            if w in sentence_words:
                bag[idx] = 1

        return bag
    except Exception as e:
        print(f"Error in bag of words: {e}")
        # Return a bag of all zeros except for common greeting words
        bag = np.zeros(len(words), dtype=np.float32)
        common_stems = ["hi", "hello", "hey", "greet"]

        for idx, w in enumerate(words):
            if w in common_stems:
                bag[idx] = 1

        return bag