# -*- coding: utf-8 -*-
"""SafaricomSentiment2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dzgJpnUT9Kdc4sSqKZUYtzucnOFJzCHf
"""

# Imports
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
import numpy as np

from google.colab import files
uploaded = files.upload()

data = pd.read_csv("processed_batch.csv")
data.head()

# Importing LabelEncoder from Sklearn
# library from preprocessing Module.
from sklearn.preprocessing import LabelEncoder
 
# Creating a instance of label Encoder.
le = LabelEncoder()
 
# Using .fit_transform function to fit label
# encoder and return encoded label
label = le.fit_transform(data['Classification'])
 
# printing label
label
# removing the column 'Classification' from data
# as it is of no use now.
data.drop("Classification", axis=1, inplace=True)
 
# Appending the array to our dataFrame
# with column name 'Label'
data["label"] = label
 
# printing Dataframe
data

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Install if necessary
print('Installing packages')
!pip install datasets==1.18.3 transformers[sentencepiece]==4.16.2 tweet-preprocessor

from datasets import Dataset
from sklearn.model_selection import train_test_split

# Put clean data in a dataset split into train and test sets
dataset = Dataset.from_pandas(data).train_test_split(train_size=0.8, seed=123)
print(dataset)

# Cast labels column as class labels
dataset = dataset.class_encode_column("label")

from transformers import AutoTokenizer

# Load DistilBERT tokenizer and tokenize (encode) the texts
tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

# Make a list of columns to remove before tokenization
cols_to_remove = [col for col in dataset["train"].column_names if col != "label"]
print(cols_to_remove)

# Tokenize and encode the dataset
def tokenize(batch):
    tokenized_batch = tokenizer(batch['Tweet'], padding=True, truncation=True, max_length=128)
    return tokenized_batch

dataset_enc = dataset.map(tokenize, batched=True, remove_columns= cols_to_remove, num_proc=4)

# Set dataset format for PyTorch
dataset_enc.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])

# Check the output
print(dataset_enc["train"].column_names)

from transformers import DataCollatorWithPadding
from torch.utils.data import DataLoader

# Instantiate a data collator with dynamic padding
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Create data loaders for to reshape data for PyTorch model
train_dataloader = DataLoader(
    dataset_enc["train"], shuffle=True, batch_size=8, collate_fn=data_collator
)
eval_dataloader = DataLoader(
    dataset_enc["test"], batch_size=8, collate_fn=data_collator
)

#!pip install huggingface_hub

#from huggingface_hub import notebook_login

#notebook_login()

#from huggingface_hub import create_repo
#create_repo("JoanWaweru/Code-Switched-Sentiment-Analysis", private=False)

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoModelForSequenceClassification

# Dynamically set number of class labels based on dataset
num_labels = dataset["train"].features["label"].num_classes
print(f"Number of labels: {num_labels}")

# Load model from checkpoint
model = AutoModelForSequenceClassification.from_pretrained("bert-base-multilingual-cased", 
                                                           num_labels=num_labels)

from transformers import AdamW
from transformers import get_scheduler

# Model parameters
learning_rate = 5e-5
num_epochs = 5
push_to_hub=True

# Create the optimizer
optimizer = AdamW(model.parameters(), lr=learning_rate)

# Further define learning rate scheduler
num_training_batches = len(train_dataloader)
num_training_steps = num_epochs * num_training_batches
lr_scheduler = get_scheduler(
    "linear",                   # linear decay
    optimizer=optimizer,
    num_warmup_steps=0,
    num_training_steps=num_training_steps,
)

lr_scheduler

num_training_batches

num_training_steps

# Set the device automatically (GPU or CPU)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(device)

# Move model to device
model.to(device)

from tqdm.auto import tqdm

progress_bar = tqdm(range(num_training_steps))

# Train the model with PyTorch training loop
model.train()
for epoch in range(num_epochs):
    for batch in train_dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        outputs = model(**batch)
        loss = outputs.loss
        loss.backward()

        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()
        progress_bar.update(1)

from datasets import load_metric

# Load metric
metric = load_metric("glue", "mrpc")

# Iteratively evaluate the model and compute metrics
model.eval()
for batch in eval_dataloader:
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.no_grad():
        outputs = model(**batch)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    metric.add_batch(predictions=predictions, references=batch["labels"])

# Get model accuracy and F1 score
metric.compute()

metric

# Tweet from Safaricom user
trial_tweet = ["Safaricom ni mbaya sana"]

# Tokenize inputs
inputs = tokenizer(trial_tweet, padding=True, truncation=True, return_tensors="pt").to(device) # Move the tensor to the GPU

# Inference model and get logits
outputs = model(**inputs)
print(outputs)

predictions = torch.nn.functional.sigmoid(outputs.logits)
print(predictions)

#saving the model into a pickle file
import pickle
with open('safaricomModel.pkl', 'wb') as fid:
    pickle.dump(model, fid)
pickle.dump(model, open('transform.pkl', 'wb'))

from google.colab import drive

# Mount Google Drive
drive.mount('/content/drive')

# Define root dir in Google Drive
root_dir = "/content/drive/MyDrive/colab_data"
# Save model to disk
model.save_pretrained(f"{root_dir}/models/Code-Switched-Sentiment-Analysis")

# Install git-lfs
import huggingface_hub
from huggingface_hub import lfs

#!git lfs install

#!git clone https://huggingface.co/JoanWaweru/Code-Switched-Sentiment-Analysis

from huggingface_hub import notebook_login

notebook_login()

#create_repo('JoanWaweru/Code-Switched-Sentiment-Analysis2')

# Alternatively if you have a token,
# you can use it instead of your password
#!git clone https://JoanWaweru:token@huggingface.co/JoanWaweru/Code-Switched-Sentiment-Analysis2

#!cd Code-Switched-Sentiment-Analysis2
#!git config --global user.email "joan.waweru@strathmore.edu"
# Tip: using the same email than for your huggingface.co account will link your commits to your profile
#!git config --global user.name "Joan Waweru"

#!git add .
#!git commit -m "Initial commit"
#!git push

#import os

# Configure git settings
#!git config --global user.email "joan.waweru@strathmore.edu"
#!git config --global user.name "JoanWaweru"

# Push PT model to hub
#model.push_to_hub(
#    "JoanWaweru/Code-Switched-Sentiment-Analysis2",                            # model name
#    language="en",                                            # language
#    dataset_tags="processed_batch.csv",                # HF dataset used for training
#    library_name="pytorch",
#    metrics=["accuracy", "f1"],                               
#    tags=["text-classification", "transformers", "pytorch", "multilingual"],  # model tags
#    finetuned_from="bert-base-multilingual-cased",                 # base model
    # commit_message="..."
#    )

from datasets import load_metric

# Load metric
metric = load_metric("glue", "mrpc")

# Iteratively evaluate the model and compute metrics
model.eval()
for batch in eval_dataloader:
    batch = {k: v.to(device) for k, v in batch.items()}
    with torch.no_grad():
        outputs = model(**batch)

    logits = outputs.logits
    predictions = torch.argmax(logits, dim=-1)
    metric.add_batch(predictions=predictions, references=batch["labels"])

# Get model accuracy and F1 score
metric.compute()

#!pip3 install scipy
#import socket

#from flask import Flask, request, jsonify, render_template

#app = Flask(__name__)

#BERTClassifier = pickle.load(open('safaricomModel.pkl', 'rb'))
#cv = pickle.load(open('transform.pkl','rb'))

#@app.route('/')
#def home():
#    return render_template('templates/index.html')

#def ValuePredictor(to_predict_list):
#    pickle.dump(model, open('safaricomModel.pkl', 'rb'))
#    to_predict = np.array(to_predict_list).reshape(1, 1)
#    with (open("safaricomModel.pkl", "rb")) as openfile:
#        while True:
#            try:
#                loaded_model = pickle.load(open("safaricomModel.pkl", "rb"))
#            except EOFError:
#                break
#    result = loaded_model.predict(to_predict)
#    return result[0]
#@app.route('/predict',methods=['POST'])
#def predict():
    # prediction function

    #For rendering results on HTML GUI

#    if request.method == "POST":
#        tweet = request.form['Tweet']
#        vect = cv.transform([tweet])
#        my_prediction = BERTClassifier.predict(vect)
#        if my_prediction == 0:
#            return render_template("templates/index.html", prediction_text='The tweet is {}'.format(my_prediction)+',which is Negative :(')
        #if my_prediction == 1:
        #    return render_template("index.html", prediction_text='The tweet is {}'.format(my_prediction)+',which is Neutral :/')
#        if my_prediction == 1:
#            return render_template("templates/index.html", prediction_text='The tweet is {}'.format(my_prediction)+',which is Positive :)')

#@app.route('/predict_api',methods=['POST'])
#def predict_api():
#    '''
#    For direct API calls through request
#    '''
#    data = request.get_json(force=True)
#    prediction = model.predict([np.array(list(data.values()))])

#    output = prediction[0]
#    return jsonify(output)

#if __name__ == "__main__":
#  app.run(debug=True)

!git clone https://huggingface.co/spaces/JoanWaweru/Sentiment

!pip install streamlit

!pip install python-dotenv

!pip install tensorflow

import streamlit as st
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

def predict(message):
    model=load_model(model)
    with open('safaricomModel.pkl', 'rb') as handle:
        tokenizer = pickle.load(handle)
    x_1 = tokenizer.texts_to_sequences([message])
    x_1 = pad_sequences(x_1, maxlen=300)
    predictions = model.predict(x_1)[0][0]
    return predictions

st.title("Sentiment Analyzer")
message = st.text_area("Enter Text","Type Here ..")

if st.button("Predict"):
 with st.spinner('Analyzing the text …'):
     prediction=predict(message)
     if prediction == 1:
         st.success(f"Positive! With {round(prediction*100, 2)}% confidence")
         st.balloons()
     elif prediction == 0:
         st.error(f"Negative! With {round(prediction*100, 2)}% confidence")
     else:
         st.warning("Not sure man ¯\_(ツ)_/¯")

