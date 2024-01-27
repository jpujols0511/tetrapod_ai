# Path: main.py
# Create a main.py file that will be used to run the program.
# The main function will be used to run the program.
# The program will be run using the main function.

# import agent.agent as agent

# def main():
#     n_games = 1000
#     epsilon = 0.9
#     gamma = 0.99
#     batch_size = 1000
#     game = agent.QAgent(n_games, epsilon, gamma)
#     game.play(True)
    
# if __name__ == "__main__":
#     main()


import asyncio
import websockets
import json
from agent.agent import QAgent

async def hello(websocket, path):
    while True:
        try:
            data = await websocket.recv()
            reply = f"Data recieved as:  {data}!"
            json_data = json.loads(data)
            epsilon = 0.9
            gamma = 0.99
            n_games = json_data['games']
            game = QAgent(n_games, epsilon, gamma)
        
            # Init the game        
            if(json_data['type'] == 'new_game' and json_data['playing'] == False):
                json_data['playing'] = True
                await websocket.send(json.dumps(json_data))
                
            while json_data['game_number'] < json_data['games']:
                try:
                    
                    json_data = json.loads(await websocket.recv())
                
                    if(json_data['playing'] == True and json_data['over'] == False):
                        print(f"Playing... Game: {json_data['game']} Game #: {json_data['game_number']}")
                    
                        game_state = json_data['state']
                        print(f'Game state: {game_state} game number {json_data["game_number"]} ')
                        game.init_game(game_state)
                        json_data['move'] = game.get_move(game_state)
                    
                        print(json_data['move'])
                        # Send move
                        await websocket.send(json.dumps(json_data))
                    
                    if(json_data['playing'] == True and json_data['over'] == True):
                        print(f'game over - starting again {json_data}')
                        
                        await websocket.send(json.dumps(json_data))
                        break
                    
                except:
                    print(f"Terminated")
                    break
                    
            if json_data['game_number'] == json_data['games']:
                print(f"Terminated")
                break
            # if json_data['over'] == True:
            #     break    
            
            
        except websockets.ConnectionClosed:
            print(f"Terminated")
            break

        
start_server = websockets.serve(hello, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


