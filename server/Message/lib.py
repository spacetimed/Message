import asyncio
import websockets

class Server:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.start = websockets.serve(self.handleNewClient, self.host, self.port)

    async def handleNewClient(self, websocket, path):
        print('New Client=>', websocket, path)
        try:
            while True:
                message = await websocket.recv()
                print('Recv=>', message)
        except websockets.ConnectionClosed:
            print('DC')

class Client:
    def __init__(self, websocket, path):
        print('New Client!')