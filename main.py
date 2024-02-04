# Path: main.py
# Create a main.py file that will be used to run the program.
# The main function will be used to run the program.
# The program will be run using the main function.

# import asyncio
# import websockets
# import json
# from agent.agent import QAgent

# # @todo - train the model while is playing with the website (currently not being trained)

# async def hello(websocket, path):
#     while True:
#         try:
#             data = await websocket.recv()
#             reply = f"Data recieved as:  {data}!"
#             json_data = json.loads(data)
#             epsilon = 0.9
#             gamma = 0.99
#             n_games = json_data['games']
#             game = QAgent(n_games, epsilon, gamma)
            
#             if json_data['game_number'] > json_data['games']:
#                 print(f"Terminated")
#                 break
        
#             # Init the game        
#             if(json_data['type'] == 'new_game' and json_data['playing'] == False):
#                 json_data['playing'] = True
#                 await websocket.send(json.dumps(json_data))
                
#             while json_data['game_number'] <= json_data['games']:
#                 try:
                    
#                     json_data = json.loads(await websocket.recv())
                
#                     if(json_data['playing'] == True and json_data['over'] == False):
#                         print(f"Playing... Game: {json_data['game']} Game #: {json_data['game_number']}")
                    
#                         game_state = json_data['state']
#                         print(f'Game state: {game_state} game number {json_data["game_number"]} ')
#                         game.init_game(game_state)
#                         json_data['move'] = game.get_move(game_state)
                    
#                         print(json_data['move'])
#                         # Send move
#                         await websocket.send(json.dumps(json_data))
                    
#                     if(json_data['playing'] == True and json_data['over'] == True):
#                         print(f'game over - starting again {json_data}')
                        
#                         await websocket.send(json.dumps(json_data))
#                         break
                    
#                 except:
#                     print(f"Terminated")
#                     break
                
            
#         except websockets.ConnectionClosed:
#             print(f"Terminated")
#             break

        
# start_server = websockets.serve(hello, "localhost", 8080)

# asyncio.get_event_loop().run_until_complete(start_server)
# asyncio.get_event_loop().run_forever()

#  63 - 69.9% - 1000 games 

# 22 gems 3 mines

# import agent.agent as agent

# def main():
#     n_games = 1000
#     epsilon = 0.9
#     gamma = 0.99
#     batch_size = 1000
#     game = agent.QAgent(n_games, epsilon, gamma, True)
#     game.play(True)
    
# if __name__ == "__main__":
#     main()

# import pickle
# import gym
# from agent.dsnagent import DSNAgent
# from game.mines import MinesGameEnv
# import numpy as np
# import torch
# import matplotlib.pyplot as plt

# # Register the environment
# gym.register(
#     id='MinesGameEnv-v0',
#     entry_point='game.mines:MinesGameEnv'
# )
# env = gym.make('MinesGameEnv-v0')

# done = False
# agent = DSNAgent(env)

# num_episodes = 1000
# max_steps = 2

# epsilon = 1
# reward_list_sarsa = []
# final_rewards = []
# wins = 0

# np.random.seed(420)

# for episode in np.arange(num_episodes):
#     state =  env.reset()
   
#     reward_sum = 0
#     action = agent.epsilon_greedy_action(torch.from_numpy(np.array(state)).float().view(-1), epsilon)    
#     x = action // 5
#     y = action % 5
#     state_1, reward, terminal, info = env.step((x, y))
    
#     state_1 = info['state']
    
#     print(f'state_1, reward, terminal, info {state_1, reward, terminal} episode {episode} action {x, y} episilon: {epsilon}')
    
#     #Checks for early Finish
#     if terminal:
        
#         action_1 = agent.epsilon_greedy_action(torch.from_numpy(np.array(state_1)).float().view(-1), epsilon)
#         agent.replay_buffer.add_to_buffer((state, state_1, [action], [action_1], [reward],[terminal]))
        
#         reward_sum += reward
        
#         final_rewards.append(reward)
        
#         reward_list_sarsa.append(reward_sum)
        
        
#         print('Early finish!', 'reward =', reward)
#         print('episode:', episode, 'sum_of_rewards_for_episode:', reward_sum, 'final reward', \
#                       reward, 'epsilon:', epsilon)
        
#         #If not finished after first action - continue learning
#     else:
#         for i in np.a(max_steps):
            
#             action_1 = agent.epsilon_greedy_action(torch.from_numpy(np.array(state_1)).view(-1).float(), epsilon)
#             x = action_1 // 5
#             y = action_1 % 5
#             state_2, reward_1, terminal_1, info = env.step((x, y))

#             agent.replay_buffer.add_to_buffer((state, state_1, [action], [action_1], [reward],[terminal]))

#             reward_sum += reward
#             state_2 = info['state']
#             state = state_1
#             state_1 = state_2
#             action = action_1
#             reward = reward_1
#             terminal = terminal_1
            
#             print(f'state_1, reward, terminal, info {state_1, reward, terminal, info} episode {episode}')

#             if terminal:

#                 action_1 = agent.epsilon_greedy_action(torch.from_numpy(np.array(state_1)).float().view(-1), epsilon)

#                 agent.replay_buffer.add_to_buffer((state, state_1, [action], [action_1], [reward],[terminal]))

#                 reward_sum += reward
                
#                 final_rewards.append(reward)
                
#                 reward_list_sarsa.append(reward_sum)

#                 print('episode:', episode, 'sum_of_rewards_for_episode:', reward_sum, 'final reward', \
#                       reward, 'epsilon:', epsilon)

                
#                 break
            
#     agent.update_s(128) 
    
#     if epsilon > 0.2:
#         epsilon *= 0.995
    
#     if epsilon <= 0.2:
#         epsilon = 0.2
        
# print(final_rewards, reward_list_sarsa)
        
# def m_a(values, window=50):
#     weight = np.repeat(1.0, window)/window
#     smas = np.convolve(values,weight,'valid')
#     return smas
# print(reward_list_sarsa)
# smas = m_a(reward_list_sarsa)

# if len(smas) > 9:
#     fig, ax = plt.subplots(figsize=(10,5))
#     ax.plot(reward_list_sarsa)
#     ax.plot(smas)
#     ax.set_ylabel('Rewards')
#     ax.set_xlabel('Episodes')
#     ax.set_title('Deep SARSA learning (600 episodes training)')
        

# ep_1000 = reward_list_sarsa
# with open("rewards_ep.txt", "wb") as fp:
#     pickle.dump(ep_1000, fp)


import gym
from agent.q_agent import Agent
from game.mines import MinesGameEnv
import numpy as np
import torch
from utils.helper import plot_loss

# Register the environment
gym.register(
    id='MinesGameEnv-v0',
    entry_point='game.mines:MinesGameEnv'
)
env = gym.make('MinesGameEnv-v0')

batch_size = 16
discount_factor = 0.99
learning_rate = 0.001
exploration_rate = 0.92

# Initialize the agent
agent = Agent(env, learning_rate, exploration_rate)

# Load the model parameters
agent.model.load_state_dict(torch.load("model_weights.pth"))

agent.target_network.load_state_dict(agent.model.state_dict())

# Train the agent
num_episodes = 500
losses = []  # Keep track of losses
wins = 0
most_gems_collected = 0
looses = 0

for episode in np.arange(num_episodes):
    state = env.reset()
    done = False

    while not done:
        # Choose an action based on the current state
        action = agent.epsilon_greedy_action(torch.cat((state if type(state) is torch.Tensor else torch.tensor(state).float().view(-1), torch.tensor([0])), 0), agent.exploration_rate)
        print(f'action: {action // 5, action % 5}')
        # Take the action and observe the result
        next_state, reward, done, info = env.step(action)
        
        if done == True and reward > 0:
            wins += 1
            if env.num_gems_collected > most_gems_collected:
                most_gems_collected = env.num_gems_collected
        elif done == True and reward <= 0:
            looses += 1
        
        next_state = torch.from_numpy(info['state']).float().view(-1)
        
        state_game_end = torch.cat([torch.tensor(state).float().view(-1), torch.tensor(info['end_game']).float().view(-1)])
        state_game_end_next = torch.cat([next_state, torch.tensor(info['end_game']).float().view(-1)])
        action = torch.tensor(action).view(-1)
        
        # Store the experience in the replay buffer
        agent.replay_buffer.add(state_game_end, action, reward, state_game_end_next, done)
        
        if len(agent.replay_buffer.buffer) > batch_size:
            batch = agent.replay_buffer.sample(batch_size)
            loss = agent.model.train_step(batch, agent.target_network, learning_rate, discount_factor)
            agent.update_target_network(tau=0.1)
            loss = loss.detach().numpy()
            losses.append(loss)
        # Update the state
        state = next_state
    
    env.print_board()  
     # Update the target network
    if episode % 10 == 0:
        agent.target_network.load_state_dict(agent.model.state_dict())

    # Print the episode reward
    print(f"Episode {episode}: Reward {reward}")

    # Improve the agent's performance
    # agent.improve()

    # Update the target network
    agent.update_target_network(tau=0.1)
    
print(f'wins {wins} looses {looses} most_gems_collected {most_gems_collected}')

# Plot the loss function
if(len(losses) > 0):
    plot_loss(losses, num_episodes)

# Evaluate the agent's performance
average_reward, average_episode_length, win_rate = agent.evaluate()
print(f"Average reward: {average_reward}")
print(f"Average episode length: {average_episode_length}")
print(f"Win rate: {win_rate}")

# Save the model parameters
torch.save(agent.model.state_dict(), "model_weights.pth")
# Continue training or re-evaluate the agent...