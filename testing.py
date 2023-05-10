from sklearn.metrics import classification_report, roc_curve, confusion_matrix, auc
from keras.models import Sequential
from keras.layers import Dense, Dropout
import nfl_projection
import matplotlib.pyplot as plt
import torch
import tensorflow as tf
import numpy as np


def getDataTensor(df):
    _vec = []
    _lab = []

    for _, row in df.iterrows():
        x_vec = []
        label = int(row["ProBowl"])
        _lab.append(float(label))

        for i in range(len(row)):
            if i == 19: # position index, skip for now, come back later
                continue
            data = row[i]
            if i > 3:
                if str(data).lower() == "nan":
                    x_vec.append(0) # just to keep it simple for now
                else: 
                    x_vec.append(float(data))
       
        _vec.append(x_vec)

    print("Vectors: ", np.shape(_vec))
    print("Labels: ", np.shape(_lab))

    return tf.constant(_vec, shape=np.shape(_vec)), tf.constant(_lab, shape=np.shape(_lab))

def getData(dfPath, combineDfPath):
    df = nfl_projection.main(dfPath, combineDfPath)
    vector, label = getDataTensor(df)
    return vector, label

print("Getting Train vector and label...")
xTrain, yTrain = getData('TrainData/trainDf.csv', 'TrainData/combineTrainDf.csv') 
print("---------- xTrain: ", xTrain)
print("----- xTrain size: ", xTrain.shape)
print("---------- yTrains: ", yTrain)
print("----- yTrain size: ", yTrain.shape)
print()

print("Getting Validation vector and label...")
xVal, yVal = getData('ValidationData/valDf.csv', 'ValidationData/combineValDf.csv') 
print("---------- xVal: ", xVal)
print("----- xVal size: ", xVal.shape) 
print("---------- yVal: ", yVal) 
print("----- yVal size: ", yVal.shape)
print()

print("Getting Test vector and label...")
xTest, yTest = getData('TestData/testDf.csv', 'TestData/combineTestDf.csv') 
print("---------- xTest: ", xTest)
print("----- xTest size: ", xTest.shape) 
print("---------- yTest: ", yTest) 
print("----- yTest size: ", yTest.shape)
print()

print(len(xTrain))
xTrain = np.expand_dims(xTrain, axis=1)
yTrain = np.expand_dims(yTrain, axis=1)
model = Sequential()
model.add(Dense(256, activation='relu', input_shape=xTrain[0].shape))
model.add(Dropout(0.4))
model.add(Dense(128, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.1))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

model.fit(xTrain, yTrain, validation_split=0.1, epochs=35, batch_size=10, verbose=1)

plt.plot(model.history.history['accuracy'])
plt.plot(model.history.history['val_accuracy'])
plt.title("Model Accuracy")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend(['Train', 'Val'], loc='upper left')
plt.savefig(f"neuralnet_accuracy.png")
plt.clf()

plt.plot(model.history.history['loss'])
plt.plot(model.history.history['val_loss'])
plt.title("Model Loss")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.legend(['Train', 'Val'], loc='upper left')
plt.savefig(f"neuralnet_loss.png")
plt.clf()

# pred_probs = model.predict_proba(X_test)[:, 1]
xTest = np.expand_dims(xTest, axis=1)
yTest = np.expand_dims(yTest, axis=1) # vot the fuck are these for and vy are they needed

#stackoverflow
# vell.

# model is currently retarded
# ytest is size 17 and only 2 players are probowl so yTest has two 1s and sixteen 0s
# pred has seventeen 0s
# so accuracy is currently 15/17 = around 88%
#oh shet

pred_probs = model.predict(xTest)
preds = np.round(pred_probs, 0)
print("yTest: ", yTest)
print(yTest.shape)
print("preds: ", preds)
print(preds.shape)