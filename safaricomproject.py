# -*- coding: utf-8 -*-
"""SafaricomProject.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Q0IBBWS6EJsk7j1mGoRghqpR-dePQ3yi

"""
import pip

# pip install pandas

import numpy as np
import pandas as pd
from pip._internal.operations.install.legacy import install

# Read csv file into a pandas dataframe
# from google.colab import files
# uploaded = files.upload()
import emoji
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
import matplotlib.pyplot as plt
import re
from wordcloud import WordCloud
from collections import Counter
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfVectorizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB

# Reading Dataset

df = pd.read_csv('safaricomDataset.csv')
df.head()

df.columns

df.shape

tweets_df = df[["Date", "User", "Tweet"]]
tweets_df.head()

# from sklearn import utils
tweets_df.shape

"""#Preprocessing and Cleaning of the Dataset """

nltk.download('punkt')


# pip install emoji

# import re

# import emoji


def tokenize_tweets(text):
    # remove emojis
    text = emoji.demojize(text)
    # remove urls
    text = re.sub('http[s]?://\S+', '', text)
    # remove punctuations
    text = re.sub(r'[^\w\s]', '', text)
    # strip numbers
    text = re.sub('[0-9]+', '', text)
    text = word_tokenize(text)

    return text


tweets_df["Tweets"] = tweets_df["Tweet"].apply(lambda x: tokenize_tweets(x))


nltk.download('stopwords')
stop = stopwords.words("english")
tweets_df["stop_words"] = tweets_df["Tweets"].apply(lambda x: [w for w in x if w in stop])
tweets_df["Tweets"] = tweets_df["Tweets"].apply(lambda x: [w.lower() for w in x if w not in stop])

tweets_df.head(10)

tweets_df.head()


string.punctuation

from nltk.stem.porter import *

stemmer = PorterStemmer()
tweets_df["Tweets"] = tweets_df["Tweets"].apply(lambda x: [stemmer.stem(w) for w in x])
tweets_df.head()


def remove_punct(text):
    text = " ".join([char for char in text if char not in string.punctuation])
    text = re.sub('[0-9]+', '', text)

    return text


tweets_df['tweet_punct'] = tweets_df['Tweets'].apply(lambda x: remove_punct(x))

tweets_df.head()

"""#Data Visualization(Word Cloud)"""

all_words = ' '.join([text for text in df['Tweet']])

wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110).generate(all_words)

plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
plt.show()

"""#Get the most frequent words"""

cnt = Counter()
for text in df["Tweet"].values:
    for word in text.split():
        cnt[word] += 1

cnt.most_common(20)

"""#Using Vader Library to analyse sentiments in Text"""

# !pip install vaderSentiment

"""#Training of Dataset"""

analyzer = SentimentIntensityAnalyzer()

"""#Getting the sentiments label"""


def sentiment_score_compound(sentence):
    score = analyzer.polarity_scores(sentence)
    return score['compound']


def sentiment_score_pos(sentence):
    score = analyzer.polarity_scores(sentence)
    return score['pos']


def sentiment_score_neg(sentence):
    score = analyzer.polarity_scores(sentence)
    return score['neg']


def sentiment_score_neu(sentence):
    score = analyzer.polarity_scores(sentence)
    return score['neu']


tweets_df["tweets_sent_compound"] = tweets_df["Tweet"].apply(lambda x: sentiment_score_compound(x))
tweets_df["tweets_sent_pos"] = tweets_df["Tweet"].apply(lambda x: sentiment_score_pos(x))
tweets_df["tweets_sent_neg"] = tweets_df["Tweet"].apply(lambda x: sentiment_score_neg(x))
tweets_df.head()

tweets_df.tail()

wordlist = nltk.FreqDist(all_words)
word_features = wordlist.keys()

"""#Vectorization"""

cv = CountVectorizer()
tweets_list = []
for tweet in tweets_df["tweet_punct"]:
    tweets_list.append(tweet)
len(tweets_list)
tfIdf = TfidfVectorizer(max_features=20000)

X = tweets_df["tweet_punct"]

vec = TfidfVectorizer(min_df=5, max_df=0.95, sublinear_tf=True, use_idf=True, ngram_range=(1, 2))
len(all_words)

"""#Define Labels(Positive, Negative, Neutral)"""


# negative label is 0
# neutral label is 1
# positive label is 2

def label_value(val):
    if val < 0:
        return 0
    elif val == 0:
        return 1
    else:
        return 2


tweets_df["label"] = tweets_df["tweets_sent_compound"].apply(lambda x: label_value(x))
tweets_df.head()

cv = CountVectorizer(binary=True)
cv.fit(tweets_list)
X = cv.transform(tweets_list)
y = tweets_df["label"].values

"""#Plotting the Label Results"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
plt.rcParams['figure.figsize'] = [10, 8]
for index, Tweets in enumerate(df.index):
    x = tweets_df.tweets_sent_pos.loc[Tweets]
    y = tweets_df.tweets_sent_neg.loc[Tweets]
    plt.scatter(x, y, color='Blue')

plt.title('Safaricom Tweets Sentiment Analysis', fontsize=20)
plt.xlabel('← Negative — — — Neutral — — — Positive →', fontsize=15)
plt.ylabel('← Facts — — — — — — — Opinions →', fontsize=15)
plt.show()

"""#Plotting on a Pie Chart and Bar Chart

"""

# Commented out IPython magic to ensure Python compatibility.

# %matplotlib inline
tweets_df['label'].value_counts().plot(kind='pie', autopct='%1.0f%%')
plt.show()

tweets_df['label'].value_counts().sort_index().plot.bar()
plt.show()

"""#Classification using SVM"""

# encoder = preprocessing.LabelEncoder()
# X = tfIdf.fit_transform(df['Text'])
# y = df['tweets_sent_compound']
# X.shape

# X_train, X_test, y_train, y_test= train_test_split(X,y, test_size=0.2, random_state=0)
# encoder = preprocessing.LabelEncoder()
# y_train = encoder.fit_transform(y_train)
# y_test = encoder.fit_transform(y_test)

# X_train, X_val, y_train, y_val = train_test_split(X, y, train_size = 0.2, random_state = 0)

epochs = 20
for epoch in range(epochs):
    print(f'Epochs: {epoch + 1}')
    train_loss = 0
    valid_loss = 0

    ngram_vectorizer = CountVectorizer(binary=True, ngram_range=(1, 3))
    ngram_vectorizer.fit(tweets_list)
    X = ngram_vectorizer.transform(tweets_list)
    y = tweets_df["label"].values
    X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.2, random_state=0)
    svm = LinearSVC()
    svm.fit(X_train, y_train)

# clf = LinearSVC()
# clf.fit(X_train, y_train)

pred = svm.predict(X_val)
print("Accuracy: ", accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))

"""#TF-IDF Vectroization"""

for epoch in range(epochs):
    print(f'Epochs: {epoch + 1}')
    train_loss = 0
    valid_loss = 0

    tfidf_vectorizer = TfidfVectorizer()
    tfidf_vectorizer.fit(tweets_list)
    X = tfidf_vectorizer.transform(tweets_list)
    y = tweets_df["label"].values

    X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.2, random_state=0)

svm = LinearSVC()
svm.fit(X_train, y_train)
pred = svm.predict(X_val)
print("Accuracy: ", accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))

"""#Classification using Logistic Regression"""

lr = LogisticRegression()
lr.fit(X_train, y_train)

pred = lr.predict(X_val)
print("Accuracy: ", accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))

"""#Using TF-IDF Vectorization"""

tfidf_vectorizer = TfidfVectorizer()
tfidf_vectorizer.fit(tweets_list)
X = tfidf_vectorizer.transform(tweets_list)
y = tweets_df["label"].values

X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.2, random_state=0)

lr = LogisticRegression()
lr.fit(X_train, y_train)

pred = lr.predict(X_val)
print("Accuracy:", accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))

"""#Classification using Naives Bayes"""

MNB = MultinomialNB()
MNB.fit(X_train, y_train)
pred = MNB.predict(X_val)
print(accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))

"""# TF-IDF Vectorization"""

tfidf_vectorizer = TfidfVectorizer()
tfidf_vectorizer.fit(tweets_list)
X = tfidf_vectorizer.transform(tweets_list)
y = tweets_df["label"].values

X_train, X_val, y_train, y_val = train_test_split(X, y, train_size=0.2, random_state=0)
MNB = MultinomialNB()
MNB.fit(X_train, y_train)
pred = MNB.predict(X_val)
print("Accuracy: ", accuracy_score(y_val, pred))
print(classification_report(y_val, pred))
print(confusion_matrix(y_val, pred))
