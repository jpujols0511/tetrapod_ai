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

class DeepSarsaNetwork(nn.Module):
    def __init__(self, input_size, output_size, hidden_size=128):
        super(DeepSarsaNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

    def train_step(self, batch, target_network, learning_rate, discount_factor):
        # Extract the batch data
        states, actions, rewards, next_states, dones = batch
        states_tensor = torch.cat(states).view(-1, 26)
        next_states_tensor = torch.cat(next_states).view(-1, 26)
       
        # # Convert the concatenated tensors to a single tensor
        states_tensor = torch.tensor(states_tensor)
        actions_tensor = torch.tensor(actions).unsqueeze(1)
        rewards_tensor = torch.tensor(rewards).unsqueeze(1)
        dones_tensor = torch.tensor(dones).unsqueeze(1).type_as(rewards_tensor)
        
        # Calculate the Q-values for the current states and actions
        q_values = self(states_tensor).gather(1, actions_tensor)

        # Calculate the target Q-values for the next states
        next_q_values = target_network(states_tensor).max(1)[0].unsqueeze(1)

        # Calculate the expected Q-values
        expected_q_values = rewards_tensor + (1 - dones_tensor) * discount_factor * next_q_values

        # Calculate the loss
        loss = F.mse_loss(q_values, expected_q_values)

        # Perform a gradient descent step
        optimizer = torch.optim.Adam(self.parameters(), lr=learning_rate)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        return loss

    def choose_action(self, state):
        # Convert the state to a tensor
        state = torch.tensor(state, dtype=torch.float32)

        # Calculate the Q-values for the state
        q_values = self(state)

        # Choose the action with the highest Q-value
        action = torch.argmax(q_values).item()

        return action