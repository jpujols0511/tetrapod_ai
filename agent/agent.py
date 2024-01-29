# Path: agent.py
        
import torch
import random
import numpy as np
from collections import deque
from game.game import MinesweeperGame
from model.model import QNetwork
from trainer.trainer import QTrainer
from utils.helper import plot, plot_loss

class QAgent:
    def __init__(self, n_games, epsilon, gamma, train_manual=False):
        self.n_games = n_games
        self.epsilon = epsilon
        self.gamma = gamma
        self.memory = deque(maxlen=100000)
        self.model = QNetwork()
        self.trainer = QTrainer(self.model, lr=0.05, gamma=self.gamma)
        self.total_wins = 0
        self.total_losses = 0
        self.model.load_state_dict(torch.load("model_2.pth"))
        # self.model.load_state_dict(torch.load("model.pth")) if not train_manual else self.model.load_state_dict(torch.load("model_2.pth"))
        self.train_manual = train_manual
        torch.manual_seed(42)
        np.random.seed(42)

    def get_state(self):
        return np.array(self.game.board).ravel()

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(1, 25) if not self.train_manual else random.randint(0, 24)
        else:
            state = torch.tensor(state, dtype=torch.float)
            return torch.argmax(self.model(state)).item()

    def perform_action(self, action):
        reward = self.game.uncover_cell(action)
        next_state = self.get_state()
        done = self.game.is_game_over()
        self.memory.append((self.state, action, reward, next_state, done))
        self.state = next_state

    def train(self, batch_size):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        
    def step(self, action):
        self.game.uncover_cell(action)
        next_state = self.get_state()
        reward = self.game.reward
        done = self.game.is_game_over()
        return next_state, reward, done
        
    def play(self, withModel=False):
        scores = []
        mean_scores = []
        total_wins = 0
        total_losses = 0
        if withModel and not self.train_manual:
            self.model.load_state_dict(torch.load("model.pth"))
        for i in range(self.n_games):
            self.game = MinesweeperGame()
            self.state = self.get_state()
            print(f"Game {i} state before playing {self.state}")
            self.done = False
            score = 0
            
            while not self.done:
                action = self.get_action(self.state)
                print(f"Game {i} action {action}")
                next_state, reward, self.done = self.step(action)
                self.memory.append((self.state, action, reward, next_state, self.done))
                self.state = next_state
                score = reward
                
            if score > 0:
                total_wins += 1
            elif score == -1:
                total_losses += 1
                
                
            self.game.print_board()
            scores.append(score)
            mean_score = np.mean(scores[::])
            mean_scores.append(mean_score)
            # plot(scores, mean_scores)
            if len(self.trainer.losses) > 0:
                plot_loss(self.trainer.losses)
            print(f"Game {i} Score: {score} Mean Score: {mean_score} Wins: {total_wins} Losses: {total_losses}")
            self.train(10)
            
            
        if not self.train_manual:
            torch.save(self.model.state_dict(), "model.pth")
        elif self.train_manual:
            torch.save(self.model.state_dict(), "model_2.pth")
        
    def init_game(self, state):
       
        # Load initial state
        self.state = np.array(state)
       
       
    def get_move(self, data):
        self.done = False
        
        if not self.done:
            action = self.get_action(self.state)
            return action
            # print(f"Action {action}")
            # next_state, reward, self.done = self.step(action)
            # self.state = next_state
            
            # ##step
            # self.game.uncover_cell(action)
            # next_state = self.get_state()
            # reward = self.game.reward
            # done = self.game.is_game_over()
            # return next_state, reward, done
        
        
        
    
    def play_games(self):
        for i in range(self.n_games):
            total_reward = self.play()
            print(f"Game {i+1}: {total_reward}")
        torch.save(self.model.state_dict(), "model.pth")

    def play_games_with_model(self):
        plot_scores = []
        plot_mean_scores = []
        total_score = 0
        total_wins = 0
        total_losses = 0
        self.model.load_state_dict(torch.load("model.pth"))
        for i in range(self.n_games):
            total_reward = self.play()
            
            if total_reward > 0:
                total_wins += 1
            else:
                total_losses += 1
                
            ratio = total_wins / total_losses if total_losses > 0 else total_wins
            
            # plot result 
            total_score += total_reward
            plot_scores.append(total_reward)
            mean_score = total_score / (i+1)
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)
            
            print(f"Game {i+1}: {total_reward} Wins: {total_wins} Lossses: {total_losses} W/L: {ratio}")


