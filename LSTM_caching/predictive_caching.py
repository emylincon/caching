import numpy as np
import random as r
import pandas as pd
import pickle
from sklearn.preprocessing import MinMaxScaler
import os
# import tensorflow as tf
# import tensorflow.keras as keras
# #import keras
# import keras.backend as K
# from keras.models import Model, Sequential, load_model
# from keras.layers import Dense, Embedding, Dropout, Input, Concatenate


def get_model(filename):
    # load the model from disk
    loaded_model = pickle.load(open(filename, 'rb'))
    return loaded_model


def predict_next(model, data):
    scaler = MinMaxScaler(feature_range=(0, 1))

    history = np.array(data)
    dataset = scaler.fit_transform(history)
    print(dataset.shape)
    # Scale the data to be values between 0 and 1
    # scaled_history = scaler.transform(history)
    # Create an empty list
    X_test = []
    # Append teh past 60 days
    X_test.append(dataset)
    # Convert the X_test data set to a numpy array
    X_test = np.array(X_test)
    print(X_test.shape)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    # Get the predicted scaled price
    print(X_test.shape)
    pred_value = model.predict(X_test)
    # undo the scaling
    pred_value = scaler.inverse_transform(pred_value)
    return pred_value


def test():
    pather = 'models'
    fn = os.listdir(pather)[0]
    data = [[r.randrange(40)] for _ in range(80)]
    model = get_model(f'{pather}/{fn}')
    pred = predict_next(model, data)
    print(pred)

test()
