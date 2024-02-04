import torch as torch
import torch.nn as nn
import numpy as np

def sarsa(env, q_network, num_episodes, alpha=0.5, gamma=0.95, epsilon=0.1):
    optimizer = torch.optim.Adam(q_network.parameters())
    loss_fn = nn.MSELoss()

    for _ in range(num_episodes):
        state = env.reset()
        state_tensor = torch.tensor(state, dtype=torch.float32)
        action_values = q_network(state_tensor)
        action = torch.argmax(action_values).item() if np.random.uniform() > epsilon else env.action_space.sample()

        while True:
            next_state, reward, done = env.step(action)
            next_state_tensor = torch.tensor(next_state, dtype=torch.float32)
            next_action_values = q_network(next_state_tensor)
            next_action = torch.argmax(next_action_values).item() if np.random.uniform() > epsilon else env.action_space.sample()

            target = reward + gamma * next_action_values[next_action]
            loss = loss_fn(action_values[action], target)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            state, action, action_values = next_state, next_action, next_action_values

            if done:
                break
