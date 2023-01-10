import pandas as pd
from bs4 import BeautifulSoup  

from selenium.webdriver.support import expected_conditions as EC
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import string
import re
import requests
from flask import Flask, request, render_template
from bs4 import BeautifulSoup  
import time
from urllib.parse import urlparse
from urllib.parse import urljoin

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



app = Flask(__name__)


@app.route('/')
def form():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect():
    url = request.form['url']
    reviews = scrape_reviews(url) 
    real_count = 0
    for review in reviews:
        result = is_real_review(review)
        if result:
            real_count += 1
    total_count = len(reviews)
    if total_count == 0:
        percentage = 0
    else:
        percentage = real_count / total_count * 100
    return render_template('index.html', percentage=percentage)

def scrape_reviews(url):
    reviews = []
    parsed_url = urlparse(url)
    base_url = parsed_url.scheme + '://' + parsed_url.netloc
    while True:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        for i in range(3):  # retry the request up to 3 times
            try:
                r = requests.get(url, headers=headers)
                html_content = r.text
                break  
            except requests.exceptions.RequestException:
                time.sleep(1)  
        else:  
            raise requests.exceptions.RequestException('Error: the request was not successful')

        soup = BeautifulSoup(html_content, 'html.parser')
        
        review_elements = soup.find_all(class_='a-size-base review-text review-text-content')
        for element in review_elements:
            review = element.get_text()
            reviews.append(review)
        # find the "Next" button element
        next_button = soup.find(class_='a-last')
        # check if the "Next" button element exists
        if next_button is None:
            print('dddd')
            break
        # if the "Next" button exists, get the URL of the next page
        next_url = next_button.get('href')
        url =  urljoin(base_url , next_url)
    return reviews

def is_real_review(review):
    result1 = lrPrediction(review)  # call first algorithm
    result2 = dtPrediction(review)  # call second algorithm
    result3 = rfPrediction(review)  # call third algorithm
    total = result1 + result2 + result3
    if total >= 2:
        return True
    else:
        return False

if __name__ == '__main__':
    app.run()


