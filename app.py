from flask import Flask, render_template
import nltk
from nltk.stem import WordNetLemmatizer
import numpy as np
from keras.models import load_model
import json
import random
import pickle

app = Flask(__name__)

@app.route("/")
def start():
    return "vny has LEGENDER"

@app.route("/mbsa")
def mbsa():
    return render_template('index.html')

