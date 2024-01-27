# Path: game.py
import torch
import random
import numpy as np
from collections import deque
from model.model import QNetwork
from trainer.trainer import QTrainer
from utils.helper import plot
from game.game import Minesweeper

class MinesweeperGame:
    def __init__(self, n_games, epsilon, gamma):
        self.n_games = n_games
        self.epsilon = epsilon
        self.gamma = gamma
        self.memory = deque(maxlen=100000)
        self.model = QNetwork()
        self.trainer = QTrainer(self.model, lr=0.001, gamma=self.gamma)

    def get_state(self):
        return np.array(self.game.board).ravel()

    def get_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, 24)
        else:
            state = torch.tensor(state, dtype=torch.float)
            return torch.argmax(self.model(state)).item()

    def step(self, action):
        self.game.uncover(action)
        next_state = self.get_state()
        reward = self.game.reward
        done = self.game.done
        return next_state, reward, done

    def memory_replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        batch = random.sample(self.memory, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def play(self, withModel=True):
        scores = []
        mean_scores = []
        if withModel:
            self.model.load_state_dict(torch.load("model.pth"))
        for i in range(self.n_games):
            self.game = Minesweeper()
            self.state = self.get_state()
            self.done = False
            score = 0
            while not self.done:
                action = self.get_action(self.state)
                next_state, reward, self.done = self.step(action)
                self.memory.append((self.state, action, reward, next_state, self.done))
                self.state = next_state
                score += reward
            scores.append(score)
            mean_score = np.mean(scores[-100:])
            mean_scores.append(mean_score)
            plot(scores, mean_scores)
            if i % 10 == 0:
                print(f"Game {i} Score: {score} Mean Score: {mean_score}")
            self.memory_replay(100)
        torch.save(self.model.state_dict(), "model.pth")