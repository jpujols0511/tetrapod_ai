# Path: model.py
# Create a model.py file that will be used to create the neural network model.
# The QNetwork class will be used to create the neural network model.
# The model will be a fully connected neural network with 3 hidden layers.
# The first hidden layer will have 256 nodes.
# The second hidden layer will have 256 nodes.
# The third hidden layer will have 128 nodes.
# The output layer will have 25 nodes.
# The activation function used for the hidden layers will be ReLU.
# The activation function used for the output layer will be linear.
# The forward method will return the output of the model.

# Path: model.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class QNetwork(nn.Module):
    def __init__(self, input_size=25, hidden_size1=256, hidden_size2=256, hidden_size3=128, output_size=25):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size1)
        self.fc2 = nn.Linear(hidden_size1, hidden_size2)
        self.fc3 = nn.Linear(hidden_size2, hidden_size3)
        self.fc4 = nn.Linear(hidden_size3, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x)) 
        x = F.relu(self.fc3(x))
        x = self.fc4(x)
        return x
    