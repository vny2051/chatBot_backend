from flask import Flask, jsonify, request
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
from keras.models import load_model
import json
import random
import pickle
nltk.download('wordnet')

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

lemmatizer = WordNetLemmatizer()
model = load_model('chatassistant_model.h5')

# Load data
try:
    intents = json.loads(open('intents.json').read())
    words = pickle.load(open('words.pkl', 'rb'))
    classes = pickle.load(open('classes.pkl', 'rb'))
    print("Files loaded successfully.")
except Exception as e:
    print(f"Error loading files: {e}")

def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bow(sentence, words, show_details=True):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

@app.route("/")
def start():
    return "Backend Running"

@app.route('/chat', methods=['POST'])
def chatbot_response():
    try:
        data = request.get_json()
        msg = data['message']
        print(f"Received message: {msg}")

        ints = predict_class(msg, model)
        print(f"Predicted classes: {ints}")

        if ints:
            res = get_response(ints, intents)
            print(f"Response: {res}")
            return jsonify({"response": res})
        else:
            return jsonify({"response": "I'm not sure how to respond to that."})
    except Exception as e:
        print(f"Error during processing: {e}")
        return jsonify({"response": "Sorry, I couldn't process your request at the moment. Please try again later."})

