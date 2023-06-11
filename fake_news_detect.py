from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from bs4 import BeautifulSoup
import nltk
import re
import pickle
import numpy as np


model = load_model(f"Files/fake_news3.h5")

#Removal of HTML Contents
def remove_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()

#Removal of Punctuation Marks
def remove_punctuations(text):
    return re.sub('\[[^]]*\]', '', text)

# Removal of Special Characters
def remove_characters(text):
    return re.sub("[^a-zA-Z]"," ",text)

#Removal of stopwords 
def remove_stopwords_and_lemmatization(text):
    final_text = []
    text = text.lower()
    text = nltk.word_tokenize(text)
    
    for word in text:
        if word not in set(nltk.corpus.stopwords.words('english')):
            lemma = nltk.WordNetLemmatizer()
            word = lemma.lemmatize(word) 
            final_text.append(word)
    return " ".join(final_text)

#Total function
def cleaning(text):
    text = remove_html(text)
    text = remove_punctuations(text)
    text = remove_characters(text)
    text = remove_stopwords_and_lemmatization(text)
    return text

def predict(title, text, subject):
    maxlen = 300

    text = subject + " " + title + " " + text
    text = cleaning(text)
    with open(r"Files/tokenizer.pkl", "rb") as file:
        tokenizer = pickle.load(file)
    
    sequence = tokenizer.texts_to_sequences([text])
    pad_sequence = pad_sequences(sequence, maxlen=maxlen)
    
    pred = model.predict(pad_sequence)[0]
    cls = np.argmax(pred)
    prob = np.round(pred[cls], 4)*100
    label = ["Fake News", "Real News"][cls]
    print(pred)
    return cls, label, prob
    



