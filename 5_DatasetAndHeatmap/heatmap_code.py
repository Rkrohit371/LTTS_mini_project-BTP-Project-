# -*- coding: utf-8 -*-
"""heatmap_code.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1QnyugJoXYjtxUXhRtpFC7bh8J6Q2QOHN
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets,transforms
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from keras.layers import merge
from functools import partial
import tensorflow as tf

import tensorflow as tf
from tensorflow.python.ops import nn
from tensorflow.python.keras import activations, regularizers, initializers, constraints, engine
from tensorflow.python.keras.utils import conv_utils
from tensorflow.python.keras.layers import Layer, deserialize, Conv1D, GRU, LSTM
from tensorflow.python.keras import backend as K
from tensorflow.python.ops import array_ops


# tf.compat.v1.enable_eager_execution()
tf.compat.v1.disable_eager_execution()

tester_data = pd.read_csv("/content/1000_tweets_per_user_train.csv", encoding='utf-8')
print(tester_data.head(10))
tester_data = tester_data.sample(frac=0.1)
tester_data.info()

tester_data.rename(columns = {'0':'text', '1':'authors'}, inplace = True)
tester_data['authors'].value_counts()

from tensorflow.python.keras.models import Sequential,Model
from tensorflow.python.keras.layers import Flatten, Dense,AveragePooling1D,GRU,Convolution1D, MaxPooling1D, AveragePooling1D,Embedding,Input, Dense, Dropout, Flatten

import pandas as pd
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(tester_data['text'], tester_data['authors'], test_size=0.33, random_state=0)

print(X_train.shape,y_train.shape,X_test.shape,y_test.shape)

X_train=pd.DataFrame(X_train)
X_test=pd.DataFrame(X_test)
y_train=pd.DataFrame(y_train)
y_test=pd.DataFrame(y_test)


print('Tweet: After Changing to Dataframe ', X_train.shape,y_train.shape,X_test.shape,y_test.shape)

X_train=X_train.iloc[:,:].values
X_test=X_test.iloc[:,:].values
y_train=y_train.iloc[:,:].values
y_test=y_test.iloc[:,:].values

print('Tweet: After Changing to Dataframe ', X_train.shape,y_train.shape,X_test.shape,y_test.shape)

train=np.concatenate((X_train,y_train),axis=1)
test=np.concatenate((X_test,y_test),axis=1)
print('Tweet: Train and Test size = ', train.shape, test.shape)

print(type(train), type(test))

np.random.shuffle(train)
np.random.shuffle(test)

train=pd.DataFrame(train)
test=pd.DataFrame(test)

print(train)
print(test)

print('Tweet: Train and Test size = ', train.shape, test.shape)

X = train[train.columns[0]]
y = train[train.columns[1:]]
print(X.shape)
print(y.shape)

y



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
print(X_train.shape,y_train.shape,X_test.shape,y_test.shape)

from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
encoder = LabelEncoder()
# encoder_ml = LabelEncoder()
encoder.fit(y_train)
# # encoder_ml.fit(y_train_ml)
encoded_Y = encoder.transform(y_train)
# # # encoded_Y_ml = encoder_ml.transform(y_train_ml)
# convert integers to dummy variables (i.e. one hot encoded)
y_train = np_utils.to_categorical(encoded_Y)
# # y_train_ml = np_utils.to_categorical(encoded_Y_ml)

from sklearn.preprocessing import LabelEncoder
from keras.utils import np_utils
encoder = LabelEncoder()
# encoder_ml = LabelEncoder()
encoder.fit(y_test)
# # encoder_ml.fit(y_test_ml)
encoded_Y = encoder.transform(y_test)
# # # encoded_Y_ml = encoder_ml.transform(y_test_ml)
# convert integers to dummy variables (i.e. one hot encoded)
y_test = np_utils.to_categorical(encoded_Y)
# # y_test_ml = np_utils.to_categorical(encoded_Y_ml)

def create_vocab_set():
    alphabet = (list(string.ascii_lowercase) + list(string.digits) + list(string.punctuation) + ['\n'] + [' '] )
    vocab_size = len(alphabet)
    check = set(alphabet)

    vocab = {}
    reverse_vocab = {}
    for ix, t in enumerate(alphabet):
        vocab[t] = ix
        reverse_vocab[ix] = t
    return vocab, reverse_vocab, vocab_size, check

import string

maxlen = 140
vocab, reverse_vocab, vocab_size, check =create_vocab_set()
print(vocab_size)

def encode_data(x, maxlen, vocab, vocab_size, check):

    input_data = np.zeros((len(x), maxlen, vocab_size))
    for dix, sent in enumerate(x):
        counter = 0
        sent_array = np.zeros((maxlen, vocab_size))
        chars = list(sent.lower())
        for c in chars:
            if counter >= maxlen:
                pass
            else:
                char_array = np.zeros(vocab_size, dtype=np.int)
                if c in check:
                    ix = vocab[c]
                    char_array[ix] = 1
                sent_array[counter, :] = char_array
                counter += 1
        input_data[dix, :, :] = sent_array

    return input_data

# X_train = X_train.astype(str)
# X_test = X_test.astype(str)
X_train = encode_data(X_train, maxlen, vocab, vocab_size, check)
X_test= encode_data(X_test, maxlen, vocab, vocab_size, check)

# X_train_ml = encode_data(X_train_ml, maxlen, vocab, vocab_size, check)
# X_test_ml = encode_data(X_test_ml, maxlen, vocab, vocab_size, check)

# print('Mail: Before ', X_train_ml.shape,y_train_ml.shape,X_test_ml.shape,y_test_ml.shape)

from sklearn.model_selection import train_test_split
X_train, X_eval, y_train, y_eval = train_test_split(X_train,y_train, test_size = 0.25, random_state = 0)
# X_train_ml, X_eval_ml, y_train_ml, y_eval_ml = train_test_split(X_train_ml,y_train_ml, test_size = 0.25, random_state = 0)

print('TweetA: fter ', X_train.shape,y_train.shape,X_test.shape,y_test.shape)
# print('Mail: After ', X_train_ml.shape,y_train_ml.shape,X_test_ml.shape,y_test_ml.shape)

from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint
es = EarlyStopping(monitor='val_loss', mode='min', verbose=1,patience=3)
callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3)

gru_len = 128
Routings = 5
Num_capsule = 10
Dim_capsule = 16
dropout_p = 0.3
rate_drop_dense = 0.3

def squash(x, axis=-1):
    s_squared_norm = K.sum(K.square(x), axis, keepdims=True) + K.epsilon()
    scale = K.sqrt(s_squared_norm) / (0.5 + s_squared_norm)
    return scale * x


# define our own softmax function instead of K.softmax
# because K.softmax can not specify axis.
def softmax(x, axis=-1):
    ex = K.exp(x - K.max(x, axis=axis, keepdims=True))
    return ex / K.sum(ex, axis=axis, keepdims=True)


# define the margin loss like hinge loss
def margin_loss(y_true, y_pred):
    lamb, margin = 0.5, 0.1
    return K.sum(y_true * K.square(K.relu(1 - margin - y_pred)) + lamb * (
        1 - y_true) * K.square(K.relu(y_pred - margin)), axis=-1)

class Capsule(Layer):
    """A Capsule Implement with Pure Keras
    There are two vesions of Capsule.
    One is like dense layer (for the fixed-shape input),
    and the other is like timedistributed dense (for various length input).

    The input shape of Capsule must be (batch_size,
                                        input_num_capsule,
                                        input_dim_capsule
                                       )
    and the output shape is (batch_size,
                             num_capsule,
                             dim_capsule
                            )

    Capsule Implement is from https://github.com/bojone/Capsule/
    Capsule Paper: https://arxiv.org/abs/1710.09829
    """

    def __init__(self,
                 num_capsule,
                 dim_capsule,
                 routings=3,
                 share_weights=True,
                 activation='squash',
                 **kwargs):
        super(Capsule, self).__init__(**kwargs)
        self.num_capsule = num_capsule
        self.dim_capsule = dim_capsule
        self.routings = routings
        self.share_weights = share_weights
        if activation == 'squash':
            self.activation = squash
        else:
            self.activation = activations.get(activation)

    def build(self, input_shape):
        input_dim_capsule = input_shape[-1]
        if self.share_weights:
            self.kernel = self.add_weight(
                name='capsule_kernel',
                shape=(1, input_dim_capsule,
                       self.num_capsule * self.dim_capsule),
                initializer='glorot_uniform',
                trainable=True)
        else:
            input_num_capsule = input_shape[-2]
            self.kernel = self.add_weight(
                name='capsule_kernel',
                shape=(input_num_capsule, input_dim_capsule,
                       self.num_capsule * self.dim_capsule),
                initializer='glorot_uniform',
                trainable=True)

    def call(self, inputs):
        """Following the routing algorithm from Hinton's paper,
        but replace b = b + <u,v> with b = <u,v>.

        This change can improve the feature representation of Capsule.

        However, you can replace
            b = K.batch_dot(outputs, hat_inputs, [2, 3])
        with
            b += K.batch_dot(outputs, hat_inputs, [2, 3])
        to realize a standard routing.
        """

        if self.share_weights:
            hat_inputs = K.conv1d(inputs, self.kernel)
        else:
            hat_inputs = K.local_conv1d(inputs, self.kernel, [1], [1])

        batch_size = K.shape(inputs)[0]
        input_num_capsule = K.shape(inputs)[1]
        hat_inputs = K.reshape(hat_inputs,
                               (batch_size, input_num_capsule,
                                self.num_capsule, self.dim_capsule))
        hat_inputs = K.permute_dimensions(hat_inputs, (0, 2, 1, 3))

        b = K.zeros_like(hat_inputs[:, :, :, 0])
        for i in range(self.routings):
            c = softmax(b, 1)
            o = self.activation(K.batch_dot(c, hat_inputs, [2, 2]))
            if i < self.routings - 1:
                b = K.batch_dot(o, hat_inputs, [2, 3])
                if K.backend() == 'theano':
                    o = K.sum(o, axis=1)

        return o

    def compute_output_shape(self, input_shape):
        return (None, self.num_capsule, self.dim_capsule)

def model2(filter_kernels, dense_outputs, maxlen, vocab_size, nb_filter,cat_output):
    d = 300
    inputs = Input(shape=(maxlen, vocab_size), name='input', dtype='float32')
    conv1 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[0], activation='relu',input_shape=(maxlen, vocab_size))(inputs)
    conv2 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[1], activation='relu',input_shape=(maxlen, vocab_size))(inputs)
    conv3 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[2], activation='relu',input_shape=(maxlen, vocab_size))(inputs)
    conv4 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[3], activation='relu',input_shape=(maxlen, vocab_size))(inputs)


    # conv1 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[0],
    #                        activation='relu')(conv1)
    # conv2 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[0],
    #                        activation='relu')(conv2)
    #conv3 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[1], activation='relu')(conv3)

    conv1 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[0],
                           activation='relu')(conv1)
    conv2 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[1],
                           activation='relu')(conv2)

    conv3 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[2],
                           activation='relu')(conv3)
    conv4 = Convolution1D(filters=nb_filter, kernel_size=filter_kernels[3],
                           activation='relu')(conv4)

    #conv1 = MaxPooling1D()(conv1)
    #conv2 = MaxPooling1D()(conv2)
    #conv3 = MaxPooling1D()(conv3)
    #conv4 = MaxPooling1D()(conv4)

    conv1 = LSTM(100)(conv1)
    conv2 = GRU(100)(conv2)
    conv3 = Capsule(num_capsule=1 ,dim_capsule=72, routings=1,share_weights=True)(conv3)
    conv4 = Capsule(num_capsule=1 ,dim_capsule=72, routings=1,share_weights=True)(conv4)

#    conv2 = MaxPooling1D()(conv2)

    conv1 = Flatten()(conv1)
    conv2 = Flatten()(conv2)
    conv3 = Flatten()(conv3)
    conv4 = Flatten()(conv4)

    conv_comb = tf.keras.layers.Concatenate(axis=1)([conv1, conv2, conv3, conv4])
    pred = Dense(cat_output, activation='softmax', name='output')(conv_comb)
    model = Model(inputs=inputs, outputs=pred)

    return model

print('Tweet: Last ', X_train.shape,y_train.shape,X_test.shape,y_test.shape)
# print('Mail: Last ', X_train_ml.shape,y_train_ml.shape,X_test_ml.shape,y_test_ml.shape)
nb_filter = 500
dense_outputs = 256
filter_kernels = [1,3,3,4,5]
cat_output = 50
# cat_output_ml = 20
early_stopping = EarlyStopping(monitor='val_loss', patience=5)
#model = model2(filter_kernels, dense_outputs,maxlen, vocab_size, nb_filter, cat_output)
# model = model2(filter_kernels, dense_outputs,maxlen, vocab_size, nb_filter, cat_output)
model = model2(filter_kernels, dense_outputs,maxlen, vocab_size, nb_filter, cat_output)
#print(model.summary())
print(model.summary())

#adam1=Adam(lr=1.00, beta_1=0.9, beta_2=0.999, amsgrad=False)
model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])
#model.compile(optimizer="adam", loss = loss_funcs_DW, metrics = metrics_DW)
model.fit(np.array(X_train), np.array(y_train),validation_data=(np.array(X_eval), np.array(y_eval)),batch_size=32,epochs=1, verbose=1,callbacks=[callback])

# model.fit([np.array(X_train), np.array(X_train_ml)], [np.array(y_train), np.array(y_train_ml)], validation_data=([np.array(X_eval), np.array(X_eval_ml)], [np.array(y_eval), np.array(y_eval_ml)]),batch_size=32,epochs=200, verbose=2,callbacks=[callback])
#model_ml.fit(np.array(X_train_ml), np.array(y_train_ml),validation_data=(np.array(X_eval_ml), np.array(y_eval_ml)),batch_size=32,epochs=200, verbose=1,callbacks=[callback])
#model.compile(loss='categorical_crossentropy', optimizer="adam", metrics=['accuracy'])

# model.fit(np.array(X_train), np.array(y_train),validation_data=(np.array(X_eval), np.array(y_eval)),batch_size=32,epochs=100, verbose=1,callbacks=[callback])

y_pred  = model.predict([np.array(X_test)])
y_pred=pd.DataFrame(y_pred)
y_pred=y_pred.eq(y_pred.where(y_pred != 0).max(1), axis=0).astype(int)
y_pred=y_pred.iloc[:,:].values
y_test=pd.DataFrame(y_test)
y_test=y_test.eq(y_test.where(y_test != 0).max(1), axis=0).astype(int)
y_test=y_test.iloc[:,:].values


result=[]
for i in range(0,len(y_test)):
  for j in range(0,len(y_test[0])):
    if(y_test[i][j]==1):
      result.append(j)

predicted=[]
for i in range(0,len(y_pred)):
  for j in range(0,len(y_pred[0])):
    if(y_pred[i][j]==1):
      predicted.append(j)

# result_ml=[]
# for i in range(0,len(y_test_ml)):
#   for j in range(0,len(y_test_ml[0])):
#     if(y_test_ml[i][j]==1):
#       result_ml.append(j)



# predicted_ml=[]
# for i in range(0,len(y_pred_ml)):
#   for j in range(0,len(y_pred_ml[0])):
#     if(y_pred_ml[i][j]==1):
#       predicted_ml.append(j)

#print('Tweet: ', result)
#print('Tweet: ',predicted)

# print('Mail: ',result_ml)
# print('Mail: ',predicted_ml)

from sklearn.metrics import confusion_matrix
cm = confusion_matrix(result,predicted)

#print(cm)

# cm_ml = confusion_matrix(result_ml,predicted_ml)

# print(cm_ml)

from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
print('Tweet Report')
print('Confusion Matrix :')
#print(cm)
print('Accuracy Score :',accuracy_score(result, predicted))
print('Report : ')
print(classification_report(result, predicted, digits=6))

k=20
X_train1=[]
y_train1=[]
for i in range(0,2):
  for j in range(k,k+20):
    X_train1.append(tester_data.iloc[j,0])
    y_train1.append(tester_data.iloc[j,1])
  k+=1000

# tf.compat.v1.enable_eager_execution()
# tf.compat.v1.enable_eager_execution(
#     config=None, device_policy=None, execution_mode=None
# )
# tf.compat.v1.enable_eager_execution()
def watch_layer(layer, tape):
    """
    Make an intermediate hidden `layer` watchable by the `tape`.
    After calling this function, you can obtain the gradient with
    respect to the output of the `layer` by calling:

        grads = tape.gradient(..., layer.result)

    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Store the result of `layer.call` internally.
            layer.result = func(*args, **kwargs)
            # From this point onwards, watch this tensor.
            tape.watch(layer.result)
            # Return the result to continue with the forward pass.
            return layer.result
        return wrapper
    layer.call = decorator(layer.call)
    return layer

# tf.compat.v1.disable_eager_execution()
import math

file=open("heatmap_authorshipatribution2_new.html","w")
for i in range(0,40):
  type_here=[]
  type_here.append(X_train1[i])
  typr_here=pd.DataFrame(type_here)
  typr_here = encode_data(type_here, maxlen, vocab, vocab_size, check)
  y_pred = model.predict(typr_here)
  Xtst=typr_here
  class_idx = np.argmax(y_pred[0]) #not needed in this case as only two classes
  class_output = model.output[:, class_idx]
  last_conv_layer = model.get_layer("conv1d_11")
  grads = K.gradients(class_output, last_conv_layer.output)[0]
  pooled_grads = K.mean(grads)
  iterate = K.function([model.input], [pooled_grads, last_conv_layer.output[0]])
  pooled_grads_value, conv_layer_output_value = iterate([Xtst])
  

  heatmap = np.mean(conv_layer_output_value, axis=-1)
  heatmap = np.maximum(heatmap,0)
  heatmap /= np.max(heatmap)#normalise values in the prediction
  norm_len = 36/last_conv_layer.output_shape[1]
  html = ""
  if y_pred[0][0]>0.5:
    pred = '90078731'
  else:
    pred = '51964081'
  html += "<span><h3>Based on the description, the model believes that text belongs to {} author ".format(pred)
  html += "<small><br>Confidence: {:.0f}%<br><br></small></h3></span>".format(abs(((y_pred[0][0]*100)-50)*2))
  for j,i in enumerate(type_here[0].split()):
    html += "<span style='background-color:rgba({},0,15,{})'>{} </span>".format(heatmap[math.floor(j/norm_len)]*255,heatmap[math.floor(j/norm_len)]-0.3,i)
  file.write(html)
file.close()

