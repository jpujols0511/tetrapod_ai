import torch
import numpy as np
from utils.replay_buffer import ReplayBuffer
from model.model import DeepSarsaNetwork
from model.target_network import TargetNetwork

class Agent:
    def __init__(self, env, learning_rate, exploration_rate):
        self.env = env
        self.replay_buffer = ReplayBuffer(max_size=1000)
        self.model = DeepSarsaNetwork(input_size=env.action_space.n, output_size=env.action_space.n)
        self.learning_rate = learning_rate
        self.exploration_rate = exploration_rate
        # Initialize the target network
        self.target_network = TargetNetwork(env.action_space.n, env.action_space.n)

    def epsilon_greedy_action(self, state, epsilon):
        if np.random.rand() < epsilon:
            # Explore: take a random action
            action = self.env.action_space.sample()
        else:
            model_action = self.model(state).data.numpy()
            target_action = self.target_network(state).data.numpy()
            
            if len(model_action) > len(target_action):
                action = np.argmax(model_action)
            # Exploit: take the best action based on the current knowledge
            else:
                action = np.argmax(target_action)
            
        return action

    def update_target_network(self, tau):
        for main_param, target_param in zip(self.model.parameters(), self.target_network.parameters()):
            if target_param.shape == main_param.shape:
                target_param.data.copy_(tau * main_param.data + (1.0 - tau) * target_param.data)
            
    def evaluate(self):
        # Initialize performance metrics
        total_reward = 0
        num_episodes = 10
        episode_length = 0
        wins = 0

        # Run a fixed number of evaluation episodes
        for _ in np.arange(num_episodes):
            state = self.env.reset()
            done = False

            while not done:
                end_game_tensor = torch.from_numpy(self.env.end_game).float()
                if type(state) == torch.Tensor:
                    state_tensor = state 
                else:
                    state_tensor = torch.from_numpy(state).float().view(-1)
                # Take the best action based on the current knowledge
                model_action = self.model(torch.cat([state_tensor, end_game_tensor])).data.numpy()
                target_action = self.target_network(torch.cat([state_tensor, end_game_tensor])).data.numpy()
            
                if len(model_action) > len(target_action):
                    action = np.argmax(model_action)
                # Exploit: take the best action based on the current knowledge
                else:
                    action = np.argmax(target_action)

                print(f'action: {action // 5, action % 5}')
                # Take the action and observe the result
                next_state, reward, done, info = self.env.step(action)
                
                next_state = torch.from_numpy(info['state']).float().view(-1)
                end_game_tensor = torch.from_numpy(info['end_game']).float().view(-1)
                

                # Update performance metrics
                
                if reward == -1:
                    total_reward = reward
                elif reward > 0:  # Assuming a win is rewarded with 1
                    if done: 
                        wins += 1
                    total_reward += reward
                    
                episode_length += 1
                
                # Update the state
                state = next_state
            
           
                
        # Calculate average performance metrics
        average_reward = total_reward / num_episodes
        average_episode_length = self.env.steps / num_episodes
        win_rate = wins / num_episodes
        print(f'wins {wins} average_episode_length {average_episode_length}  total_reward {total_reward}')

        return average_reward, average_episode_length, win_rate

    def improve(self):
        # Calculate the agent's performance metrics
        average_reward, average_episode_length, win_rate = self.evaluate()
        print(average_reward, average_episode_length, win_rate)
        # Adjust the agent's hyperparameters based on its performance
        if average_reward > 0.5:
            self.learning_rate *= 1.1  # Increase learning rate if average reward is high
        if average_episode_length < 1.0:
            self.exploration_rate *= 0.9  # Decrease exploration rate if average episode length is short
        if win_rate > 0.7:
            self.replay_buffer.max_size *= 2  # Increase replay buffer size if win rate is high
            
        
        