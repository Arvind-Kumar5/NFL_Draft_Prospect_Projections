import nfl_projection
import torch
from torch import nn
from torch.utils.data import DataLoader
import numpy as np
import math

class NeuralNetwork(nn.Module):
    def __init__(self, numInputs, numDimensions, numOutputs):
        super().__init__()
        self.flatten = nn.Flatten()
        # add more layers later if needed
        # change layer sizes later if needed
        # try different activation functions: sigmoid, relu, tanh
        #SUCK IT SHOURDUPUP
        # shuardtoup
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(numInputs*numDimensions, 512), # ve are in a bit of trouble right here
            nn.ReLU(), 
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, numOutputs),
        ) 

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits

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

    return torch.tensor([_vec]), torch.tensor(_lab) # added [_vec] instead of just _vec to change dimensions

trainDf = nfl_projection.main()
trainVector, trainLabels = getDataTensor(trainDf)
print("---------- trainVector: ", trainVector)
print("----- trainVector size: ", trainVector.shape) # 113x24, we have 113 training example and each example has 24 dimensions (features)
print()
print("---------- trainLabels: ", trainLabels) # 113x1
print("----- trainLabel size: ", trainLabels.shape)
print()

# device = (
#     "cuda"
#     if torch.cuda.is_available()
#     else "mps"
#     if torch.backends.mps.is_available()
#     else "cpu"
# )

model = NeuralNetwork(trainVector.shape[1], trainVector.shape[2], 1)#.to("cpu")
try:
    print(model)
    print("ve are in business")

except:

    print("ve are fucking blocked")

logits = model(trainVector)
predProbab = nn.Softmax(dim=1)(logits)
yPred = predProbab.argmax(1)
print("----- yPred")
print(yPred)

