import nfl_projection
import torch
from torch import nn
from torch.utils.data import DataLoader
import numpy as np
import math

# PyTorch TensorBoard support
from torch.utils.tensorboard import SummaryWriter
from datetime import datetime

class NeuralNetwork(nn.Module):
    def __init__(self, numInputs, numOutputs):
        super().__init__()
        self.flatten = nn.Flatten()
        # add more layers later if needed
        # change layer sizes later if needed
        # try different activation functions: sigmoid, relu, tanh
        #SUCK IT SHOURDUPUP
        # shuardtoup
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(numInputs, 512), # ve are in a bit of trouble right here
            nn.ReLU(), 
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, numOutputs),
        ) 

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

def trainOneEpoch(trainVector, trainLabels, optimizer, model, lossFunction, epochIndex, tbWriter):
    runningLoss = 0
    lastLoss = 0

    for idx, inputs in enumerate(trainVector):
        inputs = torch.tensor([inputs.tolist()])
        # get input and label for every instance
        label = torch.tensor([trainLabels[idx].tolist()])

        # zero out gradients for every batch
        optimizer.zero_grad()

        # Make predictions for this batch
        print("----- inputs: ", inputs)
        print(inputs.shape)
        print("----- label: ", label)
        print(label.shape)
        outputs = model(inputs)
        print("----- outputs: ", outputs)
        print(outputs.shape)

        # Compute the loss and its gradients
        loss = lossFunction(outputs, label)
        loss.backward()

        # Adjust learning weights
        optimizer.step()

        # Gather data and report
        runningLoss += loss.item()

        # if idx % 1000 == 999:
        lastLoss = runningLoss / 1 # loss per batch
        print(' batch {} loss: {}'.format(idx + 1, lastLoss))
        tb_x = epochIndex * len(trainVector) + idx + 1
        tbWriter.add_scalar('Loss/train', lastLoss, tb_x)
        runningLoss = 0

        return lastLoss


def getDataTensor(df):
    _vec = []
    _lab = []

    for _, row in df.iterrows():
        x_vec = []
        label = int(row["ProBowl"])
        _lab.append(label)

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

print("Getting Training Data...")
trainDf = nfl_projection.main('TrainData/trainDf.csv', 'TrainData/combineTrainDf.csv')
trainVector, trainLabels = getDataTensor(trainDf)
print("---------- trainVector: ", trainVector)
print("----- trainVector size: ", trainVector.shape) # 113x24, we have 113 training example and each example has 24 dimensions (features)
print()
print("---------- trainLabels: ", trainLabels) # 113x1
print("----- trainLabel size: ", trainLabels.shape)
print()

print("Getting Validation Data...")
valDf = nfl_projection.main('ValidationData/valDf.csv', 'ValidationData/combineValDf.csv')
valVector, valLabels = getDataTensor(valDf)
print("---------- valVector: ", valVector)
print("----- valVector size: ", valVector.shape) 
print()
print("---------- valLabels: ", valLabels) 
print("----- valLabel size: ", valLabels.shape)
print()



model = NeuralNetwork(trainVector.shape[1], 2)#.to("cpu")
try:
    print(model)
    print("ve are in business")
except:
    print("ve are fucking blocked")

# testInput = torch.tensor([trainVector[0].tolist()])
# print("test input: ", testInput)
# print("test input shape: ", testInput.shape)
# logits = model(testInput)
# predProbab = nn.Softmax(dim=1)(logits)
# yPred = predProbab.argmax(1)
# print("----- yPred")
# print(yPred)
# print(yPred.shape)

lossFunction = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
writer = SummaryWriter('runs/fashion_trainer_{}'.format(timestamp))

EPOCHS = 5
bestVloss = 1_000_000.

for epoch in range(EPOCHS):
    print('EPOCH {}:'.format(epoch + 1))

    # Make sure gradient tracking is on, and do a pass over the data
    model.train(True)
    avgLoss = trainOneEpoch(trainVector, trainLabels, optimizer, model, lossFunction, epoch, writer)

    # We don't need gradients on to do reporting
    model.train(False)

    runningValLoss = 0.0
    for i, valInputs in enumerate(valVector):
        valInputs = torch.tensor([valInputs.tolist()])
        # get input and label for every instance
        valLabel = torch.tensor([valLabels[i].tolist()])
        valOutputs = model(valInputs)
        valLoss = lossFunction(valOutputs, valLabel)
        runningValLoss += valLoss

    avgValLoss = runningValLoss / (i + 1)
    print('LOSS: train {} \t validation {}'.format(avgLoss, avgValLoss))

    # Log the running loss averaged per batch
    # for both training and validation
    writer.add_scalars('Training vs. Validation Loss',
                    { 'Training' : avgLoss, 'Validation' : avgValLoss },
                    epoch + 1)
    writer.flush()

    # Track best performance, and save the model's state
    if avgValLoss < bestVloss:
        bestVloss = avgValLoss
        model_path = 'model_{}_{}'.format(timestamp, epoch)
        torch.save(model.state_dict(), model_path)

    

