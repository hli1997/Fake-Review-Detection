import pandas as pd
import numpy as np
import seaborn as sns
from bs4 import BeautifulSoup  
from selenium import webdriver

from selenium.webdriver.support import expected_conditions as EC
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import re

from flask import Flask, request, render_template

df_test = pd.read_csv("Data/train.csv")
df_test = df_test.drop(["category", "rating"], axis = 1)
df_test['label'] = df_test['label'].map({'OR': 1, 'CG': 0})

def wordopt(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text) 
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)    
    return text

df_test["text_"] = df_test["text_"].apply(wordopt)

x = df_test["text_"]
y = df_test["label"]
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.25)

vectorization = TfidfVectorizer()
xv_train = vectorization.fit_transform(x_train)
xv_test = vectorization.transform(x_test)

LR = LogisticRegression()
LR.fit(xv_train,y_train)
pred_lr=LR.predict(xv_test)
lg_socre = LR.score(xv_test, y_test)


DT = DecisionTreeClassifier()
DT.fit(xv_train, y_train)
pred_dt = DT.predict(xv_test)
dt_score = DT.score(xv_test, y_test)


RFC = RandomForestClassifier(random_state=0)
RFC.fit(xv_train, y_train)
pred_rfc = RFC.predict(xv_test)
rfc_score= RFC.score(xv_test, y_test)


def lrPrediction(review):
    testing_review = {"text":[review]}
    new_def_test = pd.DataFrame(testing_review)
    new_def_test["text"] = new_def_test["text"].apply(wordopt) 
    new_x_test = new_def_test["text"]
    new_xv_test = vectorization.transform(new_x_test)
    pred_LR = LR.predict(new_xv_test)
    return pred_LR[0]

def dtPrediction(review):
    testing_review = {"text":[review]}
    new_def_test = pd.DataFrame(testing_review)
    new_def_test["text"] = new_def_test["text"].apply(wordopt) 
    new_x_test = new_def_test["text"]
    new_xv_test = vectorization.transform(new_x_test)
    pred_DT = DT.predict(new_xv_test)

    return pred_DT[0]

def rfPrediction(review):
    testing_review = {"text":[review]}
    new_def_test = pd.DataFrame(testing_review)
    new_def_test["text"] = new_def_test["text"].apply(wordopt) 
    new_x_test = new_def_test["text"]
    new_xv_test = vectorization.transform(new_x_test)
    pred_RFC = RFC.predict(new_xv_test)

    return pred_RFC[0]

def is_real_review(review):
    result1 = lrPrediction(review)  # call first algorithm
    result2 = dtPrediction(review)  # call second algorithm
    result3 = rfPrediction(review)  # call third algorithm
    total = result1 + result2 + result3
    if total >= 2:
        return "real"
    else:
        return "fake"

app = Flask(__name__)


@app.route('/')
def form():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    review = request.form['review']
    result = is_real_review(review)  # call your function here
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run()


