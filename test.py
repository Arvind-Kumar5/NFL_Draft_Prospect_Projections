import torch
from torch import nn

m = nn.Sigmoid()
loss = nn.BCELoss()
input = torch.randn(3, requires_grad=True)
print("input: ", input)
print("input size: ", input.shape)
print("input type: ", type(input))
target = torch.empty(3).random_(2)
print("target: ", target)
print("target size: ", target.shape)
print("target type: ", type(target))
output = loss(m(input), target)
output.backward()