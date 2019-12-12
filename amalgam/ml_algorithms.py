import nltk

nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import re

import math
from collections import Counter

WORD = re.compile(r'\w+')

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)




def preprocess(text):
    documents = []

    stemmer = WordNetLemmatizer()
    X = [text]
    for sen in range(0, len(X)):
        # Remove all the special characters
        document = re.sub(r'\W', ' ', str(X[sen]))

        # remove all single characters
        document = re.sub(r'\s+[a-zA-Z]\s+', ' ', document)

        # Remove single characters from the start
        document = re.sub(r'\^[a-zA-Z]\s+', ' ', document)

        # Substituting multiple spaces with single space
        document = re.sub(r'\s+', ' ', document, flags=re.I)

        # Removing prefixed 'b'
        document = re.sub(r'^b\s+', '', document)

        # Converting to Lowercase
        document = document.lower()

        # Lemmatization
        document = document.split()

        document = [stemmer.lemmatize(word) for word in document]
        document = ' '.join(document)

        documents.append(document)

    return document


def jaccard(text1, text2):
    intersection = len(list(set(text1).intersection(text2)))
    union = ((len(text1) + len(text2)) - intersection)
    return float(intersection) / union

def JaccardScore(base_text, resource_text):
    # Tokenize, remove punctuations, stem and standardize cases
    preprocessed_base = base_text
    pre_processed_resource = preprocess(resource_text)
    jaccard_score = jaccard(preprocessed_base, pre_processed_resource)
    print("JACCARD SCORE:", jaccard_score)
    return jaccard_score


def jaccard_root(text1, text2, root=0.5):
    intersection = len(list(set(text1).intersection(text2)))
    union = ((len(text1) + len(text2)) - intersection)**root
    return float(intersection) / union


def JaccardScoreRoot(base_text, resource_text, root):
    # Tokenize, remove punctuations, stem and standardize cases
    preprocessed_base = base_text
    pre_processed_resource = preprocess(resource_text)
    jaccard_score = jaccard(preprocessed_base, pre_processed_resource, root=root)
    print("JACCARD SCORE:", jaccard_score)
    return jaccard_score


def CosineScore(text1, text2):
    vec1, vec2 = text_to_vector(preprocess(text1)), text_to_vector(preprocess(text2))
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.00
    else:
        return round(float(numerator) / denominator,2)