# -*- coding: utf-8 -*-
"""dl.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DlwXrcWZGEOHcQFcDvGD09fjBe2CHJyl
"""



from google.colab import drive
drive.mount('/content/drive')

ls

cd drive/

cd MyDrive/

cd CMPE-255-Group-Project-FALL21/

ls

ls





import pandas as pd 
import tensorflow as tf
from tensorflow import keras
import numpy as np 
import matplotlib.pyplot as plt
import os

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.layers import Embedding
import seaborn as sns

data = pd.read_json('./data/News_Category_Dataset_v2.json', lines=True)

data

data.drop(['authors', 'link', 'date'], axis = 1, inplace = True)

data

data['news'] = data[['headline', 'short_description']].agg(' '.join, axis=1)

data.drop(['short_description', 'headline'], axis = 1, inplace = True)

data

data['words_length'] = data.news.apply(lambda i: len(i.split(" ")))
data = data[data.words_length >= 5]

data.describe()

data = data[data['category'].map(data['category'].value_counts()) > 3000]

data.category = data.category.map(lambda x: "WORLDPOST" if x == "THE WORLDPOST" else x)

data

data['category'].value_counts()

from sklearn.utils import shuffle
df = shuffle(data)
df.reset_index(inplace=True, drop=True)

df

!pip install contractions

!pip install regex

import contractions
from tqdm import tqdm
import nltk
import regex as re

clean_reviews=[]
for i in tqdm(df['news']):
    #Rremoving the html tags 
    i=re.sub('(<[\w\s]*/?>)',"",i)
    #Expanding  the contractions 
    i=contractions.fix(i)
    #Removing the special characters
    i=re.sub('[^a-zA-Z0-9\s]+',"",i)
    #Removing  the digits
    i=re.sub('\d+',"",i)
    i=i.lower()
    #converting the text to be of lower case and remvoing the stopwords and words of length less than 3
    #clean_reviews.append(" ".join([j.lower() for j in i.split() if j not in stopwords and len(j)>=3]))
    clean_reviews.append(i)

df=pd.DataFrame({'news':clean_reviews,'category':list(df['category']),'words_length':list(df['words_length'])})

df['words_length'] = df.news.apply(lambda i: len(i.split(" ")))
df = df[df.words_length >= 5]

df



vocab_size =20000
max_length = 35
trunc_type='post'
padding_type='post'
oov_tok = "<OOV>"





from sklearn.preprocessing import LabelEncoder as lencoder

le = lencoder()
labels = le.fit_transform(df['category'])

labels

from tensorflow.keras.utils import to_categorical
labels= to_categorical(labels,num_classes=21)

labels

X,Y = df['news'],df['category']
tokenizer = tf.keras.preprocessing.text.Tokenizer(num_words = vocab_size, oov_token=oov_tok)
tokenizer.fit_on_texts(X)

word_index = tokenizer.word_index

X = tokenizer.texts_to_sequences(X)
X = pad_sequences(X, maxlen= max_length, padding=padding_type, truncating=trunc_type)

X

X_train, X_val, y_train, y_val = train_test_split(X, labels, test_size=0.2, random_state=42,stratify=labels)
X_val, X_test , y_val, y_test= train_test_split(X_val,y_val, test_size=0.5, random_state=42)

X_train

X_val

num_words=20000
embeddings=300

from keras.layers import Embedding,Conv1D,LSTM,GRU,BatchNormalization,Flatten,Dense
from tensorflow.keras.layers import *
from tensorflow.keras.models import *

model= Sequential()
model.add(Embedding(num_words,embeddings,input_length=max_length))

#model.add(Conv1D(256,10,activation='relu'))
model.add(keras.layers.Bidirectional(LSTM(256,return_sequences=True)))
model.add(keras.layers.Dropout(0.4))
model.add(keras.layers.GRU(256))
model.add(keras.layers.Dropout(0.4))

model.add(Dense(64, activation='relu'))
model.add(keras.layers.Dropout(0.2))

model.add(Dense(21,activation='softmax'))

model.summary()

opt = keras.optimizers.Adam(learning_rate=0.001)
model.compile(loss="categorical_crossentropy",
              optimizer=opt,
              metrics=['accuracy']
             )



X_train.shape

y_train[1]

import tensorflow as tf
tf.config.list_physical_devices('GPU')

early_stop=tf.keras.callbacks.EarlyStopping(monitor='val_loss', 
                                            patience=3, min_delta=0.0001)



history = model.fit( X_train,y_train,validation_data=(X_val,y_val), epochs=10, batch_size=32,steps_per_epoch=len(X_train) // 32,validation_steps = len(X_val)//32, callbacks=early_stop)

print(history.history.keys())

history.history['val_loss']

score, acc = model.evaluate(X_test, y_test)

acc

fig = plt.figure(figsize=(10,10))
plt.subplot(221)
plt.plot(history.history['accuracy'],'bo-', label = "acc")
plt.plot(history.history['val_accuracy'], 'ro-', label = "val_acc")
plt.title("train_accuracy vs val_accuracy")
plt.ylabel("accuracy")
plt.xlabel("epochs")
plt.grid(True)
plt.legend()

# Plot loss function
plt.subplot(222)
plt.plot(history.history['loss'],'bo-', label = "loss")
plt.plot(history.history['val_loss'], 'ro-', label = "val_loss")
plt.title("train_loss vs val_loss")
plt.ylabel("loss")
plt.xlabel("epochs")
plt.grid(True)
plt.legend()

