import nltk
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
import re
import math
from collections import Counter
WORD = re.compile(r'\w+')
import keras
from keras.applications.xception import Xception
from keras.preprocessing import image as keras_image
from keras.applications.xception import preprocess_input, decode_predictions
import pandas as pd
import requests
from diff_match_patch import diff_match_patch
from nltk.corpus import stopwords
from nltk import download
from gensim.models import Word2Vec
import textdistance
wvmodel = Word2Vec()
download('stopwords')

stop_words = stopwords.words('english')

def word_mover(text1, text2):
    text1 = preprocess(text1)
    text2 = preprocess(text2)
    vec1, vec2 = text_to_vector(text1), text_to_vector(text2)
    vec1 = [word for word in vec1 if word not in stop_words]
    vec2 = [word for word in vec2 if word not in stop_words]
    return min(wvmodel.wmdistance(vec1,vec2), 1000)
def text_distance(text1, text2):
    text1 = preprocess(text1)
    text2 = preprocess(text2)
    vec1, vec2 = text_to_vector(text1), text_to_vector(text2)
    vec1 = [word for word in vec1 if word not in stop_words]
    vec2 = [word for word in vec2 if word not in stop_words]
    return textdistance.hamming.normalized_similarity(" ".join(vec1), " ".join(vec2))
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

def jaccard_similarity(list1, list2):
    list1, list2 = set(list1), set(list2)
    len_intersection = len(list1.intersection((list2)))
    len_union = (len(list1) + len(list2)) - len_intersection
    return float(len_intersection) / len_union
def jaccard(text1, text2):
    vec1, vec2 = text_to_vector(text1), text_to_vector(text2)
    return jaccard_similarity(vec1, vec2)

def compute_similarity_and_diff(text1, text2):
    dmp = diff_match_patch()
    dmp.Diff_Timeout = 0.0
    diff = dmp.diff_main(text1, text2, False)

    # similarity
    common_text = sum([len(txt) for op, txt in diff if op == 0])
    text_length = max(len(text1), len(text2))
    sim = common_text / text_length

    return sim, diff

def JaccardScore(base_text, resource_text):
    # Tokenize, remove punctuations, stem and standardize cases
    preprocessed_base = preprocess(base_text)
    pre_processed_resource = preprocess(resource_text)
    #jaccard_score = jaccard(preprocessed_base, pre_processed_resource)
    jaccard_score = jaccard(preprocessed_base,pre_processed_resource)
    return jaccard_score



def CosineScore(text1, text2):
    vec1, vec2 = text_to_vector(preprocess(text1)), text_to_vector(preprocess(text2))
    print("Cosine TTV,",vec1)
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x  in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.00
    else:
        return round(float(numerator) / denominator,2)



model = Xception(include_top=True, weights='imagenet', input_tensor=None, input_shape=None, pooling=None, classes=1000)
def neural_classifier_ouput_cleaner(data, confidence=0.10):
    qualifying_classes = [" ".join(classification[1].split("_")) for classification in data[0] if classification[2]>=confidence]
    return " ".join(qualifying_classes)
def neural_classifier(image):
    img_data = keras_image.img_to_array(image)
    img_data = img_data.reshape((1, img_data.shape[0], img_data.shape[1], img_data.shape[2]))
    img_data = preprocess_input(img_data)

    keras.backend.tensorflow_backend._SYMBOLIC_SCOPE.value = True
    preds = decode_predictions(model.predict(img_data))
    # decode the results into a list of tuples (class, description, probability)
    # (one such list for each sample in the batch)
    output = neural_classifier_ouput_cleaner(preds)
    print("Predicted Output:", output)
    return output


def output_cleaner(resp, confidence):
    final_dict = {"Classification": [], "Probability": []}
    for res in resp["result"]["tags"]:
        if int(res["confidence"]) >= confidence:
            final_dict["Classification"].append(res["tag"]["en"])
            final_dict["Probability"].append(res["confidence"])

    return final_dict

def online_neural_classifier(image_data, current_user, confidence=25):
    api_key = current_user.api_key
    api_secret = current_user.api_secret

    response = requests.post('https://api.imagga.com/v2/uploads',
                              auth=(api_key, api_secret),
                              files={'image_base64': image_data}
                              )


    upload_object = response.json()
    print("Upload Object", upload_object)
    image_url = 'https://api.imagga.com/v2/tags?image_upload_id={}'.format(upload_object['result']['upload_id'])
    response = requests.get(image_url,auth=(api_key, api_secret))
    data = output_cleaner(resp=response.json(), confidence=confidence)
    data_frame = pd.DataFrame.from_dict(data)
    print(data_frame)
    return data_frame
