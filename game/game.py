# Path: game.py
# A MinesweeperGame class in game.py that will be used to play the game.
# A mine game is generated with 24 separate game events, in the form of mines on the board. 
# Each float is multiplied by the number of possible unique tiles still remaining on the board. 
# This is done by subtracting the number of tiles remaining by 1 for each iteration of game event result generated using the corresponding float provided. 
# The location of the mine is plotted using a grid position from left to right, top to bottom.
# The fisher-yates shuffle implementation is utilised to prevent duplicate possible hits being generated. 
# Between 1 and 24 game event results are used, based on the settings chosen.
# The game is won when the agent uncovers a given amount of cells that may contain gems.
# The game is lost when the agent uncovers a mine.
# The agent can uncover a cell by clicking on it.
# The game is a 5x5 grid of covered tiles that may contain gems or mines.
# The agent can only uncover one tile at a time.
# The agent can only uncover a tile that has not been uncovered yet.
# Once the agent safely uncovers a tile, the tile will be uncovered and the agent will receive a reward of 1 if the tile contains a gem or -1 if the tile contains a mine.
# Once the agent uncovers a mine, the game is over and the agent will receive a reward of -1.
# The agent will receive a reward of 0 for every action that does not result in the game ending.
# implement this idea

# Path: game.py
import random
class MinesweeperGame:
    def __init__(self):
        self.board = [[0 for i in range(5)] for j in range(5)]
        self.reward_board = {x: 0 for x in range(25)}
        self.n_mines = 3
        self.n_gems = 25 - self.n_mines 
        self.n_cells_uncovered = 0
        self.n_cells_to_uncover = 1
        self.reward = 0
        self.positions = [(x, y) for x in range(5) for y in range(5)]
        self.shuffled_positions = self.fisher_yates_shuffle(self.positions)
        self.placed_gems = 0
        self.placed_mines = 0
        self.create_board()
        self.place_mines()
        self.place_gems()

    def create_board(self):
        for i in range(5):
            for j in range(5):
                self.board[i][j] = 0

    def fisher_yates_shuffle(self,array):
        for i in range(len(array)):
            j = random.randint(0, i)
            array[i], array[j] = array[j], array[i]
        return array



    def place_gems(self):
        for i in range(self.n_gems):
            while True:
                x = random.randint(0, 4)
                y = random.randint(0, 4)
                index = self.get_index(x, y)
                if self.reward_board[index] == 0:
                    self.reward_board[index] = 1
                    break

    def place_mines(self):
        for i in range(self.n_mines):
            x, y = self.shuffled_positions[i]
            index = self.get_index(x, y)
            if self.reward_board[index] == 0:
                self.reward_board[index] = -1
                
    # define a function that takes x, y coordinates and returns index from 0 - 24
    def get_index(self, x, y):
        return x * 5 + y
                
    def place_gem_or_mine(self, x, y):
        
        if self.placed_gems == self.n_gems and self.placed_mines == self.n_mines:
            # Gem coordinates
            return self.board[x][y]
        
        a = random.randint(0, 4)
        b = random.randint(0, 4)
        
        c, d = self.shuffled_positions[self.placed_mines + 1 if self.placed_mines > 0 and self.placed_mines < self.n_mines  else 1]
        print(f'Gem coordinates: ({a}, {b}) Mine coordinates: ({c}, {d}) User coordinates: ({x}, {y})')
        if(self.board[a][b] == 0 
           and self.board[c][d] == 0 
           and a != c 
           and b != d):
            self.board[a][b] = 1
            self.board[c][d] = -1
            self.placed_gems += 1
            self.placed_mines += 1

            
            
        return self.board[x][y]

    def uncover_cell(self, action):
        x = action // 5
        y = action % 5
        # print(f'Reward board {self.reward_board}')
        # self.reward = self.place_gem_or_mine(x, y)
        # return self.reward
        
        index = self.get_index(x, y)
        
        print(f"Uncovering cell at ({x}, {y})")
        if self.reward_board[index] == -1:
            self.board[x][y] = -1
            self.reward = -1
            self.n_cells_uncovered += 1
            
            return self.reward
        elif self.reward_board[index] == 1:
            self.board[x][y] = 1
            self.reward = 1
            self.n_cells_uncovered += 1
            
            return self.reward
        else:
            self.reward = 0
            self.n_cells_uncovered += 1
            print(f"Reward: {self.reward}")
            return self.reward
        
    def is_game_over(self):
        if self.n_cells_uncovered == self.n_cells_to_uncover or self.reward == -1:
            return True
        else:
            return False

    def get_reward(self):
        return self.reward
    
    def print_board(self):
        for i in range(5):
            for j in range(5):
                print(self.board[i][j], end=" ")
            print()
        print()