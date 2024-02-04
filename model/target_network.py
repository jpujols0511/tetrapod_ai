import torch.nn as nn
import torch.nn.functional as F

class TargetNetwork(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_size=128):
        super(TargetNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x
    
    