from model.model import QNetwork
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from utils.replay_buffer import ReplayBuffer

class DSNAgent(object):
    def __init__(self, env):
        self.qnet = QNetwork()
        self.qnet_optim = torch.optim.Adam(self.qnet.parameters(), lr=0.001)
        self.discount_factor = 0.99
        self.MSELoss_function = nn.MSELoss()
        self.replay_buffer = ReplayBuffer()
        self.env = env
        pass
    
    def epsilon_greedy_action(self, state, epsilon):
       
        if np.random.uniform(0, 1) < epsilon:
                return self.env.action_space.sample()  # choose random action
        else:
                network_output_to_numpy = self.qnet(state).data.numpy()
                return np.argmax(network_output_to_numpy)  # choose greedy action
        
    
    def update_Sarsa_Network(self, state, next_state, action, next_action, reward, terminals):
        
        qsa = torch.gather(self.qnet(state), dim=1, index=action.long())
        
        qsa_next_action = torch.gather(self.qnet(next_state), dim=1, index=next_action.long())

        not_terminals = 1 - terminals

        qsa_next_target = reward + not_terminals * (self.discount_factor * qsa_next_action)

        q_network_loss = F.mse_loss(qsa, qsa_next_target.detach())
        self.qnet_optim.zero_grad()
        q_network_loss.backward()
        self.qnet_optim.step()
        
            
    def update_s(self, update_rate):
        
        for i, update in enumerate(update_rate):
            (states, next_states, actions, next_actions, rewards, terminals) = self.replay_buffer.sample_batch(64)
            states = torch.tensor(states).view(64, -1).to(torch.float32)
            next_states = torch.tensor(next_states).view(64, -1).to(torch.float32)
            actions = torch.tensor(actions).view(64, -1).to(torch.float32)
            next_actions = torch.tensor(next_actions).view(64, -1).to(torch.float32)
            rewards = torch.Tensor(rewards).view(64, -1).to(torch.float32)
            terminals = torch.Tensor(terminals).view(64, -1).to(torch.float32)
            
            self.update_Sarsa_Network(states, next_states, actions, next_actions, rewards, terminals)

    def best_move(self, state):
        
        return np.argmax(self.qnet(state).data.numpy())