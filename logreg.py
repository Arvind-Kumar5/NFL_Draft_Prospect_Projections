import nfl_projection
import torch
from torch import nn
import numpy as np
from tqdm import tqdm


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

    return torch.tensor(_vec), torch.tensor(_lab) 

def getData(dfPath, combineDfPath):
    df = nfl_projection.main(dfPath, combineDfPath)
    vector, label = getDataTensor(df)
    return vector, label

class LogisticRegression(torch.nn.Module):
     
     def __init__(self, inputDim, outputDim):
         super(LogisticRegression, self).__init__()
         self.linear = torch.nn.Linear(inputDim, outputDim)

     def forward(self, x):
         outputs = torch.sigmoid(self.linear(x))
         return outputs

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

epochs = 20000
inputDim = 24 # 24 inputs --> 24 stats
outputDim = 1 # Single binary output 
learning_rate = 0.001 # can change later

model = LogisticRegression(inputDim,outputDim)
lossFunction = torch.nn.BCELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=learning_rate)

losses = []
lossesVal = []
Iterations = []
iter = 0

for epoch in tqdm(range(int(epochs)),desc='Training Epochs'):
    optimizer.zero_grad() # Setting our stored gradients equal to zero
    outputs = model(xTrain)
    outputs = torch.squeeze(outputs)
    
    loss = lossFunction(outputs, yTrain) 
    
    loss.backward() # Computes the gradient of the given tensor w.r.t. the weights/bias
    
    optimizer.step() # Updates weights and biases with the optimizer (SGD)
    
    iter+=1

    if iter%1000==0:
        with torch.no_grad():
            # Calculating the loss and accuracy for the validation dataset
            correctVal = 0
            totalVal = 0
            outputsVal = torch.squeeze(model(xVal))
            lossVal = lossFunction(outputsVal, yVal)
            
            predictedVal = outputsVal.round().detach().numpy()
            totalVal += yVal.size(0)
            correctVal += np.sum(predictedVal == yVal.detach().numpy())
            accuracyVal = 100 * correctVal/totalVal
            lossesVal.append(lossVal.item())
            
            # Calculating the loss and accuracy for the train dataset
            total = 0
            correct = 0
            total += yTrain.size(0)
            correct += np.sum(torch.squeeze(outputs).round().detach().numpy() == yTrain.detach().numpy())
            accuracy = 100 * correct/total
            losses.append(loss.item())
            Iterations.append(iter)
            
            print(f"Iteration: {iter}. \nTrain - Loss: {loss.item()}. Accuracy: {accuracy}")
            print(f"Validation -  Loss: {lossVal.item()}. Accuracy: {accuracyVal}\n")


with torch.no_grad():
    correctTest = 0
    totalTest = 0
    
    outputsTest = torch.squeeze(model(xTest))
    lossTest = lossFunction(outputsTest, yTest)

    predictedTest = outputsTest.round().detach().numpy()
    totalTest += yTest.size(0)
    correctTest += np.sum(predictedTest == yTest.detach().numpy())
    accuracyTest = 100 * correctTest/totalTest

    print()
    print("predictedTest: ", predictedTest)
    print("yTest: ", yTest)
    print(f"Test - Loss: {lossTest.item()}. Accuracy: {accuracyTest}")
