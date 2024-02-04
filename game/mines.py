"""
The game mines is a game with a 5x5 grid which contains 25 tiles. 
The game mines is registered locally stored using openai gym.
When the game begins, all the tiles are covered, the state of the game when it starts is a 5x5 grid with zeros.
Under every tile there is either a gem or a mine generated randomly by the game. 
The game also generates a reward board which contains the rewards of the game, 1 for a gem, -1 for a mine.
The game can have a combination of gems and mines that yields different multipliers depending on the amount of gems uncovered by the agent. 
The agent is able generate random coordinates from (0, 0) to (4,4) that map to the uncovered tiles to reveal the reward of a gem or a mine. 
The agent has the option of ending the game early with the reward if it uncovers at least 1 gem and feels like the risk of hitting a mine is too high and would rather walk away with the reward. 
The action space is a discrete space of size * size + 1, the agent can pick from tile (0, 0) to tile (size - 1, size - 1) and the agent can also pick the "Quit" which would be represented in an array as a 0 to continue or 1 to stop the game early.
If the game has 22 gems and 3 mines, the agent canpotentially get a reward of 22 if it uncovers all the gems without hitting a mine.
The risk of uncovering a mine increases as the amount of gems that the agent uncovers increases.
The agent has to balance the amount of steps that it must take to get the best reward without hitting a mine. 
If the agent uncovers a mine, the game ends with a reward of a negative amount of the gems uncovered and the agent loses the game.
The agent can only uncover one tile at a time and the game ends when all the tiles are uncovered or the agent uncovers a mine.
The agent can only uncover a tile that has not been uncovered yet. If the agent tries to uncover a mine that has already been uncovered the agent receives a reward of 0.

size is the size of the grid (size x size)
num_gems is the number of gems in the game
num_mines is the number of mines in the game
state is the state of the game starts as a grid of zeros
reward_board is the reward board that contains the rewards of the game, 1 for a gem, -1 for a mine
positions is a list of random positions that the agent can uncover ranging from (0, 0) to (size - 1, size - 1)
positions are shuffled to randomize the positions of the gems and mines
place_mines places the mines in the reward board
place_gems places the gems in the reward board

The agent can pick from tile (0, 0) to tile (size - 1, size - 1)
The observation space is a tuple of the size of the grid
The action space is a discrete space of size * size
The agent can only uncover one tile at a time
The agent can only uncover a tile that has not been uncovered yet
The step function takes an action and returns the next state, reward, done, and info the action is a tuple of the x and y coordinates of the tile that the agent wants to uncover
The reward is the reward of the tile that the agent uncovers
The done is a boolean that is true if the game is over if the agent uncovers a mine or if all the tiles are uncovered or if the agent decides to end the game early
The info is a dictionary that contains the next state of the game with the action that the agent took
"""

import numpy as np
import gym
from gym import spaces

class MinesGameEnv(gym.Env):
    def __init__(self, size=5, num_gems=22):
        super(MinesGameEnv, self).__init__()
        self.size = size
        self.num_mines = np.power(self.size, 2) - num_gems 
        self.num_gems = num_gems
        self.max_steps = num_gems
        self.steps = 0
        self.num_gems_collected = 0
        self.state = np.zeros((size, size), dtype=np.int8)
        self.end_game = np.array([0]) # 0 for continue, 1 for end game
        self.reward_board = np.zeros((size, size), dtype=np.int8)
        self.positions = [(i, j) for i in np.arange(self.size) for j in np.arange(self.size)]
        
        np.random.shuffle(self.positions)
        
        self.place_mines()    
        self.place_gems()
        
        # Agent can pick from tile (0, 0) to tile (size - 1, size - 1)
        self.action_space = spaces.Discrete(size * size + 1) # +1 for the "Quit" action
        self.observation_space = spaces.Tuple((spaces.Discrete(size), spaces.Discrete(size)))
        
    def reset(self):
        self.state = np.zeros((self.size, self.size), dtype=np.int8)
        self.reward_board = np.zeros((self.size, self.size), dtype=np.int8)
        self.end_game = np.array([0]) # 0 for continue, 1 for end game
        self.positions = [(i, j) for i in np.arange(self.size) for j in np.arange(self.size)]
        np.random.shuffle(self.positions)
        self.place_mines()    
        self.place_gems()
        self.num_gems_collected = 0
        self.steps = 0
        return self.state
    
    def place_gems(self):
        for _ in np.arange(self.num_gems):
            x, y = self.positions.pop()
            if(self.reward_board[x][y] == 0):
                self.reward_board[x][y] = 1

    
    def place_mines(self):
        for _ in np.arange(self.num_mines):
            x, y = self.positions.pop()
            
            if(self.reward_board[x][y] == 0):
                self.reward_board[x][y] = -1
                
   
    def step(self, action):
        # Calculate the reward
        #debug here
        if self.steps >= self.max_steps:
            print(f'exceeding max steps {self.steps}')
            self.end_game = np.array([1])
            reward = self.num_gems_collected if self.num_gems_collected > 0 else -1
            done = True
           
            return (action - 1 // self.size, action - 1 % self.size), reward, done, {'state': self.state, 'end_game': self.end_game}
        if action == 25 and self.num_gems_collected > 0:  # 25 is the index of the "Quit" action, agent must collect at least 1 gem to quit
            print(f'quitting game early {self.num_gems_collected}')
            reward = self.num_gems_collected  # Reward based on the number of gems collected
            done = True
            self.end_game = np.array([1]) # End the game
            
            return (action - 1 // self.size, action - 1 % self.size), reward, done, {'state': self.state, 'end_game': self.end_game}
        elif action < 25 and self._is_valid_action(action):
            x = action // self.size
            y = action % self.size
            self.steps += 1
            reward = self.reward_board[x][y]
            self.state[x][y] = reward # Uncover the tile
            if reward == 1: 
                self.num_gems_collected += 1
                self.end_game = np.array([0])
            elif reward == -1: 
                reward = self.num_gems_collected * -1
                self.end_game = np.array([1])
            
            done = reward <= -1 or not np.any(self.state)  # End the game if a mine is uncovered or all tiles are uncovered
            if(done): 
                print(f"Game ended, gems collected = {self.num_gems_collected}")
            return (x, y), reward, done, {'state': self.state, 'end_game': self.end_game}
        
        elif action < 25 and not self._is_valid_action(action):
            self.steps += 1
            reward = 0
            done = False
            return (action // self.size, action % self.size), reward, done, {'state': self.state, 'end_game': self.end_game}
        else:
            x =  (action if action < 25 and action > 0 else 0 ) // self.size
            y = (action if action < 25 and action > 0 else 0) % self.size
            #debug
            self.steps += 1
            reward = 0
            # self.end_game = np.array([1]) # End the game
            # reward = self.reward_board[x][y]
            # if reward == 1: 
            #     self.num_gems_collected += 1
                
            # if reward == -1: 
            #     reward = self.num_gems_collected * -1
            #     self.end_game = np.array([1])
            
            return (x, y), reward, True if self.steps > self.max_steps else False, {'state': self.state, 'end_game': self.end_game}


    def render(self):
        print(self.state)
        
    def __getstate__(self):
        return self.state
    
    def get_index(self, x, y):
        return x * self.size + y

    def _is_valid_action(self, action):
        x = action // self.size
        y = action % self.size
        return self.state[x][y] == 0
    
    def print_board(self):
        for i in np.arange(self.size):
            for j in np.arange(self.size):
                print(self.reward_board[i][j], end=" ")
            print()