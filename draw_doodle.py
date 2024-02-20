# -*- coding: utf-8 -*-
"""draw-doodle.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kkTH2_i0CPnf3rR25SypWBk0DDOzRXdI
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from matplotlib import pyplot as plt
import urllib.request
import os
import glob
import numpy as np

!mkdir data

with open('classes.txt') as f:
  classes = [line.strip() for line in f.readlines()]

def download():
  base = 'https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap/'
  for cls in classes:
    cls_url = cls.replace(' ', '%20')
    print(cls_url)
    path = base+cls_url+'.npy'
    print(path)
    urllib.request.urlretrieve(path, 'data/'+cls+'.npy')

download()

def load_data(root, vfold_ratio=0.2, max_items_per_class= 4000 ):
    all_files = glob.glob(os.path.join(root, '*.npy'))

    #initialize variables
    x = np.empty([0, 784])
    y = np.empty([0])
    class_names = []

    #load each data file
    for idx, file in enumerate(all_files):
        data = np.load(file)
        data = data[0: max_items_per_class, :]
        labels = np.full(data.shape[0], idx)

        x = np.concatenate((x, data), axis=0)
        y = np.append(y, labels)

        class_name, ext = os.path.splitext(os.path.basename(file))
        class_names.append(class_name)

    data = None
    labels = None

    #randomize the dataset
    permutation = np.random.permutation(y.shape[0])
    x = x[permutation, :]
    y = y[permutation]

    #separate into training and testing
    vfold_size = int(x.shape[0]/100*(vfold_ratio*100))

    x_test = x[0:vfold_size, :]
    y_test = y[0:vfold_size]

    x_train = x[vfold_size:x.shape[0], :]
    y_train = y[vfold_size:y.shape[0]]
    return x_train, y_train, x_test, y_test, class_names

x_train, y_train, x_test, y_test, class_names = load_data('data')
num_classes = len(class_names)
image_size = 28

# Preprocess the data
x_train = x_train.reshape(-1, image_size, image_size, 1).astype("float32") / 255.0
x_test = x_test.reshape(-1, image_size, image_size, 1).astype("float32") / 255.0

# Define the model architecture
model = keras.Sequential(
  [
    layers.Conv2D(16, (3, 3), padding='same', activation='relu', input_shape=(image_size, image_size, 1)),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Conv2D(32, (3, 3), padding='same', activation= 'relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Conv2D(64, (3, 3), padding='same', activation= 'relu'),
    layers.MaxPooling2D(pool_size=(2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dense(30, activation='softmax'),
  ]
)

# Compile the model
model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

print(model.summary())

# Train the model
model.fit(x_train, y_train, batch_size=128, epochs=10, validation_split=0.1)

# Evaluate the model
test_loss, test_acc = model.evaluate(x_test, y_test)
print("Test accuracy:", test_acc)

def showImage(x, y, index):
  plt.figure(figsize=(15,2))
  plt.imshow(x[index])
  plt.xlabel(class_names[int(y[index])])

index = np.random.randint(0, len(x_test))
print(index)
showImage(x_test, y_test, index)
y_pred = model.predict(x_test[index:index+1])
y_pred = [np.argmax(arr) for arr in y_pred]
print(y_pred[0])
print(class_names)
print(class_names[y_pred[0]])

import json

with open('class_names.json', 'w') as f:
  json.dump(class_names, f)

from tensorflow.python.saved_model.save import save

save_dir = os.path.join('./' 'saved_model.h5')
model.save(save_dir)

!pip install tensorflowjs

!python --version

!pip install jax==0.4.21

!pip install jaxlib==0.4.21

import tensorflowjs as tfjs
tfjs.__version__

!tensorflowjs_converter --input_format=keras --output_format=tfjs_layers_model ./saved_model.h5 ./tfjs_model

