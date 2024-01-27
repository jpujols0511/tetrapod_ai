# Implement a websocket server that will connect the javascript service to the python service
# This will allow the javascript service to send data to the python service and viceversa

import asyncio
import websockets
import json
from agent.agent import QAgent

async def hello(websocket, path):
    while True:
        try:
            data = await websocket.recv()
        except websockets.ConnectionClosed:
            print(f"Terminated")
            break

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
            
        json_data = json.loads(data)
        
        if(json_data['playing'] == True and json_data['over'] == False):
            print(f"Playing... Game: {json_data['game']} Game #: {json_data['game_number']}")
        
            game_state = json_data['state']
            game.init_game(game_state)
            json_data['move'] = game.get_move(game_state)
            
            # Send move
            await websocket.send(json.dumps(json_data))
            
        # print(json_data, reply)
        print(reply, json_data)
        

start_server = websockets.serve(hello, "localhost", 8080)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


